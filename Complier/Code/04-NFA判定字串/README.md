# 04 給 NFA，直接判定字串

| 項目 | 內容 |
|---|---|
| 程式 | [nfa_check.cpp](nfa_check.cpp) |
| 類型 | 優先使用（短版） |
| 測例 | [nfa_check.in](nfa_check.in) → [nfa_check.expected](nfa_check.expected) |
| 相關資料夾 | [13-NFA轉DFA完整版](../13-NFA轉DFA完整版/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror nfa_check.cpp -o main
./main < nfa_check.in | diff -u nfa_check.expected -
```

## 題目內容

> Ch3 epsilon-closure 與 NFA 的字串判定模擬題；input 格式由這份手冊定義。

給定帶 epsilon edge 的 NFA，請對每個完整輸入字串判定是否接受。NFA 在同一時刻可同時位於多個 state，且不用消耗字元也可沿 epsilon edge 移動。每讀一個字元，對全部當前 state 做 move，再做 epsilon-closure。所有字元用完後，只要集合含至少一個接受 state 就接受。

- **輸入規格**：先讀 n m start k；再讀 k 個 final state；再讀 alphabet；接著 m 條 from symbol to。state 是 0..n-1；# 是 epsilon。其後每行一個字串，空行是 epsilon 案例。
- **輸出規格**：每案一行 ACCEPT / REJECT。非法 alphabet 字元直接拒絕該字串；非法 NFA 描述則 stderr、exit 1。
- **限制與適用範圍**：1&lt;=n&lt;=256、0&lt;=m&lt;=65536；alphabet 非空、無重複、不能含 #；只接受單 byte 符號。本份不輸出 subset DFA 表。

**Code 檔案名稱：**[`nfa_check.cpp`](nfa_check.cpp) （04-NFA判定字串/nfa\_check.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror nfa_check.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

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

**輸出**

```text
ACCEPT
ACCEPT
ACCEPT
REJECT
REJECT
REJECT
REJECT
```

### 邊界測例 01

**輸入**

```text
3 2 0 1
2
a
0 # 1
1 a 2
a

aa
z
```

**輸出**

```text
ACCEPT
REJECT
REJECT
REJECT
```

## 邏輯與手動追蹤

初始集合是 start 的 ε-closure。每讀一字元，先 move 再 ε-closure；讀完才檢查是否含接受狀態。空行代表空字串。這份只判定字串；要 DFA 表須用 nfa\_to\_dfa.cpp。

- 0 --#→ 1 --a→ 2(final)：初始 {0,1}；讀 a 後 {2}，接受。
- epsilon cycle：set 去重，只有新 state 進 todo，所以 closure 不會卡住。
- 先碰 final 再走死：必須等字串讀完，不能中途接受。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| state 編號從 1 開始 | 31；40 | [修改範例 01（後文）](#nfa_check-change-1) |
| epsilon 用 @ | 20；37；44 | [修改範例 02（後文）](#nfa_check-change-2) |
| 輸出 YES / NO | 68 | [修改範例 03（後文）](#nfa_check-change-3) |
| 印初始及每讀一字元後的 state 集合 | 55；63 | [修改範例 04（後文）](#nfa_check-change-4) |
| 忽略字串前後空白 | 53 | [修改範例 05（後文）](#nfa_check-change-5) |

<a id="nfa_check-change-1"></a>

### 01 state 編號從 1 開始：改前／改後與測例

valid 行改成 auto valid = \[n\](int state) { return state >= 1 &amp;&amp; state &lt;= n; }; resize 行改成 edges.resize(n + 1);；輸入 start、finals、edges 皆維持 1-based。

第 31 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        auto valid = [n](int state) { return state >= 0 && state < n; };
```

**改後（對照修改）**

```cpp
auto valid = [n](int state) { return state >= 1 && state <= n; };
```

第 40 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        edges.resize(n);
```

**改後（對照修改）**

```cpp
edges.resize(n + 1);
```

已試編並執行的變體測例：

**輸入**

```text
2 1 1 1
2
a
1 a 2
a
b
```

**輸出**

```text
ACCEPT
REJECT
```

<a id="nfa_check-change-2"></a>

### 02 epsilon 用 @：改前／改後與測例

這三行的 '#' 與 "#" 改成 '@' 與 "@"。

第 20 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        for (int to : edges[from]['#']) if (states.insert(to).second) todo.push_back(to);
```

**改後（對照修改）**

```cpp
        for (int to : edges[from]['@']) if (states.insert(to).second) todo.push_back(to);
```

第 37 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        if (!(cin >> alphabet) || alphabet.find('#') != string::npos ||
```

**改後（對照修改）**

```cpp
        if (!(cin >> alphabet) || alphabet.find('@') != string::npos ||
```

第 44 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
                (symbol != "#" && alphabet.find(symbol[0]) == string::npos)) fail();
```

**改後（對照修改）**

```cpp
                (symbol != "@" && alphabet.find(symbol[0]) == string::npos)) fail();
```

已試編並執行的變體測例：

**輸入**

```text
3 2 0 1
2
a
0 @ 1
1 a 2
a
```

**輸出**

```text
ACCEPT
```

<a id="nfa_check-change-3"></a>

### 03 輸出 YES / NO：改前／改後與測例

將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。

第 68 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            cout << (accepted ? "ACCEPT\n" : "REJECT\n");
```

**改後（對照修改）**

```cpp
            cout << (accepted ? "YES\n" : "NO\n");
```

已試編並執行的變體測例：

**輸入**

```text
2 1 0 1
1
a
0 a 1
a
```

**輸出**

```text
YES
```

<a id="nfa_check-change-4"></a>

### 04 印初始及每讀一字元後的 state 集合：改前／改後與測例

第 55 行：在此行後插入

**改前（原碼）**

```cpp
            States states = closure({start});
```

**改後（對照修改）**

```cpp
for (int state : states) cout << state << ' ';
cout << '\n';
```

第 63 行：在此行後插入

**改前（原碼）**

```cpp
                states = closure(next);
```

**改後（對照修改）**

```cpp
for (int state : states) cout << state << ' ';
cout << '\n';
```

已試編並執行的變體測例：

**輸入**

```text
3 2 0 1
2
a
0 # 1
1 a 2
a
```

**輸出**

```text
0 1 
2 
ACCEPT
```

<a id="nfa_check-change-5"></a>

### 05 忽略字串前後空白：改前／改後與測例

第 53 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            if (!word.empty() && word.back() == '\r') word.pop_back();
```

**改後（對照修改）**

```cpp
size_t first = word.find_first_not_of(" \t\r");
word = first == string::npos ? "" : word.substr(first, word.find_last_not_of(" \t\r") - first + 1);
```

已試編並執行的變體測例：

**輸入**

```text
2 1 0 1
1
a
0 a 1
  a 
```

**輸出**

```text
ACCEPT
```
