---
title: "Compiler - Ch1-Ch3 考場短版 C++"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "既有 Ch1–3 作業實作與使用者 HTML parser 線索；短版為補充"
source_pages: "Ch2 p.15、p.36–46；Ch3 p.53–60；HTML 為使用者線索，LL(1) 為範圍未確認的補充"
---

# Compiler - Ch1-Ch3 考場短版 C++

> [!abstract] 考場優先用這份
> 考試直接攜帶下列八份 `.cpp` 原檔，每份可獨立編譯。程式保留 **160 行追加的中文註解**，目前共 806 行。這份筆記與 [[Complier/Review/Compiler-Ch1-Ch3-Cpp-Short.html|HTML 查題／改題指南]] 提供題目、檔名、邏輯及修改行號；完整原碼請直接開檔。需要較完整功能時，查 [[Compiler - Ch1-Ch3 考試 C++ 程式集|原完整版]]。

先準備 HTML、Scanner、運算式、ac 與 HW5。LL(1) 放最後。以下每份的「範圍」就是適用條件，不能把不同 I/O 或題目要求當成已通過。

| 題型 | 行數 | 最短使用方式 |
|---|---:|---|
| HTML 標籤配對 | 130 | `html_check.cpp` |
| 遞迴下降運算式 | 123 | `expression.cpp` |
| Scanner：沿用現有短程式 | 93 | `lexer.cpp` |
| NFA 直接判定字串 | 73 | `nfa_check.cpp` |
| HW5 固定四狀態 DFA | 35 | `hw5_check.cpp` |
| ac 邊解析邊產 dc | 142 | `ac_dc.cpp` |
| Stack VM：沿用現有短程式 | 75 | `stack_vm.cpp` |
| LL(1)：較低優先補充 | 135 | `ll1.cpp` |

## 考場先看

- 直接攜帶 .cpp 原檔；依題目選一份編譯，每份獨立 main，不能一起連結。
- 只字串判定：HTML 用 html_check，NFA 用 nfa_check，固定 HW5 用 hw5_check。
- 輸出 AST/postfix：expression 第一行 MODE 改 ast/postfix；eval 的變數不合法。
- ac 產碼：ac_dc 保留型別檢查與精確 decimal；要樹／摺疊改用原完整版本。
- Scanner、VM、LL(1) 沿用直接流程；中文註解增加閱讀長度，不增加執行步驟。
- HTML 引號內 > 不結束 tag；<p a=x/> 的 slash 屬於 value，p 仍未關閉。
- HW5(a) accept state 可接下一個 a/b/d；HW5(d) accept 後再讀字元就拒絕。
- 案例數 T、EOF、空行、大小寫、輸出字樣、精度一律對齊原題。沒有原題就不能保證 Accepted。
- 所有程式只用標準 C++17。getline 字串題移除尾端 CR；整份 source 把 CR 視為空白。
- 直接修改 .cpp 並提交；完整版本仍保留 token/tree/text/DFA table 功能。

## 驗證

610 項檢查＋sanitizer；Linux 交叉編譯成功，Linux 實跑／DOMjudge Accepted 未驗證。另有 200 個 HTML 新舊版比對、200 個獨立 Fraction 求值、97,222 個固定 DFA 字串及 768 個隨機 NFA 字串；完整報告見 `cpp-short-validation.json`。

```sh
python3 Complier/Code/check_cpp_short.py
python3 Complier/Code/check_cpp_short.py --sanitize
```

## HTML 標籤配對

[[Complier/Code/exam/short/html_check.cpp|原始單檔]]

**輸入輸出**：整份 stdin 為一個 HTML fragment；只印 VALID／INVALID，兩種判定皆 exit 0。stack 保存未關閉標籤，END 必須配 top；空輸入合法。

**範圍**：保留原版 check 的屬性驗證、註解、DOCTYPE html、13 個 void 與 script/style/textarea/title raw text；名稱不分 ASCII 大小寫。明示關閉，普通元素 <x/> 採本題子集自閉合；非 browser DOM，不省略 end tag、不解碼 entity。

