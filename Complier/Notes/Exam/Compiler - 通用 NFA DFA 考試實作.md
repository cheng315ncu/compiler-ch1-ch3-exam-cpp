---
title: "Compiler - 通用 NFA DFA 考試實作"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "[[Compiler-Ch3-p041-p050#PPT p.042｜Subset construction 的核心不變量]]；[[Compiler-Ch3-p041-p050#PPT p.046｜Revised Fig 3.23 演算法與九個 marker]]"
source_pages: "Ch3 p.42、p.46–50"
---

# Compiler - 通用 NFA DFA 考試實作

> [!abstract] 題型定位
> Ch3 子集構造直接延伸：由固定 HW5 圖改為讀 stdin 的任意轉移表。 以下為 **C++ 實作（補充）**；[[Complier/Code/exam/nfa_to_dfa.cpp|單檔原碼]] · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

## 契約與模式

`--check（預設）／--trace／--table`

n m start k；k 個 final states；alphabet 字串；m 行 from symbol to。states 0..n-1，# 代表 epsilon，不在 alphabet。其後每行完整待辨識字串，空行為 epsilon，預設 ACCEPT/REJECT。--trace 印每一步 NFA 集合；--table 只印完整 DFA，不處理後面案例。

## 演算法與易錯點

起點 closure({start})；對集合 S、每個 c 計算 closure(move(S,c))。新集合加入 worklist，以 map 去重；空集合也建為 sink。辨識同時計算 direct NFA 與 DFA，確認結果一致。

closure 要到固定點，不止一層；每次 move 後再 closure；集合含任一 final 即接受。接受狀態仍有外出邊，不能提早停止。編號依 alphabet 發現順序，與教材 A/B 不必相同。

> [!note] 支援範圍
> n≤256、m≤65536、DFA≤4096 subsets，超過明確失敗。子集構造最壞會指數成長。alphabet 為非空、不重複、非空白的單 byte 字元字串，不含 #；純 epsilon 語言可用未使用的 dummy alphabet 字元。沒有 RE→Thompson NFA parser 或最小化。

## 考場修改位置

1 起算 states 可輸入時減 1；多起點改 initial closure 集合；只求辨識可刪 construct，直接保留 closure/move/direct simulation。需要 Unicode 字母表則改 symbol 表示，不能按 UTF-8 byte 當一個字元。

用 std::set 處理多於 32 個 states；每個 DFA state×alphabet 都列出，包括 sink。

## 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/nfa_to_dfa.cpp -o /tmp/nfa_to_dfa
/tmp/nfa_to_dfa < Complier/Code/exam/nfa_to_dfa.in
```

輸入：

```text
6 7 0 1
5
bcd
0 # 1
0 # 4
1 b 2
2 c 3
3 # 1
3 # 4
4 d 5
d
bcd
bcbcd

