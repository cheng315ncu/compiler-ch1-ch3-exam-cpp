# 13 通用 NFA→DFA 完整版（check／trace／table）

| 項目 | 內容 |
|---|---|
| 程式 | [nfa_to_dfa.cpp](nfa_to_dfa.cpp) |
| 類型 | 完整功能版 |
| 測例 | [nfa_to_dfa.in](nfa_to_dfa.in) → [nfa_to_dfa.expected](nfa_to_dfa.expected) |
| 相關資料夾 | [04-NFA判定字串](../04-NFA判定字串/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror nfa_to_dfa.cpp -o main
./main < nfa_to_dfa.in | diff -u nfa_to_dfa.expected -
```

## 筆記：Compiler - 通用 NFA DFA 考試實作

> 原 `Complier/Notes/Exam/Compiler - 通用 NFA DFA 考試實作.md`，已整份移到這裡。教材頁碼：Ch3 p.42、p.46–50。


> [!abstract] 題型定位
> Ch3 子集構造直接延伸：由固定 HW5 圖改為讀 stdin 的任意轉移表。 以下為 **C++ 實作（補充）**；[單檔原碼](nfa_to_dfa.cpp) · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

### 契約與模式

`--check（預設）／--trace／--table`

n m start k；k 個 final states；alphabet 字串；m 行 from symbol to。states 0..n-1，# 代表 epsilon，不在 alphabet。其後每行完整待辨識字串，空行為 epsilon，預設 ACCEPT/REJECT。--trace 印每一步 NFA 集合；--table 只印完整 DFA，不處理後面案例。

### 演算法與易錯點

起點 closure({start})；對集合 S、每個 c 計算 closure(move(S,c))。新集合加入 worklist，以 map 去重；空集合也建為 sink。辨識同時計算 direct NFA 與 DFA，確認結果一致。

closure 要到固定點，不止一層；每次 move 後再 closure；集合含任一 final 即接受。接受狀態仍有外出邊，不能提早停止。編號依 alphabet 發現順序，與教材 A/B 不必相同。

> [!note] 支援範圍
> n≤256、m≤65536、DFA≤4096 subsets，超過明確失敗。子集構造最壞會指數成長。alphabet 為非空、不重複、非空白的單 byte 字元字串，不含 #；純 epsilon 語言可用未使用的 dummy alphabet 字元。沒有 RE→Thompson NFA parser 或最小化。

### 考場修改位置

1 起算 states 可輸入時減 1；多起點改 initial closure 集合；只求辨識可刪 construct，直接保留 closure/move/direct simulation。需要 Unicode 字母表則改 symbol 表示，不能按 UTF-8 byte 當一個字元。

用 std::set 處理多於 32 個 states；每個 DFA state×alphabet 都列出，包括 sink。

### 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/13-NFA轉DFA完整版/nfa_to_dfa.cpp -o /tmp/nfa_to_dfa
/tmp/nfa_to_dfa < Complier/Code/13-NFA轉DFA完整版/nfa_to_dfa.in
```

輸入：

```text
6 7 0 1
5
bcd
0 # 1
0 # 4
1 b 2
2 c 3
3 # 1
3 # 4
4 d 5
d
bcd
bcbcd

bc
bd
bcdd
```

預設輸出：

```text
ACCEPT
ACCEPT
ACCEPT
REJECT
REJECT
REJECT
REJECT
```

其他測例：配套是 (bc)*d 的 NFA 改成 0 起算；d/bcd/bcbcd 接受，空字串/bc/bd/bcdd 拒絕。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

### 完整 C++17 程式

完整程式就是同資料夾的 [nfa_to_dfa.cpp](nfa_to_dfa.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