**考場修改**：改 main 的輸出字樣；一行一案才改成 getline 外層。配對時累積 stack.size() 可求最大深度。若要 token／tree／text，使用原 html_parser.cpp 的相應模式。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/short/html_check.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/short/html_check.in
```

輸入：

```text
<div id="main"><p title="a>b">Hello <b>world</b></p><br><img src=x><!--ok--></div>
```

輸出：

```text
VALID
```

### 完整題目（教材／模擬來源已區分）

歷屆 HTML parser 是使用者提供的線索，未提供原考卷；以下是完整模擬題。

請撰寫程式讀入一份 HTML fragment，判斷所有非 void、非自閉合元素是否正確巢狀。開始標籤必須依相反順序關閉；END 名稱須與最內層未關閉元素相同。名稱不分 ASCII 大小寫。支援 boolean、單雙引號與無引號屬性、註解、短 DOCTYPE html；script/style/textarea/title 內容讀到匹配 END。多個根元素與空 fragment 均合法。

**輸入**：stdin 全部內容到 EOF 是一個案例，可能跨行。普通元素必須顯式關閉；本模擬題將 <x/> 視為自閉合。無額外案例數 T。

**輸出**：合法印 VALID，否則印 INVALID，每次只印一行；這兩種分類都正常結束。

**範圍**：不是完整 browser DOM：不恢復錯誤、不省略 end tag、不解碼 entity、不檢查內容模型。這裡的「合法」指指定子集。

### 手動追蹤

- <a><b>x</b></a>：[] → [a] → [a,b] → [a] → []，接受。
- <a><b></a></b>：讀 </a> 時 top 是 b，立即拒絕。
- <p title="a>b">x</p>：引號中的 > 不切開 tag。
- <p a=x/> 沒有關 p；<p a=x /> 則已自閉合。

### 已試編修改範例

#### 輸出 YES / NO

原檔第 127 行，取代這行／區塊：

```cpp
    cout << (valid ? "YES\n" : "NO\n");
```

輸入：

```text
<p/>```

輸出：

```text
YES
```

#### 一行一案

原檔第 121、127 行，取代這行／區塊：

```cpp
while (getline(cin, s)) {
    p = 0; bool valid = false;
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
}
if (cin.bad()) return 1;
```

輸入：

```text
<p/>
<p>
```

輸出：

```text
VALID
INVALID
```

#### XML 式：br 等也須配對關閉

原檔第 32、33 行，取代這行／區塊：

```cpp
const set<string> empty{};
```

輸入：

```text
<br></br>```

輸出：

```text
VALID
```

#### 求最大巢狀深度

原檔第 11 行，在行後插入：

```cpp
size_t deepest = 0;
```

原檔第 101 行，在行後插入：

```cpp
if (stack.size() > deepest) deepest = stack.size();
```

原檔第 127 行，取代這行／區塊：

```cpp
if (valid) cout << deepest << "\n"; else cout << "INVALID\n";
```

輸入：

```text
<a><b></b></a>```

輸出：

```text
2
```

#### 首行 T，其後一行一案

原檔第 121、127 行，取代這行／區塊：

```cpp
int T; if (!(cin >> T) || T < 0) return 1;
getline(cin, s);
if (s.find_first_not_of(" \t\r") != string::npos) return 1;
for (int tc = 0; tc < T; ++tc) {
    if (!getline(cin, s)) return 1;
    p = 0; bool valid = false;
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
}
if (cin.bad()) return 1;
```

輸入：

```text
2
<p/>
<p>
```

輸出：

```text
VALID
INVALID
```


## 遞迴下降運算式

[[Complier/Code/exam/short/expression.cpp|原始單檔]]

**輸入輸出**：一行一式；常數 MODE=eval（預設求值）、postfix 或 ast，修改這一行選題。+ - * /、括號、一元正負、十進位及 e/E；二元左結合。錯誤 stderr、exit 1，整份 stdout 暫存。

**範圍**：eval 使用 long double、15 位有效數字，拒絕零除／非有限數／變數；ID 僅用於 postfix/ast。嵌套括號與一元鏈深度 <=256；AST 字串拼接最壞 O(n²)。長加減鏈用 while，不占深遞迴。

**考場修改**：只求值可刪 postfix 與 ast 相關行；只畫 AST 可刪 number 的計算。若嵌套超過 256 或 AST 很長，原版 iterative expression.cpp 保留相同運算規則。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/short/expression.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/short/expression.in
```

輸入：

```text
(2+3)*4
100-30-1
8/2/2
-2*-3
.5 + 1e-2
```

輸出：

```text
20
69
2
6
0.51
```

### 完整題目（教材／模擬來源已區分）

Ch2 recursive descent / AST 的延伸模擬題；乘除、括號與一元正負不在原 ac 文法。

請讀入每行運算式，依通常優先序計算結果，或依題目指定改為 postfix / AST。一元正負優先於乘除，乘除優先於加減；同級二元左結合。括號可覆寫優先序。number 允許 .5、10.、十進位小數及 e/E 科學記號；ID 符合 [A-Za-z_][A-Za-z_0-9]*。求值模式不允許變數。

