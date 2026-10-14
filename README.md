# Compiler Ch1–3：考試 C++ 原碼與手冊

繁體中文註解、標準 C++17、Linux／DOMjudge 輸入輸出；採直接函式與標準容器的 ponytail 寫法。共有 **21 份獨立程式**，包含八題優先使用的短版／簡單版本、兩題課程作業、完整功能版本與六題模擬題。

**每份程式各有一個資料夾**（`Complier/Code/NN-題型/`），裡面放 `.cpp`、`.in`、`.expected` 測例和 `README.md`：完整題意、輸入輸出、範例、手動追蹤、修改範例與該題筆記都在那份 README。看資料夾名稱就能找到題目。

## 先讀這兩份

- [70 頁 A4 完整列印手冊（雙面 35 張）](Complier/Review/Compiler-Ch1-Ch3-Print-Handbook.pdf)：完整題意、選檔索引、流程圖、40 個改動範例與三章速查表。
- [完整程式指南 HTML](Complier/Review/Compiler-Ch1-Ch3-Print-Handbook.html)：前 47 頁指南內容全部攤開；三章附錄收於完整 PDF。

下載或 clone 後，用瀏覽器開啟 HTML 即可離線閱讀；GitHub 的 HTML 檔案頁顯示原始內容。列印設定為 A4、雙面、長邊翻頁、實際大小 100%。程式直接帶 `.cpp`。

## 資料夾索引

| 資料夾 | 程式 | 類型 |
|---|---|---|
| [01-HTML標籤配對](Complier/Code/01-HTML標籤配對/README.md) | `html_check.cpp` | 優先（短版） |
| [02-遞迴下降運算式](Complier/Code/02-遞迴下降運算式/README.md) | `expression.cpp` | 優先（短版） |
| [03-Scanner與註解](Complier/Code/03-Scanner與註解/README.md) | `lexer.cpp` | 優先 |
| [04-NFA判定字串](Complier/Code/04-NFA判定字串/README.md) | `nfa_check.cpp` | 優先（短版） |
| [05-HW5固定DFA](Complier/Code/05-HW5固定DFA/README.md) | `hw5_check.cpp` | 優先（短版） |
| [06-ac產dc](Complier/Code/06-ac產dc/README.md) | `ac_dc.cpp` | 優先（短版） |
| [07-StackVM](Complier/Code/07-StackVM/README.md) | `stack_vm.cpp` | 優先 |
| [08-LL1](Complier/Code/08-LL1/README.md) | `ll1.cpp` | 較低優先補充 |
| [09-作業ScannerTest](Complier/Code/09-作業ScannerTest/README.md) | `scanner.cpp` | 課程作業 |
| [10-作業ParserTest](Complier/Code/10-作業ParserTest/README.md) | `parser.cpp` | 課程作業 |
| [11-HTML-parser完整版](Complier/Code/11-HTML-parser完整版/README.md) | `html_parser.cpp` | 完整功能 |
| [12-運算式parser完整版](Complier/Code/12-運算式parser完整版/README.md) | `expression.cpp` | 完整功能 |
| [13-NFA轉DFA完整版](Complier/Code/13-NFA轉DFA完整版/README.md) | `nfa_to_dfa.cpp` | 完整功能 |
| [14-ac作業完整版](Complier/Code/14-ac作業完整版/README.md) | `ac_homework.cpp` | 作業完整版 |
| [15-HW5-NFA-DFA作業完整版](Complier/Code/15-HW5-NFA-DFA作業完整版/README.md) | `automata_homework.cpp` | 作業完整版 |
| [16-模擬Scanner宣告敘述](Complier/Code/16-模擬Scanner宣告敘述/README.md) | `decl_scanner.cpp` | 模擬題 |
| [17-模擬Scanner比較運算子與註解](Complier/Code/17-模擬Scanner比較運算子與註解/README.md) | `compare_scanner.cpp` | 模擬題 |
| [18-模擬Parser四則運算](Complier/Code/18-模擬Parser四則運算/README.md) | `expr_parser.cpp` | 模擬題 |
| [19-模擬Parser函式呼叫鏈](Complier/Code/19-模擬Parser函式呼叫鏈/README.md) | `call_parser.cpp` | 模擬題 |
| [20-模擬Parser-JSON](Complier/Code/20-模擬Parser-JSON/README.md) | `json_parser.cpp` | 模擬題 |
| [21-模擬Parser-HTML標籤](Complier/Code/21-模擬Parser-HTML標籤/README.md) | `html_tags.cpp` | 模擬題 |

