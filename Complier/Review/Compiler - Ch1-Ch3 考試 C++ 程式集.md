---
title: "Compiler - Ch1-Ch3 考試 C++ 程式集"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement, source/user-provided]
chapter: [1, 2, 3]
source: "使用者提供 HTML parser 歷屆線索；Ch1–3 教材與既有作業筆記"
source_pages: "Ch1 p.12–19；Ch2 p.6–38、p.39–46；Ch3 p.3、p.15–20、p.42–60；延伸題非確認考題"
---

# Compiler - Ch1-Ch3 考試 C++ 程式集

> [!tip] 考場手寫優先用短版
> [[Compiler - Ch1-Ch3 考場短版 C++|八題考場短版]]：未加中文註解時五份為 839 → 400 行；保留原功能版本供 token／tree／DFA 表等題型。

> [!abstract] 八份完整程式，依題目選用
> 新增六份，保留原本 ac 與 HW5 NFA／DFA 兩份，均有 `main()`、只用標準 C++17、stdin/stdout、Linux 編譯指令與 CRLF 測例。程式採 ponytail：直接函式、標準容器、沒有外部套件或通用 framework。[[Complier/Review/Compiler-Ch1-Ch3-Cpp-Exam-Pack.pdf|A4 列印 PDF]] · [[Complier/Review/Compiler-Ch1-Ch3-Cpp-Exam-Pack.html|離線 HTML]] · [[Compiler - Ch1-Ch3 作業完整 C++17 實作|原作業兩份]]。

[[Compiler - 知識庫首頁|回首頁]]

## 題型證據與準備順序

**已知線索**：使用者在 2026-10-14 表示歷屆出過 HTML parser，但未附原題與 I/O。既有 [[Compiler - 第二次小考題目紀錄]] 有 CFG 與 AST 題；[[Compiler - 第一次小考題目與標準答案]] 有 token、compiler/interpreter、語法／語意及平台相容題。Ch2/Ch3 實際作業包含 scanner 擴充、parse tree／AST／產碼、NFA→DFA。

**下面是準備優先度，不是出題機率，也不是取得的考卷**：先 HTML 與 scanner，接運算式 AST 與原 ac 作業，再 NFA／DFA；stack VM 為產碼／直譯練習，FIRST/FOLLOW/LL(1) 為較低優先的補充（正式術語預告於 Ch4）。

| # | 題型 | 說明入口 | 單檔 |
|---|---|---|---|
| 01 | HTML parser 與標籤配對 | [[Compiler - HTML parser 考試實作|說明與完整 code]] | `html_parser.cpp` |
| 02 | 運算式 AST、後序式與求值 | [[Compiler - 運算式 parser 考試實作|說明與完整 code]] | `expression.cpp` |
| 03 | Scanner、註解與 longest match | [[Compiler - Scanner 與註解考試實作|說明與完整 code]] | `lexer.cpp` |
| 04 | 通用 epsilon-NFA → DFA | [[Compiler - 通用 NFA DFA 考試實作|說明與完整 code]] | `nfa_to_dfa.cpp` |
| 05 | FIRST／FOLLOW／SELECT／LL(1) | [[Compiler - Predict 與 LL1 考試實作|說明與完整 code]] | `ll1.cpp` |
| 06 | Stack VM 與最小 interpreter | [[Compiler - 堆疊機 Interpreter 考試實作|說明與完整 code]] | `stack_vm.cpp` |
| 07 | ac：parse tree／AST／語意／摺疊／dc | [[Compiler - Ch1-Ch3 作業完整 C++17 實作|完整作業]] | `Code/ch02/ac_homework.cpp` |
| 08 | 固定 HW5(a)/(d) NFA→DFA | [[Compiler - Ch1-Ch3 作業完整 C++17 實作|完整作業]] | `Code/ch03/automata_homework.cpp` |

## 看見題目時，選哪個與改哪裡

| 題目要求 | 選程式／模式 | 最先確認 |
|---|---|---|
| HTML tag 是否正確巢狀 | html_parser 預設 | case-sensitive？void？一行還是整份？有無 optional closing？ |
| HTML token、tree、text | html_parser --tokens／--tree／--text | 是否 entity 解碼、是否保留空白、是否排除 script？ |
| 列 token、跳註解、最長運算子 | lexer | ID／底線規則、keyword、number 格式、輸出名稱 |
| expression 畫 AST／轉 postfix／計算 | expression --ast／預設／--eval | precedence、associativity、unary minus、數值精度 |
| ac 作業的 AST／型別／產碼 | ac_homework | 單字母 ID、宣告順序、目標為 dc，不是 numeric output |
| NFA 讀轉移表或追蹤集合 | nfa_to_dfa 預設／--trace／--table | state 起算、epsilon 字元、alphabet、完整字串還是 tokenizing |
| 題目直接給 HW5 RE | automata_homework 5a／5d | 固定命令列模式；judge 通常不會幫你傳參數 |
| FIRST／FOLLOW／predict／LL(1) | ll1 預設／--check | #／$ 規則、一行一 alternative、token 種類先分好 |
| 執行 postfix／stack IR | stack_vm | pop 右再左、PRINT 是否 pop、integer 還是 floating |

## 考場使用契約

各 `.cpp` 都是**獨立程式**，只編譯選中的一份，不能全部連結造成多個 main。試題若沒有命令列參數，就改 main 的預設模式／固定 HW5 題號；不要往 stdout 印提示、debug、額外 table 或 EOF，除非題目要求。測例數 T、空白行是否是案例、VALID/INVALID/YES/NO 字樣與精度，全部依原題改。

HTML 巢狀配對需要 stack；單一 regular expression 不適合任意深度的 tag nesting。這份 parser 是明示子集，不冒充 browser DOM。運算式 precedence 是補充；原 ac 仍只有加減與單字母 ID。不同數字／identifier 規格不要混在一起。

## 編譯、驗證與列印

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/html_parser.cpp -o /tmp/html_parser
/tmp/html_parser < Complier/Code/exam/html_parser.in
python3 Complier/Code/check_cpp_exam.py
python3 Complier/Code/check_cpp_exam.py --sanitize
python3 Complier/Code/check_cpp_homework.py
```

新六份：151 項檢查、300 個獨立 Fraction expression、1,524 個隨機 NFA 字串，含 LF／CRLF／無末尾換行與 malformed／deep input。正常與 sanitizer 通過。Linux x86-64 musl 靜態 ELF 編譯通過，未做 Linux 實機執行或 DOMjudge Accepted 驗證；本機 g++ 指向 Apple Clang，沒有宣稱 GNU GCC 已實跑。

PDF 包含全部八份完整 source，帶行號及頁碼、樣例與考場改法；依目錄頁碼只印需要的題型。PDF 的長行會視覺換行，真正提交／複製以 `.cpp` 為準。HTML 為離線單檔，沒有外部資源。筆記中的完整 code 與原檔逐字比對；來源／測試與 PDF 校驗見 `Complier/Review/cpp-exam-validation.json`。沒有上傳 Notion。
