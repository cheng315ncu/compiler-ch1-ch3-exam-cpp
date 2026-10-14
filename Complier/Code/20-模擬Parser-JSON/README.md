# 20 模擬 ParserTest：JSON 子集 Parser

| 項目 | 內容 |
|---|---|
| 程式 | [json_parser.cpp](json_parser.cpp) |
| 類型 | 模擬題（ParserTest 風格，巢狀結構） |
| 測例 | [json_parser.in](json_parser.in) → [json_parser.expected](json_parser.expected) |
| 相關資料夾 | [10-作業ParserTest](../10-作業ParserTest/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror json_parser.cpp -o main
./main < json_parser.in | diff -u json_parser.expected -
```

## Description

Please write a program to read **one JSON value** from stdin and check whether it follows the token definition and grammar rules below. If Yes, print each token's type and the string of token separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token!).

※ 請使用 Recursive-Descent-Parsing 撰寫。此為 JSON 子集：字串沒有跳脫字元，數字沒有小數與指數。

| Terminal | Regular Expression |
|---|---|
| LCB | `\{` |
| RCB | `\}` |
| LSB | `\[` |
| RSB | `\]` |
| COLON | `:` |
| COMMA | `,` |
| STRING | `"[^"]*"` |
| NUMBER | `-?( 0 \| [1-9][0-9]* )` |
| TRUE | `true` |
| FALSE | `false` |
| NULL | `null` |

### Productions

```text
1  value         → object
2  value         → array
3  value         → STRING
4  value         → NUMBER
5  value         → TRUE
6  value         → FALSE
7  value         → NULL
8  object        → LCB members RCB
9  members       → pair members_tail
10 members       → λ
11 members_tail  → COMMA pair members_tail
12 members_tail  → λ
13 pair          → STRING COLON value
14 array         → LSB elements RSB
15 elements      → value elements_tail
16 elements      → λ
17 elements_tail → COMMA value elements_tail
18 elements_tail → λ
```

## Input Format

整份輸入恰好是一個 value，token 之間可能有空白或換行。value 後面還有其他 token 就不合法。

## Output Format

合法：每個 token 一行「種類 原字串」。不合法：只印 `invalid input`。

## Samples

### Sample Input 1

```text
{"name": "Amy", "age": 20}
```

### Sample Output 1

```text
LCB {
STRING "name"
COLON :
STRING "Amy"
COMMA ,
STRING "age"
COLON :
NUMBER 20
RCB }
```

### Sample Input 2

```text
[1, -2, true,
 {"a": [null, false]}, []]
```

### Sample Output 2

```text
LSB [
NUMBER 1
COMMA ,
NUMBER -2
COMMA ,
TRUE true
COMMA ,
LCB {
STRING "a"
COLON :
LSB [
NULL null
COMMA ,
FALSE false
RSB ]
RCB }
COMMA ,
LSB [
RSB ]
RSB ]
```

### Sample Input 3

```text
[1, 2,]
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
{"a" 1}
```

### Sample Output 4

```text
invalid input
```

### Sample Input 5

```text
[01]
```

### Sample Output 5

```text
invalid input
```

### Sample Input 6

```text
True
```

### Sample Output 6

```text
invalid input
```

## 解題重點

- `value` 看第一個 token 選產生式；LCB、LSB 才遞迴，所以巢狀深度不限。
- `members`／`elements` 的 λ 只在下一個是 RCB／RSB 時成立；逗號後一定要再有一項，`[1, 2,]` 不合法。
- keyword 先讀完整個字母串再比對：`True`、`truex` 都是 INVALID。
- `01` 依 NUMBER 的 RE 切成 `NUMBER 0`、`NUMBER 1`，中間缺 COMMA 而不合法。
