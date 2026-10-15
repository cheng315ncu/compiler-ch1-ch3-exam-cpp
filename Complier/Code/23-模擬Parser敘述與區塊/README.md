# 23 模擬 ParserTest：if／while／區塊敘述

| 項目 | 內容 |
|---|---|
| 程式 | [stmt_parser.cpp](stmt_parser.cpp) |
| 類型 | 模擬題（ParserTest 風格） |
| 測例 | [stmt_parser.in](stmt_parser.in) → [stmt_parser.expected](stmt_parser.expected) |
| 相關資料夾 | [18-模擬Parser四則運算](../18-模擬Parser四則運算/README.md)、[16-模擬Scanner宣告敘述](../16-模擬Scanner宣告敘述/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror stmt_parser.cpp -o main
./main < stmt_parser.in | diff -u stmt_parser.expected -
```

## Description

Please write a program to read a **statement list** from stdin and check whether it follows the token definition and grammar rules below.

If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token).

※ 請使用 Recursive-Descent-Parsing 撰寫。`if`、`else`、`while`、`print` 是 keyword；先讀完整個字再判斷（`iff` 是 ID）。

| Terminal | Regular Expression |
|---|---|
| IF／ELSE／WHILE／PRINT | `if`／`else`／`while`／`print` |
| ID | `[A-Za-z_][A-Za-z0-9_]*`（keyword 除外） |
| NUM | `[0-9]+` |
| ASSIGN | `=` |
| PLUS | `\+` |
| LPR／RPR | `\(`／`\)` |
| LBR／RBR | `\{`／`\}` |
| SEMI | `;` |

### Productions

```text
1  stmts     → stmt stmts
2  stmts     → λ
3  stmt      → ID ASSIGN expr SEMI
4  stmt      → PRINT expr SEMI
5  stmt      → IF LPR expr RPR stmt else_part
6  stmt      → WHILE LPR expr RPR stmt
7  stmt      → LBR stmts RBR
8  else_part → ELSE stmt
9  else_part → λ
10 expr      → atom expr_tail
11 expr_tail → PLUS atom expr_tail
12 expr_tail → λ
13 atom      → ID
14 atom      → NUM
```

`else_part` 在 ELSE 上有 LL(1) 衝突（dangling else）：規定 **else 接給最近的 if**，看到 ELSE 就選規則 8。

## Input Format

整份輸入是一段敘述，可能跨多行。空輸入是合法的 stmts（不輸出任何東西）。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`。

## Samples

### Sample Input 1

```text
x = 1;
print x + 2;
```

### Sample Output 1

```text
ID x
ASSIGN =
NUM 1
SEMI ;
PRINT print
ID x
PLUS +
NUM 2
SEMI ;
```

### Sample Input 2

```text
if (a) if (b) x = 1; else x = 2;
```

### Sample Output 2

```text
IF if
LPR (
ID a
RPR )
IF if
LPR (
ID b
RPR )
ID x
ASSIGN =
NUM 1
SEMI ;
ELSE else
ID x
ASSIGN =
NUM 2
SEMI ;
```

### Sample Input 3

```text
else x = 1;
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
if (a) { x = 1;
```

### Sample Output 4

```text
invalid input
```

## 解題重點

- `stmts` 寫成 while：token 屬於 FIRST(stmt) = {ID, PRINT, IF, WHILE, LBR} 才繼續；之後由呼叫端查 RBR（區塊）或 END（main）。
- dangling else：`(!match(ELSE) || stmt())`，看到 ELSE 就吃，自然接給最近的 if。
- keyword 先讀完整字再比對；`iff = 1;` 是合法的 ID 指定。