**輸入**：每行一個完整運算式到 EOF，沒有 T；完全空輸入是零案例，但空白行本身是非法運算式。

**輸出**：預設 eval：每行印 15 位有效數字的 long double 結果。postfix：以一個空白分隔 token。一元正負用 pos/neg。ast：印前序括號表示。

**範圍**：嵌套括號／一元鏈最多 256；不支援 %、^、函式或隱含乘法。非法字元、缺 operand、零除、非有限值：stdout 空、stderr 訊息、exit 1。

### 手動追蹤

- 100-30-1：先 100-30，再 -1，結果 69。
- a+b*c：AST 是 (+ a (* b c))；postfix 是 a b c * +。
- -2*-3：讀 2 → neg → 3 → neg → *，結果 6。
- 2(3) 並非隱含乘法，會因多餘內容拒絕。

### 已試編修改範例

#### 只輸出 postfix

原檔第 12 行，取代這行／區塊：

```cpp
const string MODE = "postfix";
```

輸入：

```text
a+b*c```

輸出：

```text
a b c * +
```

#### 只輸出 AST

原檔第 12 行，取代這行／區塊：

```cpp
const string MODE = "ast";
```

輸入：

```text
a+b*c```

輸出：

```text
(+ a (* b c))
```

#### 固定小數點後 2 位

原檔第 106 行，取代這行／區塊：

```cpp
ostringstream out; out << fixed << setprecision(2);
```

輸入：

```text
1/4```

輸出：

```text
0.25
```

#### 所有模式均禁止變數

原檔第 51 行，在行後插入：

```cpp
if (id) fail();
```

輸入：

```text
x+1```

輸出：

```text
```

stderr（exit 1）：

```text
invalid expression
```

#### 每次除法結果向零截斷

原檔第 85 行，取代這行／區塊：

```cpp
        if (op == '/') { if (b.number == 0) fail(); a.number = trunc(a.number / b.number); }
```

輸入：

```text
-7/2```

輸出：

```text
-3
```


## Scanner：沿用現有短程式

[[Complier/Code/exam/lexer.cpp|原始單檔]]

**輸入輸出**：整份 stdin；印 KW/ID/NUM/STRING/CHAR/OP/PUNCT 與帶引號 lexeme，最後 EOF。忽略 // 與非巢狀 /* */。長運算子先比，完整 ID 再查 keyword。

**範圍**：C-like 補充，非完整 C/C++；ID [A-Za-z_][A-Za-z_0-9]*；number 支援 .5、10.、e/E；CHAR 單 byte 或單 escape。

**考場修改**：keyword 改 keywords；運算子改 ops；輸出改最後兩行。沿用原本順序掃描的邏輯，追加中文註解；不新增架構。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/lexer.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/lexer.in
```

輸入：

```text
int sum=12; // skip
float x=1.2e-3; /*skip*/ sum+=2; print("a>b");
```

輸出：

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

### 完整題目（教材／模擬來源已區分）

Ch3 scanner / longest match 的延伸模擬題。教材 HW3 要擴充 ac 的 f/float、i/int、scientific number；本份是一般 C-like token 題，規格不同。

請對一份類 C 程式做詞彙分析，依序列出 keyword、identifier、number、string、char、operator 與 punctuation。忽略空白、單行 // 註解及非巢狀 /* */ 註解。先讀完整 identifier 再查保留字，operator 採最長匹配。quoted literal 中的註解符號不可當作註解，跳脫引號不得提早終止 literal。

**輸入**：整份 stdin 到 EOF；ID 可含底線；number 允許 .5、10.、e/E。keyword 名單及 operator 名單以檔案常數為準。

**輸出**：每個 token 一行：類型、空白、std::quoted 包裝的原始 lexeme；最後一行 EOF。

**範圍**：不是完整 C/C++ lexer：沒有 preprocessing、raw string、數字 suffix 或完整字元 escape 語意；CHAR 只允許單 byte / 單簡單 escape。遇未閉註解／引號或非法 byte，exit 1 且 stdout 空。

### 手動追蹤

- intx：先讀四個字元，查 keyword 失敗，因此為 ID，不拆 int + x。
- a>>=2：>>= 先於 >> / >，只有一個 operator token。
- "//x"：整段是 STRING，// 不觸發註解。
- -1e-2：前面的 - 是 OP，指數內的 - 是 NUM 的一部分。

### 已試編修改範例

#### 增加保留字

原檔第 23 行，取代這行／區塊：

```cpp
        const std::set<std::string> keywords{"switch","case","int","float","double","char","bool","void","if","else","while","for","return","print"};
