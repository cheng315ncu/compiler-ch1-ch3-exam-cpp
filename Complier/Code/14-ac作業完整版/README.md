# 14 ac 作業完整版（tokens／parse tree／AST／check／dc）

| 項目 | 內容 |
|---|---|
| 程式 | [ac_homework.cpp](ac_homework.cpp) |
| 類型 | 課程作業完整版 |
| 測例 | [ac_homework.in](ac_homework.in) → [ac_homework.expected](ac_homework.expected) |
| 相關資料夾 | [06-ac產dc](../06-ac產dc/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror ac_homework.cpp -o main
./main < ac_homework.in | diff -u ac_homework.expected -
```

## 筆記：Compiler - Ch1-Ch3 作業完整 C++17 實作

> 原 `Complier/Notes/Compiler - Ch1-Ch3 作業完整 C++17 實作.md`，已整份移到這裡。教材頁碼：Ch1 PPT 25–30；Ch2 PPT 39–46；Ch3 PPT 53–60。


> [!abstract] 程式入口
> **C++ 實作（補充）**：兩份獨立、有 `main()` 的 C++17 程式。[ac_homework.cpp](ac_homework.cpp) 完成 ac 的詞法分析（scanning）、語法分析（parsing）、剖析樹（parse tree）、抽象語法樹（AST）、語意分析（semantic analysis）與 dc 產碼；[automata_homework.cpp](../15-HW5-NFA-DFA作業完整版/automata_homework.cpp) 完成兩題非確定／確定有限自動機（NFA／DFA）。完整程式碼直接看各資料夾的 `.cpp` 原檔。

[[Compiler - 知識庫首頁|回首頁]] · [[Compiler - ac 編譯器全流程]] · [[Compiler - NFA 到 DFA 的完整構造]]

考試可攜帶的擴充版：[[Compiler - Ch1-Ch3 考試 C++ 程式集]]，含 HTML parser 等六份新程式與全部八份原碼的列印 PDF。


HW5 NFA／DFA 部分見 [15-HW5-NFA-DFA作業完整版](../15-HW5-NFA-DFA作業完整版/README.md)。

### 作業範圍與來源

| 作業 | 來源 | 本次交付 |
|---|---|---|
| Ch1 第 4 題：編譯期／執行期錯誤 | [[Compiler-Ch1-p021-p030#PPT p.025｜習題 4：compile-time 與 run-time 錯誤|p.25–26]] | 原題是問答；`--check` 示範靜態拒絕非法程式，不執行 C++ 除零 |
| Ch1 第 8 題：JVM interpreter | [[Compiler-Ch1-p021-p030#PPT p.027｜習題 8：JVM interpreter 為何較容易|p.27–28]] | 原題是問答，見下方觀念解答 |
| Ch1 第 11 題：產生 C 的利弊 | [[Compiler-Ch1-p021-p030#PPT p.029｜習題 11：以 C 當萬用組合語言|p.29–30]] | 原題是問答，見下方觀念解答 |
| Ch2 HW1：依 Fig.2.1 建 parse tree | [[Compiler-Ch2-p036-p046#PPT p.039｜習題 1：畫 parse tree|p.39–40]] | `ac_homework --parse-tree`，包含 terminal、詞素、epsilon、$ |
| Ch2 HW2(a)：建 AST | [[Compiler-Ch2-p036-p046#PPT p.042｜習題 2(a) 教材解答：AST|p.41–42]] | `--ast`；`--typed-ast` 顯示型別提升節點 |
| Ch2 HW2(b)：語意分析／教材常數摺疊 | [[Compiler-Ch2-p036-p046#PPT p.043｜習題 2(b) 教材解答：常數摺疊|p.43]] | `--check`；`--ast --fold` 將 `x+30+1` 化成 `x+31` |
| Ch2 HW2(c)：產生碼 | [[Compiler-Ch2-p036-p046#PPT p.044｜習題 2(c) 教材解答：產生的碼|p.44]] | 預設輸出 dc；加 `--fold` 對齊本題教材摺疊後的碼 |
| Ch2 HW3(a)(b)(c)／Ch3 HW3 | [[Compiler-Ch2-p036-p046#PPT p.045｜習題 3：擴充 scanner|Ch2 p.45–46]]、[[Compiler-Ch3-p051-p060#PPT p.053｜作業 3：keyword 與可選科學記號|Ch3 p.53–54]] | 同一 scanner 支援 `f/float`、`i/int`、可選帶正負號的 exponent |
| Ch3 HW5(d)：`(bc)*d` | [[Compiler-Ch3-p051-p060#PPT p.055｜作業 5(d)：(bc)*d 的語言|p.55–57]] | `automata_homework 5d`；`5d --table` 印 NFA 邊與完整 DFA |
| Ch3 HW5(a)：`(a\|(bc)*d)+` | [[Compiler-Ch3-p051-p060#PPT p.058｜作業 5(a)：(a 或 (bc)*d)+ 的分組與正閉包|p.58–60]] | `automata_homework 5a`；`5a --table` 印 NFA 邊與完整 DFA |

原始 OCR 已與既有逐頁筆記交叉核對：[[Complier/Output/Ch01 introduction--0854d720-.document-rfLphW/auto/Ch01 introduction.md]]、[[Complier/Output/Ch02 a simple compiler--d580fadd-.document-YWemcl/auto/Ch02 a simple compiler.md]]、[[Complier/Output/Ch03 scanning--74ffa97a-.document-iPjp26/auto/Ch03 scanning.md]]。原料保持不變。本次只實作投影片列出的題目，不假定未提供的教科書其他小題或考試題目。

### Linux／DOMjudge 編譯與輸入規則

在 vault 根目錄操作；執行檔放 `/tmp`：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/14-ac作業完整版/ac_homework.cpp -o /tmp/ac_homework
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/15-HW5-NFA-DFA作業完整版/automata_homework.cpp -o /tmp/automata_homework
/tmp/ac_homework < Complier/Code/14-ac作業完整版/ac_homework.in
/tmp/ac_homework --fold < Complier/Code/14-ac作業完整版/ac_homework.in
/tmp/automata_homework 5a < Complier/Code/15-HW5-NFA-DFA作業完整版/automata_homework.in
```

只使用標準 C++ 標頭；沒有 `windows.h`、`conio.h`、`getch()`、`gets()`、`system()`、`bits/stdc++.h`、變長陣列或 flex／bison 依賴。程式從標準輸入讀取、結果寫至標準輸出，沒有提示字串；錯誤只寫到標準錯誤並回傳 1。ac 將 CR、LF、tab 等視為空白；自動機逐行讀取時只去掉行尾的一個 `\r`，保留其他空白作為不合法字元。

> [!warning] 提交格式邊界
> 尚未提供 DOMjudge 的實際題目、限制與輸出格式。以下是**投影片作業參考程式的明確契約**，不是已獲評測 Accepted 的提交。ac 無參數預設輸出 dc；自動機需 `5a/5d` 參數。若評測系統不傳命令列參數，依題目固定選擇一題／一種模式，再保留其需要的輸出格式；接受字串的文字也須遵循題目規定。

### ac 程式的契約與範例

從 stdin 讀取**整份** ac 原始碼直到 EOF；不是每行各自一個案例。宣告在敘述之前，變數仍是單一小寫字母，`f/i/p` 是保留字。完整 `float/int` 優先匹配；`floatx` 是 `float` 加 `x`，`fl` 是 `f` 加 `l`，沒有擅自改成多字母識別字。註解、分號、括號、乘除、一元負號不在此 ac 文法內。

```text
Prog  → Dcls Stmts $
Dcls  → Dcl Dcls | epsilon
Dcl   → floatdcl id | intdcl id
Stmts → Stmt Stmts | epsilon
Stmt  → id assign Val Expr | print id
Expr  → plus Val Expr | minus Val Expr | epsilon
Val   → id | inum | fnum
```

| 模式 | stdout |
|---|---|
| `--tokens` | 每行 `token-kind lexeme`，最後一行 `$`；只做詞法分析 |
| `--parse-tree` | 一行完整 S-expression parse tree；只做詞法／語法分析 |
| `--ast` | 一行原始 AST，葉標示 `id x`、數字等；不先檢查語意 |
| `--typed-ast` | 一行語意檢查後的 AST，必要時含 `int2float` |
| `--check` | 全程成功輸出 `OK`；檢查重複宣告、未宣告變數、float 指定給 int |
| `--dc`／無參數 | 每行一條 dc 指令；整份程式成功後才發出結果 |
| `--fold` | 搭配 `--ast/--typed-ast/--check/--dc`；折疊非負整數加法、相鄰整數常數加數 |

`--check` 只做教材的靜態型別規則，不分析變數是否已賦值，不等於執行成功保證。`--typed-ast` 以提升節點展示型別處理，不額外替每個節點印型別欄位。

輸入（[ac_homework.in](ac_homework.in)）：

```text
i x
x=100
x=x+30+1
p x
```

`--ast` 輸出：

```text
(Prog intdcl x (= id x 100) (= id x (+ (+ id x 30) 1)) print x)
```

`--ast --fold` 輸出：

```text
(Prog intdcl x (= id x 100) (= id x (+ id x 31)) print x)
```

`--fold` 產生的 dc 碼：

```text
100
sx
0 k
lx
31
+
sx
0 k
lx
p
si
```

本機實際把未摺疊與摺疊碼交給 `dc`，兩者均印 `131`。原 Fig.2.15 範例 `f b i a a=5 b=a+3.2 p b` 產碼後印 `8.2`。

> [!warning] 教材歧義與本程式的補充決定
> Ch2 p.42 的教材 AST 是右結合 `x+(30+1)`。本程式沿用既有 `ac.c` 的**左結合**，所以 `100-30-1` 是 `69`。`--fold` 只在 dc 的精確整數加法語意下重組 `(x+30)+1 → x+(30+1) → x+31`，不重組減法或浮點式。完整 parse tree 仍保留原本右遞迴文法的 `Expr` 結構。
>
> Ch2 p.43 的教材寫「No」，但已宣告的 integer `x` 加整數常數沒有違反已提供的型別規則；因此本程式接受原例，`--check` 印 `OK`。常數摺疊是最佳化，不是修復這份輸入的語意錯誤。原解答的待核對狀態保留在逐頁筆記。

#### Scanner 科學記號

題意修正版的數字格式（**補充**）：`[0-9]+([.][0-9]+)?(e[+-]?[0-9]+)?`。保留原題的小寫 `e`；`.1`、`10.`、`1e`、`1e+` 不接受。小數點或 exponent 已開始卻缺數字時直接報詞法錯誤。純數字是 `inum`；有小數點或 exponent 一律是 `fnum`，所以 `123e-22` 不會誤當 integer。這是本程式明示的型別政策。

例如 `--tokens` 對 `12 12.3 1.0e10 123e-22 12e+3` 輸出：

```text
inum 12
fnum 12.3
fnum 1.0e10
fnum 123e-22
fnum 12e+3
$
```

GNU dc 不支援 exponent 表示法，程式將 `123e-22` 精確轉成 `0.0000000000000000000123` 再產碼，避免先用 `double` 帶來捨入。[GNU dc 官方手冊](https://www.gnu.org/software/bc/manual/dc-1.05/html_mono/dc.html)。`5 k`／`0 k` 沿用教材型別提升與重設精度的產碼慣例；本章加減結果仍取決於運算元的小數位數。

**補充限制**：僅 dc 產碼需要展開 exponent；exponent 絕對值上限 10,000、mantissa 文字上限 10,000 字元，超過明確報錯。scanner 與 `--check` 不把浮點值轉成機器數字。整數加法摺疊使用十進位字串相加，沒有 `int/long long` 溢位。採整份輸入與 arena 儲存，記憶體隨輸入／節點量增長；未提供評測規模前不加串流框架。樹輸出、型別檢查、產碼使用迴圈，長加法鏈不依賴深層函式遞迴。

### Ch1 三題觀念解答

這三題原題沒有要求撰寫程式。第 4 題依教材設定，含編譯期錯誤的程式應先拒絕執行，讓所有原始碼先通過靜態檢查；不能拿「可能不走到那一行」當接受理由。ac 的型別檢查可示範此行為，但 ac 不含除法，沒有冒充能偵測 Ch1 的 `b/0`。

第 8 題依教材，VM interpreter 實作階段較少、較容易開發；缺點是原始碼先變 bytecode，執行時再由 interpreter 處理而增加時間。這是投影片的比較前提，不推廣成所有 JVM 實作的效能結論。

第 11 題依教材，輸出 C 可利用各架構已有的 C 編譯器，提高可攜性；代價是多一道 C → assembly 的翻譯。這與「用 C++ 寫本次 compiler」是不同概念。本次 Ch2 的目標碼仍是教材 dc。

### 驗證與重跑

```sh
python3 Complier/Code/check_cpp_homework.py
python3 Complier/Code/check_cpp_homework.py --sanitize
CXX=g++ python3 Complier/Code/check_cpp_homework.py
```

驗證器只用 Python 標準庫，將二進位檔放暫存目錄。逐字比較配套 `.in/.expected`，檢查教材 parse tree、AST、摺疊／未摺疊 dc 碼、型別提升、錯誤時 stdout 為空、LF／CRLF／無末尾換行、長輸入、5,001 項加法、超過 64-bit 的整數相加；並對兩題全部長度 0～8 的 **97,222** 個字串比較 NFA、DFA 與獨立 Python regular expression。

本次 macOS Clang C++17 在 `-Wall -Wextra -Wpedantic -Werror` 下兩份皆編譯成功，52 項檢查通過；AddressSanitizer／UndefinedBehaviorSanitizer 下同組檢查通過。另以 Zig C++ 交叉編譯 Linux musl 靜態 ELF，ARM64／x86-64 兩目標均檢查。**Linux 實機執行與 DOMjudge Accepted 尚未驗證**；本機 `g++` 名稱實際也指向 Apple Clang，不能聲稱已測 GNU GCC。詳細環境、程式 SHA-256 與實際結果見 `Complier/Review/cpp-homework-validation.json`。Obsidian 文字／連結靜態核對與執行驗證分開，不將 CLI 讀取視為 UI 渲染證據。

### 完整 C++：ac_homework.cpp

完整程式就是同資料夾的 [ac_homework.cpp](ac_homework.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
