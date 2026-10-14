---
title: "Compiler - Ch1-Ch3 考場列印手冊"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "八份註解原檔、40 個已驗證變體、Quiz 1／2 紀錄與 Ch1–3 完整速查表"
source_pages: "各章原有 PPT 頁碼保留在合併 PDF；本冊頁碼另列於下"
---

# Compiler - Ch1-Ch3 考場列印手冊

> [!abstract] 可直接列印的完整版本
> [[Complier/Review/Compiler-Ch1-Ch3-Print-Handbook.html|考場速查 HTML]]：10 頁 A4，寫 code 用的骨架、觀念與各題改法。完整題意與改前／改後範例見 [[Complier/Review/Compiler-Ch1-Ch3-Detail.html|完整指南 HTML]]；舊版 70 頁 PDF 已不在 repo，下方 PDF 頁碼僅供參考。

程式直接攜帶 `.cpp`；紙本提供選檔、完整題意、輸入輸出、解題追蹤、3 張流程圖、40 個修改範例的改前／改後及測例。八份原碼未修改，不在紙本重抄整份程式。附錄收錄 Ch1 7 頁、Ch2 6 頁、Ch3 10 頁，全部保留。

## 查找入口

| 內容 | 本冊 PDF 頁 |
|---|---:|
| 選檔索引 | 1 |
| 三章內容索引 | 2 |
| 完整版本與模式 | 3 |
| 跨平台與 I/O | 4 |
| 除錯與提交前測例 | 5 |
| 小考原題與英文參考答案 | 6 |
| HTML 標籤配對 · [[Complier/Code/01-HTML標籤配對/html_check.cpp|原碼]] | 8 |
| 遞迴下降運算式 · [[Complier/Code/02-遞迴下降運算式/expression.cpp|原碼]] | 13 |
| Scanner：沿用現有短程式 · [[Complier/Code/03-Scanner與註解/lexer.cpp|原碼]] | 17 |
| NFA 直接判定字串 · [[Complier/Code/04-NFA判定字串/nfa_check.cpp|原碼]] | 22 |
| HW5 固定四狀態 DFA · [[Complier/Code/05-HW5固定DFA/hw5_check.cpp|原碼]] | 28 |
| ac 邊解析邊產 dc · [[Complier/Code/06-ac產dc/ac_dc.cpp|原碼]] | 32 |
| Stack VM：沿用現有短程式 · [[Complier/Code/07-StackVM/stack_vm.cpp|原碼]] | 38 |
| LL(1)：較低優先補充 · [[Complier/Code/08-LL1/ll1.cpp|原碼]] | 43 |

## 三章速查表頁碼

| 原章節頁 | 主題 | 本冊 PDF 頁 |
|---|---|---:|
| Ch1 原第 1 頁 | 編譯器定義與目標碼 | 48 |
| Ch1 原第 2 頁 | Compiler／Interpreter 與編譯流程 | 49 |
| Ch1 原第 3 頁 | Scanner C 實作與前後端 | 50 |
| Ch1 原第 4 頁 | Bootstrapping 與 T 圖 | 51 |
| Ch1 原第 5 頁 | Optimizer：矩陣乘法 | 52 |
| Ch1 原第 6 頁 | HW 4／8／11 與短答 | 53 |
| Ch1 原第 7 頁 | 名詞速查與自測 | 54 |
| Ch2 原第 1 頁 | 詞法、Token 與英文短答 | 55 |
| Ch2 原第 2 頁 | 15 條 ac 文法、Predict 與 Parser | 56 |
| Ch2 原第 3 頁 | 推導、Parse Tree 與 AST | 57 |
| Ch2 原第 4 頁 | Symbol Table、型別與錯誤 | 58 |
| Ch2 原第 5 頁 | dc 產碼與 Stack Trace | 59 |
| Ch2 原第 6 頁 | HW 1／2／3 與 Scanner 擴充 | 60 |
| Ch3 原第 1 頁 | 中英術語與階段速查 | 61 |
| Ch3 原第 2 頁 | 六類題目解題步驟 | 62 |
| Ch3 原第 3 頁 | CFG 與概念英文短答 | 63 |
| Ch3 原第 4 頁 | AST 畫法與優先序 | 64 |
| Ch3 原第 5 頁 | RE、Identifier 與 Exponent | 65 |
| Ch3 原第 6 頁 | DFA／NFA 與 Scanner 行為 | 66 |
| Ch3 原第 7 頁 | RE→NFA 與 (bc)*d | 67 |
| Ch3 原第 8 頁 | NFA→DFA 子集構造 | 68 |
| Ch3 原第 9 頁 | (a|b)*abb 構造與追蹤 | 69 |
| Ch3 原第 10 頁 | HW5(a) 完整表與短答 | 70 |

## 來源與證據界線

- [[Compiler - Ch1-Ch3 考場短版 C++]]：八題輸入輸出與註解原檔。
- [[Compiler - 第一次小考題目與標準答案]]：五題原文與教材整理的參考答案，非教師逐字解答。
- [[Compiler - 第二次小考題目紀錄]]：CFG／AST 兩題，原 AST 程式未附，手冊算式例另標補充。
- Ch1／Ch2／Ch3 原速查 PDF 全頁納入；保留教材頁碼、來源／補充分界與已知疑義，原檔不改。
- HTML parser 歷屆線索由使用者提供；本冊完整題意及 I/O 是模擬規格。
- FIRST／FOLLOW／LL(1) 是較低優先延伸，正式考試範圍尚未確認。
- 八份來源雜湊與目前 610 項 native／sanitizer 驗證報告一致，40 個變體與 82 個樣例的既有證據亦核對，此次沒有變更 C++。
- Linux 交叉編譯成功；Linux 實跑、GNU GCC 執行結果與 DOMjudge Accepted 未驗證。

## 列印設定

A4、雙面、長邊翻頁、100%／實際大小。最底端 `Print handbook N / TOTAL` 為本冊連續頁碼，各章原 footer 是章內頁碼。用紙籤分開程式指南、Ch1、Ch2、Ch3 即可。

## 重建與驗證

```sh
/Volumes/D/graduate/presentation/.venv/bin/python Complier/Code/build_cpp_print_handbook.py
```

使用現有 WeasyPrint 與 PyMuPDF；圖表為向量，文字可搜尋。附錄只改 RGB 色彩指令為灰階，保留原字型及文字。重建檢查原碼雜湊、變體 patch／行號、灰階後全頁文字、A4 尺寸、頁碼索引與書籤。視覺校讀記於 `cpp-print-handbook-validation.json`。
