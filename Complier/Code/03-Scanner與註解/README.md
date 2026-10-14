# 03 Scanner、註解與 Longest Match

| 項目 | 內容 |
|---|---|
| 程式 | [lexer.cpp](lexer.cpp) |
| 類型 | 優先使用 |
| 測例 | [lexer.in](lexer.in) → [lexer.expected](lexer.expected) |
| 相關資料夾 | [09-作業ScannerTest](../09-作業ScannerTest/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror lexer.cpp -o main
./main < lexer.in | diff -u lexer.expected -
```

## 題目內容

> Ch3 scanner / longest match 的延伸模擬題。教材 HW3 要擴充 ac 的 f/float、i/int、scientific number；本份是一般 C-like token 題，規格不同。

請對一份類 C 程式做詞彙分析，依序列出 keyword、identifier、number、string、char、operator 與 punctuation。忽略空白、單行 // 註解及非巢狀 /\* \*/ 註解。先讀完整 identifier 再查保留字，operator 採最長匹配。quoted literal 中的註解符號不可當作註解，跳脫引號不得提早終止 literal。

- **輸入規格**：整份 stdin 到 EOF；ID 可含底線；number 允許 .5、10.、e/E。keyword 名單及 operator 名單以檔案常數為準。
- **輸出規格**：每個 token 一行：類型、空白、std::quoted 包裝的原始 lexeme；最後一行 EOF。
- **限制與適用範圍**：不是完整 C/C++ lexer：沒有 preprocessing、raw string、數字 suffix 或完整字元 escape 語意；CHAR 只允許單 byte / 單簡單 escape。遇未閉註解／引號或非法 byte，exit 1 且 stdout 空。

**Code 檔案名稱：**[`lexer.cpp`](lexer.cpp) （03-Scanner與註解/lexer.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror lexer.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

```text
int sum=12; // skip
float x=1.2e-3; /*skip*/ sum+=2; print("a>b");
```

**輸出**

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

### 邊界測例 01

**輸入**

```text
intx >>= 2
```

**輸出**

```text
ID "intx"
OP ">>="
NUM "2"
EOF
```

### 邊界測例 02

**輸入**

```text
int x; // hi
```

**輸出**

```text
KW "int"
ID "x"
PUNCT ";"
EOF
```

### 邊界測例 03

**輸入**

```text
"//x"
```

**輸出**

```text
STRING "\"//x\""
EOF
```

### 邊界測例 04

**輸入**

```text
1e+
```

**輸出**

```text
stdout：空
stderr：error: missing exponent digits
exit 1
```

### 邊界測例 05

**輸入**

```text
/* unfinished
```

**輸出**

```text
stdout：空
stderr：error: unclosed block comment
exit 1
```

## 邏輯與手動追蹤

依序判定空白、註解、ID、number、literal、operator。讀完整 ID 才查 keyword；多字元 operator 由長到短比對；字串內的註解符號不當成註解。

- intx：先讀四個字元，查 keyword 失敗，因此為 ID，不拆 int + x。
- a>>=2：>>= 先於 >> / >，只有一個 operator token。
- "//x"：整段是 STRING，// 不觸發註解。
- -1e-2：前面的 - 是 OP，指數內的 - 是 NUM 的一部分。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 增加保留字 | 23 | [修改範例 01（後文）](#lexer-change-1) |
| 增加多字元運算子 | 25 | [修改範例 02（後文）](#lexer-change-2) |
| lexeme 不加引號 | 87 | [修改範例 03（後文）](#lexer-change-3) |
| 不要印 EOF | 90 | [修改範例 04（後文）](#lexer-change-4) |
| 不區分 keyword，全部列為 ID | 44 | [修改範例 05（後文）](#lexer-change-5) |

<a id="lexer-change-1"></a>

### 01 增加保留字：改前／改後與測例

在 keywords 名單加入 "switch", "case" 等題目指定字。

第 23 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        const std::set<std::string> keywords{"int","float","double","char","bool","void","if","else","while","for","return","print"};
```

**改後（對照修改）**

```cpp
        const std::set<std::string> keywords{"switch","case","int","float","double","char","bool","void","if","else","while","for","return","print"};
```

已試編並執行的變體測例：

**輸入**

```text
switch case
```

**輸出**

```text
KW "switch"
KW "case"
EOF
```

<a id="lexer-change-2"></a>

### 02 增加多字元運算子：改前／改後與測例

在 ops 名單加入所需運算子；維持較長字串先列。這裡只分詞，不增加 parser 的運算規則。

第 25 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        const std::vector<std::string> ops{"<<=",">>=","++","--","==","!=","<=",">=","&&","||","+=","-=","*=","/=","%=","<<",">>","->","&=","|=","^=","::"};
```

**改後（對照修改）**

```cpp
        const std::vector<std::string> ops{"<<=",">>=","**","++","--","==","!=","<=",">=","&&","||","+=","-=","*=","/=","%=","<<",">>","->","&=","|=","^=","::"};
```

已試編並執行的變體測例：

**輸入**

```text
a**b
```

**輸出**

```text
ID "a"
OP "**"
ID "b"
EOF
```

<a id="lexer-change-3"></a>

### 03 lexeme 不加引號：改前／改後與測例

output &lt;&lt; kind &lt;&lt; ' ' &lt;&lt; s.substr(start, p - start) &lt;&lt; '\\n';

第 87 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            output << kind << ' ' << std::quoted(s.substr(start, p - start)) << '\n';
```

**改後（對照修改）**

```cpp
output << kind << ' ' << s.substr(start, p - start) << '\n';
```

已試編並執行的變體測例：

**輸入**

```text
int x
```

**輸出**

```text
KW int
ID x
EOF
```

<a id="lexer-change-4"></a>

### 04 不要印 EOF：改前／改後與測例

刪除這一行。

第 90 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        output << "EOF\n";
```

**改後（對照修改）**

```cpp
（刪除；不要貼這段提示文字）
```

已試編並執行的變體測例：

**輸入**

```text
int
```

**輸出**

```text
KW "int"
```

<a id="lexer-change-5"></a>

### 05 不區分 keyword，全部列為 ID：改前／改後與測例

第 44 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
                kind = keywords.count(s.substr(start, p - start)) ? "KW" : "ID";
```

**改後（對照修改）**

```cpp
kind = "ID";
```

已試編並執行的變體測例：

**輸入**

```text
int x
```

**輸出**

```text
ID "int"
ID "x"
EOF
```

## 筆記：Compiler - Scanner 與註解考試實作

> 原 `Complier/Notes/Exam/Compiler - Scanner 與註解考試實作.md`，已整份移到這裡。教材頁碼：Ch3 p.3、p.15–16、p.20。


> [!abstract] 題型定位
> Ch3 token／identifier／comment／string／longest match 的常見延伸。 以下為 **C++ 實作（補充）**；[單檔原碼](lexer.cpp) · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

### 契約與模式

`無參數`

stdin 整份來源到 EOF。每行 KIND "lexeme"，std::quoted 轉義引號／反斜線，末行 EOF。KW／ID／NUM／STRING／CHAR／OP／PUNCT；空白與 //、/* */ 不回傳 token。任何錯誤使 stdout 為空、stderr 診斷、exit 1。

### 演算法與易錯點

先略過空白／註解，再分類 ID、數字、引號 literal、運算子。ID 全部讀完才查 keyword set，所以 ifx 不拆成 if+x。三字元運算子先於二字元，再單字元；string 的 escaped quote 不結束 literal。

=／==，/／//／/*，keyword／longer ID 都要分清。exponent 以外正負號為 OP。字串內 /* 或 // 是文字。12abc 切成 NUM 12、ID abc 是否為合法敘述，還要由 parser 判斷。

> [!note] 支援範圍
> 補充 C-like lexer，非完整 C/C++。ID [A-Za-z_][A-Za-z_0-9]* 與教材的底線限制不同。NUM 允許 .5、10.、e/E；沒有 hex/octal 語意、suffix、raw string、preprocessor、行拼接。CHAR 只容一個 byte／簡單兩字元 escape，不解碼 hex／Unicode escape；STRING 保留詞素，不完整驗證 C escape 意義。block comment 不巢狀。

### 考場修改位置

keyword 改 keywords；多字元運算子改 ops 並維持長到短。若題目要求教材 ID，須在 ID 後驗證每個 _ 後至少一個 alnum、首字元為字母。要位置時集中於游標前進更新行欄，CRLF 算一次換行。

此版 floatx 為一個 ID；ac_homework 的單字母規格則為 floatdcl + id x。不要混用兩種語言契約。

### 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/03-Scanner與註解/lexer.cpp -o /tmp/lexer
/tmp/lexer < Complier/Code/03-Scanner與註解/lexer.in
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

### 完整 C++17 程式

完整程式就是同資料夾的 [lexer.cpp](lexer.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
