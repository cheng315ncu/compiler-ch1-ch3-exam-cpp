---
title: "Compiler - Predict 與 LL1 考試實作"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "[[Compiler - Predict set 與 recursive descent]]；[[Compiler-Ch2-p012-p022#PPT p.018｜Predict set：{id} 與 {print}]]；[[Compiler-Ch2-p023-p035#PPT p.023｜Stmts 的 predict set 怎麼算]]"
source_pages: "Ch2 p.18–24；FIRST/FOLLOW 正式名稱為補充"
---

# Compiler - Predict 與 LL1 考試實作

> [!abstract] 題型定位
> Ch2 predict set 的補充工具；FIRST/FOLLOW 的正式名稱預告於 Ch4，列為較低優先的延伸。 以下為 **C++ 實作（補充）**；[[Complier/Code/exam/ll1.cpp|單檔原碼]] · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

## 契約與模式

`--table（預設）／--check`

第一行 P（1..1000），接 P 行 LHS -> RHS，符號空白分隔，一行一個 alternative，# 單獨表示 epsilon。第一 LHS 為 start；所有 LHS 為 nonterminal，其他 RHS 為 terminal。$ 保留 EOF，不寫進 grammar。預設印 FIRST/FOLLOW/SELECT、所有非空 table cells、LL1 YES/NO；--check 讀後續每行 terminal tokens，補 $，印 ACCEPT/REJECT；空行測 epsilon。

## 演算法與易錯點

反覆聯集到 FIRST 固定，再求 start FOLLOW={$} 與各 suffix 的 FIRST／nullable 直到 FOLLOW 固定。SELECT=FIRST(RHS) 去 epsilon；nullable 時加 FOLLOW(LHS)。同格多規則為 CONFLICT；recognizer 用非遞迴 stack。

epsilon 不放 FOLLOW 或輸入；SELECT epsilon 分支加 FOLLOW；FOLLOW 看整個 suffix。ac 的 Prog → Dcls Stmts $ 應輸入 Prog → Dcls Stmts，本工具已補 EOF。# 不可與其他 RHS 並列，| 必須拆成多行。

> [!note] 支援範圍
> 不自動消除左遞迴／left factoring；非 LL(1) 不等於 ambiguous。--check 遇 conflict 報錯；最多 1,000,000 parsing steps。缺少 table cell 表示 error。RHS 名称是否為 nonterminal 由 LHS 集合決定，拼錯名稱會被當 terminal。

## 考場修改位置

只求 FIRST/FOLLOW 可刪 table／recognizer；要求全矩形表格則補印缺格為 error。解析來源 expression 先由 lexer 把實際數字映射為 num token，再送 --check。

較低準備優先度：這是 predict 的通用延伸，不能宣稱 FIRST/FOLLOW 正式考試範圍已確認。