## 優先使用的八份

| 題型 | 原檔 | 預設／修改重點 |
|---|---|---|
| HTML 配對 | [01-HTML標籤配對/html_check.cpp](Complier/Code/01-HTML標籤配對/html_check.cpp) | 整份 stdin 一案；VALID／INVALID |
| 算式求值／AST／Postfix | [02-遞迴下降運算式/expression.cpp](Complier/Code/02-遞迴下降運算式/expression.cpp) | MODE=eval；可改 ast／postfix |
| Scanner、註解、Longest Match | [03-Scanner與註解/lexer.cpp](Complier/Code/03-Scanner與註解/lexer.cpp) | keywords／ops；C-like 規格 |
| 給 NFA，判字串 | [04-NFA判定字串/nfa_check.cpp](Complier/Code/04-NFA判定字串/nfa_check.cpp) | #=epsilon；每行一案 |
| 固定 HW5 DFA | [05-HW5固定DFA/hw5_check.cpp](Complier/Code/05-HW5固定DFA/hw5_check.cpp) | HW5A=true 選 (a\|(bc)*d)+；false 選 (bc)*d |
| ac 型別檢查與 dc 產碼 | [06-ac產dc/ac_dc.cpp](Complier/Code/06-ac產dc/ac_dc.cpp) | 只輸出 target code |
| Stack VM | [07-StackVM/stack_vm.cpp](Complier/Code/07-StackVM/stack_vm.cpp) | PRINT 會 pop；非 dc 指令集 |
| FIRST／FOLLOW／LL(1) | [08-LL1/ll1.cpp](Complier/Code/08-LL1/ll1.cpp) | 預設表格；--check 判 token 序列，較低優先補充 |

## 課程作業

| 題型 | 原檔 | 預設／修改重點 |
|---|---|---|
| ScannerTest：算式 Token | [09-作業ScannerTest/scanner.cpp](Complier/Code/09-作業ScannerTest/scanner.cpp) | NUM／PLUS／MINUS／MUL／DIV／LPR／RPR；NUM 開頭 0 只吃一位 |
| ParserTest：Recursive-Descent | [10-作業ParserTest/parser.cpp](Complier/Code/10-作業ParserTest/parser.cpp) | 合法才印「種類 原字串」；否則只印 invalid input |

## 模擬題

16–21 是照 ScannerTest／ParserTest 作業格式出的模擬題：Terminal RE 表、Productions、Input／Output Format、Sample。每份 README 就是題目，`.cpp` 是對應解答；README 裡的 Sample 由 `check_cpp_homework.py` 直接拿來測。

| 題目 | 考點 |
|---|---|
| 16 宣告敘述 Scanner | keyword 讀完整字再查表；INUM 開頭 0；FNUM 兩字元 lookahead |
| 17 比較運算子與註解 | longest match（`<=` 先於 `<`）；`//`、`/* */`；錯誤時只印 invalid input |
| 18 四則運算 Parser | expr／term／factor 遞迴下降；必須停在 END |
| 19 函式呼叫鏈 Parser | ParserTest 延伸：`a[0].b(c(1), "x");`、args 的 λ |
| 20 JSON 子集 Parser | 巢狀 object／array；逗號後必須還有一項；keyword 完整比對 |
| 21 HTML 標籤 Parser | 歷屆 HTML 題 × ParserTest：OPEN／CLOSE 名稱配對、TEXT 空白整理 |

## 需要完整功能時

