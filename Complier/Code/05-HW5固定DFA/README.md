# 05 HW5 固定四狀態 DFA

| 項目 | 內容 |
|---|---|
| 程式 | [hw5_check.cpp](hw5_check.cpp) |
| 類型 | 優先使用（短版） |
| 測例 | [hw5_check.in](hw5_check.in) → [hw5_check.expected](hw5_check.expected) |
| 相關資料夾 | [15-HW5-NFA-DFA作業完整版](../15-HW5-NFA-DFA作業完整版/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror hw5_check.cpp -o main
./main < hw5_check.in | diff -u hw5_check.expected -
```

## 題目內容

> 教材原題（Ch3 PPT p.55、p.58）：Write NFA, and then DFA that recognizes the tokens defined by the following regular expression；5(d)=(bc)\*d，5(a)=(a|(bc)\*d)+。以下字串 I/O 是另外定義的程式練習。

請以 DFA 判定字串是否屬於 5(a) 或 5(d) 的語言。5(a) 是一段或多段 a 或 (bc)\*d 的串接；5(d) 是零次或多次 bc 後接單一 d。所有字元必須用完才可接受。原作業若要求畫 NFA / subset DFA，另外用 automata\_homework.cpp 的 --table；本短版只給辨識結果。

- **輸入規格**：HW5A=true 選 5(a)，改 false 選 5(d)。其後每行一個字串到 EOF，沒有 T；空行代表空字串。
- **輸出規格**：每案印 ACCEPT / REJECT。大小寫敏感，僅題目語言內的字母可接受。
- **限制與適用範圍**：不支援任意正則表示式輸入；這是固定兩個語言的四個可達 state 加 dead state。

**Code 檔案名稱：**[`hw5_check.cpp`](hw5_check.cpp) （05-HW5固定DFA/hw5\_check.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror hw5_check.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

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

**輸出**

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

### 邊界測例 01

**輸入**

```text

a
d
ad
bcd
bc
dd
z
```

**輸出**

```text
REJECT
ACCEPT
ACCEPT
ACCEPT
ACCEPT
REJECT
ACCEPT
REJECT
```

## 邏輯與手動追蹤

state 0 起始、1 剛讀 b、2 剛讀 bc、3 接受、-1 死狀態。1 只能接 c；2 只能接 b 或 d；HW5(a) 的 3 可接下一組，HW5(d) 的 3 再讀字元就拒絕。

- 5(a)：a、d、ad、bcd、dd 接受；bc、空字串拒絕。
- 5(d)：d、bcd、bcbcd 接受；a、dd、bc 拒絕。
- bcd：0 --b→ 1 --c→ 2 --d→ 3；最後在 3，接受。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 改解 HW5(d) | 6 | [修改範例 01（後文）](#hw5_check-change-1) |
| 輸出 YES / NO | 30 | [修改範例 02（後文）](#hw5_check-change-2) |
| HW5(a) 外層 + 改成 \* | 30 | [修改範例 03（後文）](#hw5_check-change-3) |
| ASCII 大小寫不敏感 | 13 | [修改範例 04（後文）](#hw5_check-change-4) |
| 輸出 Case 1: 結果 | 9；30 | [修改範例 05（後文）](#hw5_check-change-5) |

<a id="hw5_check-change-1"></a>

### 01 改解 HW5(d)：改前／改後與測例

const bool HW5A = false;

第 6 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
const bool HW5A = true;
```

**改後（對照修改）**

```cpp
const bool HW5A = false;
```

已試編並執行的變體測例：

**輸入**

```text
d
dd
bcd
```

**輸出**

```text
ACCEPT
REJECT
ACCEPT
```

<a id="hw5_check-change-2"></a>

### 02 輸出 YES / NO：改前／改後與測例

將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。

第 30 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        cout << (state == 3 ? "ACCEPT\n" : "REJECT\n");
```

**改後（對照修改）**

```cpp
        cout << (state == 3 ? "YES\n" : "NO\n");
```

已試編並執行的變體測例：

**輸入**

```text
a
b
```

**輸出**

```text
YES
NO
```

<a id="hw5_check-change-3"></a>

### 03 HW5(a) 外層 + 改成 \*：改前／改後與測例

HW5A 保持 true；輸出條件 state == 3 改成 (state == 3 || word.empty())，使空字串也接受。

第 30 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        cout << (state == 3 ? "ACCEPT\n" : "REJECT\n");
```

**改後（對照修改）**

```cpp
        cout << ((state == 3 || word.empty()) ? "ACCEPT\n" : "REJECT\n");
```

已試編並執行的變體測例：

**輸入**

```text

a
bc
```

**輸出**

```text
ACCEPT
ACCEPT
REJECT
```

<a id="hw5_check-change-4"></a>

### 04 ASCII 大小寫不敏感：改前／改後與測例

第 13 行：在此行後插入

**改前（原碼）**

```cpp
        if (!word.empty() && word.back() == '\r') word.pop_back();
```

**改後（對照修改）**

```cpp
for (char& c : word) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
```

已試編並執行的變體測例：

**輸入**

```text
BCD
A
```

**輸出**

```text
ACCEPT
ACCEPT
```

<a id="hw5_check-change-5"></a>

### 05 輸出 Case 1: 結果：改前／改後與測例

第 9 行：在此行後插入

**改前（原碼）**

```cpp
    string word;
```

**改後（對照修改）**

```cpp
int case_no = 0;
```

第 30 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        cout << (state == 3 ? "ACCEPT\n" : "REJECT\n");
```

**改後（對照修改）**

```cpp
        cout << "Case " << ++case_no << ": " << (state == 3 ? "ACCEPT\n" : "REJECT\n");
```

已試編並執行的變體測例：

**輸入**

```text
a
b
```

**輸出**

```text
Case 1: ACCEPT
Case 2: REJECT
```
