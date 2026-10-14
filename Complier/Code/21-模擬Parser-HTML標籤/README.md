# 21 模擬 ParserTest：HTML 標籤 Parser

| 項目 | 內容 |
|---|---|
| 程式 | [html_tags.cpp](html_tags.cpp) |
| 類型 | 模擬題（ParserTest 風格 × 歷屆 HTML parser） |
| 測例 | [html_tags.in](html_tags.in) → [html_tags.expected](html_tags.expected) |
| 相關資料夾 | [01-HTML標籤配對](../01-HTML標籤配對/README.md)、[11-HTML-parser完整版](../11-HTML-parser完整版/README.md)、[10-作業ParserTest](../10-作業ParserTest/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror html_tags.cpp -o main
./main < html_tags.in | diff -u html_tags.expected -
```

## Description

Please write a program to read an HTML fragment from stdin and check whether it follows the token definition and grammar rules below. If Yes, print each token's type and its value separated by a whitespace and end with a newline. If No, print only `invalid input` with a newline (don't output any token!).

除了文法之外還有一條**語意規則**：element 的 CLOSE 標籤名稱必須等於它的 OPEN 標籤名稱，所以 `<b><i></b></i>` 不合法。

※ 請使用 Recursive-Descent-Parsing 撰寫。

| Terminal | Regular Expression | 輸出的 value |
|---|---|---|
| OPEN | `<[a-z]+>` | 標籤名稱 |
| CLOSE | `</[a-z]+>` | 標籤名稱 |
| SELF | `<[a-z]+/>` | 標籤名稱 |
| TEXT | `[^<>]+` | 去掉頭尾空白，內部連續空白（含換行）壓成一個空格 |

TEXT 若全是空白（例如標籤之間的換行與縮排）就略過，不產生 token。標籤內不允許空白或屬性；文字中出現 `>` 不合法。

### Productions

```text
1 document → content
2 content  → element content
3 content  → TEXT content
4 content  → SELF content
5 content  → λ
6 element  → OPEN content CLOSE
```

## Input Format

整份輸入是一段 HTML，可能跨多行。長度在 10000 字元內。

## Output Format

合法：每個 token 一行「種類 value」。不合法：只印 `invalid input`。

## Samples

### Sample Input 1

```text
<html><body><p>Hello  World</p><br/></body></html>
```

### Sample Output 1

```text
OPEN html
OPEN body
OPEN p
TEXT Hello World
CLOSE p
SELF br
CLOSE body
CLOSE html
```

### Sample Input 2

```text
<ul>
  <li>one</li>
  <li>two <b>bold</b></li>
</ul>
```

### Sample Output 2

```text
OPEN ul
OPEN li
TEXT one
CLOSE li
OPEN li
TEXT two
OPEN b
TEXT bold
CLOSE b
CLOSE li
CLOSE ul
```

### Sample Input 3

```text
<b><i>x</b></i>
```

### Sample Output 3

```text
invalid input
```

### Sample Input 4

```text
<p>a > b</p>
```

### Sample Output 4

```text
invalid input
```

### Sample Input 5

```text
<p>open
```

### Sample Output 5

```text
invalid input
```

### Sample Input 6

```text
text only
```

### Sample Output 6

```text
TEXT text only
```

## 解題重點

- 和 stack 配對同一件事：`element()` 進入時記住 OPEN 名稱，遞迴 `content()` 之後檢查 CLOSE 名稱。遞迴的 call stack 就是那個 stack。
- `content()` 遇到 CLOSE／END 就回傳，讓呼叫端判斷：在 `element` 裡要求 CLOSE，在最外層要求 END（多出的 `</p>` 會在這裡被擋下）。
- TEXT 用 `istringstream >>` 逐字讀，再用單一空白接回，一次完成去頭尾與壓縮空白。
- 和 [01-HTML標籤配對](../01-HTML標籤配對/README.md) 的差別：這題規格較窄（無屬性、無註解、無 void element），但要輸出 token。
