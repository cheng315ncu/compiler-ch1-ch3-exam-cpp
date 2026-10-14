# 16 模擬 ScannerTest：宣告敘述 Scanner

| 項目 | 內容 |
|---|---|
| 程式 | [decl_scanner.cpp](decl_scanner.cpp) |
| 類型 | 模擬題（ScannerTest 風格） |
| 測例 | [decl_scanner.in](decl_scanner.in) → [decl_scanner.expected](decl_scanner.expected) |
| 相關資料夾 | [09-作業ScannerTest](../09-作業ScannerTest/README.md)、[03-Scanner與註解](../03-Scanner與註解/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror decl_scanner.cpp -o main
./main < decl_scanner.in | diff -u decl_scanner.expected -
```

## Description

請依下表規則寫一個 Scanner，把一段宣告／指定敘述切成 token 並印出。keyword 與 ID 的規則重疊時，**先讀完整個字再判斷**：`intx` 是一個 ID，不是 `int` 加 `x`。

| Terminal | Regular Expression |
|---|---|
| INT | `int` |
| FLOAT | `float` |
| PRINT | `print` |
| ID | `[A-Za-z_][A-Za-z0-9_]*`（不是上面三個 keyword） |
| INUM | `( [1-9][0-9]* ) \| 0` |
| FNUM | `INUM \. [0-9]+` |
| ASSIGN | `=` |
| PLUS | `\+` |
| MINUS | `-` |
| SEMI | `;` |

## Input Format

整份輸入是一段程式，token 之間可能夾雜空格、tab 或換行。測試資料不會有錯誤資料，長度在 1000 字元內（不含換行）。

## Output Format

每個 token 一行。ID、INUM、FNUM 要附上原字串，以一個空白分隔，例如 `ID x`、`FNUM 0.25`；其餘只印種類名稱。

## Samples

### Sample Input 1

```text
int x;
x = 10;
```

### Sample Output 1

```text
INT
ID x
SEMI
ID x
ASSIGN
INUM 10
SEMI
```

### Sample Input 2

```text
float rate=0.25;
intx = rate+3.0-007;
print intx;
```

### Sample Output 2

```text
FLOAT
ID rate
ASSIGN
FNUM 0.25
SEMI
ID intx
ASSIGN
ID rate
PLUS
FNUM 3.0
MINUS
INUM 0
INUM 0
INUM 7
SEMI
PRINT
ID intx
SEMI
```

### Sample Input 3

```text
  print
	12.5
;
```

### Sample Output 3

```text
PRINT
FNUM 12.5
SEMI
```

## 解題重點

- keyword：讀完整個 `[A-Za-z0-9_]*` 才比對 `int／float／print`，所以 `intx`、`printf` 都是 ID。
- INUM 開頭 0 只吃一位：`007` → `INUM 0`、`INUM 0`、`INUM 7`（照 RE 最長匹配，不是一個數字）。
- FNUM 需要兩字元 lookahead：看到 `.` 還要確認下一個是數字，才把 `.` 吃進來。
