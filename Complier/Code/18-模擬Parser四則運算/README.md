# 18 模擬 ParserTest：四則運算 Parser

| 項目 | 內容 |
|---|---|
| 程式 | [expr_parser.cpp](expr_parser.cpp) |
| 類型 | 模擬題（ParserTest 風格） |
| 測例 | [expr_parser.in](expr_parser.in) → [expr_parser.expected](expr_parser.expected) |
| 相關資料夾 | [10-作業ParserTest](../10-作業ParserTest/README.md)、[02-遞迴下降運算式](../02-遞迴下降運算式/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror expr_parser.cpp -o main
./main < expr_parser.in | diff -u expr_parser.expected -
```

## Description

Please write a program to read **one arithmetic expression** from stdin and check whether it follows the token definition and grammar rules below.

If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token).

※ 請使用 Recursive-Descent-Parsing 撰寫。

| Terminal | Regular Expression |
|---|---|
| NUM | `( [1-9][0-9]* ) \| 0` |
| ID | `[A-Za-z_][A-Za-z0-9_]*` |
| PLUS | `\+` |
| MINUS | `-` |
| MUL | `\*` |
| DIV | `/` |
| LPR | `\(` |
| RPR | `\)` |

### Productions

```text
1  expr      → term expr_tail
2  expr_tail → PLUS term expr_tail
3  expr_tail → MINUS term expr_tail
4  expr_tail → λ
5  term      → factor term_tail
6  term_tail → MUL factor term_tail
7  term_tail → DIV factor term_tail
8  term_tail → λ
9  factor    → NUM
10 factor    → ID
11 factor    → LPR expr RPR
```

## Input Format

整份輸入是一個運算式，token 之間可能有空白或換行。空輸入不是合法的 expr。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`。

## Samples

### Sample Input 1

```text
1+2*3
```

### Sample Output 1

```text
NUM 1
PLUS +
NUM 2
MUL *
NUM 3
```

### Sample Input 2

```text
(a + 10)
 / b2
```

### Sample Output 2

```text
LPR (
ID a
PLUS +
NUM 10
RPR )
DIV /
ID b2
```

### Sample Input 3

```text
1+*2
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
(1+2
```

### Sample Output 4

```text
invalid input
```

### Sample Input 5

```text
012
```

### Sample Output 5

```text
invalid input
```

## 解題重點

- 一個非終端符號一個函式：`expr`、`term`、`factor`；`*_tail` 的右遞迴寫成 while 迴圈。
- `factor` 看目前 token 選產生式：NUM／ID 直接吃，LPR 就遞迴 `expr` 再 match RPR，其他都失敗。
- 主程式要求 `expr()` 成功**而且**停在 END：`1+2)` 的多餘 RPR 會被這裡擋下。
- `012` 依 NUM 的 RE 切成 `NUM 0`、`NUM 12`；兩個 NUM 相鄰不符合文法。
