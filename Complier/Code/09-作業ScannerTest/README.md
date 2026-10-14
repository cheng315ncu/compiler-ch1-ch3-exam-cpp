# 09 作業 ScannerTest：算式 Scanner

| 項目 | 內容 |
|---|---|
| 程式 | [scanner.cpp](scanner.cpp) |
| 類型 | 課程作業 |
| 測例 | [scanner.in](scanner.in) → [scanner.expected](scanner.expected) |
| 原題 PDF | [ScannerTest.txt](ScannerTest.txt)（Google Drive 連結） |
| 相關資料夾 | [03-Scanner與註解](../03-Scanner與註解/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror scanner.cpp -o main
./main < scanner.in | diff -u scanner.expected -
```

## 題目內容

> 課程作業原題（ScannerTest）。Token 規則照題目表格；與 03 的 C-like lexer 不同，只有數字、四則運算子與括號。

Scanner 先把 input text 依規則轉成 Token，Parser 才能處理。請依題目規則寫一個 Scanner，取得 Tokens 並印出。Terminal：NUM ( \[1-9\]\[0-9\]\* ) | 0；PLUS \\+；MINUS \\-；MUL \\\*；DIV \\/；LPR \\(；RPR \\)。

- **輸入規格**：整份 stdin 是一條運算式，中間可能夾雜空格或換行；測資不會有錯誤資料，長度在 1000 字元內（不含換行）。
- **輸出規格**：每個 token 一行：種類名稱；NUM 另加一個空白與數值，例如 NUM 0。每個 token 後接 \\n。
- **限制與適用範圍**：逐字元串流讀取，不存整份輸入。NUM 開頭 0 只吃一位，所以 012 切成 NUM 0、NUM 12。非法字元不在題目範圍：已印的 token 保留，之後 exit 1。

**Code 檔案名稱：**[`scanner.cpp`](scanner.cpp) （09-作業ScannerTest/scanner.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror scanner.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

### 題目範例 01

**輸入**

```text
1+2
```

**輸出**

```text
NUM 1
PLUS
NUM 2
```

### 題目範例 02

**輸入**

```text
( 1+
 - 2
 )
```

**輸出**

```text
LPR
NUM 1
PLUS
MINUS
NUM 2
RPR
```

### 題目範例 03

**輸入**

```text
   (
(1  +

 2*   3
 / 4   )
 )
```

**輸出**

```text
LPR
LPR
NUM 1
PLUS
NUM 2
MUL
NUM 3
DIV
NUM 4
RPR
RPR
```

### 邊界測例 01

**輸入**

```text
012
```

**輸出**

```text
NUM 0
NUM 12
```

### 邊界測例 02

**輸入**

```text
1+2
```

**輸出**

```text
NUM 1
PLUS
NUM 2
```

### 邊界測例 03

**輸入**

```text

```

**輸出**

```text
stdout：空
```

### 邊界測例 04

**輸入**

```text
1$2
```

**輸出**

```text
NUM 1
exit 1
```

## 邏輯與手動追蹤

一次讀一個字元 c：空白直接跳過；數字開始讀 NUM，其餘六個字元用 switch 對應名稱。讀 NUM 時會多讀一個字元才知道數字結束，所以那個字元留在 c，下一輪直接處理，不能再 cin.get()。

- 10+0：讀 1 → 0 是數字繼續 → 讀到 + 結束，印 NUM 10；+ 已在 c，下一輪印 PLUS；0 開頭只吃一位，印 NUM 0。
- 012：0 開頭立即結束，印 NUM 0；c 是 1，下一輪讀成 NUM 12（照 RE 最長匹配）。
- ( 1+ 換行 - 2：空白與換行都跳過，不產生 token；- 是 MINUS，不和 2 合成負數。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 允許前導 0 的數字（NUM -> \[0-9\]+） | 17 | [修改範例 01（後文）](#hw_scanner-change-1) |
| 增加 MOD（%） | 28 | [修改範例 02（後文）](#hw_scanner-change-2) |
| 非法字元印 ERROR 後繼續 | 30 | [修改範例 03（後文）](#hw_scanner-change-3) |

<a id="hw_scanner-change-1"></a>

### 01 允許前導 0 的數字（NUM -> \[0-9\]+）：改前／改後與測例

拿掉 num != "0" 的條件，任何數字都繼續讀到非數字為止。

第 17 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            if (num != "0") while (isdigit(c)) { num += char(c); c = cin.get(); }
```

**改後（對照修改）**

```cpp
            while (isdigit(c)) { num += char(c); c = cin.get(); }
```

已試編並執行的變體測例：

**輸入**

```text
012+3
```

**輸出**

```text
NUM 012
PLUS
NUM 3
```

<a id="hw_scanner-change-2"></a>

### 02 增加 MOD（%）：改前／改後與測例

在 switch 多加一個 case；其他 token 不變。

第 28 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            case ')': cout << "RPR\n";   break;
```

**改後（對照修改）**

```cpp
            case ')': cout << "RPR\n";   break;
            case '%': cout << "MOD\n";   break;
```

已試編並執行的變體測例：

**輸入**

```text
7 % 3
```

**輸出**

```text
NUM 7
MOD
NUM 3
```

<a id="hw_scanner-change-3"></a>

### 03 非法字元印 ERROR 後繼續：改前／改後與測例

default 不再結束程式，改印 ERROR 與該字元，再讀下一個字元。

第 30 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            default: return 1;
```

**改後（對照修改）**

```cpp
            default: cout << "ERROR " << char(c) << '\n'; break;
```

已試編並執行的變體測例：

**輸入**

```text
1$2
```

**輸出**

```text
NUM 1
ERROR $
NUM 2
```