```

輸入：

```text
switch case```

輸出：

```text
KW "switch"
KW "case"
EOF
```

#### 增加多字元運算子

原檔第 25 行，取代這行／區塊：

```cpp
        const std::vector<std::string> ops{"<<=",">>=","**","++","--","==","!=","<=",">=","&&","||","+=","-=","*=","/=","%=","<<",">>","->","&=","|=","^=","::"};
```

輸入：

```text
a**b```

輸出：

```text
ID "a"
OP "**"
ID "b"
EOF
```

#### lexeme 不加引號

原檔第 87 行，取代這行／區塊：

```cpp
output << kind << ' ' << s.substr(start, p - start) << '\n';
```

輸入：

```text
int x```

輸出：

```text
KW int
ID x
EOF
```

#### 不要印 EOF

原檔第 90 行，取代這行／區塊：

```cpp

```

輸入：

```text
int```

輸出：

```text
KW "int"
```

#### 不區分 keyword，全部列為 ID

原檔第 44 行，取代這行／區塊：

```cpp
kind = "ID";
```

輸入：

```text
int x```

輸出：

```text
ID "int"
ID "x"
EOF
```


## NFA 直接判定字串

[[Complier/Code/exam/short/nfa_check.cpp|原始單檔]]

**輸入輸出**：n m start k；k 個接受 state；alphabet；m 條 from symbol to；其後一行一字串。state=0..n-1，#=epsilon，空行=空字串。印 ACCEPT／REJECT。

**範圍**：n<=256，m<=65536；只做 closure(move(states,c)) 的 NFA 模擬，不產 DFA 表。不再因完整 DFA 超過 4096 states 而失敗。

**考場修改**：字串辨識就用這份；若題目明確要求 subset construction／DFA 表／集合 trace，改用原 nfa_to_dfa.cpp，勿用字串判定代替表格作答。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/short/nfa_check.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/short/nfa_check.in
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

輸出：

```text
ACCEPT
ACCEPT
ACCEPT
REJECT
REJECT
REJECT
REJECT
```

### 完整題目（教材／模擬來源已區分）

Ch3 epsilon-closure 與 NFA 的字串判定模擬題；input 格式由這份手冊定義。

給定帶 epsilon edge 的 NFA，請對每個完整輸入字串判定是否接受。NFA 在同一時刻可同時位於多個 state，且不用消耗字元也可沿 epsilon edge 移動。每讀一個字元，對全部當前 state 做 move，再做 epsilon-closure。所有字元用完後，只要集合含至少一個接受 state 就接受。

**輸入**：先讀 n m start k；再讀 k 個 final state；再讀 alphabet；接著 m 條 from symbol to。state 是 0..n-1；# 是 epsilon。其後每行一個字串，空行是 epsilon 案例。

**輸出**：每案一行 ACCEPT / REJECT。非法 alphabet 字元直接拒絕該字串；非法 NFA 描述則 stderr、exit 1。

**範圍**：1<=n<=256、0<=m<=65536；alphabet 非空、無重複、不能含 #；只接受單 byte 符號。本份不輸出 subset DFA 表。

### 手動追蹤

- 0 --#→ 1 --a→ 2(final)：初始 {0,1}；讀 a 後 {2}，接受。
- epsilon cycle：set 去重，只有新 state 進 todo，所以 closure 不會卡住。
- 先碰 final 再走死：必須等字串讀完，不能中途接受。

### 已試編修改範例

#### state 編號從 1 開始

原檔第 31 行，取代這行／區塊：

```cpp
auto valid = [n](int state) { return state >= 1 && state <= n; };
```

原檔第 40 行，取代這行／區塊：

```cpp
edges.resize(n + 1);
```

輸入：

```text
2 1 1 1
2
a
1 a 2
a
b
```

輸出：

```text
ACCEPT
REJECT
```

#### epsilon 用 @

原檔第 20 行，取代這行／區塊：

```cpp
        for (int to : edges[from]['@']) if (states.insert(to).second) todo.push_back(to);
```

原檔第 37 行，取代這行／區塊：

```cpp
        if (!(cin >> alphabet) || alphabet.find('@') != string::npos ||
```

原檔第 44 行，取代這行／區塊：

```cpp
                (symbol != "@" && alphabet.find(symbol[0]) == string::npos)) fail();
```

輸入：

```text
3 2 0 1
2
a
0 @ 1
1 a 2
a
```

輸出：

```text
ACCEPT
```

#### 輸出 YES / NO

原檔第 68 行，取代這行／區塊：

```cpp
            cout << (accepted ? "YES\n" : "NO\n");
