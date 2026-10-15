# 27 模擬 ScannerTest：複合運算子

| 項目 | 內容 |
|---|---|
| 程式 | [op_scanner.cpp](op_scanner.cpp) |
| 類型 | 模擬題（ScannerTest 風格） |
| 測例 | [op_scanner.in](op_scanner.in) → [op_scanner.expected](op_scanner.expected) |
| 相關資料夾 | [09-作業ScannerTest](../09-作業ScannerTest/README.md)、[17-模擬Scanner比較運算子與註解](../17-模擬Scanner比較運算子與註解/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror op_scanner.cpp -o main
./main < op_scanner.in | diff -u op_scanner.expected -
```

## Description

請依下表規則寫一個 Scanner。運算子採 **longest match**：`++` 是一個 INC，不是兩個 PLUS；`+++` 是 INC PLUS。

| Terminal | Regular Expression |
|---|---|
| NUM | `( [1-9][0-9]* ) \| 0` |
| INC／ADDASSIGN／PLUS | `\+\+`／`\+=`／`\+` |
| DEC／SUBASSIGN／ARROW／MINUS | `--`／`-=`／`->`／`-` |
| POW／MUL | `\*\*`／`\*` |
| EQ／ASSIGN | `==`／`=` |
| LPR／RPR | `\(`／`\)` |

## Input Format

整份輸入是一段文字，token 之間可能夾雜空格、tab 或換行。測試資料不會有錯誤資料，長度在 1000 字元內（不含換行）。

## Output Format

每個 token 一行：種類名稱；NUM 另加一個空白與數值，例如 `NUM 0`。

## Samples

### Sample Input 1

```text
1+++2
```

### Sample Output 1

```text
NUM 1
INC
PLUS
NUM 2
```

### Sample Input 2

```text
3 += 2 ** 4 -> 5
```

### Sample Output 2

```text
NUM 3
ADDASSIGN
NUM 2
POW
NUM 4
ARROW
NUM 5
```

### Sample Input 3

```text
1--2-=3 == 4=0
```

### Sample Output 3

```text
NUM 1
DEC
NUM 2
SUBASSIGN
NUM 3
EQ
NUM 4
ASSIGN
NUM 0
```

## 解題重點

- 串流版看下一字元用 `cin.peek()`：符合才 `cin.get()` 吃掉，不符合就不動，不必退回字元。
- 兩字元的候選先試：`next_is('+') ? INC : next_is('=') ? ADDASSIGN : PLUS`。
- `**=` 沒有對應 token，切成 POW ASSIGN；`012` 同 09 切成 NUM 0、NUM 12。
