# 26 模擬 ScannerTest：ParserTest 的 Token

| 項目 | 內容 |
|---|---|
| 程式 | [token_scanner.cpp](token_scanner.cpp) |
| 類型 | 模擬題（ScannerTest 風格） |
| 測例 | [token_scanner.in](token_scanner.in) → [token_scanner.expected](token_scanner.expected) |
| 相關資料夾 | [09-作業ScannerTest](../09-作業ScannerTest/README.md)、[10-作業ParserTest](../10-作業ParserTest/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror token_scanner.cpp -o main
./main < token_scanner.in | diff -u token_scanner.expected -
```

## Description

Scanner 先把 input text 依規則轉成 Token，Parser 才能處理。請依下表（就是 ParserTest 的 terminal）寫一個 Scanner，取得 Tokens 並印出。不需檢查文法：`(a)`、`a.` 這類 ParserTest 不合法的輸入，Scanner 照樣切。

| Terminal | Regular Expression |
|---|---|
| ID | `[A-Za-z_][A-Za-z0-9_]*` |
| STRLIT | `"[^"]*"` |
| LBR | `\(` |
| RBR | `\)` |
| DOT | `\.` |

## Input Format

整份輸入是一段文字，token 之間可能夾雜空格、tab 或換行。測試資料不會有錯誤資料，長度在 1000 字元內（不含換行）。 STRLIT 內可含空白與換行。

## Output Format

每個 token 一行：種類名稱；ID 與 STRLIT 另加一個空白與原字串（STRLIT 含引號），例如 `ID x`、`STRLIT "a b"`。

## Samples

### Sample Input 1

```text
"test_string"
Test_ID
```

### Sample Output 1

```text
STRLIT "test_string"
ID Test_ID
```

### Sample Input 2

```text
printf("Hello World").len
```

### Sample Output 2

```text
ID printf
LBR
STRLIT "Hello World"
RBR
DOT
ID len
```

### Sample Input 3

```text
(a.
```

### Sample Output 3

```text
LBR
ID a
DOT
```

## 解題重點

- 用 `cin.get()` 逐字元讀（同 09）：ID 會多讀一個字元才知道結束，那個字元留在 c，下一輪直接處理，不能再 get。
- STRLIT：讀到下一個 `"` 為止，中間字元（含換行）原樣保留；吃掉結尾引號後才讀下一字元。
- ScannerTest 不做文法檢查，`(a.` 也照樣輸出三個 token。
