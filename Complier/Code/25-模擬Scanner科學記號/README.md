# 25 模擬 ScannerTest：科學記號與最後接受位置

| 項目 | 內容 |
|---|---|
| 程式 | [sci_scanner.cpp](sci_scanner.cpp) |
| 類型 | 模擬題（ScannerTest 風格，含錯誤輸入） |
| 測例 | [sci_scanner.in](sci_scanner.in) → [sci_scanner.expected](sci_scanner.expected) |
| 相關資料夾 | [17-模擬Scanner比較運算子與註解](../17-模擬Scanner比較運算子與註解/README.md)、[16-模擬Scanner宣告敘述](../16-模擬Scanner宣告敘述/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror sci_scanner.cpp -o main
./main < sci_scanner.in | diff -u sci_scanner.expected -
```

## Description

請寫一個 Scanner，NUM 支援小數與科學記號，採 **longest match**。若較長的候選在中途失敗，要退回**最後一個接受位置**，剩下的字元從頭再掃：`12e` 是 NUM `12`、ID `e`；`1.2e-` 是 NUM `1.2`、ID `e`、MINUS。

NUM 與 ID 輸出「種類 原字串」，其他 token 只輸出種類。若出現無法辨識的字元（例如 `.5`、`3.` 裡單獨的 `.`），只輸出 `invalid input`，**不可輸出任何 token**。

| Terminal | Regular Expression |
|---|---|
| NUM | `[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)?` |
| ID | `[A-Za-z_][A-Za-z0-9_]*` |
| PLUS | `\+` |
| MINUS | `-` |
| MUL | `\*` |
| DIV | `/` |
| LPR | `\(` |
| RPR | `\)` |

## Input Format

整份輸入是一段算式，可能跨多行，token 之間可有空白。指數只收小寫 `e`。

## Output Format

每個 token 一行。有錯只印 `invalid input`。

## Samples

### Sample Input 1

```text
1.5e-3 * (x + 2)
```

### Sample Output 1

```text
NUM 1.5e-3
MUL
LPR
ID x
PLUS
NUM 2
RPR
```

### Sample Input 2

```text
12e
```

### Sample Output 2

```text
NUM 12
ID e
```

### Sample Input 3

```text
1.2e-5-1.2e-
```

### Sample Output 3

```text
NUM 1.2e-5
MINUS
NUM 1.2
ID e
MINUS
```

### Sample Input 4

```text
3.
```

### Sample Output 4

```text
invalid input
```

## 解題重點

- 小數點、指數各自「整段成立才吃」：`.` 後要有數字；`e` 後（可選 `+`／`-`）要有數字，否則停在前一個接受位置。
- 不必真的存「最後接受位置」變數：每段用 lookahead 先確認，失敗就不前進，效果相同。
- `12E3` 是 NUM `12`、ID `E3`（大寫 E 不是指數）；`007e+1` 合法（`[0-9]+` 允許前導 0）。
