# 07 Stack VM 直譯器

| 項目 | 內容 |
|---|---|
| 程式 | [stack_vm.cpp](stack_vm.cpp) |
| 類型 | 優先使用 |
| 測例 | [stack_vm.in](stack_vm.in) → [stack_vm.expected](stack_vm.expected) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror stack_vm.cpp -o main
./main < stack_vm.in | diff -u stack_vm.expected -
```

## 題目內容

> Ch1 interpreter / Ch2 dc 產碼的延伸模擬題；指令名稱由本題定義，不是 GNU dc。

請執行 stack-based 虛擬機指令。PUSH number 把常數入 stack；STORE name pop 並保存；LOAD name 複製變數值。ADD/SUB/MUL/DIV 先取右 operand b，再取左 a，計算 a op b。NEG 取反，DUP 複製頂端，PRINT pop 並輸出。未知指令、未定義變數、underflow、零除或非有限值均視為錯誤。

- **輸入規格**：每行一條指令到 EOF；空行忽略。PUSH/LOAD/STORE 恰有一個參數，其餘沒有參數；變數名採一般 ID 規則。
- **輸出規格**：每次 PRINT 一行，15 位有效數字。整份成功後才發出累積輸出；任何錯誤 stdout 空、stderr 訊息、exit 1。
- **限制與適用範圍**：long double，非任意精度；沒有跳躍、條件、函式或字串。EOF 可留未使用 stack；PRINT 與 dc p 的 pop 規則不同。

**Code 檔案名稱：**[`stack_vm.cpp`](stack_vm.cpp) （07-StackVM/stack\_vm.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror stack_vm.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

```text
PUSH 100
STORE x
LOAD x
PUSH 30
PUSH 1
ADD
ADD
STORE x
LOAD x
PRINT
```

**輸出**

```text
131
```

### 邊界測例 01

**輸入**

```text
PUSH 8
PUSH 2
SUB
PRINT
```

**輸出**

```text
6
```

### 邊界測例 02

**輸入**

```text
PUSH 2
DUP
MUL
NEG
PRINT
```

**輸出**

```text
-4
```

### 邊界測例 03

**輸入**

```text
PUSH 1
PUSH 0
DIV
PRINT
```

**輸出**

```text
stdout：空
stderr：error: division by zero
exit 1
```

### 邊界測例 04

**輸入**

```text
LOAD x
```

**輸出**

```text
stdout：空
stderr：error: undefined variable x
exit 1
```

### 邊界測例 05

**輸入**

```text
PRINT
```

**輸出**

```text
stdout：空
stderr：error: stack underflow
exit 1
```

## 邏輯與手動追蹤

vector 當 stack，map 存變數。二元先 pop 右 b，再 pop 左 a，算 a op b；STORE 與 PRINT 都 pop。空 stack、未定義 LOAD、零除均報錯。

- PUSH 8 / PUSH 2 / SUB / PRINT：8-2=6，不能算成 2-8。
- PUSH 2 / DUP / MUL / NEG / PRINT：2\*2 再取負，得 -4。
- PRINT 後 stack 少一項；若題目要求保留，要改成 peek。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| PRINT 保留 stack 頂端 | 54 | [修改範例 01（後文）](#stack_vm-change-1) |
| 固定小數點後 2 位 | 29 | [修改範例 02（後文）](#stack_vm-change-2) |
| PRINT 指令改名為 OUT | 54 | [修改範例 03（後文）](#stack_vm-change-3) |
| 指令名稱忽略 ASCII 大小寫 | 38 | [修改範例 04（後文）](#stack_vm-change-4) |
| PRINT 不移除值，DUP 後連續列印 | 54 | [修改範例 05（後文）](#stack_vm-change-5) |

<a id="stack_vm-change-1"></a>

### 01 PRINT 保留 stack 頂端：改前／改後與測例

} else if (op == "PRINT") { if (stack.empty()) throw std::runtime\_error("stack underflow"); const auto value = stack.back(); output &lt;&lt; (value == 0 ? 0 : value) &lt;&lt; '\\n'; }

第 54 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            } else if (op == "PRINT") { const auto value = pop(); output << (value == 0 ? 0 : value) << '\n'; }
```

**改後（對照修改）**

```cpp
} else if (op == "PRINT") {
    if (stack.empty()) throw std::runtime_error("stack underflow");
    const auto value = stack.back();
    output << (value == 0 ? 0 : value) << '\n';
}
```

已試編並執行的變體測例：

**輸入**

```text
PUSH 2
PRINT
PRINT
```

**輸出**

```text
2
2
```

<a id="stack_vm-change-2"></a>

### 02 固定小數點後 2 位：改前／改後與測例

把 output &lt;&lt; std::setprecision(15); 改成 output &lt;&lt; std::fixed &lt;&lt; std::setprecision(2);。

