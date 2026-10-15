# 30 模擬 ParserTest：布林運算式

| 項目 | 內容 |
|---|---|
| 程式 | [bool_parser.cpp](bool_parser.cpp) |
| 類型 | 模擬題（ParserTest 風格） |
| 測例 | [bool_parser.in](bool_parser.in) → [bool_parser.expected](bool_parser.expected) |
| 相關資料夾 | [18-模擬Parser四則運算](../18-模擬Parser四則運算/README.md)、[23-模擬Parser敘述與區塊](../23-模擬Parser敘述與區塊/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror bool_parser.cpp -o main
./main < bool_parser.in | diff -u bool_parser.expected -
```

## Description

Please write a program to read one **boolean expression** from stdin and check whether it follows the token definition and grammar rules below.

If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token).

※ 請使用 Recursive-Descent-Parsing 撰寫。優先序：`not` > `and` > `or`；keyword 先讀完整個字再判斷（`order` 是 ID）。

| Terminal | Regular Expression |
|---|---|
| OR／AND／NOT | `or`／`and`／`not` |
| ID | `[A-Za-z_][A-Za-z0-9_]*`（keyword 除外） |
| NUM | `[0-9]+` |
| EQ | `==` |
| LT | `<` |
| GT | `>` |
| LPR | `\(` |
| RPR | `\)` |

### Productions

```text
1  bexpr      → bterm bexpr_tail
2  bexpr_tail → OR bterm bexpr_tail
3  bexpr_tail → λ
4  bterm      → bfactor bterm_tail
5  bterm_tail → AND bfactor bterm_tail
6  bterm_tail → λ
7  bfactor    → NOT bfactor
8  bfactor    → LPR bexpr RPR
9  bfactor    → rel
10 rel        → operand relop operand
11 relop      → EQ | LT | GT
12 operand    → ID | NUM
```

## Input Format

整份輸入是一個布林運算式，token 之間可能有空白或換行。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`（不可輸出任何 token）。

## Samples

### Sample Input 1

```text
a < 3 and not (b == c or d > 0)
```

### Sample Output 1

```text
ID a
LT <
NUM 3
AND and
NOT not
LPR (
ID b
EQ ==
ID c
OR or
ID d
GT >
NUM 0
RPR )
```

### Sample Input 2

```text
order == 1
```

### Sample Output 2

```text
ID order
EQ ==
NUM 1
```

### Sample Input 3

```text
a = 1
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
not a
```

### Sample Output 4

```text
invalid input
```

## 解題重點

- 分層同四則運算：or 層 while 吃 OR、and 層 while 吃 AND；not 是一元，遞迴 `NOT bfactor`。
- `(` 一定開始括號內的 bexpr，因為 operand 不含括號，所以 bfactor 三條規則看第一個 token 就能選。
- 單獨的 `=` 不是 token（invalid）；`not a` 缺比較運算子也不合法。
