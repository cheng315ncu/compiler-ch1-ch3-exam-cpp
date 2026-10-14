# Compiler Ch1–3：考試 C++ 原碼與手冊

繁體中文註解、標準 C++17、Linux／DOMjudge 輸入輸出；採直接函式與標準容器的 ponytail 寫法。共有 **13 份獨立程式**，包含八題優先使用的短版／簡單版本與完整功能版本，每份都有 `.in`、`.expected` 測例。

## 先讀這三份

- [70 頁 A4 完整列印手冊（雙面 35 張）](Complier/Review/Compiler-Ch1-Ch3-Print-Handbook.pdf)：完整題意、選檔索引、流程圖、40 個改動範例與三章速查表。
- [精簡查題／改題 HTML](Complier/Review/Compiler-Ch1-Ch3-Cpp-Short.html)：直接連到原碼，詳細改前／改後與測例可展開。
- [完整程式指南 HTML](Complier/Review/Compiler-Ch1-Ch3-Print-Handbook.html)：前 47 頁指南內容全部攤開；三章附錄收於完整 PDF。

下載或 clone 後，用瀏覽器開啟 HTML 即可離線閱讀；GitHub 的 HTML 檔案頁顯示原始內容。列印設定為 A4、雙面、長邊翻頁、實際大小 100%。程式直接帶 `.cpp`。

## 優先使用的八份

| 題型 | 原檔 | 預設／修改重點 |
|---|---|---|
| HTML 配對 | [exam/short/html_check.cpp](Complier/Code/exam/short/html_check.cpp) | 整份 stdin 一案；VALID／INVALID |
| 算式求值／AST／Postfix | [exam/short/expression.cpp](Complier/Code/exam/short/expression.cpp) | MODE=eval；可改 ast／postfix |
| Scanner、註解、Longest Match | [exam/lexer.cpp](Complier/Code/exam/lexer.cpp) | keywords／ops；C-like 規格 |
| 給 NFA，判字串 | [exam/short/nfa_check.cpp](Complier/Code/exam/short/nfa_check.cpp) | #=epsilon；每行一案 |
| 固定 HW5 DFA | [exam/short/hw5_check.cpp](Complier/Code/exam/short/hw5_check.cpp) | HW5A=true 選 (a\|(bc)*d)+；false 選 (bc)*d |
| ac 型別檢查與 dc 產碼 | [exam/short/ac_dc.cpp](Complier/Code/exam/short/ac_dc.cpp) | 只輸出 target code |
| Stack VM | [exam/stack_vm.cpp](Complier/Code/exam/stack_vm.cpp) | PRINT 會 pop；非 dc 指令集 |
| FIRST／FOLLOW／LL(1) | [exam/ll1.cpp](Complier/Code/exam/ll1.cpp) | 預設表格；--check 判 token 序列，較低優先補充 |

## 需要完整功能時

| 原檔 | 功能／模式 |
|---|---|
| [exam/html_parser.cpp](Complier/Code/exam/html_parser.cpp) | --check（預設）／--tokens／--tree／--text |
| [exam/expression.cpp](Complier/Code/exam/expression.cpp) | --postfix（預設）／--ast／--eval；迭代式實作 |
| [exam/nfa_to_dfa.cpp](Complier/Code/exam/nfa_to_dfa.cpp) | --check（預設）／--trace／--table |
| [ch02/ac_homework.cpp](Complier/Code/ch02/ac_homework.cpp) | --dc（預設）／--tokens／--parse-tree／--ast／--typed-ast／--check；可加 --fold |
| [ch03/automata_homework.cpp](Complier/Code/ch03/automata_homework.cpp) | 5a 或 5d；加 --table 印原 NFA 與完整 subset DFA |

`exam/expression.cpp` 與 `exam/short/expression.cpp` 同名但預設模式不同，選檔時看完整路徑。每份有自己的 `main()`，只編譯選中的一份，不能把全部原檔一起連結。

## 編譯與測例

在 repository 根目錄執行：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/short/html_check.cpp -o main
./main < Complier/Code/exam/short/html_check.in > actual.out
diff -u Complier/Code/exam/short/html_check.expected actual.out
```

所有 C++ 程式不需外部套件。逐行字串題處理末尾 CR，LF／CRLF 都有測例；不用 Windows 專屬 API。

## 驗證腳本

前三支只需要 Python 3 標準庫與 C++17 compiler：

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
python3 Complier/Code/build_cpp_short_pack.py
python3 Complier/Code/build_cpp_print_handbook.py
```

