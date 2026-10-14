---
title: "Compiler - Ch1-Ch3 作業完整 C++17 實作"
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/course-note
  - course/compiler
  - source/fischer-cytron-leblanc
chapter: [1, 2, 3]
source:
  - "[[Complier/Inbox/Ch01 introduction.pptx]]"
  - "[[Complier/Inbox/Ch02 a simple compiler.pptx]]"
  - "[[Complier/Inbox/Ch03 scanning.pptx]]"
source_pages: "Ch1 PPT 25–30；Ch2 PPT 39–46；Ch3 PPT 53–60"
---

# Compiler - Ch1-Ch3 作業完整 C++17 實作

> [!abstract] 程式入口
> **C++ 實作（補充）**：兩份獨立、有 `main()` 的 C++17 程式。[[Complier/Code/ch02/ac_homework.cpp|ac_homework.cpp]] 完成 ac 的詞法分析（scanning）、語法分析（parsing）、剖析樹（parse tree）、抽象語法樹（AST）、語意分析（semantic analysis）與 dc 產碼；[[Complier/Code/ch03/automata_homework.cpp|automata_homework.cpp]] 完成兩題非確定／確定有限自動機（NFA／DFA）。本頁下半部收錄兩份**完整程式碼**，供文字鏡像閱讀。實際編譯請用 `.cpp` 原檔。

[[Compiler - 知識庫首頁|回首頁]] · [[Compiler - ac 編譯器全流程]] · [[Compiler - NFA 到 DFA 的完整構造]]

考試可攜帶的擴充版：[[Compiler - Ch1-Ch3 考試 C++ 程式集]]，含 HTML parser 等六份新程式與全部八份原碼的列印 PDF。

## 作業範圍與來源

