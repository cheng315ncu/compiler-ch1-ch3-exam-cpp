# 10 作業 ParserTest：Recursive-Descent Parser

| 項目 | 內容 |
|---|---|
| 程式 | [parser.cpp](parser.cpp) |
| 類型 | 課程作業 |
| 測例 | [parser.in](parser.in) → [parser.expected](parser.expected) |
| 原題 PDF | [ParserTest.txt](ParserTest.txt)（Google Drive 連結） |
| 相關資料夾 | [02-遞迴下降運算式](../02-遞迴下降運算式/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror parser.cpp -o main
./main < parser.in | diff -u parser.expected -
```

## 題目內容

> 課程作業原題（ParserTest）。題目要求使用 Recursive-Descent Parsing（ch02 ppt p.20 起）撰寫，否則不予計分；測試檔換行皆為 \\n。

從 stdin 讀入程式，依 token 定義與文法檢查。合法時逐行印出 token 種類與原字串（以一個空白分隔、換行結尾）；不合法只印 invalid input，不可輸出任何 token。Terminal：ID \[A-Za-z\_\]\[A-Za-z0-9\_\]\*；STRLIT "\[^"\]\*"；LBR \\(；RBR \\)；DOT \\.。Productions：program → stmts；stmts → stmt stmts | λ；stmt → primary | STRLIT | λ；primary → ID primary\_tail；primary\_tail → DOT ID primary\_tail | LBR stmt RBR primary\_tail | λ。

- **輸入規格**：整份 stdin 到 EOF；token 之間可有任意空白與換行。STRLIT 的 \[^"\]\* 可含空白與換行。
- **輸出規格**：合法：每個 token 一行「種類 原字串」。不合法：只印一行 invalid input。空輸入合法（stmts → λ），不輸出任何東西。
- **限制與適用範圍**：先完整檢查再重掃輸出，所以不合法時不會漏印 token。primary\_tail 的右遞迴寫成 while 迴圈，stmt 仍遞迴處理括號內部。

**Code 檔案名稱：**[`parser.cpp`](parser.cpp) （10-作業ParserTest/parser.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror parser.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

### 題目範例 01

**輸入**

```text
"test_string"
Test_ID
```

**輸出**

```text
STRLIT "test_string"
ID Test_ID
```

### 題目範例 02

**輸入**

```text
illiga!id
```

**輸出**

```text
invalid input
```

### 題目範例 03

**輸入**

```text
Str. length()
```

**輸出**

```text
ID Str
DOT .
ID length
LBR (
RBR )
```

### 題目範例 04

**輸入**

```text
printf("HelloWorld")
```

**輸出**

```text
ID printf
LBR (
STRLIT "HelloWorld"
RBR )
```

### 邊界測例 01

**輸入**

```text

```

**輸出**

```text
stdout：空
```

### 邊界測例 02

**輸入**

```text
f(g(x)).y
```

**輸出**

```text
ID f
LBR (
ID g
LBR (
ID x
RBR )
RBR )
DOT .
ID y
```

### 邊界測例 03

**輸入**

```text
"abc
```

**輸出**

```text
invalid input
```

### 邊界測例 04

**輸入**

```text
a.
```

**輸出**

```text
invalid input
```

### 邊界測例 05

**輸入**

```text
(a)
```

**輸出**

```text
invalid input
```

### 邊界測例 06

**輸入**

```text
"a
b"
```

**輸出**

```text
STRLIT "a
b"
```

## 邏輯與手動追蹤

next\_token 是 Scanner，token 記目前種類，\[start, pos) 是原字串。stmt 依目前 token 選產生式：STRLIT 直接 match；ID 之後重複吃 DOT ID 或 LBR stmt RBR；都不是時走 λ，但 λ 後面只能是 RBR 或 EOF。main 以 while 實作 stmts，最後必須停在 END；全部合法才把 pos 歸零重掃並輸出。

- Str. length()：ID Str → DOT → match(ID length) → LBR → stmt 看到 RBR 走 λ → match(RBR) → END，合法。
- illiga!id：ID illiga 之後是 INVALID(!)，stmt 回到 main，迴圈停下時 token 不是 END → invalid input。
- a.：DOT 後 match(ID) 遇到 END 失敗；(a)：開頭 LBR 不能開始 stmt，main 迴圈不進入，token ≠ END。
- "abc 沒有結尾引號：Scanner 回傳 INVALID，整份輸入 invalid。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 括號內允許逗號分隔多個 stmt | 7；31；54；62 | [修改範例 01（後文）](#hw_parser-change-1) |
| 只判斷合法：輸出 YES / NO | 62；73–80 | [修改範例 02（後文）](#hw_parser-change-2) |
| STRLIT 不可跨行 | 26 | [修改範例 03（後文）](#hw_parser-change-3) |

<a id="hw_parser-change-1"></a>

### 01 括號內允許逗號分隔多個 stmt：改前／改後與測例

新增 COMMA token；LBR 之後改成 stmt (COMMA stmt)\* 再 match(RBR)。enum 與 names 順序要一致。注意 stmt 可為 λ，f(a,) 仍會被接受。

第 7 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
enum Token { ID, STRLIT, LBR, RBR, DOT, END, INVALID };
```

**改後（對照修改）**

```cpp
enum Token { ID, STRLIT, LBR, RBR, DOT, COMMA, END, INVALID };
```

第 31 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    else if (c == '.') token = DOT;
```

**改後（對照修改）**

```cpp
    else if (c == '.') token = DOT;
    else if (c == ',') token = COMMA;
```

第 54 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            if (!stmt() || !match(RBR)) return false;
```

**改後（對照修改）**

```cpp
            if (!stmt()) return false;
            while (token == COMMA) { next_token(); if (!stmt()) return false; }
            if (!match(RBR)) return false;
```

第 62 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    const char* names[] = {"ID", "STRLIT", "LBR", "RBR", "DOT"};
```

**改後（對照修改）**

```cpp
    const char* names[] = {"ID", "STRLIT", "LBR", "RBR", "DOT", "COMMA"};
```

已試編並執行的變體測例：

**輸入**

```text
f(a, "b").g()
```

**輸出**

```text
ID f
LBR (
ID a
COMMA ,
STRLIT "b"
RBR )
DOT .
ID g
LBR (
RBR )
```

**輸入**

```text
f(,a)
```

**輸出**

```text
invalid input
```

<a id="hw_parser-change-2"></a>

### 02 只判斷合法：輸出 YES / NO：改前／改後與測例

刪除 names（否則 -Werror 會報未使用變數），輸出區塊改成一行。

第 62 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    const char* names[] = {"ID", "STRLIT", "LBR", "RBR", "DOT"};
```

**改後（對照修改）**

```cpp
（刪除；不要貼這段提示文字）
```

第 73–80 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    if (!valid || token != END) {
        cout << "invalid input\n";
    } else {
        // 全部合法後才從頭重掃並輸出 token。
        pos = 0;
        for (next_token(); token != END; next_token())
            cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
    }
```

**改後（對照修改）**

```cpp
    cout << (valid && token == END ? "YES\n" : "NO\n");
```

已試編並執行的變體測例：

**輸入**

```text
a.b("c")
```

**輸出**

```text
YES
```

**輸入**

```text
a..b
```

**輸出**

```text
NO
```

<a id="hw_parser-change-3"></a>

### 03 STRLIT 不可跨行：改前／改後與測例

找結尾引號時同時找換行；先遇到換行就視為未結束的字串（INVALID）。

第 26 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        size_t end = src.find('"', pos);
```

**改後（對照修改）**

```cpp
        size_t end = src.find_first_of("\"\n", pos);
        if (end != string::npos && src[end] == '\n') end = string::npos;
```

已試編並執行的變體測例：

**輸入**

```text
"a
b"
```

**輸出**

```text
invalid input
```

**輸入**

```text
"a b"
```

**輸出**

```text
STRLIT "a b"
```