```

輸入：

```text
2 1 0 1
1
a
0 a 1
a
```

輸出：

```text
YES
```

#### 印初始及每讀一字元後的 state 集合

原檔第 55 行，在行後插入：

```cpp
for (int state : states) cout << state << ' ';
cout << '\n';
```

原檔第 63 行，在行後插入：

```cpp
for (int state : states) cout << state << ' ';
cout << '\n';
```

輸入：

```text
3 2 0 1
2
a
0 # 1
1 a 2
a
```

輸出：

```json
"0 1 \n2 \nACCEPT\n"
```

此 JSON 表示完整測試字串；`\n` 是換行，尾端空白保留。

#### 忽略字串前後空白

原檔第 53 行，取代這行／區塊：

```cpp
size_t first = word.find_first_not_of(" \t\r");
word = first == string::npos ? "" : word.substr(first, word.find_last_not_of(" \t\r") - first + 1);
```

輸入：

```json
"2 1 0 1\n1\na\n0 a 1\n  a \n"
```

此 JSON 表示完整測試字串；`\n` 是換行，尾端空白保留。

輸出：

```text
ACCEPT
```


## HW5 固定四狀態 DFA

[[Complier/Code/exam/short/hw5_check.cpp|原始單檔]]

**輸入輸出**：一行一字串，空行拒絕；HW5A=true 辨識 (a|(bc)*d)+，改 false 辨識 (bc)*d。印 ACCEPT／REJECT，不需命令列參數。

**範圍**：只有固定兩個語言；0=start、1=剛讀 b、2=剛讀 bc、3=accept、-1=dead。這是精簡的辨識 DFA，不是投影片子集構造的原始 state sets。

**考場修改**：HW5A 常數選題；改 ACCEPT/REJECT 字樣。若要求原 NFA 邊、epsilon closure 或 subset DFA 表，用 automata_homework.cpp 5a/5d --table。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/short/hw5_check.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/short/hw5_check.in
```

輸入：

```text

a
d
ad
bcd
bcbcd
abcbcdad
b
bc
abca
bcdd
```

輸出：

```text
REJECT
ACCEPT
ACCEPT
ACCEPT
ACCEPT
ACCEPT
ACCEPT
REJECT
REJECT
REJECT
ACCEPT
```

### 完整題目（教材／模擬來源已區分）

教材原題（Ch3 PPT p.55、p.58）：Write NFA, and then DFA that recognizes the tokens defined by the following regular expression；5(d)=(bc)*d，5(a)=(a|(bc)*d)+。以下字串 I/O 是另外定義的程式練習。

請以 DFA 判定字串是否屬於 5(a) 或 5(d) 的語言。5(a) 是一段或多段 a 或 (bc)*d 的串接；5(d) 是零次或多次 bc 後接單一 d。所有字元必須用完才可接受。原作業若要求畫 NFA / subset DFA，另外用 automata_homework.cpp 的 --table；本短版只給辨識結果。

**輸入**：HW5A=true 選 5(a)，改 false 選 5(d)。其後每行一個字串到 EOF，沒有 T；空行代表空字串。

**輸出**：每案印 ACCEPT / REJECT。大小寫敏感，僅題目語言內的字母可接受。

**範圍**：不支援任意正則表示式輸入；這是固定兩個語言的四個可達 state 加 dead state。

### 手動追蹤

- 5(a)：a、d、ad、bcd、dd 接受；bc、空字串拒絕。
- 5(d)：d、bcd、bcbcd 接受；a、dd、bc 拒絕。
- bcd：0 --b→ 1 --c→ 2 --d→ 3；最後在 3，接受。

### 已試編修改範例

#### 改解 HW5(d)

原檔第 6 行，取代這行／區塊：

```cpp
const bool HW5A = false;
```

輸入：

```text
d
dd
bcd
```

輸出：

```text
ACCEPT
REJECT
ACCEPT
```

#### 輸出 YES / NO

原檔第 30 行，取代這行／區塊：

```cpp
        cout << (state == 3 ? "YES\n" : "NO\n");
```

輸入：

```text
a
b
```

輸出：

```text
YES
NO
```

#### HW5(a) 外層 + 改成 *

原檔第 30 行，取代這行／區塊：

```cpp
        cout << ((state == 3 || word.empty()) ? "ACCEPT\n" : "REJECT\n");
```

輸入：

```text

a
bc
```

輸出：

```text
ACCEPT
ACCEPT
REJECT
```

#### ASCII 大小寫不敏感

原檔第 13 行，在行後插入：

```cpp
for (char& c : word) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
```

輸入：

```text
BCD
A
```

輸出：

```text
ACCEPT
ACCEPT
```

#### 輸出 Case 1: 結果

