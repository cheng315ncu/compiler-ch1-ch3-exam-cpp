---
title: "Compiler - Scanner 與註解考試實作"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "[[Compiler-Ch3-p001-p010#PPT p.003｜Token type、lexeme 與 attribute]]；[[Compiler-Ch3-p011-p020#PPT p.015｜Identifier 的完整規則與底線限制]]；[[Compiler-Ch3-p011-p020#PPT p.016｜日期、註解、字串與 John 的 regex]]"
source_pages: "Ch3 p.3、p.15–16、p.20"
---

# Compiler - Scanner 與註解考試實作

> [!abstract] 題型定位
> Ch3 token／identifier／comment／string／longest match 的常見延伸。 以下為 **C++ 實作（補充）**；[[Complier/Code/exam/lexer.cpp|單檔原碼]] · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

## 契約與模式

`無參數`

stdin 整份來源到 EOF。每行 KIND "lexeme"，std::quoted 轉義引號／反斜線，末行 EOF。KW／ID／NUM／STRING／CHAR／OP／PUNCT；空白與 //、/* */ 不回傳 token。任何錯誤使 stdout 為空、stderr 診斷、exit 1。

## 演算法與易錯點

先略過空白／註解，再分類 ID、數字、引號 literal、運算子。ID 全部讀完才查 keyword set，所以 ifx 不拆成 if+x。三字元運算子先於二字元，再單字元；string 的 escaped quote 不結束 literal。

=／==，/／//／/*，keyword／longer ID 都要分清。exponent 以外正負號為 OP。字串內 /* 或 // 是文字。12abc 切成 NUM 12、ID abc 是否為合法敘述，還要由 parser 判斷。

> [!note] 支援範圍
> 補充 C-like lexer，非完整 C/C++。ID [A-Za-z_][A-Za-z_0-9]* 與教材的底線限制不同。NUM 允許 .5、10.、e/E；沒有 hex/octal 語意、suffix、raw string、preprocessor、行拼接。CHAR 只容一個 byte／簡單兩字元 escape，不解碼 hex／Unicode escape；STRING 保留詞素，不完整驗證 C escape 意義。block comment 不巢狀。

## 考場修改位置

keyword 改 keywords；多字元運算子改 ops 並維持長到短。若題目要求教材 ID，須在 ID 後驗證每個 _ 後至少一個 alnum、首字元為字母。要位置時集中於游標前進更新行欄，CRLF 算一次換行。

此版 floatx 為一個 ID；ac_homework 的單字母規格則為 floatdcl + id x。不要混用兩種語言契約。

