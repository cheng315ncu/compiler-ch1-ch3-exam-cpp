# 08 FIRST／FOLLOW／LL(1)

| 項目 | 內容 |
|---|---|
| 程式 | [ll1.cpp](ll1.cpp) |
| 類型 | 較低優先補充 |
| 測例 | [ll1.in](ll1.in) → [ll1.expected](ll1.expected) |
| 相關資料夾 | [22-文法改寫與遞迴下降產生](../22-文法改寫與遞迴下降產生/README.md)：先消左遞迴／left factoring，再產 RD parser |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror ll1.cpp -o main
./main < ll1.in | diff -u ll1.expected -
```

## 題目內容

> predict 的通用延伸模擬題；正式 FIRST/FOLLOW 術語預告於 Ch4，不能視為已確認 Ch1–3 考題。

給定 CFG，請計算各 nonterminal 的 FIRST / FOLLOW、各 production 的 SELECT，並建立 LL(1) 解析表。FIRST / FOLLOW 必須反覆傳播至固定點。RHS 可空時將 LHS 的 FOLLOW 加入 SELECT。同格若有多條 production，列出 conflict，判定非 LL(1)。無衝突時另可用 predictive stack 判定 token 序列。

- **輸入規格**：先讀 P（1..1000），再讀 P 行 A -> X Y。每行只含一條 alternative；# 必須單獨表示 epsilon，$ 保留為 EOF。start 是第一個 LHS。--check 模式才讀其後每行空白分隔的 token sequence。
- **輸出規格**：預設列 FIRST/FOLLOW/SELECT、非空表格 cell、CONFLICT 與 LL1 YES/NO。--check 每案印 ACCEPT/REJECT；不由字串原始字元自動 tokenize。
- **限制與適用範圍**：不消除左遞迴、不做 left factoring（要做用 22 rd_gen），也不判定任意 CFG 是否無歧義。有 LL(1) conflict 時不任選規則繼續。

**Code 檔案名稱：**[`ll1.cpp`](ll1.cpp) （08-LL1/ll1.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror ll1.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

```text
4
E -> T R
R -> + T R
R -> #
T -> num
```

**輸出**

```text
FIRST(E)={num} FOLLOW(E)={$}
FIRST(R)={#,+} FOLLOW(R)={$}
FIRST(T)={num} FOLLOW(T)={$,+}
SELECT(1)={num}
SELECT(2)={+}
SELECT(3)={$}
SELECT(4)={num}
M[E,num]=1
M[R,$]=3
M[R,+]=2
M[T,num]=4
LL1 YES
```

### 邊界測例 01

**輸入**

```text
2
S -> a S
S -> #
```

**輸出**

```text
FIRST(S)={#,a} FOLLOW(S)={$}
SELECT(1)={a}
SELECT(2)={$}
M[S,$]=2
M[S,a]=1
LL1 YES
```

## 邏輯與手動追蹤

FIRST 與 FOLLOW 反覆合併至固定點；nullable RHS 將 FOLLOW 加進 SELECT。用 SELECT 填表，同格多條規則就是 conflict；解析用 stack 與 lookahead 查表。# 單獨代表 ε。

- S -> a S | #：FIRST(S)={#,a}、FOLLOW(S)={$}。
- SELECT(S->#)={$}，所以 EOF 時才選 epsilon，而不是看到任何字元都選。
- A -> B C：若 C nullable，FOLLOW(A) 也要傳給 FOLLOW(B)。
- 展開 S -> a S 時先 push S 再 push a，讓 a 先被處理。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| judge 不傳參數，只判定字串 | 35 | [修改範例 01（後文）](#ll1-change-1) |
| 只印 FIRST 與 FOLLOW | 96–103 | [修改範例 02（後文）](#ll1-change-2) |
| 字串判定輸出 YES / NO | 129 | [修改範例 03（後文）](#ll1-change-3) |
| 指定 S 為 start，不使用第一個 LHS | 68；112 | [修改範例 04（後文）](#ll1-change-4) |
| 只輸出是否為 LL(1) | 93–103 | [修改範例 05（後文）](#ll1-change-5) |

<a id="ll1-change-1"></a>

### 01 judge 不傳參數，只判定字串：改前／改後與測例

const std::string mode = argc == 1 ? "--check" : argv\[1\];

第 35 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        const std::string mode = argc == 1 ? "--table" : argv[1];
```

**改後（對照修改）**

```cpp
const std::string mode = argc == 1 ? "--check" : argv[1];
```

已試編並執行的變體測例：

**輸入**

```text
2
S -> a S
S -> #
a a

b
```

**輸出**

```text
ACCEPT
ACCEPT
REJECT
```

<a id="ll1-change-2"></a>

### 02 只印 FIRST 與 FOLLOW：改前／改後與測例

刪除這段 SELECT / table / LL1 輸出；FIRST/FOLLOW 兩行不刪，前面的集合計算不刪。

第 96–103 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            for (std::size_t i = 0; i < rules.size(); ++i) { std::cout << "SELECT(" << i + 1 << ")="; print_set(select[i]); std::cout << '\n'; }
            for (const auto& cell : table) {
                std::cout << "M[" << cell.first.first << ',' << cell.first.second << "]=";
                for (std::size_t i = 0; i < cell.second.size(); ++i) std::cout << (i ? "," : "") << cell.second[i] + 1;
                if (cell.second.size() > 1) std::cout << " CONFLICT";
                std::cout << '\n';
            }
            std::cout << (ll1 ? "LL1 YES\n" : "LL1 NO\n");
```

**改後（對照修改）**

```cpp
（刪除；不要貼這段提示文字）
```

已試編並執行的變體測例：

**輸入**

```text
2
S -> a S
S -> #
```

**輸出**

```text
FIRST(S)={#,a} FOLLOW(S)={$}
```

<a id="ll1-change-3"></a>

### 03 字串判定輸出 YES / NO：改前／改後與測例

將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。

第 129 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
                std::cout << (accepted && pos == words.size() ? "ACCEPT\n" : "REJECT\n");
```

**改後（對照修改）**

```cpp
                std::cout << (accepted && pos == words.size() ? "YES\n" : "NO\n");
```

此變體執行參數：`./main --check`

已試編並執行的變體測例：

**輸入**

```text
2
S -> a S
S -> #
a
b
```

**輸出**

```text
YES
NO
```

<a id="ll1-change-4"></a>

### 04 指定 S 為 start，不使用第一個 LHS：改前／改後與測例

第 68 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        follow[rules[0].lhs].insert("$");
```

**改後（對照修改）**

```cpp
        follow["S"].insert("$");
```

第 112 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
                words.push_back("$"); std::vector<std::string> stack{"$", rules[0].lhs}; std::size_t pos = 0, steps = 0;
```

**改後（對照修改）**

```cpp
                words.push_back("$"); std::vector<std::string> stack{"$", "S"}; std::size_t pos = 0, steps = 0;
```

此變體執行參數：`./main --check`

已試編並執行的變體測例：

**輸入**

```text
2
A -> b
S -> a
a
b
```

**輸出**

```text
ACCEPT
REJECT
```

<a id="ll1-change-5"></a>

### 05 只輸出是否為 LL(1)：改前／改後與測例

第 93–103 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            for (const auto& nt : nonterminals) {
                std::cout << "FIRST(" << nt << ")="; print_set(first[nt]); std::cout << " FOLLOW(" << nt << ")="; print_set(follow[nt]); std::cout << '\n';
            }
            for (std::size_t i = 0; i < rules.size(); ++i) { std::cout << "SELECT(" << i + 1 << ")="; print_set(select[i]); std::cout << '\n'; }
            for (const auto& cell : table) {
                std::cout << "M[" << cell.first.first << ',' << cell.first.second << "]=";
                for (std::size_t i = 0; i < cell.second.size(); ++i) std::cout << (i ? "," : "") << cell.second[i] + 1;
                if (cell.second.size() > 1) std::cout << " CONFLICT";
                std::cout << '\n';
            }
            std::cout << (ll1 ? "LL1 YES\n" : "LL1 NO\n");
```

**改後（對照修改）**

```cpp
std::cout << (ll1 ? "LL1 YES\n" : "LL1 NO\n");
```

已試編並執行的變體測例：

**輸入**

```text
2
S -> a S
S -> #
```

**輸出**

```text
LL1 YES
```

## 筆記：Compiler - Predict 與 LL1 考試實作

> 原 `Complier/Notes/Exam/Compiler - Predict 與 LL1 考試實作.md`，已整份移到這裡。教材頁碼：Ch2 p.18–24；FIRST/FOLLOW 正式名稱為補充。


> [!abstract] 題型定位
> Ch2 predict set 的補充工具；FIRST/FOLLOW 的正式名稱預告於 Ch4，列為較低優先的延伸。 以下為 **C++ 實作（補充）**；[單檔原碼](ll1.cpp) · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

### 契約與模式

`--table（預設）／--check`

第一行 P（1..1000），接 P 行 LHS -> RHS，符號空白分隔，一行一個 alternative，# 單獨表示 epsilon。第一 LHS 為 start；所有 LHS 為 nonterminal，其他 RHS 為 terminal。$ 保留 EOF，不寫進 grammar。預設印 FIRST/FOLLOW/SELECT、所有非空 table cells、LL1 YES/NO；--check 讀後續每行 terminal tokens，補 $，印 ACCEPT/REJECT；空行測 epsilon。

### 演算法與易錯點

反覆聯集到 FIRST 固定，再求 start FOLLOW={$} 與各 suffix 的 FIRST／nullable 直到 FOLLOW 固定。SELECT=FIRST(RHS) 去 epsilon；nullable 時加 FOLLOW(LHS)。同格多規則為 CONFLICT；recognizer 用非遞迴 stack。

epsilon 不放 FOLLOW 或輸入；SELECT epsilon 分支加 FOLLOW；FOLLOW 看整個 suffix。ac 的 Prog → Dcls Stmts $ 應輸入 Prog → Dcls Stmts，本工具已補 EOF。# 不可與其他 RHS 並列，| 必須拆成多行。

> [!note] 支援範圍
> 不自動消除左遞迴／left factoring；非 LL(1) 不等於 ambiguous。--check 遇 conflict 報錯；最多 1,000,000 parsing steps。缺少 table cell 表示 error。RHS 名称是否為 nonterminal 由 LHS 集合決定，拼錯名稱會被當 terminal。

### 考場修改位置

只求 FIRST/FOLLOW 可刪 table／recognizer；要求全矩形表格則補印缺格為 error。解析來源 expression 先由 lexer 把實際數字映射為 num token，再送 --check。

較低準備優先度：這是 predict 的通用延伸，不能宣稱 FIRST/FOLLOW 正式考試範圍已確認。

### 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/08-LL1/ll1.cpp -o /tmp/ll1
/tmp/ll1 < Complier/Code/08-LL1/ll1.in
```

輸入：

```text
4
E -> T R
R -> + T R
R -> #
T -> num
```

預設輸出：

```text
FIRST(E)={num} FOLLOW(E)={$}
FIRST(R)={#,+} FOLLOW(R)={$}
FIRST(T)={num} FOLLOW(T)={$,+}
SELECT(1)={num}
SELECT(2)={+}
SELECT(3)={$}
SELECT(4)={num}
M[E,num]=1
M[R,$]=3
M[R,+]=2
M[T,num]=4
LL1 YES
```

其他測例：num + num 接受；num + 拒絕；S → S a／S → b 會列 conflict。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

### 完整 C++17 程式

完整程式就是同資料夾的 [ll1.cpp](ll1.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
