# 24 RE → NFA（Thompson）

| 項目 | 內容 |
|---|---|
| 程式 | [re_to_nfa.cpp](re_to_nfa.cpp) |
| 類型 | 工具（輸出接 04／13） |
| 測例 | [re_to_nfa.in](re_to_nfa.in) → [re_to_nfa.expected](re_to_nfa.expected) |
| 相關資料夾 | [04-NFA判定字串](../04-NFA判定字串/README.md)、[13-NFA轉DFA完整版](../13-NFA轉DFA完整版/README.md) |

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror re_to_nfa.cpp -o main
./main < re_to_nfa.in | diff -u re_to_nfa.expected -
```

## 用途

第一行是 RE，輸出 04 `nfa_check`／13 `nfa_to_dfa` 的輸入格式（`n m start k`、final、alphabet、`from sym to`，`#` 是 λ）。第二行起的測試字串原樣接在後面，所以一份輸入就能走完整條 pipeline：

```sh
./main < re_to_nfa.in | ../04-NFA判定字串/main            # 每行 ACCEPT／REJECT
./main < re_to_nfa.in | ../13-NFA轉DFA完整版/main --table  # subset DFA 表
```

RE 語法：`|` 聯集、相鄰即串接、`*` `+` `?` 後置、`( )` 分組、`#` 是 λ；其他非空白字元都是字母，空白忽略。

| 片段 | Thompson 構造 |
|---|---|
| 字元 c | `s ─c→ f` |
| A\|B | 新 s λ 分到 A、B；兩出口 λ 到新 f |
| AB | A 出口 λ 接 B 入口 |
| A* | 新 s λ→ A 入口；A 出口 λ→ 新 f；A 出口 λ→ A 入口（重複）；s λ→ f（零次） |
| A+ | 同 A*，但沒有零次旁路 |
| A? | 同 A*，但沒有重複邊 |

## 範例

**輸入**

```text
(a|b)*abb
abb
aabb
abba

b
```

**接 04 的輸出**

```text
ACCEPT
ACCEPT
REJECT
REJECT
REJECT
```

接 13 `--table` 得 5 個 DFA state，與手冊 `(a|b)*abb` 表同構（state 編號不同）。

## 限制

- RE 只有 `#`（alphabet 為空）時，04／13 會拒絕輸入；這種 RE 不用工具。
- 不支援 `[a-z]` 字元類別與跳脫；需要時直接展開成 `(a|b|…)`。
