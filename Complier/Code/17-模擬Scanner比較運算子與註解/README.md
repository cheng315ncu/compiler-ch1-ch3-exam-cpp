# 17 模擬 ScannerTest：比較運算子與註解

| 項目 | 內容 |
|---|---|
| 程式 | [compare_scanner.cpp](compare_scanner.cpp) |
| 類型 | 模擬題（ScannerTest 風格，含錯誤輸入） |
| 測例 | [compare_scanner.in](compare_scanner.in) → [compare_scanner.expected](compare_scanner.expected) |
| 相關資料夾 | [09-作業ScannerTest](../09-作業ScannerTest/README.md)、[03-Scanner與註解](../03-Scanner與註解/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror compare_scanner.cpp -o main
./main < compare_scanner.in | diff -u compare_scanner.expected -
```

## Description

請寫一個 Scanner 處理比較運算子與註解。多字元運算子採 **longest match**：`<=` 是一個 LE，不是 LT 加 ASSIGN。註解不產生 token：`//` 到行尾（或 EOF），`/*` 到第一個 `*/`（不巢狀）。

輸入**可能有錯誤**：若出現無法辨識的字元（例如單獨的 `!` 或 `/`），或 `/*` 沒有對應的 `*/`，只輸出 `invalid input`，**不可輸出任何 token**。

| Terminal | Regular Expression |
|---|---|
| ID | `[A-Za-z_][A-Za-z0-9_]*` |
| NUM | `[0-9]+` |
| LE | `<=` |
| GE | `>=` |
| EQ | `==` |
| NE | `!=` |
| LT | `<` |
| GT | `>` |
| ASSIGN | `=` |
| LPR | `\(` |
| RPR | `\)` |
| SEMI | `;` |

## Input Format

整份輸入是一段程式，可能跨多行。長度在 1000 字元內（不含換行）。

## Output Format

合法時每個 token 一行；ID、NUM 附上原字串（以一個空白分隔），其餘只印種類名稱。不合法時只印一行 `invalid input`。

## Samples

### Sample Input 1

```text
if (a<=b) x=1;
```

### Sample Output 1

```text
ID if
LPR
ID a
LE
ID b
RPR
ID x
ASSIGN
NUM 1
SEMI
```

### Sample Input 2

```text
a == b // compare
/* block
comment */ c != d >= e
```

### Sample Output 2

```text
ID a
EQ
ID b
ID c
NE
ID d
GE
ID e
```

### Sample Input 3

```text
a<b>c=d
```

### Sample Output 3

```text
ID a
LT
ID b
GT
ID c
ASSIGN
ID d
```

### Sample Input 4

```text
x = 3 ! 4
```

### Sample Output 4

```text
invalid input
```

### Sample Input 5

```text
a /* not closed
```

### Sample Output 5

```text
invalid input
```

### Sample Input 6

```text
x / 2
```

### Sample Output 6

```text
invalid input
```

## 解題重點

- 運算子表把兩字元的排在前面，依序比對，第一個吻合的就是最長的。
- 先判斷 `//`、`/*`，再判斷運算子；單獨的 `/` 不是 token。
- 「錯誤時不印任何 token」：先把輸出存在字串，全部掃完才決定印 token 還是 `invalid input`。