## 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/ll1.cpp -o /tmp/ll1
/tmp/ll1 < Complier/Code/exam/ll1.in
```

輸入：

```text
4
E -> T R
R -> + T R
R -> #
T -> num
```

預設輸出：

```text
FIRST(E)={num} FOLLOW(E)={$}
FIRST(R)={#,+} FOLLOW(R)={$}
FIRST(T)={num} FOLLOW(T)={$,+}
SELECT(1)={num}
SELECT(2)={+}
SELECT(3)={$}
SELECT(4)={num}
M[E,num]=1
M[R,$]=3
M[R,+]=2
M[T,num]=4
LL1 YES
```

其他測例：num + num 接受；num + 拒絕；S → S a／S → b 會列 conflict。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

## 完整 C++17 程式

```cpp
// FIRST / FOLLOW / SELECT / LL(1) table. P productions, each "A -> X Y".
// One alternative per line; '#' alone is epsilon; '$' is reserved EOF.
// Start symbol = first LHS. --check reads whitespace-separated token sequences afterward.
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
// 符號採字串，所以 num、Expr、ExprTail 不必改成單字元代號。
using Set = std::set<std::string>;
struct Rule { std::string lhs; std::vector<std::string> rhs; };
// 計算整段 RHS 的 FIRST，不是只看第一字元。
// 如果前方可為 epsilon，還要繼續合併下一符號的 FIRST。
Set first_sequence(const std::vector<std::string>& rhs, std::size_t start, const std::map<std::string, Set>& first) {
    Set result;
    for (std::size_t i = start; i < rhs.size(); ++i) {
        // first 表只含 nonterminal；找不到表示 terminal，自己就是 FIRST。
        const auto it = first.find(rhs[i]);
        if (it == first.end()) { result.insert(rhs[i]); return result; }
        for (const auto& t : it->second) if (t != "#") result.insert(t);
        if (!it->second.count("#")) return result;
    }
    // 整段 RHS 都 nullable，或 suffix 是空串，FIRST 才包含 epsilon。
    result.insert("#"); return result;
}
// 只有集合真的增加才回傳 true；用這個旗標決定固定點迴圈能否停止。
bool merge(Set& target, const Set& source) { const auto before = target.size(); target.insert(source.begin(), source.end()); return target.size() != before; }
void print_set(const Set& s) { std::cout << '{'; bool first = true; for (const auto& t : s) { if (!first) std::cout << ','; std::cout << t; first = false; } std::cout << '}'; }
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        const std::string mode = argc == 1 ? "--table" : argv[1];
        if (argc > 2 || (mode != "--table" && mode != "--check")) throw std::runtime_error("usage: ll1 [--table|--check]");
        int count; std::string line;
        if (!(std::cin >> count) || count < 1 || count > 1000) throw std::runtime_error("production count must be 1..1000");
        std::getline(std::cin, line);
        if (line.find_first_not_of(" \t\r") != std::string::npos) throw std::runtime_error("production starts on next line");
        std::vector<Rule> rules; Set nonterminals;
        // 一行一條 production、同一 LHS 的替代規則分開寫；不要直接輸入 |。
        for (int i = 0; i < count; ++i) {
            if (!std::getline(std::cin, line)) throw std::runtime_error("missing production");
            std::istringstream input(line); Rule rule; std::string arrow, symbol;
            if (!(input >> rule.lhs >> arrow) || arrow != "->" || rule.lhs == "#" || rule.lhs == "$" || rule.lhs == "|") throw std::runtime_error("expected A -> symbols");
            while (input >> symbol) {
                if (symbol == "$" || symbol == "|") throw std::runtime_error("reserved symbol; use one alternative per line");
                rule.rhs.push_back(symbol);
            }
            // 不允許省略 epsilon 記號；輸入空 RHS 必須明寫 #。
            if (rule.rhs.empty()) throw std::runtime_error("write # for epsilon");
            // # 只可單獨表示 epsilon；內部改用空 vector 表示空 RHS。
            if (rule.rhs.size() == 1 && rule.rhs[0] == "#") rule.rhs.clear();
            else for (const auto& s : rule.rhs) if (s == "#") throw std::runtime_error("epsilon must be alone");
            nonterminals.insert(rule.lhs); rules.push_back(std::move(rule));
        }
        // 先收齊所有 LHS 才知道 nonterminal，避免尚未讀到的規則被當 terminal。
        std::map<std::string, Set> first, follow;
        for (const auto& nt : nonterminals) { first[nt] = {}; follow[nt] = {}; }
        // FIRST 與 FOLLOW 都反覆掃規則到集合不再增加；支援循環相依。
        bool changed;
        do {
            changed = false;
            for (const auto& rule : rules) if (merge(first[rule.lhs], first_sequence(rule.rhs, 0, first))) changed = true;
        } while (changed);
        // 第一條 production 的 LHS 是 start；start 的 FOLLOW 包含 EOF $。
        follow[rules[0].lhs].insert("$");
        do {
            changed = false;
            for (const auto& rule : rules) for (std::size_t i = 0; i < rule.rhs.size(); ++i) {
                if (!nonterminals.count(rule.rhs[i])) continue;
                // 對 A -> α B β：把 FIRST(β) 去掉 epsilon 後加進 FOLLOW(B)。
                auto suffix = first_sequence(rule.rhs, i + 1, first);
                const bool nullable = suffix.erase("#") != 0;
                if (merge(follow[rule.rhs[i]], suffix)) changed = true;
                // β 可空時，再把 FOLLOW(A) 加進 FOLLOW(B)，不能漏掉這個傳播。
                if (nullable && merge(follow[rule.rhs[i]], follow[rule.lhs])) changed = true;
            }
        } while (changed);
        // SELECT = FIRST(RHS) 去 epsilon；若 RHS nullable，再加 FOLLOW(LHS)。
        std::vector<Set> select;
        std::map<std::pair<std::string, std::string>, std::vector<int>> table;
        bool ll1 = true;
        for (std::size_t i = 0; i < rules.size(); ++i) {
            auto s = first_sequence(rules[i].rhs, 0, first);
            if (s.erase("#")) merge(s, follow[rules[i].lhs]);
            select.push_back(s);
            // 表格同一格若有兩條 production 就是 conflict；不可隨便選第一條。
            for (const auto& token : s) { auto& cell = table[{rules[i].lhs, token}]; cell.push_back(static_cast<int>(i)); if (cell.size() > 1) ll1 = false; }
        }
        if (mode == "--table") {
            for (const auto& nt : nonterminals) {
                std::cout << "FIRST(" << nt << ")="; print_set(first[nt]); std::cout << " FOLLOW(" << nt << ")="; print_set(follow[nt]); std::cout << '\n';
            }
            for (std::size_t i = 0; i < rules.size(); ++i) { std::cout << "SELECT(" << i + 1 << ")="; print_set(select[i]); std::cout << '\n'; }
            for (const auto& cell : table) {
                std::cout << "M[" << cell.first.first << ',' << cell.first.second << "]=";
                for (std::size_t i = 0; i < cell.second.size(); ++i) std::cout << (i ? "," : "") << cell.second[i] + 1;
                if (cell.second.size() > 1) std::cout << " CONFLICT";
                std::cout << '\n';
            }
            std::cout << (ll1 ? "LL1 YES\n" : "LL1 NO\n");
        } else {
            // 只能用無衝突的 LL(1) 表做這份 predictive parser。
            if (!ll1) throw std::runtime_error("grammar has LL(1) conflicts");
            while (std::getline(std::cin, line)) {
                std::istringstream input(line); std::vector<std::string> words; std::string word;
                bool accepted = true;
                while (input >> word) { if (word == "$" || word == "#" || nonterminals.count(word)) accepted = false; words.push_back(word); }
                // 輸入自動補 EOF；解析 stack 初始是 $ 與 start，頂端在 vector 尾端。
                words.push_back("$"); std::vector<std::string> stack{"$", rules[0].lhs}; std::size_t pos = 0, steps = 0;
                while (accepted && !stack.empty()) {
                    // ponytail: a finite study budget prevents pathological expansion; raise for larger judges.
                    if (++steps > 1000000) throw std::runtime_error("parse exceeds 1000000 steps");
                    // vector 尾端就是 stack top；push RHS 的順序要反過來。
                    const auto top = stack.back(); stack.pop_back();
                    // terminal 必須匹配 lookahead，才前進輸入位置；nonterminal 只展開，不吃字元。
                    if (!nonterminals.count(top)) { if (top != words[pos]) accepted = false; else ++pos; }
                    else {
                        const auto it = table.find({top, words[pos]});
                        if (it == table.end()) { accepted = false; continue; }
                        // 選到的 RHS 要反向 push，讓最左符號先被 pop／處理。
                        const auto& rhs = rules[it->second[0]].rhs;
                        for (auto r = rhs.rbegin(); r != rhs.rend(); ++r) stack.push_back(*r);
                    }
                }
                // stack 用完且輸入也全用完才接受；只匹配前綴不算成功。
                std::cout << (accepted && pos == words.size() ? "ACCEPT\n" : "REJECT\n");
            }
        }
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
```
