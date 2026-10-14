---
title: "Compiler - 第一次小考題目與標準答案"
aliases:
  - Compiler 第一次小考
  - Compiler Quiz 1
created: 2026-09-27
updated: 2026-09-27
tags:
  - type/exam-review
  - course/compiler
  - source/user-provided
  - source/fischer-cytron-leblanc
chapter: 1
source:
  - "使用者提供的第一次小考五題原文"
  - "[[Complier/Inbox/Ch01 introduction.pptx]]"
  - "[[Complier/Output/Ch01 introduction--0854d720-.document-rfLphW/auto/Ch01 introduction]]"
source_pages: "原題未附頁碼；對照 Chapter 1 PPT p.003、p.006–009、p.012–014、p.017–019"
notion_url: https://app.notion.com/p/3e89eb9d3cee81ffbe69d70e3ad19dd4
notion_synced: 2026-09-27
notion_sync_status: verified
---

# Compiler - 第一次小考題目與標準答案

> [!abstract] 使用方式
> 每題保留英文原文，先列可直接作答的英文答案，再用繁體中文解釋考點。以下是依教材整理的參考標準答案，並非教師公布的逐字解答。

| 題號 | 考點 | 作答核心 |
|---|---|---|
| [[#第 1 題｜Compiler 與 Interpreter\|1]] | 編譯與直譯 | 編譯產生目標程式；直譯執行程式並產生結果 |
| [[#第 2 題｜Token 是什麼\|2]] | 詞法分析 | Scanner 把字元分組成有種類、可帶屬性的 token |
| [[#第 3 題｜Windows x86 的 C 程式能否在 Linux x86 執行\|3]] | 可攜性 | 分清原始碼與執行檔；相同 CPU 不保證 OS 相容 |
| [[#第 4 題｜取得可在 ARM 執行的 javac\|4]] | 交叉編譯 | 用 C 交叉編譯器編譯 javac 的 C 原始碼 |
| [[#第 5 題｜Grammatical error 與 Semantic error\|5]] | 語法與語意 | 語法看結構是否合法；語意看名稱、型別等規則是否合法 |

## 第 1 題｜Compiler 與 Interpreter

> [!question] 題目原文
> What is the difference between compiler and interpreter ?

> [!success] 英文標準答案
> A compiler translates a source program into a target program, which is then executed. An interpreter executes a source program or its intermediate representation using input data and directly produces results. The main distinction is translation into a target program versus execution of the program.

**中文解釋：**編譯器（compiler）的主要工作是把一種程式表示翻成另一種，產物仍然是「程式」；之後再執行這個產物。直譯器（interpreter）則根據程式的意思，配合輸入資料完成運算，產生執行結果。

| 比較項目 | Compiler | Interpreter |
|---|---|---|
| 課本中的主要輸入 | Source program | Source program／IR 與 input data |
| 主要產出 | Target program，例如組合語言、機器碼或 bytecode | 程式的執行結果 |
| 翻譯與執行的關係 | 課本模型分成 compilation、execution 兩階段 | 在執行系統中解讀並執行程式 |

> [!warning] 不要用這些絕對說法
> 不要寫「compiler 一定只輸出機器碼」或「interpreter 一定逐行執行、完全不做翻譯」。教材 p.014 已列出先轉成中介表示再執行的直譯策略。執行速度也不是兩者的定義。

教材對照：[[Compiler-Ch1-p011-p020#PPT p.012｜Compiler 與 Interpreter 的兩階段差別|Ch1 p.012]]、[[Compiler-Ch1-p011-p020#PPT p.013｜Fig 1.3 直譯器的資料流|p.013]]、[[Compiler-Ch1-p011-p020#PPT p.014｜直譯器的三種執行策略|p.014]]。延伸整理：[[Compiler - Compiler 與 Interpreter]]。

## 第 2 題｜Token 是什麼

> [!question] 題目原文
> Explain what a token is ?

> [!success] 英文標準答案
> A token is a basic lexical unit recognized by the scanner, such as a keyword, identifier, literal, operator, or punctuation symbol. A token has a kind and may carry an attribute, such as an identifier name or a literal value. The actual character sequence forming a token is called its lexeme.

**中文解釋：**詞法分析器（scanner／lexer）逐字元讀入原始碼，依詞法規則把字元分組，交給 parser 的單位就是 token。Token 不必只有一個字元，也不等於一行程式。

以 C 宣告片段 `int sum = 12;` 為例，會辨識出 **5 個 tokens**：

| 實際字串（lexeme） | Token kind | 可能攜帶的屬性 |
|---|---|---|
| `int` | Keyword（int） | 通常不需額外屬性，種類已能辨認它 |
| `sum` | Identifier | 名稱 `sum` 或符號表項目的參照 |
| `=` | Assignment operator | 通常不需額外屬性 |
| `12` | Integer literal | 數值 `12` |
| `;` | Punctuation／separator | 通常不需額外屬性 |

種類的實際名稱由編譯器實作決定。`sum` 是 lexeme，identifier 是它的 token kind；`12` 是兩個字元組成的一個 token。這段 C 中的空白用來分隔字串，不是交給 parser 的一般 token。

**Scanner 與 parser 的分工：**scanner 辨認「這些字元組成什麼 token」；parser 檢查「這串 tokens 能否依文法組成宣告、運算式或敘述」。

教材對照：[[Compiler-Ch1-p011-p020#PPT p.017｜Scanner 與 Parser|Ch1 p.017]]。延伸整理：[[Compiler - 編譯器組織]]。

## 第 3 題｜Windows x86 的 C 程式能否在 Linux x86 執行

> [!question] 題目原文
> A program written in C can be compile and execute in Win (x86) , is it also work in Linux (x86) ?

> [!success] 英文標準答案
> Not necessarily. A Windows x86 executable normally cannot run directly on Linux x86, because the executable format, operating-system interfaces, ABI, and runtime libraries may differ. The C source code can be recompiled and linked for Linux if it is portable and its dependencies are available. Windows-specific code must be ported first.

**中文解釋：**題目的「program」可能指原始碼，也可能指已編譯的執行檔。作答時把兩種情況分開，就不會把「C 可攜」誤寫成「同一個執行檔到處都能跑」。

| 帶到 Linux 的東西 | 能否使用 | 原因／需要做的事 |
|---|---|---|
| Windows 已編譯好的 x86 執行檔 | 一般不能直接當 Linux 原生程式執行 | 同為 x86 只解決部分 CPU 指令相容性；OS 介面、載入格式與相依環境仍可能不同 |
| 可攜的 C 原始碼 | 可以在符合條件時重新編譯、連結並執行 | 使用適合 Linux 的工具鏈與函式庫，且原始碼不依賴不相容的平台特性 |
| 使用 Windows 專屬 API 的 C 原始碼 | 不保證直接編譯成功 | 先替換、移植或提供對應的平台相依部分 |

**教材依據：**p.007 的 augmented machine code 除了 CPU 指令，還會用到作業系統與 runtime 提供的服務。因此，**CPU 架構相同是部分條件，不是整個執行環境相同。**

> [!note] 補充辨析：檔案格式
> Windows 原生執行檔通常使用 PE；Linux 原生執行檔通常使用 ELF。執行檔也需要符合應用程式二進位介面（ABI）等約定。這題討論原生執行；相容層或虛擬化是另外提供執行環境，不能據此推論二進位檔天然相容。
>
> 格式依據：[Microsoft PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)、[Linux man-pages：elf(5)](https://man7.org/linux/man-pages/man5/elf.5.html)。

教材對照：[[Compiler-Ch1-p001-p010#PPT p.006｜Pure machine code|Ch1 p.006]]、[[Compiler-Ch1-p001-p010#PPT p.007｜Augmented machine code|p.007]]。延伸整理：[[Compiler - 目標碼種類]]。

## 第 4 題｜取得可在 ARM 執行的 javac

> [!question] 題目原文
> We have a java compiler written in C on X86, how can we get a javac for arm device ?

> [!success] 英文標準答案
> Use a C cross-compiler that runs on x86 and generates code for the ARM device. Compile the C source of the Java compiler and link it with the appropriate ARM target libraries to produce an ARM executable of javac. Transfer it and its required runtime dependencies to the ARM device. Alternatively, build the same C source with a native C compiler on ARM.

**先依題目設定作答：**這是一支「用 C 寫的 Java compiler」，我們能取得它的 C 原始碼，目標是讓這支 compiler **在 ARM 上執行**。以下按一般 javac 的功能理解：把 Java 原始碼翻成 JVM bytecode，而非直接產生特定 CPU 的機器碼。

### 建置步驟

| 步驟 | 工具在哪裡執行 | 輸入 | 產出 |
|---|---|---|---|
| 1. 準備 C 交叉工具鏈 | x86 | 符合 ARM 裝置 CPU、OS、ABI 的工具鏈與相依函式庫 | 能在 x86 上將 C 編成 ARM 程式的工具 |
| 2. 編譯、連結 javac | x86 | **javac 的 C 原始碼**，必要時先移植平台相依部分 | 可在目標 ARM 裝置執行的 javac |
| 3. 部署 javac | ARM | 上一步的執行檔與必要 runtime 相依項 | ARM 上可用的 Java compiler |
| 4. 使用 javac | ARM | **Java 原始碼** | JVM bytecode／`.class` 檔 |

第 2 步是在「製作編譯器」；第 4 步才是「使用製作好的編譯器」。不要把兩者的輸入語言混在一起。

### 三個容易混淆的角色

| 項目 | 題目中的意義 |
|---|---|
| Implementation language | javac 本身用 **C** 寫成 |
| Host platform | javac 執行的平台，從 **x86 改成 ARM** |
| javac 的 source／target language | 輸入 **Java**，輸出 **JVM bytecode**；不因 host 改變就自動變成 ARM 機器碼 |

> [!warning] 關鍵辨析
> 要產生 ARM 機器碼的是用來**建置 javac 的 C 交叉編譯器**。不需要因 javac 要在 ARM 上執行，就把 javac 的 bytecode 後端改成 ARM 後端；也不能把 javac 的 C 原始碼交給只接受 Java 的 javac 編譯。

若 x86 上還沒有 ARM 的 C 交叉編譯器，可先建立或取得該工具鏈；教材 p.009 示範如何從已有的 C compiler 建立 cross-compiler。若 ARM 已有可用的 C compiler，直接在 ARM 編譯這份 C 原始碼也可達成目的。若只有 x86 執行檔、沒有 C 原始碼，則不能直接套用本題的重新編譯方法。

**補充辨析：**這個過程主要是交叉編譯（cross-compilation）與移植（porting），不是因為「正在編譯一支編譯器」就一定屬於自我編譯。對建置工具而言 ARM 是產碼目標；對產出的 javac 而言 ARM 是執行平台。[GNU GCC 的 build／host／target 定義](https://gcc.gnu.org/onlinedocs/gccint/Configure-Terms.html)可用來核對這個區別；Java → `.class` 的一般功能見 [Oracle javac 文件](https://docs.oracle.com/en/java/javase/26/docs/specs/man/javac.html)。此處沿用題目給定的 C 實作，不推論實際 JDK 的實作語言。

教材對照：[[Compiler-Ch1-p001-p010#PPT p.009｜Bootstrapping：改 code generator 再自我編譯|Ch1 p.009]]、[[Compiler-Ch1-p001-p010#PPT p.008｜Virtual machine code 與可攜性|p.008]]。延伸整理：[[Compiler - Bootstrapping]]。

## 第 5 題｜Grammatical error 與 Semantic error

> [!question] 題目原文
> Explain grammatical error and Semantic error

> [!success] 英文標準答案
> A grammatical error, also called a syntax error, violates the grammar of a language, such as a missing expression or an unmatched parenthesis. A semantic error violates the language's meaning rules even when the syntax is valid, such as using an undeclared identifier or calling a non-function object. The parser checks syntax, while the semantic analyzer checks static semantic constraints such as names and types.

**中文解釋：**語法（syntax）決定 tokens 如何排列成合法結構；語意（semantics）則檢查這個結構中的名稱、型別與操作是否有合法的意義。

以下是 **C 語法說明片段，刻意含錯，不是可執行範例**：

| 類別 | 說明片段 | 為什麼錯 | 典型檢查階段 |
|---|---|---|---|
| Grammatical／syntax error | `int x = ;` | `=` 後沒有 initializer，無法依 C 文法完成這個宣告 | Parser／syntax analysis |
| Static semantic error | 在函式內先宣告 `int x;`，再寫 `x();` | 函式呼叫的語法形式成立，但 `x` 是整數物件，不能當函式呼叫 | Semantic analyzer／type checker |

判斷順序是：先問「**文法能否組出合法結構？**」，再問「**結構中的名稱、型別與操作是否符合語言規則？**」。不同實作可能交錯執行檢查，表格描述的是概念上的分工。

> [!warning] Semantic error 不等於所有「答案算錯」
> 例如本來要算加總，卻寫成合法的乘法，可能只是程式邏輯錯誤（logic error）；語法與型別都正確，編譯器不一定能知道人的原意。本題編譯器前端的重點是可檢查的靜態語意規則，也不要把所有語意問題都說成只能在執行時發現。

教材對照：[[Compiler-Ch1-p011-p020#PPT p.017｜Scanner 與 Parser|Ch1 p.017]]、[[Compiler-Ch1-p011-p020#PPT p.018｜Type checker 與 decorated AST|p.018]]、[[Compiler-Ch1-p011-p020#PPT p.019｜Translator 把 AST 翻成 IR|p.019]]。延伸整理：[[Compiler - 編譯器組織]]。

## 考前五句速記

1. **Compiler produces a target program; interpreter executes a program and produces results.**
2. **Scanner groups characters into tokens; lexemes are the actual character sequences.**
3. **Portable source code does not imply a portable executable.**
4. **Cross-compile the C implementation of javac for an ARM host.**
5. **Syntax checks structure; static semantics checks names, types, and valid operations.**

[[Compiler - 知識庫首頁|回編譯器首頁]] · [[Compiler - 自測與詳解|20 題自測與詳解]] · [[Compiler - Chapter 1 導讀|Chapter 1 逐頁索引]]
