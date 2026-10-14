# 12 運算式 parser 完整版（postfix／ast／eval，迭代式）

| 項目 | 內容 |
|---|---|
| 程式 | [expression.cpp](expression.cpp) |
| 類型 | 完整功能版 |
| 測例 | [expression.in](expression.in) → [expression.expected](expression.expected) |
| 相關資料夾 | [02-遞迴下降運算式](../02-遞迴下降運算式/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror expression.cpp -o main
./main < expression.in | diff -u expression.expected -
```

## 筆記：Compiler - 運算式 parser 考試實作

> 原 `Complier/Notes/Exam/Compiler - 運算式 parser 考試實作.md`，已整份移到這裡。教材頁碼：Ch2 p.15、p.27–28；擴充運算子為補充。


> [!abstract] 題型定位
> Ch2 parser／AST 的常見延伸；括號、乘除、一元正負不在原 ac 文法。 以下為 **C++ 實作（補充）**；[單檔原碼](expression.cpp) · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

### 契約與模式

`--postfix（預設）／--ast／--eval`

每行一個完整運算式，無案例數。預設每行印空白分隔的 postfix；--ast 每行印一棵 S-expression；--eval 只接受常數，印 15 位有效數字。空白行非法，完全空的輸入表示零案例。任一案例失敗不發出任何暫存輸出，stderr 診斷、exit 1。

### 演算法與易錯點

Shunting-yard：value stack 保存 AST 索引，operator stack 保存待處理運算子。* / 高於 + -；二元同優先序用 >= 彈出以實現左結合；一元 neg/pos 從右向左結合。apply 建立父節點，arena 按子先父後排列，可直接輸出 postfix 與求值。

a+b*c 的根是 +；100-30-1 得 69；8/2/2 得 2；1+-2 合法，2(3) 非法。postfix neg 是一元指令，不等於二元 -。括號決定結構，不留 AST 節點。

> [!note] 支援範圍
> 支援 + - * /、括號、一元正負、小數與 e/E。ID 採 [A-Za-z_][A-Za-z_0-9]*，只供 AST/postfix；求值沒有變數環境。沒有 =、%、^、函式、隱含乘法。long double 拒絕零除／非有限值，但非精確有理數，顯示會捨入。

### 考場修改位置

只畫 AST 用 --ast；只求值把 main 預設改 --eval。求值變數要在 evaluate 葉節點加入符號表。新增 ^ 必須另定右結合及相對 unary minus 的優先序，不能只加入運算子字串。

文法：expr → term {(+|- ) term}；term → unary {(*|/) unary}；unary → (+|-) unary | primary；primary → number | ID | (expr)。採迴圈與 arena，長加法鏈不依賴深層函式遞迴。

### 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/12-運算式parser完整版/expression.cpp -o /tmp/expression
/tmp/expression < Complier/Code/12-運算式parser完整版/expression.in
```

輸入：

```text
a+b*c
(2+3)*4
-2*-3
100-30-1
```

預設輸出：

```text
a b c * +
2 3 + 4 *
2 neg 3 neg *
100 30 - 1 -
```

其他測例：a+b*c → a b c * +／(+ a (* b c))；(2+3)*4 → 20；-2*-3 → 6。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

### 完整 C++17 程式

完整程式就是同資料夾的 [expression.cpp](expression.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