| 原檔 | 功能／模式 |
|---|---|
| [11-HTML-parser完整版/html_parser.cpp](Complier/Code/11-HTML-parser完整版/html_parser.cpp) | --check（預設）／--tokens／--tree／--text |
| [12-運算式parser完整版/expression.cpp](Complier/Code/12-運算式parser完整版/expression.cpp) | --postfix（預設）／--ast／--eval；迭代式實作 |
| [13-NFA轉DFA完整版/nfa_to_dfa.cpp](Complier/Code/13-NFA轉DFA完整版/nfa_to_dfa.cpp) | --check（預設）／--trace／--table |
| [14-ac作業完整版/ac_homework.cpp](Complier/Code/14-ac作業完整版/ac_homework.cpp) | --dc（預設）／--tokens／--parse-tree／--ast／--typed-ast／--check；可加 --fold |
| [15-HW5-NFA-DFA作業完整版/automata_homework.cpp](Complier/Code/15-HW5-NFA-DFA作業完整版/automata_homework.cpp) | 5a 或 5d；加 --table 印原 NFA 與完整 subset DFA |

`12-運算式parser完整版/expression.cpp` 與 `02-遞迴下降運算式/expression.cpp` 同名但預設模式不同，選檔時看完整路徑。每份有自己的 `main()`，只編譯選中的一份，不能把全部原檔一起連結。

## 編譯與測例

在 repository 根目錄執行：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/01-HTML標籤配對/html_check.cpp -o main
./main < Complier/Code/01-HTML標籤配對/html_check.in > actual.out
diff -u Complier/Code/01-HTML標籤配對/html_check.expected actual.out
```

所有 C++ 程式不需外部套件。逐行字串題處理末尾 CR，LF／CRLF 都有測例；不用 Windows 專屬 API。

## 驗證腳本

這三支只需要 Python 3 標準庫與 C++17 compiler：

```sh
python3 Complier/Code/check_cpp_short.py
python3 Complier/Code/check_cpp_exam.py
python3 Complier/Code/check_cpp_homework.py
```

可加 `--sanitize` 執行 AddressSanitizer／UndefinedBehaviorSanitizer；可用 `CXX=g++` 指定 compiler。

40 個手冊改動範例的試編與 PDF 重建另需文件工具：

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-docs.txt
python3 Complier/Code/check_cpp_handbook.py
python3 Complier/Code/build_cpp_print_handbook.py
```

WeasyPrint 的系統字型／Pango 依賴需由執行環境提供。現成 HTML／PDF 已包含於此 repo，不需重建即可閱讀。

## 詳細說明

- 每題的完整說明：各資料夾的 `README.md`（見上方資料夾索引）。原 `Complier/Notes/` 的七份筆記已搬進對應資料夾的 README；ac／HW5 作業筆記拆成 14 與 15 兩份。
- [列印手冊頁碼索引](Complier/Review/Compiler%20-%20Ch1-Ch3%20%E8%80%83%E5%A0%B4%E5%88%97%E5%8D%B0%E6%89%8B%E5%86%8A.md)

Markdown 說明保留原 Obsidian wikilink 與教材頁碼；可直接閱讀，完整導覽使用上方 HTML／PDF。來源投影片或 OCR 的追溯連結指向原知識庫。

## 題型與證據界線

HTML parser 是使用者提供的歷屆線索，未附原考卷；手冊完整題意／I/O 是模擬規格。Ch2／Ch3 作業、教材解答及補充另有標示。FIRST／FOLLOW／LL(1) 正式範圍尚未確認。

原短版有 610 項檢查、完整考試版本有 151 項檢查、作業與模擬題有 132 項檢查，40 個修改範例有 82 次樣例檢查。手冊報告收於 `Complier/Review/cpp-handbook-examples.json` 與 `cpp-print-handbook-validation.json`；此 repo 匯出後的實測另見 `repo-validation.json`。Linux x86-64 交叉編譯成功，Linux 實跑／DOMjudge Accepted 未驗證；本機 compiler 為 Apple Clang。

這是原課程知識庫的匯出副本；程式已改成一題一資料夾，測試腳本與手冊路徑已同步更新；只收錄這份 C++ 程式集相關檔案。`export-manifest.json` 列出匯出當時的來源 commit、檔案大小及 SHA-256（重整成一題一資料夾之前的路徑）。

## License

[MIT](LICENSE)