## 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/lexer.cpp -o /tmp/lexer
/tmp/lexer < Complier/Code/exam/lexer.in
```

輸入：

```text
int sum=12; // skip
float x=1.2e-3; /*skip*/ sum+=2; print("a>b");
```

預設輸出：

```text
KW "int"
ID "sum"
OP "="
NUM "12"
PUNCT ";"
KW "float"
ID "x"
OP "="
NUM "1.2e-3"
PUNCT ";"
ID "sum"
OP "+="
NUM "2"
PUNCT ";"
KW "print"
PUNCT "("
STRING "\"a>b\""
PUNCT ")"
PUNCT ";"
EOF
```

其他測例：int sum=12; → 5 tokens；ifx==1 → ID、OP ==、NUM；x<<=2 的 <<= 是一個 OP。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

## 完整 C++17 程式

```cpp
// C-like exam lexer: identifiers, decimal/exponent, strings, comments, longest operators.
// Supplement identifier rule: [A-Za-z_][A-Za-z_0-9]* (not Ch3's restricted underscores).
#include <iomanip>
#include <iostream>
#include <iterator>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
// 採 ASCII 範圍比較，避免 signed char 直接傳給 cctype 造成問題。
bool digit(char c) { return c >= '0' && c <= '9'; }
// 此補充題的 ID 可用底線；不要直接套用到 Ch3 另有底線限制的原題。
bool letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_'; }
bool space(char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '\f' || c == '\v'; }
int main() {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        // 整份 source 讀到 EOF；不可用 cin >> s，否則空白後的內容會遺失。
        const std::string s{std::istreambuf_iterator<char>(std::cin), {}};
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        // 先讀完整 ID 再查這張表：intx 是 ID，不是 int 接 x。
        const std::set<std::string> keywords{"int","float","double","char","bool","void","if","else","while","for","return","print"};
        // Longest match：三字元運算子放在二字元前；單字元最後判斷。
        const std::vector<std::string> ops{"<<=",">>=","++","--","==","!=","<=",">=","&&","||","+=","-=","*=","/=","%=","<<",">>","->","&=","|=","^=","::"};
        // 只在完整掃描成功後輸出 token，避免非法尾端造成半份輸出。
        std::ostringstream output;
        for (std::size_t p = 0; p < s.size();) {
            if (space(s[p])) { ++p; continue; }
            // 註解先於 / 運算子；單行註解遇 CR 或 LF 都結束。
            if (s.compare(p, 2, "//") == 0) { while (p < s.size() && s[p] != '\r' && s[p] != '\n') ++p; continue; }
            // 區塊註解採非巢狀規則；找不到 */ 必須報錯。
            if (s.compare(p, 2, "/*") == 0) {
                const auto end = s.find("*/", p + 2);
                if (end == std::string::npos) throw std::runtime_error("unclosed block comment");
                p = end + 2; continue;
            }
            // start 記住 token 起點；結束位置 p 可用來直接切原始 lexeme。
            const auto start = p;
            std::string kind;
            // ID 一次讀到底，再分成 keyword / identifier，避免錯切前綴。
            if (letter(s[p])) {
                ++p; while (p < s.size() && (letter(s[p]) || digit(s[p]))) ++p;
                kind = keywords.count(s.substr(start, p - start)) ? "KW" : "ID";
            // 小數的點只有接數字才可當 number 起點；獨立 . 是 punctuation。
            } else if (digit(s[p]) || (s[p] == '.' && p + 1 < s.size() && digit(s[p + 1]))) {
                kind = "NUM";
                while (p < s.size() && digit(s[p])) ++p;
                if (p < s.size() && s[p] == '.') { ++p; while (p < s.size() && digit(s[p])) ++p; }
                // 指數的正負號屬於 number；一般 -12 的 - 仍是獨立 operator。
                if (p < s.size() && (s[p] == 'e' || s[p] == 'E')) {
                    ++p; if (p < s.size() && (s[p] == '+' || s[p] == '-')) ++p;
                    if (p == s.size() || !digit(s[p])) throw std::runtime_error("missing exponent digits");
                    while (p < s.size() && digit(s[p])) ++p;
                }
            // 進入 literal 後，// 與 /* 不再當作註解；只找未跳脫的配對引號。
            } else if (s[p] == '\'' || s[p] == '"') {
                const char quote = s[p++];
                // token 的類型與 lexeme 分開存；內容不需轉成執行期字串值。
                kind = quote == '"' ? "STRING" : "CHAR";
                int units = 0;
                while (p < s.size() && s[p] != quote) {
                    if (s[p] == '\r' || s[p] == '\n' || s[p] == '\0') throw std::runtime_error("newline/NUL in literal");
                    // 反斜線連同下一個字元一起吃掉；例如 \" 不會提早結束 string。
                    if (s[p] == '\\') {
                        ++p;
                        if (p == s.size() || s[p] == '\r' || s[p] == '\n' || s[p] == '\0') throw std::runtime_error("incomplete escape");
                    }
                    ++p; ++units;
                }
                if (p == s.size()) throw std::runtime_error("unclosed literal");
                ++p;
                // CHAR 只允許一個 byte 或一個簡單 escape；不是完整 C 字元常量規範。
                if (quote == '\'' && units != 1) throw std::runtime_error("character literal needs one character/escape");
            } else {
                // 先試完整多字元 operator，再退到單字元；不要用固定切兩字元的做法。
                for (const auto& op : ops) if (s.compare(p, op.size(), op) == 0) { p += op.size(); kind = "OP"; break; }
                if (kind.empty()) {
                    const char c = s[p++];
                    // 此處才退到單字元 operator，確保 += 不被切成 + 和 =。
                    if (std::string("+-*/%=<>!&|^~?:").find(c) != std::string::npos) kind = "OP";
                    else if (std::string("(){}[],;.").find(c) != std::string::npos) kind = "PUNCT";
                    else throw std::runtime_error("invalid byte at " + std::to_string(start));
                }
            }
            // std::quoted 是輸出包裝；lexeme 本身仍保留原始大小寫與引號。
            output << kind << ' ' << std::quoted(s.substr(start, p - start)) << '\n';
        }
        // 只有題目要求才保留額外 EOF token；考場可刪此行。
        output << "EOF\n";
        std::cout << output.str(); return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
```