WeasyPrint 的系統字型／Pango 依賴需由執行環境提供。現成 HTML／PDF 已包含於此 repo，不需重建即可閱讀。`build_cpp_short_pack.py --pdf` 可另產出原碼 PDF；預設只重建查題指南。

## 詳細說明

- [八題短版說明](Complier/Review/Compiler%20-%20Ch1-Ch3%20%E8%80%83%E5%A0%B4%E7%9F%AD%E7%89%88%20C%2B%2B.md)
- [完整程式集索引](Complier/Review/Compiler%20-%20Ch1-Ch3%20%E8%80%83%E8%A9%A6%20C%2B%2B%20%E7%A8%8B%E5%BC%8F%E9%9B%86.md)
- [ac／HW5 完整作業](Complier/Notes/Compiler%20-%20Ch1-Ch3%20%E4%BD%9C%E6%A5%AD%E5%AE%8C%E6%95%B4%20C%2B%2B17%20%E5%AF%A6%E4%BD%9C.md)
- [列印手冊頁碼索引](Complier/Review/Compiler%20-%20Ch1-Ch3%20%E8%80%83%E5%A0%B4%E5%88%97%E5%8D%B0%E6%89%8B%E5%86%8A.md)
- [Compiler - HTML parser 考試實作](Complier/Notes/Exam/Compiler%20-%20HTML%20parser%20%E8%80%83%E8%A9%A6%E5%AF%A6%E4%BD%9C.md)
- [Compiler - Predict 與 LL1 考試實作](Complier/Notes/Exam/Compiler%20-%20Predict%20%E8%88%87%20LL1%20%E8%80%83%E8%A9%A6%E5%AF%A6%E4%BD%9C.md)
- [Compiler - Scanner 與註解考試實作](Complier/Notes/Exam/Compiler%20-%20Scanner%20%E8%88%87%E8%A8%BB%E8%A7%A3%E8%80%83%E8%A9%A6%E5%AF%A6%E4%BD%9C.md)
- [Compiler - 堆疊機 Interpreter 考試實作](Complier/Notes/Exam/Compiler%20-%20%E5%A0%86%E7%96%8A%E6%A9%9F%20Interpreter%20%E8%80%83%E8%A9%A6%E5%AF%A6%E4%BD%9C.md)
- [Compiler - 通用 NFA DFA 考試實作](Complier/Notes/Exam/Compiler%20-%20%E9%80%9A%E7%94%A8%20NFA%20DFA%20%E8%80%83%E8%A9%A6%E5%AF%A6%E4%BD%9C.md)
- [Compiler - 運算式 parser 考試實作](Complier/Notes/Exam/Compiler%20-%20%E9%81%8B%E7%AE%97%E5%BC%8F%20parser%20%E8%80%83%E8%A9%A6%E5%AF%A6%E4%BD%9C.md)

Markdown 說明保留原 Obsidian wikilink 與教材頁碼；可直接閱讀，完整導覽使用上方 HTML／PDF。來源投影片或 OCR 的追溯連結指向原知識庫。

## 題型與證據界線

HTML parser 是使用者提供的歷屆線索，未附原考卷；手冊完整題意／I/O 是模擬規格。Ch2／Ch3 作業、教材解答及補充另有標示。FIRST／FOLLOW／LL(1) 正式範圍尚未確認。

原短版有 610 項檢查、完整考試版本有 151 項檢查，40 個修改範例有 82 次樣例檢查。既有報告收於 `Complier/Review/cpp-*.json`；此 repo 匯出後的實測另見 `repo-validation.json`。Linux x86-64 交叉編譯成功，Linux 實跑／DOMjudge Accepted 未驗證；本機 compiler 為 Apple Clang。

這是原課程知識庫的私人匯出副本，保留原路徑讓測試與手冊能對上；只收錄這份 C++ 程式集相關檔案。`export-manifest.json` 列出來源 commit、檔案大小及 SHA-256，可核對原碼與文件未改動。