原檔第 9 行，在行後插入：

```cpp
int case_no = 0;
```

原檔第 30 行，取代這行／區塊：

```cpp
        cout << "Case " << ++case_no << ": " << (state == 3 ? "ACCEPT\n" : "REJECT\n");
```

輸入：

```text
a
b
```

輸出：

```text
Case 1: ACCEPT
Case 2: REJECT
```


## ac 邊解析邊產 dc

[[Complier/Code/exam/short/ac_dc.cpp|原始單檔]]

**輸入輸出**：整份 stdin 為 ac 程式；f/float、i/int 宣告在前，p 印變數，單字母 ID，加減左結合。保留重複／未宣告／float→int 檢查，正確時只印 dc code。

**範圍**：支援小數與 lowercase e signed exponent；帶 . 或 e 就是 float。精確移動小數點，exponent 絕對值及 mantissa 長度 <=10000；無括號／乘除／註解。print 使用 l<變數>/p/si 形式。

**考場修改**：int→float 時印 5 k；assign 後印 0 k。value 直接回 leaf code 與型別，主迴圈直接產碼，沒有樹走訪。題目要求 parse tree／AST／常數摺疊時，用原 ac_homework.cpp 的相應模式。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/short/ac_dc.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/short/ac_dc.in
```

輸入：

```text
i x
x=100
x=x+30+1
p x
```

輸出：

```text
100
sx
0 k
lx
30
+
1
+
sx
0 k
lx
p
si
```

### 完整題目（教材／模擬來源已區分）

教材原題（Ch2 PPT p.39–46）：HW1 對 i x x=100 x=x+30+1 p x 建 parse tree；HW2(a) 建 AST、(b) 判斷語意與所需語言變更、(c) 顯示產碼；HW3 讓 f/float、i/int 均可宣告，number 可帶 optionally signed exponent。本檔只解產碼與型別檢查部分。

請把 ac 程式編譯為 dc stack code。所有宣告在敘述前，型別為 int / float；identifier 為一個小寫字母，i/f/p 是保留字。敘述為 id=val{(+|-)val} 或 p id。val 為 variable 或非負 number。加減左結合。檢查重複宣告、未宣告及 float→int 指定；int→float 可提升。科學記號用精確字串移動小數點轉為 dc 可讀的小數。

**輸入**：整份 stdin 到 EOF；沒有分號或 T。f 或 float、i 或 int 均可。小數的點後必須有數字，指數字母限 lowercase e，可有正負。

**輸出**：只印 dc target code，不直接印數值答案。非法 ac 時 stdout 空、stderr 訊息、exit 1。

**範圍**：帶 . 或 e 的 number 在本實作一律 float；exponent 絕對值與 mantissa 長度 <=10000。無乘除、括號、unary、註解。短版無 parse tree / AST / folding，這些要求使用 ac_homework.cpp。教材對 HW2(b) 的 No 與型別規則有疑義，詳見既有作業校讀。

### 手動追蹤

- x=100：100 → sx → 0 k；p x：lx → p → si。
- i a f b b=a+3.2：la → 5 k → 3.2 → +；提升必須在對應 operand 後。
- 123e-22 → 0.0000000000000000000123，不能先轉 double 再印。
- i x x=1e0：數值雖為 1，來源型別是 float，所以拒絕指定給 int。

### 已試編修改範例

#### 只允許 i / f 短宣告

原檔第 43 行，取代這行／區塊：

```cpp

```

原檔第 44 行，取代這行／區塊：

```cpp

```

原檔第 45 行，取代這行／區塊：

```cpp
            if ((kind >= 'a' && kind <= 'z') || kind == '=' || kind == '+' || kind == '-') {}
