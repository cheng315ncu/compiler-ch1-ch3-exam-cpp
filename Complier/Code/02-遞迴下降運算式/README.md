# 02 遞迴下降運算式（求值／Postfix／AST）

| 項目 | 內容 |
|---|---|
| 程式 | [expression.cpp](expression.cpp) |
| 類型 | 優先使用（短版） |
| 測例 | [expression.in](expression.in) → [expression.expected](expression.expected) |
| 相關資料夾 | [12-運算式parser完整版](../12-運算式parser完整版/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror expression.cpp -o main
./main < expression.in | diff -u expression.expected -
```

## 題目內容

> Ch2 recursive descent / AST 的延伸模擬題；乘除、括號與一元正負不在原 ac 文法。

請讀入每行運算式，依通常優先序計算結果，或依題目指定改為 postfix / AST。一元正負優先於乘除，乘除優先於加減；同級二元左結合。括號可覆寫優先序。number 允許 .5、10.、十進位小數及 e/E 科學記號；ID 符合 \[A-Za-z\_\]\[A-Za-z\_0-9\]\*。求值模式不允許變數。

- **輸入規格**：每行一個完整運算式到 EOF，沒有 T；完全空輸入是零案例，但空白行本身是非法運算式。
- **輸出規格**：預設 eval：每行印 15 位有效數字的 long double 結果。postfix：以一個空白分隔 token。一元正負用 pos/neg。ast：印前序括號表示。
- **限制與適用範圍**：嵌套括號／一元鏈最多 256；不支援 %、^、函式或隱含乘法。非法字元、缺 operand、零除、非有限值：stdout 空、stderr 訊息、exit 1。

**Code 檔案名稱：**[`expression.cpp`](expression.cpp) （02-遞迴下降運算式/expression.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror expression.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

```text
(2+3)*4
100-30-1
8/2/2
-2*-3
.5 + 1e-2
```

**輸出**

```text
20
69
2
6
0.51
```

### 邊界測例 01

**輸入**

```text
1+2*3
```

**輸出**

```text
7
```

### 邊界測例 02

**輸入**

```text
(2+3)*4
```

**輸出**

```text
20
```

### 邊界測例 03

**輸入**

```text
100-30-1
```

**輸出**

```text
69
```

### 邊界測例 04

**輸入**

```text
8/2/2
```

**輸出**

```text
2
```

### 邊界測例 05

**輸入**

```text
-2*-3
```

**輸出**

```text
6
```

### 邊界測例 06

**輸入**

```text
.5+1e-2
```

**輸出**

```text
0.51
```

### 邊界測例 07

**輸入**

```text
1/0
```

**輸出**

```text
stdout：空
stderr：invalid expression
exit 1
```

### 邊界測例 08

**輸入**

```text
2(3)
```

**輸出**

```text
stdout：空
stderr：invalid expression
exit 1
```

## 邏輯與手動追蹤

expr 迴圈處理 + -，呼叫 term；term 迴圈處理 \* /，呼叫 unary。unary 讀數字、變數或括號；同級二元由左往右合併。eval 不接受變數；括號／一元鏈嵌套上限 256。

- 100-30-1：先 100-30，再 -1，結果 69。
- a+b\*c：AST 是 (+ a (\* b c))；postfix 是 a b c \* +。
- -2\*-3：讀 2 → neg → 3 → neg → \*，結果 6。
- 2(3) 並非隱含乘法，會因多餘內容拒絕。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 只輸出 postfix | 12 | [修改範例 01（後文）](#expression-change-1) |
| 只輸出 AST | 12 | [修改範例 02（後文）](#expression-change-2) |
| 固定小數點後 2 位 | 106 | [修改範例 03（後文）](#expression-change-3) |
| 所有模式均禁止變數 | 51 | [修改範例 04（後文）](#expression-change-4) |
| 每次除法結果向零截斷 | 85 | [修改範例 05（後文）](#expression-change-5) |

<a id="expression-change-1"></a>

### 01 只輸出 postfix：改前／改後與測例

const string MODE = "postfix";

第 12 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
const string MODE = "eval";
```

**改後（對照修改）**

```cpp
const string MODE = "postfix";
```

已試編並執行的變體測例：

**輸入**

```text
a+b*c
```

**輸出**

```text
a b c * +
```

<a id="expression-change-2"></a>

### 02 只輸出 AST：改前／改後與測例

const string MODE = "ast";

第 12 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
const string MODE = "eval";
```

**改後（對照修改）**

```cpp
const string MODE = "ast";
```

已試編並執行的變體測例：

**輸入**

```text
a+b*c
```

**輸出**

```text
(+ a (* b c))
```

<a id="expression-change-3"></a>

### 03 固定小數點後 2 位：改前／改後與測例

ostringstream out; out &lt;&lt; fixed &lt;&lt; setprecision(2);

第 106 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    ostringstream out; out << setprecision(15);
```

**改後（對照修改）**

```cpp
ostringstream out; out << fixed << setprecision(2);
```

已試編並執行的變體測例：

**輸入**

```text
1/4
```

**輸出**

```text
0.25
```

<a id="expression-change-4"></a>

### 04 所有模式均禁止變數：改前／改後與測例

在這行後插入 if (id) fail();；eval 原本已禁止。

第 51 行：在此行後插入

**改前（原碼）**

```cpp
    bool id = letter(c);
```

**改後（對照修改）**

```cpp
if (id) fail();
```

已試編並執行的變體測例：

**輸入**

```text
x+1
```

**輸出**

```text
stdout：空
stderr：invalid expression
exit 1
```

<a id="expression-change-5"></a>

### 05 每次除法結果向零截斷：改前／改後與測例

第 85 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        if (op == '/') { if (b.number == 0) fail(); a.number /= b.number; }
```

**改後（對照修改）**

```cpp
        if (op == '/') { if (b.number == 0) fail(); a.number = trunc(a.number / b.number); }
```

已試編並執行的變體測例：

**輸入**

```text
-7/2
```

**輸出**

```text
-3
```
