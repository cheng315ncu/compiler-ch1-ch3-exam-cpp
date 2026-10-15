# 29 模擬 ParserTest：Regular Expression 語法

| 項目 | 內容 |
|---|---|
| 程式 | [re_parser.cpp](re_parser.cpp) |
| 類型 | 模擬題（ParserTest 風格） |
| 測例 | [re_parser.in](re_parser.in) → [re_parser.expected](re_parser.expected) |
| 相關資料夾 | [24-RE轉NFA](../24-RE轉NFA/README.md)、[18-模擬Parser四則運算](../18-模擬Parser四則運算/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror re_parser.cpp -o main
./main < re_parser.in | diff -u re_parser.expected -
```

## Description

Please write a program to read one **regular expression** from stdin and check whether it follows the token definition and grammar rules below.

If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token).

※ 請使用 Recursive-Descent-Parsing 撰寫。優先序：`*` > 串接 > `|`。

| Terminal | Regular Expression |
|---|---|
| CHAR | `[a-z0-9]`（一次一個字元） |
| OR | `\|` |
| STAR | `\*` |
| LPR | `\(` |
| RPR | `\)` |

### Productions

```text
1  re        → term re_tail
2  re_tail   → OR term re_tail
3  re_tail   → λ
4  term      → factor term_tail
5  term_tail → factor term_tail
6  term_tail → λ
7  factor    → atom star
8  star      → STAR star
9  star      → λ
10 atom      → CHAR
11 atom      → LPR re RPR
```

## Input Format

整份輸入是一個 RE，token 之間可能有空白或換行。空輸入不是合法的 re。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`（不可輸出任何 token）。

## Samples

### Sample Input 1

```text
(a|b)*abb
```

### Sample Output 1

```text
LPR (
CHAR a
OR |
CHAR b
RPR )
STAR *
CHAR a
CHAR b
CHAR b
```

### Sample Input 2

```text
a**(b|c1)
```

### Sample Output 2

```text
CHAR a
STAR *
STAR *
LPR (
CHAR b
OR |
CHAR c
CHAR 1
RPR )
```

### Sample Input 3

```text
a||b
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
()
```

### Sample Output 4

```text
invalid input
```

## 解題重點

- 串接沒有運算子：term_tail 看下一個 token 是否屬於 FIRST(factor) = {CHAR, LPR}，是才繼續。
- star 的右遞迴寫成 `while (match(STAR)) {}`；`a**` 合法。
- `a||b`、`()`、`|a`、`*a` 都缺少 term／atom，不合法。要把合法的 RE 變成 NFA 見 24。
