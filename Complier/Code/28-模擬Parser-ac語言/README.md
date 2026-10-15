# 28 模擬 ParserTest：ac 語言

| 項目 | 內容 |
|---|---|
| 程式 | [ac_parser.cpp](ac_parser.cpp) |
| 類型 | 模擬題（ParserTest 風格） |
| 測例 | [ac_parser.in](ac_parser.in) → [ac_parser.expected](ac_parser.expected) |
| 相關資料夾 | [14-ac作業完整版](../14-ac作業完整版/README.md)、[06-ac產dc](../06-ac產dc/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror ac_parser.cpp -o main
./main < ac_parser.in | diff -u ac_parser.expected -
```

## Description

Please write a program to read an **ac program** (Ch2 Fig 2.1) from stdin and check whether it follows the token definition and grammar rules below.

If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token).

※ 請使用 Recursive-Descent-Parsing 撰寫。只檢查語法；宣告與型別（例如 `i a a=3.2`）不在本題範圍。

| Terminal | Regular Expression |
|---|---|
| FLOATDCL | `f` |
| INTDCL | `i` |
| PRINT | `p` |
| ID | `[a-eghj-oq-z]`（單一小寫字母，扣 f、i、p） |
| ASSIGN | `=` |
| PLUS | `\+` |
| MINUS | `-` |
| INUM | `[0-9]+` |
| FNUM | `[0-9]+\.[0-9]+` |

### Productions

```text
1  Prog  → Dcls Stmts $
2  Dcls  → Dcl Dcls
3  Dcls  → λ
4  Dcl   → FLOATDCL ID
5  Dcl   → INTDCL ID
6  Stmts → Stmt Stmts
7  Stmts → λ
8  Stmt  → ID ASSIGN Val Expr
9  Stmt  → PRINT ID
10 Expr  → PLUS Val Expr
11 Expr  → MINUS Val Expr
12 Expr  → λ
13 Val   → ID
14 Val   → INUM
15 Val   → FNUM
```

## Input Format

整份輸入是一個 ac 程式，token 之間可能有空白或換行。`$` 代表輸入結束（EOF），不會出現在輸入中。空輸入合法。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`（不可輸出任何 token）。

## Samples

### Sample Input 1

```text
f b
i a
a = 5
b = a + 3.2
p b
```

### Sample Output 1

```text
FLOATDCL f
ID b
INTDCL i
ID a
ID a
ASSIGN =
INUM 5
ID b
ASSIGN =
ID a
PLUS +
FNUM 3.2
PRINT p
ID b
```

### Sample Input 2

```text
i a a = +5
```

### Sample Output 2

```text
invalid input
```

### Sample Input 3

```text
ab = 1
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
i a p 5
```

### Sample Output 4

```text
invalid input
```

## 解題重點

- ID 只有一個字母：`ab` 是 ID a、ID b，所以 `ab = 1` 不合法。f／i／p 永遠是 keyword。
- Dcls、Stmts 用 while：分別看 FIRST = {FLOATDCL, INTDCL}、{ID, PRINT}；最後 token 必須是 END（規則 1 的 `$`）。
- Expr 的 λ 不用特別處理：迴圈遇到不是 PLUS／MINUS 就停，交給 Stmts／END 檢查。`3.` 的點不屬於任何 token → invalid。