第 29 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
        std::ostringstream output; output.imbue(std::locale::classic()); output << std::setprecision(15);
```

**改後（對照修改）**

```cpp
        std::ostringstream output; output.imbue(std::locale::classic()); output << std::fixed << std::setprecision(2);
```

已試編並執行的變體測例：

**輸入**

```text
PUSH .25
PRINT
```

**輸出**

```text
0.25
```

<a id="stack_vm-change-3"></a>

### 03 PRINT 指令改名為 OUT：改前／改後與測例

把該行 op == "PRINT" 改成 op == "OUT"。

第 54 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            } else if (op == "PRINT") { const auto value = pop(); output << (value == 0 ? 0 : value) << '\n'; }
```

**改後（對照修改）**

```cpp
            } else if (op == "OUT") { const auto value = pop(); output << (value == 0 ? 0 : value) << '\n'; }
```

已試編並執行的變體測例：

**輸入**

```text
PUSH 8
OUT
```

**輸出**

```text
8
```

<a id="stack_vm-change-4"></a>

### 04 指令名稱忽略 ASCII 大小寫：改前／改後與測例

第 38 行：在此行後插入

**改前（原碼）**

```cpp
            if (!(input >> op)) continue;
```

**改後（對照修改）**

```cpp
for (char& c : op) if (c >= 'a' && c <= 'z') c -= 'a' - 'A';
```

已試編並執行的變體測例：

**輸入**

```text
push 2
print
```

**輸出**

```text
2
```

<a id="stack_vm-change-5"></a>

### 05 PRINT 不移除值，DUP 後連續列印：改前／改後與測例

第 54 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
            } else if (op == "PRINT") { const auto value = pop(); output << (value == 0 ? 0 : value) << '\n'; }
```

**改後（對照修改）**

```cpp
} else if (op == "PRINT") {
    if (stack.empty()) throw std::runtime_error("stack underflow");
    const auto value = stack.back();
    output << (value == 0 ? 0 : value) << '\n';
}
```

已試編並執行的變體測例：

**輸入**

```text
PUSH 2
DUP
PRINT
PRINT
```

**輸出**

```text
2
2
```

## 筆記：Compiler - 堆疊機 Interpreter 考試實作

> 原 `Complier/Notes/Exam/Compiler - 堆疊機 Interpreter 考試實作.md`，已整份移到這裡。教材頁碼：Ch1 p.12–14；Ch2 p.36–38。


> [!abstract] 題型定位
> Ch1 compiler/interpreter、Ch2 dc stack code 的補充練習；instruction 名稱是本版定義，不是 dc。 以下為 **C++ 實作（補充）**；[單檔原碼](stack_vm.cpp) · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

### 契約與模式

`無參數`

每行一指令到 EOF：PUSH number、LOAD name、STORE name、ADD/SUB/MUL/DIV/NEG、DUP、PRINT。空行略過。STORE pop 保存；LOAD 複製；PRINT pop 並印 15 位有效數字。EOF 可留剩餘 stack。錯誤時整份 PRINT 暫存不發出，stderr 診斷、exit 1。

### 演算法與易錯點

vector 是 stack、map 是 variables；二元先 pop 右 b，再左 a，做 a op b。NEG 只需一項；DUP 複製頂端。PUSH 必須完整轉換為有限 long double，零除／underflow／undefined LOAD 都拒絕。

8 2 SUB 得 6，DIV 得 4；不可顛倒 pop 順序。LOAD 未定義值不能默認 0。輸出數值是 interpreter 執行結果，不是 compiler 產出的 target code。

> [!note] 支援範圍
> 沒有跳躍、條件、函式、地址、型別分析、字串、註解或分號。非任意精度整數／dc。本版 PRINT 會 pop，與 GNU dc 的 p 不 pop 不同。名稱 [A-Za-z_][A-Za-z_0-9]*。

### 考場修改位置

postfix 數字→PUSH，+/-/*//→ADD/SUB/MUL/DIV，neg→NEG，pos→忽略，最後 PRINT。若仿 dc p，把 PRINT 的 pop 改成先檢查 stack 非空再讀 back。

演示 compiler → IR → interpreter 時，expression 的 --postfix 是 IR 入口；本 VM 不直接讀 C/C++ 或 ac 來源。

### 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/07-StackVM/stack_vm.cpp -o /tmp/stack_vm
/tmp/stack_vm < Complier/Code/07-StackVM/stack_vm.in
```

輸入：

```text
PUSH 100
STORE x
LOAD x
PUSH 30
PUSH 1
ADD
ADD
STORE x
LOAD x
PRINT
```

預設輸出：

```text
131
```

其他測例：配套算 x=100，再加 30+1 得 131；PUSH 2／DUP／MUL／NEG／PRINT 得 -4。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

### 完整 C++17 程式

完整程式就是同資料夾的 [stack_vm.cpp](stack_vm.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