| 作業 | 來源 | 本次交付 |
|---|---|---|
| Ch1 第 4 題：編譯期／執行期錯誤 | [[Compiler-Ch1-p021-p030#PPT p.025｜習題 4：compile-time 與 run-time 錯誤|p.25–26]] | 原題是問答；`--check` 示範靜態拒絕非法程式，不執行 C++ 除零 |
| Ch1 第 8 題：JVM interpreter | [[Compiler-Ch1-p021-p030#PPT p.027｜習題 8：JVM interpreter 為何較容易|p.27–28]] | 原題是問答，見下方觀念解答 |
| Ch1 第 11 題：產生 C 的利弊 | [[Compiler-Ch1-p021-p030#PPT p.029｜習題 11：以 C 當萬用組合語言|p.29–30]] | 原題是問答，見下方觀念解答 |
| Ch2 HW1：依 Fig.2.1 建 parse tree | [[Compiler-Ch2-p036-p046#PPT p.039｜習題 1：畫 parse tree|p.39–40]] | `ac_homework --parse-tree`，包含 terminal、詞素、epsilon、$ |
| Ch2 HW2(a)：建 AST | [[Compiler-Ch2-p036-p046#PPT p.042｜習題 2(a) 教材解答：AST|p.41–42]] | `--ast`；`--typed-ast` 顯示型別提升節點 |
| Ch2 HW2(b)：語意分析／教材常數摺疊 | [[Compiler-Ch2-p036-p046#PPT p.043｜習題 2(b) 教材解答：常數摺疊|p.43]] | `--check`；`--ast --fold` 將 `x+30+1` 化成 `x+31` |
| Ch2 HW2(c)：產生碼 | [[Compiler-Ch2-p036-p046#PPT p.044｜習題 2(c) 教材解答：產生的碼|p.44]] | 預設輸出 dc；加 `--fold` 對齊本題教材摺疊後的碼 |
| Ch2 HW3(a)(b)(c)／Ch3 HW3 | [[Compiler-Ch2-p036-p046#PPT p.045｜習題 3：擴充 scanner|Ch2 p.45–46]]、[[Compiler-Ch3-p051-p060#PPT p.053｜作業 3：keyword 與可選科學記號|Ch3 p.53–54]] | 同一 scanner 支援 `f/float`、`i/int`、可選帶正負號的 exponent |
| Ch3 HW5(d)：`(bc)*d` | [[Compiler-Ch3-p051-p060#PPT p.055｜作業 5(d)：(bc)*d 的語言|p.55–57]] | `automata_homework 5d`；`5d --table` 印 NFA 邊與完整 DFA |
| Ch3 HW5(a)：`(a\|(bc)*d)+` | [[Compiler-Ch3-p051-p060#PPT p.058｜作業 5(a)：(a 或 (bc)*d)+ 的分組與正閉包|p.58–60]] | `automata_homework 5a`；`5a --table` 印 NFA 邊與完整 DFA |

原始 OCR 已與既有逐頁筆記交叉核對：[[Complier/Output/Ch01 introduction--0854d720-.document-rfLphW/auto/Ch01 introduction.md]]、[[Complier/Output/Ch02 a simple compiler--d580fadd-.document-YWemcl/auto/Ch02 a simple compiler.md]]、[[Complier/Output/Ch03 scanning--74ffa97a-.document-iPjp26/auto/Ch03 scanning.md]]。原料保持不變。本次只實作投影片列出的題目，不假定未提供的教科書其他小題或考試題目。

## Linux／DOMjudge 編譯與輸入規則

在 vault 根目錄操作；執行檔放 `/tmp`：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/ch02/ac_homework.cpp -o /tmp/ac_homework
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/ch03/automata_homework.cpp -o /tmp/automata_homework
/tmp/ac_homework < Complier/Code/ch02/ac_homework.in
/tmp/ac_homework --fold < Complier/Code/ch02/ac_homework.in
/tmp/automata_homework 5a < Complier/Code/ch03/automata_homework.in
```

只使用標準 C++ 標頭；沒有 `windows.h`、`conio.h`、`getch()`、`gets()`、`system()`、`bits/stdc++.h`、變長陣列或 flex／bison 依賴。程式從標準輸入讀取、結果寫至標準輸出，沒有提示字串；錯誤只寫到標準錯誤並回傳 1。ac 將 CR、LF、tab 等視為空白；自動機逐行讀取時只去掉行尾的一個 `\r`，保留其他空白作為不合法字元。

> [!warning] 提交格式邊界
> 尚未提供 DOMjudge 的實際題目、限制與輸出格式。以下是**投影片作業參考程式的明確契約**，不是已獲評測 Accepted 的提交。ac 無參數預設輸出 dc；自動機需 `5a/5d` 參數。若評測系統不傳命令列參數，依題目固定選擇一題／一種模式，再保留其需要的輸出格式；接受字串的文字也須遵循題目規定。

## ac 程式的契約與範例

從 stdin 讀取**整份** ac 原始碼直到 EOF；不是每行各自一個案例。宣告在敘述之前，變數仍是單一小寫字母，`f/i/p` 是保留字。完整 `float/int` 優先匹配；`floatx` 是 `float` 加 `x`，`fl` 是 `f` 加 `l`，沒有擅自改成多字母識別字。註解、分號、括號、乘除、一元負號不在此 ac 文法內。

```text
Prog  → Dcls Stmts $
Dcls  → Dcl Dcls | epsilon
Dcl   → floatdcl id | intdcl id
Stmts → Stmt Stmts | epsilon
Stmt  → id assign Val Expr | print id
Expr  → plus Val Expr | minus Val Expr | epsilon
Val   → id | inum | fnum
```

| 模式 | stdout |
|---|---|
| `--tokens` | 每行 `token-kind lexeme`，最後一行 `$`；只做詞法分析 |
| `--parse-tree` | 一行完整 S-expression parse tree；只做詞法／語法分析 |
| `--ast` | 一行原始 AST，葉標示 `id x`、數字等；不先檢查語意 |
| `--typed-ast` | 一行語意檢查後的 AST，必要時含 `int2float` |
| `--check` | 全程成功輸出 `OK`；檢查重複宣告、未宣告變數、float 指定給 int |
| `--dc`／無參數 | 每行一條 dc 指令；整份程式成功後才發出結果 |
| `--fold` | 搭配 `--ast/--typed-ast/--check/--dc`；折疊非負整數加法、相鄰整數常數加數 |

`--check` 只做教材的靜態型別規則，不分析變數是否已賦值，不等於執行成功保證。`--typed-ast` 以提升節點展示型別處理，不額外替每個節點印型別欄位。

輸入（[[Complier/Code/ch02/ac_homework.in]]）：

```text
i x
x=100
x=x+30+1
p x
```

`--ast` 輸出：

```text
(Prog intdcl x (= id x 100) (= id x (+ (+ id x 30) 1)) print x)
```

`--ast --fold` 輸出：

```text
(Prog intdcl x (= id x 100) (= id x (+ id x 31)) print x)
```

`--fold` 產生的 dc 碼：

```text
100
sx
0 k
lx
31
+
sx
0 k
lx
p
si
```

本機實際把未摺疊與摺疊碼交給 `dc`，兩者均印 `131`。原 Fig.2.15 範例 `f b i a a=5 b=a+3.2 p b` 產碼後印 `8.2`。

> [!warning] 教材歧義與本程式的補充決定
> Ch2 p.42 的教材 AST 是右結合 `x+(30+1)`。本程式沿用既有 `ac.c` 的**左結合**，所以 `100-30-1` 是 `69`。`--fold` 只在 dc 的精確整數加法語意下重組 `(x+30)+1 → x+(30+1) → x+31`，不重組減法或浮點式。完整 parse tree 仍保留原本右遞迴文法的 `Expr` 結構。
>
> Ch2 p.43 的教材寫「No」，但已宣告的 integer `x` 加整數常數沒有違反已提供的型別規則；因此本程式接受原例，`--check` 印 `OK`。常數摺疊是最佳化，不是修復這份輸入的語意錯誤。原解答的待核對狀態保留在逐頁筆記。

### Scanner 科學記號

題意修正版的數字格式（**補充**）：`[0-9]+([.][0-9]+)?(e[+-]?[0-9]+)?`。保留原題的小寫 `e`；`.1`、`10.`、`1e`、`1e+` 不接受。小數點或 exponent 已開始卻缺數字時直接報詞法錯誤。純數字是 `inum`；有小數點或 exponent 一律是 `fnum`，所以 `123e-22` 不會誤當 integer。這是本程式明示的型別政策。

例如 `--tokens` 對 `12 12.3 1.0e10 123e-22 12e+3` 輸出：

```text
inum 12
fnum 12.3
fnum 1.0e10
fnum 123e-22
fnum 12e+3
$
```

GNU dc 不支援 exponent 表示法，程式將 `123e-22` 精確轉成 `0.0000000000000000000123` 再產碼，避免先用 `double` 帶來捨入。[GNU dc 官方手冊](https://www.gnu.org/software/bc/manual/dc-1.05/html_mono/dc.html)。`5 k`／`0 k` 沿用教材型別提升與重設精度的產碼慣例；本章加減結果仍取決於運算元的小數位數。

**補充限制**：僅 dc 產碼需要展開 exponent；exponent 絕對值上限 10,000、mantissa 文字上限 10,000 字元，超過明確報錯。scanner 與 `--check` 不把浮點值轉成機器數字。整數加法摺疊使用十進位字串相加，沒有 `int/long long` 溢位。採整份輸入與 arena 儲存，記憶體隨輸入／節點量增長；未提供評測規模前不加串流框架。樹輸出、型別檢查、產碼使用迴圈，長加法鏈不依賴深層函式遞迴。

## NFA／DFA 程式的契約與範例

`5d` 辨識 `(bc)*d`；`5a` 辨識 `(a|(bc)*d)+`。一行是一個**完整待辨識字串**，輸出一行 `ACCEPT` 或 `REJECT`；空白行表示空字串，兩題都拒絕。沒有案例數、沒有前後空白修剪，最後一行沒有換行仍可讀取。這是完整字串辨識，不是 maximal-munch token 切分。

```sh
/tmp/automata_homework 5d --table
/tmp/automata_homework 5a --table
```

`--table` 不讀 stdin，先印原 NFA 的全部邊（`epsilon` 代表 λ），再印子集構造（subset construction）所得 DFA。狀態從 0 編號、按 alphabet 廣度優先發現；與教材 A–E 名稱不同但集合相同。包含拒絕 sink `{}`，不省略無轉移格。

| 題目 | 起始集合 | 接受集合 | 完整 DFA 狀態數 |
|---|---|---|---|
| 5(d) | `{1,2,5}` | `{6}` | 5（含 sink） |
| 5(a) | `{1,2,3,6,7,10}` | `{2,3,4,5,6,7,10,12}`、`{2,3,5,6,7,10,11,12}` | 6（含 sink） |

5(d) 接受 `d/bcd/bcbcd`，拒絕空字串、`bc/bd/bcdd`。5(a) 接受 `a/d/ad/bcd/abcbcdad/bcdd`；最後一個是 `bcd` 加 `d` 兩組，不能誤拒絕。程式同時計算 NFA 與 DFA 的結果並檢查一致。原始 NFA 是固定教材圖，32-bit 集合足以放下狀態 1～12；沒有實作未要求的任意 RE parser 或 DFA 最小化。

## Ch1 三題觀念解答

這三題原題沒有要求撰寫程式。第 4 題依教材設定，含編譯期錯誤的程式應先拒絕執行，讓所有原始碼先通過靜態檢查；不能拿「可能不走到那一行」當接受理由。ac 的型別檢查可示範此行為，但 ac 不含除法，沒有冒充能偵測 Ch1 的 `b/0`。

第 8 題依教材，VM interpreter 實作階段較少、較容易開發；缺點是原始碼先變 bytecode，執行時再由 interpreter 處理而增加時間。這是投影片的比較前提，不推廣成所有 JVM 實作的效能結論。

第 11 題依教材，輸出 C 可利用各架構已有的 C 編譯器，提高可攜性；代價是多一道 C → assembly 的翻譯。這與「用 C++ 寫本次 compiler」是不同概念。本次 Ch2 的目標碼仍是教材 dc。

## 驗證與重跑

```sh
python3 Complier/Code/check_cpp_homework.py
python3 Complier/Code/check_cpp_homework.py --sanitize
CXX=g++ python3 Complier/Code/check_cpp_homework.py
```

驗證器只用 Python 標準庫，將二進位檔放暫存目錄。逐字比較配套 `.in/.expected`，檢查教材 parse tree、AST、摺疊／未摺疊 dc 碼、型別提升、錯誤時 stdout 為空、LF／CRLF／無末尾換行、長輸入、5,001 項加法、超過 64-bit 的整數相加；並對兩題全部長度 0～8 的 **97,222** 個字串比較 NFA、DFA 與獨立 Python regular expression。

本次 macOS Clang C++17 在 `-Wall -Wextra -Wpedantic -Werror` 下兩份皆編譯成功，52 項檢查通過；AddressSanitizer／UndefinedBehaviorSanitizer 下同組檢查通過。另以 Zig C++ 交叉編譯 Linux musl 靜態 ELF，ARM64／x86-64 兩目標均檢查。**Linux 實機執行與 DOMjudge Accepted 尚未驗證**；本機 `g++` 名稱實際也指向 Apple Clang，不能聲稱已測 GNU GCC。詳細環境、程式 SHA-256 與實際結果見 `Complier/Review/cpp-homework-validation.json`。Obsidian 文字／連結靜態核對與執行驗證分開，不將 CLI 讀取視為 UI 渲染證據。

## 完整 C++：ac_homework.cpp

來源類別：**C++ 實作（補充）**。以原題與既有 C 實作為基礎，採 ponytail 原則：兩個獨立檔、標準庫、單一 scanner、直接函式與 vector arena；沒有額外套件、工廠、外掛或通用編譯器框架。

```cpp
// Ch2 HW1-3 / Ch3 HW3. C++17, stdin -> stdout; errors -> stderr, exit 1.
// One-letter ac identifiers are preserved. Full keywords use longest match.
#include <algorithm>
#include <array>
#include <iostream>
#include <iterator>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Token { std::string kind, text; std::size_t offset; };
bool digit(char c) { return c >= '0' && c <= '9'; }
bool space(char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '\v' || c == '\f'; }

std::vector<Token> scan(const std::string& source) {
    std::vector<Token> tokens;
    for (std::size_t p = 0; p < source.size();) {
        if (space(source[p])) { ++p; continue; }
        const auto start = p;
        std::string kind;
        const char c = source[p];
        if (digit(c)) {
            kind = "inum";
            while (p < source.size() && digit(source[p])) ++p;
            if (p < source.size() && source[p] == '.') {
                kind = "fnum";
                ++p;
                if (p == source.size() || !digit(source[p]))
                    throw std::runtime_error("lexical: digit required after decimal point at byte " + std::to_string(p));
                while (p < source.size() && digit(source[p])) ++p;
            }
            if (p < source.size() && source[p] == 'e') {
                kind = "fnum"; // Supplement: every exponent literal has float type.
                ++p;
                if (p < source.size() && (source[p] == '+' || source[p] == '-')) ++p;
                if (p == source.size() || !digit(source[p]))
                    throw std::runtime_error("lexical: digit required in exponent at byte " + std::to_string(p));
                while (p < source.size() && digit(source[p])) ++p;
            }
        } else {
            ++p;
            if (c == 'f') { kind = "floatdcl"; if (source.compare(start, 5, "float") == 0) p = start + 5; }
            else if (c == 'i') { kind = "intdcl"; if (source.compare(start, 3, "int") == 0) p = start + 3; }
            else if (c == 'p') kind = "print";
            else if (c >= 'a' && c <= 'z') kind = "id";
            else if (c == '=') kind = "assign";
            else if (c == '+') kind = "plus";
            else if (c == '-') kind = "minus";
            else throw std::runtime_error("lexical: invalid byte at " + std::to_string(start));
        }
        tokens.push_back({kind, source.substr(start, p - start), start});
    }
    tokens.push_back({"$", "", source.size()});
    return tokens;
}

// Exact decimal-point movement: never convert a source literal to double.
std::string decimal(std::string text) {
    constexpr int limit = 10000;
    const auto e = text.find('e');
    int exponent = 0;
    if (e != std::string::npos) {
        auto p = e + 1;
        const bool negative = text[p] == '-';
        if (text[p] == '+' || text[p] == '-') ++p;
        for (; p < text.size(); ++p) {
            if (exponent > (limit - (text[p] - '0')) / 10)
                throw std::runtime_error("codegen: exponent magnitude exceeds 10000");
            exponent = exponent * 10 + (text[p] - '0');
        }
        if (negative) exponent = -exponent;
        text.resize(e);
    }
    if (text.size() > static_cast<std::size_t>(limit))
        throw std::runtime_error("codegen: mantissa exceeds 10000 characters");
    auto dot = text.find('.');
    int point = static_cast<int>(dot == std::string::npos ? text.size() : dot) + exponent;
    if (dot != std::string::npos) text.erase(dot, 1);
    if (point <= 0) text = "0." + std::string(static_cast<std::size_t>(-point), '0') + text;
    else if (point >= static_cast<int>(text.size())) text.append(static_cast<std::size_t>(point) - text.size(), '0');
    else text.insert(static_cast<std::size_t>(point), ".");
    const auto first = text.find_first_not_of('0');
    if (first == std::string::npos) return "0";
    const auto keep = text[first] == '.' ? first - 1 : first;
    return text.substr(keep);
}

enum class Type { none, integer, floating };
struct Node { std::string label; std::vector<int> children; Type type = Type::none; };
using Tree = std::vector<Node>; // Arena indices remain valid across vector growth.
int node(Tree& tree, std::string label, std::vector<int> children = {}) {
    tree.push_back({std::move(label), std::move(children), Type::none});
    return static_cast<int>(tree.size()) - 1;
}

void print_tree(const Tree& tree, int root, std::ostream& out) {
    std::vector<int> pending{root};
    while (!pending.empty()) {
        const int id = pending.back(); pending.pop_back();
        if (id == -1) { out << ')'; continue; }
        if (id == -2) { out << ' '; continue; }
        const auto& n = tree[id];
        if (n.children.empty()) { out << n.label; continue; }
        out << '(' << n.label;
        pending.push_back(-1);
        for (auto it = n.children.rbegin(); it != n.children.rend(); ++it) {
            pending.push_back(*it); pending.push_back(-2);
        }
    }
    out << '\n';
}

struct Parser {
    const std::vector<Token>& tokens;
    std::size_t pos = 0;
    Tree parse, ast;
    std::vector<int> statements;
    explicit Parser(const std::vector<Token>& input) : tokens(input) {}
    bool at(const std::string& kind) const { return tokens[pos].kind == kind; }
    int take(const std::string& kind) {
        if (!at(kind)) throw std::runtime_error("syntax: expected " + kind + " at byte " + std::to_string(tokens[pos].offset));
        const auto t = tokens[pos++];
        if (kind == "$") return node(parse, "$");
        return node(parse, kind, {node(parse, t.text)});
    }
    std::pair<int, int> value() {
        const auto t = tokens[pos];
        if (t.kind != "id" && t.kind != "inum" && t.kind != "fnum")
            throw std::runtime_error("syntax: expected value at byte " + std::to_string(t.offset));
        const int leaf = node(ast, t.kind == "id" ? "id " + t.text : t.text);
        ast[leaf].type = t.kind == "inum" ? Type::integer : t.kind == "fnum" ? Type::floating : Type::none;
        return {node(parse, "Val", {take(t.kind)}), leaf};
    }
    int program() {
        std::vector<int> declarations, stmts;
        while (at("intdcl") || at("floatdcl")) {
            const auto kind = tokens[pos].kind;
            const int keyword = take(kind);
            const auto name = tokens[pos].text;
            const int id = take("id");
            declarations.push_back(node(parse, "Dcl", {keyword, id}));
            statements.push_back(node(ast, kind + " " + name));
        }
        while (!at("$")) {
            if (at("print")) {
                const int keyword = take("print");
                const auto name = tokens[pos].text;
                stmts.push_back(node(parse, "Stmt", {keyword, take("id")}));
                statements.push_back(node(ast, "print " + name));
                continue;
            }
            const auto name = tokens[pos].text;
            const int target = take("id"), assign = take("assign");
            const auto first = value();
            int expression = first.second;
            std::vector<std::pair<int, int>> tail;
            while (at("plus") || at("minus")) {
                const auto kind = tokens[pos].kind;
                const int op = take(kind);
                const auto next = value();
                tail.push_back({op, next.first});
                expression = node(ast, kind == "plus" ? "+" : "-", {expression, next.second});
            }
            int rest = node(parse, "Expr", {node(parse, "epsilon")});
            for (auto it = tail.rbegin(); it != tail.rend(); ++it) rest = node(parse, "Expr", {it->first, it->second, rest});
            stmts.push_back(node(parse, "Stmt", {target, assign, first.first, rest}));
            statements.push_back(node(ast, "=", {node(ast, "id " + name), expression}));
        }
        int dcls = node(parse, "Dcls", {node(parse, "epsilon")});
        for (auto it = declarations.rbegin(); it != declarations.rend(); ++it) dcls = node(parse, "Dcls", {*it, dcls});
        int seq = node(parse, "Stmts", {node(parse, "epsilon")});
        for (auto it = stmts.rbegin(); it != stmts.rend(); ++it) seq = node(parse, "Stmts", {*it, seq});
        return node(parse, "Prog", {dcls, seq, take("$")});
    }
};

void check(Tree& tree) {
    std::array<Type, 26> symbols{};
    const auto lookup = [&](char c) {
        const auto type = symbols[static_cast<std::size_t>(c - 'a')];
        if (type == Type::none) throw std::runtime_error(std::string("semantic: undeclared identifier ") + c);
        return type;
    };
    const auto promote = [&](int child) {
        if (tree[child].type == Type::floating) return child;
        const int converted = node(tree, "int2float", {child});
        tree[converted].type = Type::floating;
        return converted;
    };
    const auto count = tree.size();
    // Original nodes are in child-before-parent order. New conversion nodes
    // already have a type; never hold a vector reference while adding one.
    for (std::size_t i = 0; i < count; ++i) {
        const auto label = tree[i].label;
        if (label.rfind("intdcl ", 0) == 0 || label.rfind("floatdcl ", 0) == 0) {
            auto& entry = symbols[static_cast<std::size_t>(label.back() - 'a')];
            if (entry != Type::none) throw std::runtime_error("semantic: duplicate declaration " + label);
            entry = label[0] == 'i' ? Type::integer : Type::floating;
            tree[i].type = entry;
        } else if (label.rfind("id ", 0) == 0 || label.rfind("print ", 0) == 0) tree[i].type = lookup(label.back());
        else if (label == "+" || label == "-" || label == "=") {
            const int left = tree[i].children[0], right = tree[i].children[1];
            const auto lt = tree[left].type, rt = tree[right].type;
            if (label == "=" && lt == Type::integer && rt == Type::floating)
                throw std::runtime_error("semantic: cannot assign float to int " + tree[left].label);
            tree[i].type = label == "=" ? lt : (lt == Type::floating || rt == Type::floating ? Type::floating : Type::integer);
            if (tree[i].type == Type::floating) {
                if (label != "=") { const int c = promote(left); tree[i].children[0] = c; }
                const int c = promote(right); tree[i].children[1] = c;
            }
        }
    }
}

std::string add_integer(std::string a, std::string b) {
    std::string sum;
    int carry = 0;
    while (!a.empty() || !b.empty() || carry) {
        int n = carry;
        if (!a.empty()) { n += a.back() - '0'; a.pop_back(); }
        if (!b.empty()) { n += b.back() - '0'; b.pop_back(); }
        sum.push_back(static_cast<char>('0' + n % 10)); carry = n / 10;
    }
    std::reverse(sum.begin(), sum.end());
    const auto first = sum.find_first_not_of('0');
    return first == std::string::npos ? "0" : sum.substr(first);
}

// Supplement: exact nonnegative integer + folding, matching HW2's x+31.
// Never reassociate subtraction or floating expressions.
void fold(Tree& tree) {
    const auto constant = [&](int id) { return tree[id].type == Type::integer && digit(tree[id].label[0]); };
    const auto count = tree.size();
    for (std::size_t i = 0; i < count; ++i) {
        if (tree[i].label != "+" || tree[i].type != Type::integer) continue;
        const int left = tree[i].children[0], right = tree[i].children[1];
        if (constant(left) && constant(right)) {
            tree[i].label = add_integer(tree[left].label, tree[right].label); tree[i].children.clear();
        } else if (tree[left].label == "+" && constant(tree[left].children[1]) && constant(right)) {
            const int before = tree[left].children[0], c = tree[left].children[1];
            const int sum = node(tree, add_integer(tree[c].label, tree[right].label));
            tree[sum].type = Type::integer;
            tree[i].children = {before, sum};
        }
    }
}

void generate(const Tree& tree, const std::vector<int>& statements, std::ostream& out) {
    for (const int root : statements) {
        std::vector<std::pair<int, bool>> pending{{root, false}};
        while (!pending.empty()) {
            const auto item = pending.back(); pending.pop_back();
            const auto& n = tree[item.first];
            if (!item.second) {
                pending.push_back({item.first, true});
                if (n.label == "=") pending.push_back({n.children[1], false});
                else for (auto it = n.children.rbegin(); it != n.children.rend(); ++it) pending.push_back({*it, false});
                continue;
            }
            if (n.label == "=") out << 's' << tree[n.children[0]].label.back() << "\n0 k\n";
            else if (n.label == "+" || n.label == "-") out << n.label << '\n';
            else if (n.label == "int2float") out << "5 k\n";
            else if (n.label.rfind("id ", 0) == 0) out << 'l' << n.label.back() << '\n';
            else if (n.label.rfind("print ", 0) == 0) out << 'l' << n.label.back() << "\np\nsi\n";
            else if (digit(n.label[0])) out << decimal(n.label) << '\n';
        }
    }
}

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        std::string mode = "--dc";
        bool optimize = false;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--fold") optimize = true;
            else if (arg == "--tokens" || arg == "--parse-tree" || arg == "--ast" || arg == "--typed-ast" || arg == "--check" || arg == "--dc") mode = arg;
            else throw std::runtime_error("usage: ac_homework [--tokens|--parse-tree|--ast|--typed-ast|--check|--dc] [--fold]");
        }
        if (optimize && (mode == "--tokens" || mode == "--parse-tree"))
            throw std::runtime_error("--fold requires --ast, --typed-ast, --check or --dc");
        // ponytail: whole-input scanning; use streaming if source files outgrow RAM.
        const std::string source{std::istreambuf_iterator<char>(std::cin), {}};
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        const auto tokens = scan(source);
        std::ostringstream output; // Publish only after the complete selected phase succeeds.
        if (mode == "--tokens") {
            for (const auto& t : tokens) output << t.kind << (t.text.empty() ? "" : " " + t.text) << '\n';
        } else {
            Parser parser(tokens);
            const int root = parser.program();
            if (mode == "--parse-tree") print_tree(parser.parse, root, output);
            else if (mode == "--ast" && !optimize) print_tree(parser.ast, node(parser.ast, "Prog", parser.statements), output);
            else {
                check(parser.ast);
                if (optimize) fold(parser.ast);
                if (mode == "--check") output << "OK\n";
                else if (mode == "--ast" || mode == "--typed-ast") print_tree(parser.ast, node(parser.ast, "Prog", parser.statements), output);
                else generate(parser.ast, parser.statements, output);
            }
        }
        std::cout << output.str();
        return std::cout ? 0 : 1;
    } catch (const std::exception& error) { std::cerr << "error: " << error.what() << '\n'; return 1; }
}
```

## 完整 C++：automata_homework.cpp

來源類別：**C++ 實作（補充）**。教材 NFA 邊直接列出，確定化與辨識由程式實際計算。

```cpp
// Ch3 HW5(d)/(a): original NFA edges -> subset construction -> complete DFA.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Set = std::uint32_t;
struct Edge { int from; char symbol; int to; };
struct NFA { std::string alphabet; int start, final; std::vector<Edge> edges; };
struct DFA { std::vector<Set> states; std::vector<std::vector<int>> next; };
Set bit(int state) { return Set{1} << state; }
Set move(const NFA& nfa, Set states, char symbol) {
    Set result = 0;
    for (const auto& e : nfa.edges) if ((states & bit(e.from)) && e.symbol == symbol) result |= bit(e.to);
    return result;
}
Set closure(const NFA& nfa, Set states) {
    while (true) {
        const Set next = states | move(nfa, states, '\0');
        if (next == states) return states;
        states = next;
    }
}
DFA construct(const NFA& nfa) {
    DFA dfa;
    const auto record = [&](Set states) {
        const auto it = std::find(dfa.states.begin(), dfa.states.end(), states);
        if (it != dfa.states.end()) return static_cast<int>(it - dfa.states.begin());
        dfa.states.push_back(states);
        dfa.next.emplace_back(nfa.alphabet.size(), 0);
        return static_cast<int>(dfa.states.size()) - 1;
    };
    record(closure(nfa, bit(nfa.start)));
    for (std::size_t i = 0; i < dfa.states.size(); ++i) {
        for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) {
            const int target = record(closure(nfa, move(nfa, dfa.states[i], nfa.alphabet[c])));
            dfa.next[i][c] = target; // record may reallocate; assign afterward.
        }
    }
    return dfa;
}
bool accepts_nfa(const NFA& nfa, const std::string& word) {
    Set states = closure(nfa, bit(nfa.start));
    for (char c : word) {
        if (nfa.alphabet.find(c) == std::string::npos) return false;
        states = closure(nfa, move(nfa, states, c));
    }
    return (states & bit(nfa.final)) != 0;
}
bool accepts_dfa(const NFA& nfa, const DFA& dfa, const std::string& word) {
    int state = 0;
    for (char c : word) {
        const auto index = nfa.alphabet.find(c);
        if (index == std::string::npos) return false;
        state = dfa.next[state][index];
    }
    return (dfa.states[state] & bit(nfa.final)) != 0;
}
void print_set(Set states) {
    std::cout << '{'; bool first = true;
    for (int i = 1; i <= 12; ++i) if (states & bit(i)) {
        if (!first) std::cout << ',';
        std::cout << i; first = false;
    }
    std::cout << '}';
}
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        if (argc < 2 || argc > 3 || (std::string(argv[1]) != "5d" && std::string(argv[1]) != "5a") ||
            (argc == 3 && std::string(argv[2]) != "--table"))
            throw std::runtime_error("usage: automata_homework 5d|5a [--table]");
        // ponytail: fixed homework NFAs fit 32 bits; use a dynamic set for >=32 states.
        const NFA nfa = std::string(argv[1]) == "5d"
            ? NFA{"bcd", 1, 6, {{1,0,2},{1,0,5},{2,'b',3},{3,'c',4},{4,0,2},{4,0,5},{5,'d',6}}}
            : NFA{"abcd", 1, 12, {{1,0,2},{2,0,3},{2,0,6},{3,'a',4},{4,0,5},{5,0,2},{5,0,12},
                {6,0,7},{6,0,10},{7,'b',8},{8,'c',9},{9,0,7},{9,0,10},{10,'d',11},{11,0,5}}};
        const auto dfa = construct(nfa);
        if (argc == 3) {
            std::cout << "NFA start=" << nfa.start << " final=" << nfa.final << '\n';
            for (const auto& edge : nfa.edges) std::cout << edge.from << ' ' << (edge.symbol ? std::string(1, edge.symbol) : "epsilon") << ' ' << edge.to << '\n';
            std::cout << "DFA start=0 states=" << dfa.states.size() << '\n';
            for (std::size_t i = 0; i < dfa.states.size(); ++i) {
                std::cout << i << ' '; print_set(dfa.states[i]);
                std::cout << ((dfa.states[i] & bit(nfa.final)) ? " accept" : " reject");
                for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) std::cout << ' ' << nfa.alphabet[c] << "->" << dfa.next[i][c];
                std::cout << '\n';
            }
        } else {
            std::string word;
            while (std::getline(std::cin, word)) {
                if (!word.empty() && word.back() == '\r') word.pop_back();
                const bool result = accepts_dfa(nfa, dfa, word);
                if (result != accepts_nfa(nfa, word)) throw std::runtime_error("NFA/DFA disagreement");
                std::cout << (result ? "ACCEPT\n" : "REJECT\n");
            }
            if (std::cin.bad()) throw std::runtime_error("input read failed");
        }
        return std::cout ? 0 : 1;
    } catch (const std::exception& error) { std::cerr << "error: " << error.what() << '\n'; return 1; }
}
```
