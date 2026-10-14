# 06 ac 型別檢查並產生 dc

| 項目 | 內容 |
|---|---|
| 程式 | [ac_dc.cpp](ac_dc.cpp) |
| 類型 | 優先使用（短版） |
| 測例 | [ac_dc.in](ac_dc.in) → [ac_dc.expected](ac_dc.expected) |
| 相關資料夾 | [14-ac作業完整版](../14-ac作業完整版/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror ac_dc.cpp -o main
./main < ac_dc.in | diff -u ac_dc.expected -
```

## 題目內容

> 教材原題（Ch2 PPT p.39–46）：HW1 對 i x x=100 x=x+30+1 p x 建 parse tree；HW2(a) 建 AST、(b) 判斷語意與所需語言變更、(c) 顯示產碼；HW3 讓 f/float、i/int 均可宣告，number 可帶 optionally signed exponent。本檔只解產碼與型別檢查部分。

請把 ac 程式編譯為 dc stack code。所有宣告在敘述前，型別為 int / float；identifier 為一個小寫字母，i/f/p 是保留字。敘述為 id=val{(+|-)val} 或 p id。val 為 variable 或非負 number。加減左結合。檢查重複宣告、未宣告及 float→int 指定；int→float 可提升。科學記號用精確字串移動小數點轉為 dc 可讀的小數。

- **輸入規格**：整份 stdin 到 EOF；沒有分號或 T。f 或 float、i 或 int 均可。小數的點後必須有數字，指數字母限 lowercase e，可有正負。
- **輸出規格**：只印 dc target code，不直接印數值答案。非法 ac 時 stdout 空、stderr 訊息、exit 1。
- **限制與適用範圍**：帶 . 或 e 的 number 在本實作一律 float；exponent 絕對值與 mantissa 長度 &lt;=10000。無乘除、括號、unary、註解。短版無 parse tree / AST / folding，這些要求使用 ac\_homework.cpp。教材對 HW2(b) 的 No 與型別規則有疑義，詳見既有作業校讀。

**Code 檔案名稱：**[`ac_dc.cpp`](ac_dc.cpp) （06-ac產dc/ac\_dc.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror ac_dc.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

```text
i x
x=100
x=x+30+1
p x
```

**輸出**

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

### 邊界測例 01

**輸入**

```text
i x x=2 px
```

**輸出**

```text
2
sx
0 k
lx
p
si
```

### 邊界測例 02

**輸入**

```text
f x x=1e-2 px
```

**輸出**

```text
0.01
sx
0 k
lx
p
si
```

### 邊界測例 03

**輸入**

```text
i x x=1.2
```

**輸出**

```text
stdout：空
stderr：invalid ac program
exit 1
```

### 邊界測例 04

**輸入**

```text
p x
```

**輸出**

```text
stdout：空
stderr：invalid ac program
exit 1
```

### 邊界測例 05

**輸入**

```text
i x i x
```

**輸出**

```text
stdout：空
stderr：invalid ac program
exit 1
```

## 邏輯與手動追蹤

scan 成 token；宣告填 types；value 回傳 leaf code 與是否 float。解析加減時直接輸出 postfix；int→float 印 5 k，assign 印 s&lt;變數>，print 印 l&lt;變數>/p/si。要樹或常數摺疊，用 ac\_homework.cpp。

- x=100：100 → sx → 0 k；p x：lx → p → si。
- i a f b b=a+3.2：la → 5 k → 3.2 → +；提升必須在對應 operand 後。
- 123e-22 → 0.0000000000000000000123，不能先轉 double 再印。
- i x x=1e0：數值雖為 1，來源型別是 float，所以拒絕指定給 int。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 只允許 i / f 短宣告 | 43；44；45 | [修改範例 01（後文）](#ac_dc-change-1) |
| 科學記號也接受 E | 35；57；98 | [修改範例 02（後文）](#ac_dc-change-2) |
| 浮點運算 scale 改成 10 | 128；131；136 | [修改範例 03（後文）](#ac_dc-change-3) |
| 合法程式只輸出 OK | 140 | [修改範例 04（後文）](#ac_dc-change-4) |
| assignment 後不要產生 scale reset | 138 | [修改範例 05（後文）](#ac_dc-change-5) |

<a id="ac_dc-change-1"></a>

### 01 只允許 i / f 短宣告：改前／改後與測例

刪除 float / int 完整字的兩行判定；第三行開頭 else if 改成 if。

第 43 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            if (kind == 'f' && s.compare(start, 5, "float") == 0) j = start + 5;
```

**改後（對照修改）**

```cpp
（刪除；不要貼這段提示文字）
```

第 44 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            else if (kind == 'i' && s.compare(start, 3, "int") == 0) j = start + 3;
```

**改後（對照修改）**

```cpp
（刪除；不要貼這段提示文字）
```

第 45 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            else if ((kind >= 'a' && kind <= 'z') || kind == '=' || kind == '+' || kind == '-') {}
```

**改後（對照修改）**

```cpp
            if ((kind >= 'a' && kind <= 'z') || kind == '=' || kind == '+' || kind == '-') {}
```

已試編並執行的變體測例：

**輸入**

```text
i x x=1 px
```

**輸出**

```text
1
sx
0 k
lx
p
si
```

<a id="ac_dc-change-2"></a>

### 02 科學記號也接受 E：改前／改後與測例

條件改成 if (j &lt; s.size() &amp;&amp; (s\[j\] == 'e' || s\[j\] == 'E')) { find 改成 text.find\_first\_of("eE"); find\_first\_of(".e") 改成 find\_first\_of(".eE")。

第 35 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            if (j < s.size() && s[j] == 'e') {
```

**改後（對照修改）**

```cpp
if (j < s.size() && (s[j] == 'e' || s[j] == 'E')) {
```

第 57 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    size_t e = text.find('e');
```

**改後（對照修改）**

```cpp
size_t e = text.find_first_of("eE");
```

第 98 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    return {decimal(text) + "\n", text.find_first_of(".e") != string::npos};
```

**改後（對照修改）**

```cpp
    return {decimal(text) + "\n", text.find_first_of(".eE") != string::npos};
```

已試編並執行的變體測例：

**輸入**

```text
f x x=1E-2 px
```

**輸出**

```text
0.01
sx
0 k
lx
p
si
```

<a id="ac_dc-change-3"></a>

### 03 浮點運算 scale 改成 10：改前／改後與測例

三行的 "5 k\\n" 都改成 "10 k\\n"；assignment 的 "0 k\\n" 保留。

第 128 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
                if (!left.second && right.second) out << "5 k\n";
```

**改後（對照修改）**

```cpp
                if (!left.second && right.second) out << "10 k\n";
```

第 131 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
                if (left.second && !right.second) out << "5 k\n";
```

**改後（對照修改）**

```cpp
                if (left.second && !right.second) out << "10 k\n";
```

第 136 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            if (target_float && !left.second) out << "5 k\n";
```

**改後（對照修改）**

```cpp
            if (target_float && !left.second) out << "10 k\n";
```

已試編並執行的變體測例：

**輸入**

```text
f x x=1 px
```

**輸出**

```text
1
10 k
sx
0 k
lx
p
si
```

<a id="ac_dc-change-4"></a>

### 04 合法程式只輸出 OK：改前／改後與測例

第 140 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        cout << out.str(); return cout ? 0 : 1;
```

**改後（對照修改）**

```cpp
cout << "OK\n"; return cout ? 0 : 1;
```

已試編並執行的變體測例：

**輸入**

```text
i x x=2 px
```

**輸出**

```text
OK
```

<a id="ac_dc-change-5"></a>

### 05 assignment 後不要產生 scale reset：改前／改後與測例

第 138 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            out << 's' << target << "\n0 k\n";
```

**改後（對照修改）**

```cpp
            out << 's' << target << "\n";
```

已試編並執行的變體測例：

**輸入**

```text
i x x=2 px
```

**輸出**

```text
2
sx
lx
p
si
```
