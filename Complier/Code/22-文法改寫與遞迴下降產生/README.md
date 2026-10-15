# 22 文法改寫與遞迴下降產生器

| 項目 | 內容 |
|---|---|
| 程式 | [rd_gen.cpp](rd_gen.cpp) |
| 類型 | 工具（搭配 08 使用） |
| 測例 | [rd_gen.in](rd_gen.in) → [rd_gen.expected](rd_gen.expected) |
| 相關資料夾 | [08-LL1](../08-LL1/README.md)、[18-模擬Parser四則運算](../18-模擬Parser四則運算/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror rd_gen.cpp -o main
./main < rd_gen.in | diff -u rd_gen.expected -
```

## 用途

輸入格式與 08 `ll1.cpp` 相同。程式先自動改寫文法，再依 SELECT 產生一份**可直接編譯**的 recursive-descent parser。

1. **消除左遞迴**（直接＋間接）：`A → A α | β` 改成 `A → β A'`、`A' → α A' | #`。間接左遞迴用課本演算法：依 nonterminal 出現順序，把 `A_i → A_j γ`（j < i）代入 `A_j` 的 RHS。由上而下寫的文法（例如 ac 文法）不會觸發代入，原樣輸出。
2. **Left factoring**：`A → α β1 | α β2` 改成 `A → α A'`、`A' → β1 | β2`，反覆做到沒有共同前綴。
3. 計算 FIRST／FOLLOW／SELECT（與 08 同一套）。同一 nonterminal 的 SELECT 重疊就印 `CONFLICT` 到 stderr、exit 1，不產生會選錯分支的程式。

新 nonterminal 命名為 `A'`、`A''`…；函式名 `parse_A`、`parse_A_p`。

| 模式 | 輸出 |
|---|---|
| `--code`（預設） | 完整 C++：每個 nonterminal 一個 `bool parse_X()`，每條規則一行 `if (SELECT) return …;  // 規則`；`main` 每行讀空白分隔 token，印 ACCEPT／REJECT |
| `--grammar` | 改寫後文法，格式就是 08 的輸入，可直接接管線 |

```sh
./main --grammar < g.txt                    # 看改寫結果
./main --grammar < g.txt | ../08-LL1/main    # FIRST／FOLLOW／SELECT／M 表
./main < g.txt > p.cpp && g++ -std=c++17 p.cpp -o p && echo "num + num" | ./p
```

## 範例

**輸入**（`rd_gen.in`，左遞迴運算式文法）

```text
6
E -> E + T
E -> T
T -> T * F
T -> F
F -> ( E )
F -> num
```

**`--grammar` 輸出**

```text
8
E -> T E'
E' -> + T E'
E' -> #
T -> F T'
T' -> * F T'
T' -> #
F -> ( E )
F -> num
```

**`--code` 產生的函式（節錄）**

```cpp
bool parse_E_p() {
    if (tok() == "+") return match("+") && parse_T() && parse_E_p();  // E' -> + T E'
    if (tok() == "$" || tok() == ")") return true;  // E' -> #
    return false;
}
```

**Left factoring**：`S -> a b c`、`S -> a b d`、`S -> a e`、`S -> f` → `S -> a S'`、`S -> f`、`S' -> b S''`、`S' -> e`、`S'' -> c`、`S'' -> d`。

**間接左遞迴**（Dragon book 4.20）：`S -> A a | b`、`A -> A c | S d | #` → `A -> b d A' | A'`、`A' -> c A' | a d A' | #`。改寫後仍非 LL(1)（S 在 b 上衝突），所以只印 CONFLICT、不產碼。

## 拿來考試怎麼用

- 產出的 `tok()` 回傳目前 token 字串、結尾為 `$`；`match(t)` 比對後前進。換成自己的 scanner 時，把 `tok() == "num"` 改成 `token == NUM`、`match("num")` 改成 `match(NUM)` 即可，函式結構不用動。
- 要「錯誤時不輸出任何 token」：照手冊第 2 節 D，先 `parse_S() && tok() == "$"` 驗證，合法才重掃輸出。
- tail 規則（`E' → + T E' | #`）產出的是右遞迴；想改成 while 迴圈見手冊第 2 節 E。

## 限制

- 不處理經由 nullable 前綴的隱藏左遞迴（`A → B A x`、`B → #`）與 cycle（`A ⇒+ A`）；這類文法改寫後通常會報 CONFLICT。
- 不判定文法是否有歧義；dangling else 這類本質非 LL(1) 的文法只會報 CONFLICT。
- 完全相同的兩條規則會被 left factoring 成兩條 `#`，報 CONFLICT；輸入前先去重。
- `A → A` 沒有意義，直接丟掉。
