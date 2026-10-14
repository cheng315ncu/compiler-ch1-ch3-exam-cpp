# 15 HW5 原 NFA→subset DFA 作業完整版

| 項目 | 內容 |
|---|---|
| 程式 | [automata_homework.cpp](automata_homework.cpp) |
| 類型 | 課程作業完整版 |
| 測例 | [automata_homework.in](automata_homework.in) → [automata_homework.expected](automata_homework.expected) |
| 相關資料夾 | [05-HW5固定DFA](../05-HW5固定DFA/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror automata_homework.cpp -o main
./main 5a < automata_homework.in | diff -u automata_homework.expected -
```

## 筆記：Compiler - Ch1-Ch3 作業完整 C++17 實作

> 原 `Complier/Notes/Compiler - Ch1-Ch3 作業完整 C++17 實作.md`，已整份移到這裡。教材頁碼：Ch1 PPT 25–30；Ch2 PPT 39–46；Ch3 PPT 53–60。


> [!abstract] 程式入口
> **C++ 實作（補充）**：兩份獨立、有 `main()` 的 C++17 程式。[ac_homework.cpp](../14-ac作業完整版/ac_homework.cpp) 完成 ac 的詞法分析（scanning）、語法分析（parsing）、剖析樹（parse tree）、抽象語法樹（AST）、語意分析（semantic analysis）與 dc 產碼；[automata_homework.cpp](automata_homework.cpp) 完成兩題非確定／確定有限自動機（NFA／DFA）。完整程式碼直接看各資料夾的 `.cpp` 原檔。

[[Compiler - 知識庫首頁|回首頁]] · [[Compiler - ac 編譯器全流程]] · [[Compiler - NFA 到 DFA 的完整構造]]

考試可攜帶的擴充版：[[Compiler - Ch1-Ch3 考試 C++ 程式集]]，含 HTML parser 等六份新程式與全部八份原碼的列印 PDF。


作業範圍總表、Ch1 觀念題與 ac 部分見 [14-ac作業完整版](../14-ac作業完整版/README.md)。

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

### NFA／DFA 程式的契約與範例

`5d` 辨識 `(bc)*d`；`5a` 辨識 `(a|(bc)*d)+`。一行是一個**完整待辨識字串**，輸出一行 `ACCEPT` 或 `REJECT`；空白行表示空字串，兩題都拒絕。沒有案例數、沒有前後空白修剪，最後一行沒有換行仍可讀取。這是完整字串辨識，不是 maximal-munch token 切分。

```sh
/tmp/automata_homework 5d --table
/tmp/automata_homework 5a --table
```

`--table` 不讀 stdin，先印原 NFA 的全部邊（`epsilon` 代表 λ），再印子集構造（subset construction）所得 DFA。狀態從 0 編號、按 alphabet 廣度優先發現；與教材 A–E 名稱不同但集合相同。包含拒絕 sink `{}`，不省略無轉移格。

| 題目 | 起始集合 | 接受集合 | 完整 DFA 狀態數 |
|---|---|---|---|
| 5(d) | `{1,2,5}` | `{6}` | 5（含 sink） |
| 5(a) | `{1,2,3,6,7,10}` | `{2,3,4,5,6,7,10,12}`、`{2,3,5,6,7,10,11,12}` | 6（含 sink） |

5(d) 接受 `d/bcd/bcbcd`，拒絕空字串、`bc/bd/bcdd`。5(a) 接受 `a/d/ad/bcd/abcbcdad/bcdd`；最後一個是 `bcd` 加 `d` 兩組，不能誤拒絕。程式同時計算 NFA 與 DFA 的結果並檢查一致。原始 NFA 是固定教材圖，32-bit 集合足以放下狀態 1～12；沒有實作未要求的任意 RE parser 或 DFA 最小化。

### 驗證與重跑

```sh
python3 Complier/Code/check_cpp_homework.py
python3 Complier/Code/check_cpp_homework.py --sanitize
CXX=g++ python3 Complier/Code/check_cpp_homework.py
```

驗證器只用 Python 標準庫，將二進位檔放暫存目錄。逐字比較配套 `.in/.expected`，檢查教材 parse tree、AST、摺疊／未摺疊 dc 碼、型別提升、錯誤時 stdout 為空、LF／CRLF／無末尾換行、長輸入、5,001 項加法、超過 64-bit 的整數相加；並對兩題全部長度 0～8 的 **97,222** 個字串比較 NFA、DFA 與獨立 Python regular expression。

本次 macOS Clang C++17 在 `-Wall -Wextra -Wpedantic -Werror` 下兩份皆編譯成功，52 項檢查通過；AddressSanitizer／UndefinedBehaviorSanitizer 下同組檢查通過。另以 Zig C++ 交叉編譯 Linux musl 靜態 ELF，ARM64／x86-64 兩目標均檢查。**Linux 實機執行與 DOMjudge Accepted 尚未驗證**；本機 `g++` 名稱實際也指向 Apple Clang，不能聲稱已測 GNU GCC。詳細環境、程式 SHA-256 與實際結果見 `Complier/Review/cpp-homework-validation.json`。Obsidian 文字／連結靜態核對與執行驗證分開，不將 CLI 讀取視為 UI 渲染證據。

### 完整 C++：automata_homework.cpp

完整程式就是同資料夾的 [automata_homework.cpp](automata_homework.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