bc
bd
bcdd
```

預設輸出：

```text
ACCEPT
ACCEPT
ACCEPT
REJECT
REJECT
REJECT
REJECT
```

其他測例：配套是 (bc)*d 的 NFA 改成 0 起算；d/bcd/bcbcd 接受，空字串/bc/bd/bcdd 拒絕。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

## 完整 C++17 程式

```cpp
// Generic epsilon-NFA. Header: n m start k; k finals; alphabet; m edges.
// States 0..n-1. Edge symbol '#' means epsilon. Then one complete word per line.
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using States = std::set<int>;
struct NFA {
    int start = 0;
    States finals;
    std::string alphabet;
    std::vector<std::map<char, States>> edges;
    States closure(States states) const {
        std::vector<int> pending(states.begin(), states.end());
        while (!pending.empty()) {
            const int s = pending.back(); pending.pop_back();
            const auto it = edges[s].find('#');
            if (it != edges[s].end()) for (int next : it->second) if (states.insert(next).second) pending.push_back(next);
        }
        return states;
    }
    States move(const States& states, char c) const {
        States result;
        for (int s : states) {
            const auto it = edges[s].find(c);
            if (it != edges[s].end()) result.insert(it->second.begin(), it->second.end());
        }
        return result;
    }
    bool accepts(const States& states) const { for (int s : states) if (finals.count(s)) return true; return false; }
};
struct DFA { std::vector<States> states; std::vector<std::vector<int>> next; };
DFA construct(const NFA& nfa) {
    DFA dfa; std::map<States, int> ids;
    const auto record = [&](const States& states) {
        const auto it = ids.find(states);
        if (it != ids.end()) return it->second;
        // ponytail: subset construction can be exponential; fail explicitly above this study ceiling.
        if (dfa.states.size() >= 4096) throw std::runtime_error("DFA exceeds 4096 states");
        const int id = static_cast<int>(dfa.states.size());
        ids[states] = id; dfa.states.push_back(states); dfa.next.emplace_back(nfa.alphabet.size(), 0);
        return id;
    };
    record(nfa.closure({nfa.start}));
    for (std::size_t i = 0; i < dfa.states.size(); ++i) for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) {
        const int target = record(nfa.closure(nfa.move(dfa.states[i], nfa.alphabet[c])));
        dfa.next[i][c] = target;
    }
    return dfa;
}
void print_set(const States& states) {
    std::cout << '{'; bool first = true;
    for (int s : states) { if (!first) std::cout << ','; std::cout << s; first = false; }
    std::cout << '}';
}
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        const std::string mode = argc == 1 ? "--check" : argv[1];
        if (argc > 2 || (mode != "--check" && mode != "--table" && mode != "--trace")) throw std::runtime_error("usage: nfa_to_dfa [--check|--table|--trace]");
        NFA nfa; int n, m, k;
        if (!(std::cin >> n >> m >> nfa.start >> k) || n < 1 || n > 256 || m < 0 || m > 65536 || k < 0 || k > n)
            throw std::runtime_error("invalid NFA header (n<=256, m<=65536)");
        const auto valid = [&](int s) { return s >= 0 && s < n; };
        if (!valid(nfa.start)) throw std::runtime_error("invalid start state");
        for (int i = 0, s; i < k; ++i) {
            if (!(std::cin >> s) || !valid(s) || !nfa.finals.insert(s).second) throw std::runtime_error("invalid/duplicate final state");
        }
        if (!(std::cin >> nfa.alphabet) || nfa.alphabet.find('#') != std::string::npos ||
            std::set<char>(nfa.alphabet.begin(), nfa.alphabet.end()).size() != nfa.alphabet.size()) throw std::runtime_error("invalid alphabet");
        nfa.edges.resize(static_cast<std::size_t>(n));
        for (int i = 0; i < m; ++i) {
            int from, to; std::string symbol;
            if (!(std::cin >> from >> symbol >> to) || !valid(from) || !valid(to) || symbol.size() != 1 ||
                (symbol != "#" && nfa.alphabet.find(symbol[0]) == std::string::npos)) throw std::runtime_error("invalid edge");
            nfa.edges[from][symbol[0]].insert(to);
        }
        std::string line; std::getline(std::cin, line);
        if (line.find_first_not_of(" \t\r") != std::string::npos) throw std::runtime_error("words must start on the next line");
        const auto dfa = construct(nfa);
        if (mode == "--table") {
            std::cout << "DFA start=0 states=" << dfa.states.size() << '\n';
            for (std::size_t i = 0; i < dfa.states.size(); ++i) {
                std::cout << i << ' '; print_set(dfa.states[i]);
                std::cout << (nfa.accepts(dfa.states[i]) ? " accept" : " reject");
                for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) std::cout << ' ' << nfa.alphabet[c] << "->" << dfa.next[i][c];
                std::cout << '\n';
            }
        } else while (std::getline(std::cin, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            int state = 0; States nstates = nfa.closure({nfa.start}); bool valid_word = true;
            if (mode == "--trace") { print_set(nstates); }
            for (char c : line) {
                const auto index = nfa.alphabet.find(c);
                if (index == std::string::npos) { valid_word = false; if (mode == "--trace") std::cout << " --invalid--> {}"; break; }
                state = dfa.next[state][index]; nstates = nfa.closure(nfa.move(nstates, c));
                if (mode == "--trace") { std::cout << " --" << c << "--> "; print_set(nstates); }
            }
            if (valid_word && nfa.accepts(nstates) != nfa.accepts(dfa.states[state])) throw std::runtime_error("NFA/DFA mismatch");
            if (mode == "--trace") std::cout << ' ';
            std::cout << (valid_word && nfa.accepts(dfa.states[state]) ? "ACCEPT\n" : "REJECT\n");
        }
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
```