```

輸入：

```text
i x x=1 px```

輸出：

```text
1
sx
0 k
lx
p
si
```

#### 科學記號也接受 E

原檔第 35 行，取代這行／區塊：

```cpp
if (j < s.size() && (s[j] == 'e' || s[j] == 'E')) {
```

原檔第 57 行，取代這行／區塊：

```cpp
size_t e = text.find_first_of("eE");
```

原檔第 98 行，取代這行／區塊：

```cpp
    return {decimal(text) + "\n", text.find_first_of(".eE") != string::npos};
```

輸入：

```text
f x x=1E-2 px```

輸出：

```text
0.01
sx
0 k
lx
p
si
```

#### 浮點運算 scale 改成 10

原檔第 128 行，取代這行／區塊：

```cpp
                if (!left.second && right.second) out << "10 k\n";
```

原檔第 131 行，取代這行／區塊：

```cpp
                if (left.second && !right.second) out << "10 k\n";
```

原檔第 136 行，取代這行／區塊：

```cpp
            if (target_float && !left.second) out << "10 k\n";
```

輸入：

```text
f x x=1 px```

輸出：

```text
1
10 k
sx
0 k
lx
p
si
```

#### 合法程式只輸出 OK

原檔第 140 行，取代這行／區塊：

```cpp
cout << "OK\n"; return cout ? 0 : 1;
```

輸入：

```text
i x x=2 px```

輸出：

```text
OK
```

#### assignment 後不要產生 scale reset

原檔第 138 行，取代這行／區塊：

```cpp
            out << 's' << target << "\n";
```

輸入：

```text
i x x=2 px```

輸出：

```text
2
sx
lx
p
si
```


## Stack VM：沿用現有短程式

[[Complier/Code/exam/stack_vm.cpp|原始單檔]]

**輸入輸出**：一行一指令：PUSH、LOAD、STORE、ADD/SUB/MUL/DIV、NEG、DUP、PRINT；PRINT/STORE pop。long double，15 位有效數字；錯誤 stderr、exit 1，暫存 stdout。

**範圍**：無條件／跳躍／函式；只做 stack interpreter，不是 dc。LOAD 未定義、underflow、div0 拒絕。

**考場修改**：先 pop 右 b，再左 a，算 a op b；PRINT 若題目要求不 pop，就改讀 stack.back()。沿用原本直接執行流程，追加中文註解。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/stack_vm.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/stack_vm.in
```

輸入：

```text
PUSH 100
STORE x
LOAD x
PUSH 30
PUSH 1
ADD
ADD
STORE x
LOAD x
PRINT
```

輸出：

```text
131
```

### 完整題目（教材／模擬來源已區分）

Ch1 interpreter / Ch2 dc 產碼的延伸模擬題；指令名稱由本題定義，不是 GNU dc。

請執行 stack-based 虛擬機指令。PUSH number 把常數入 stack；STORE name pop 並保存；LOAD name 複製變數值。ADD/SUB/MUL/DIV 先取右 operand b，再取左 a，計算 a op b。NEG 取反，DUP 複製頂端，PRINT pop 並輸出。未知指令、未定義變數、underflow、零除或非有限值均視為錯誤。

**輸入**：每行一條指令到 EOF；空行忽略。PUSH/LOAD/STORE 恰有一個參數，其餘沒有參數；變數名採一般 ID 規則。

**輸出**：每次 PRINT 一行，15 位有效數字。整份成功後才發出累積輸出；任何錯誤 stdout 空、stderr 訊息、exit 1。

**範圍**：long double，非任意精度；沒有跳躍、條件、函式或字串。EOF 可留未使用 stack；PRINT 與 dc p 的 pop 規則不同。

### 手動追蹤

- PUSH 8 / PUSH 2 / SUB / PRINT：8-2=6，不能算成 2-8。
- PUSH 2 / DUP / MUL / NEG / PRINT：2*2 再取負，得 -4。
- PRINT 後 stack 少一項；若題目要求保留，要改成 peek。

### 已試編修改範例

#### PRINT 保留 stack 頂端

原檔第 54 行，取代這行／區塊：

```cpp
} else if (op == "PRINT") {
    if (stack.empty()) throw std::runtime_error("stack underflow");
    const auto value = stack.back();
    output << (value == 0 ? 0 : value) << '\n';
}
```

輸入：

```text
PUSH 2
PRINT
PRINT
```

輸出：

```text
2
2
```

#### 固定小數點後 2 位

原檔第 29 行，取代這行／區塊：

```cpp
        std::ostringstream output; output.imbue(std::locale::classic()); output << std::fixed << std::setprecision(2);
```

輸入：

```text
PUSH .25
PRINT
```

輸出：

```text
0.25
```

#### PRINT 指令改名為 OUT

原檔第 54 行，取代這行／區塊：

```cpp
            } else if (op == "OUT") { const auto value = pop(); output << (value == 0 ? 0 : value) << '\n'; }
```

輸入：

```text
PUSH 8
OUT
```

輸出：

```text
8
```

#### 指令名稱忽略 ASCII 大小寫

原檔第 38 行，在行後插入：

```cpp
for (char& c : op) if (c >= 'a' && c <= 'z') c -= 'a' - 'A';
```

輸入：

```text
push 2
print
```

輸出：

```text
2
```

#### PRINT 不移除值，DUP 後連續列印

原檔第 54 行，取代這行／區塊：

```cpp
} else if (op == "PRINT") {
    if (stack.empty()) throw std::runtime_error("stack underflow");
    const auto value = stack.back();
    output << (value == 0 ? 0 : value) << '\n';
}
```

輸入：

```text
PUSH 2
DUP
PRINT
PRINT
```

輸出：

```text
2
2
```


## LL(1)：較低優先補充

[[Complier/Code/exam/ll1.cpp|原始單檔]]

**輸入輸出**：P 條產生式，一行 A -> X Y，# 單獨為 epsilon；預設印 FIRST/FOLLOW/SELECT、table 與 conflict。--check 判定其後每行 token sequence。

**範圍**：通用表格功能需要固定點、nullable suffix 與衝突檢查；保留原本固定點演算法，追加中文註解。P<=1000；parse<=1000000 步；不消除左遞迴或做 left factoring。正式 FIRST/FOLLOW 範圍未確認。

**考場修改**：若已知題目固定文法，只寫對應 recursive descent 更好記；若要求任意 CFG 的 FIRST/FOLLOW，保留本版以免刪掉 nullable 的必要處理。DOMjudge 不傳 args 時固定 main 的 mode。

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/ll1.cpp -o /tmp/main
/tmp/main < Complier/Code/exam/ll1.in
```

輸入：

```text
4
E -> T R
R -> + T R
R -> #
T -> num
```

輸出：

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

### 完整題目（教材／模擬來源已區分）

predict 的通用延伸模擬題；正式 FIRST/FOLLOW 術語預告於 Ch4，不能視為已確認 Ch1–3 考題。

給定 CFG，請計算各 nonterminal 的 FIRST / FOLLOW、各 production 的 SELECT，並建立 LL(1) 解析表。FIRST / FOLLOW 必須反覆傳播至固定點。RHS 可空時將 LHS 的 FOLLOW 加入 SELECT。同格若有多條 production，列出 conflict，判定非 LL(1)。無衝突時另可用 predictive stack 判定 token 序列。

**輸入**：先讀 P（1..1000），再讀 P 行 A -> X Y。每行只含一條 alternative；# 必須單獨表示 epsilon，$ 保留為 EOF。start 是第一個 LHS。--check 模式才讀其後每行空白分隔的 token sequence。

**輸出**：預設列 FIRST/FOLLOW/SELECT、非空表格 cell、CONFLICT 與 LL1 YES/NO。--check 每案印 ACCEPT/REJECT；不由字串原始字元自動 tokenize。

**範圍**：不消除左遞迴、不做 left factoring，也不判定任意 CFG 是否無歧義；parse 步數 <=1000000。有 LL(1) conflict 時不任選規則繼續。

### 手動追蹤

- S -> a S | #：FIRST(S)={#,a}、FOLLOW(S)={$}。
- SELECT(S->#)={$}，所以 EOF 時才選 epsilon，而不是看到任何字元都選。
- A -> B C：若 C nullable，FOLLOW(A) 也要傳給 FOLLOW(B)。
- 展開 S -> a S 時先 push S 再 push a，讓 a 先被處理。

### 已試編修改範例

#### judge 不傳參數，只判定字串

原檔第 35 行，取代這行／區塊：

```cpp
const std::string mode = argc == 1 ? "--check" : argv[1];
```

輸入：

```text
2
S -> a S
S -> #
a a

b
```

輸出：

```text
ACCEPT
ACCEPT
REJECT
```

#### 只印 FIRST 與 FOLLOW

原檔第 96、103 行，取代這行／區塊：

```cpp

```

輸入：

```text
2
S -> a S
S -> #
```

輸出：

```text
FIRST(S)={#,a} FOLLOW(S)={$}
```

#### 字串判定輸出 YES / NO

原檔第 129 行，取代這行／區塊：

```cpp
                std::cout << (accepted && pos == words.size() ? "YES\n" : "NO\n");
```

參數：`--check`

輸入：

```text
2
S -> a S
S -> #
a
b
```

輸出：

```text
YES
NO
```

#### 指定 S 為 start，不使用第一個 LHS

原檔第 68 行，取代這行／區塊：

```cpp
        follow["S"].insert("$");
```

原檔第 112 行，取代這行／區塊：

```cpp
                words.push_back("$"); std::vector<std::string> stack{"$", "S"}; std::size_t pos = 0, steps = 0;
```

參數：`--check`

輸入：

```text
2
A -> b
S -> a
a
b
```

輸出：

```text
ACCEPT
REJECT
```

#### 只輸出是否為 LL(1)

原檔第 93、103 行，取代這行／區塊：

```cpp
std::cout << (ll1 ? "LL1 YES\n" : "LL1 NO\n");
```

輸入：

```text
2
S -> a S
S -> #
```

輸出：

```text
LL1 YES
```
