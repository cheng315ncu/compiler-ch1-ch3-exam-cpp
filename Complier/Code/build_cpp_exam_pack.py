#!/usr/bin/env python3
"""Rebuild source-backed Obsidian notes, offline HTML, and A4 PDF. Requires PyMuPDF.
Run with /Volumes/D/graduate/presentation/.venv/bin/python from any directory.
Run check_cpp_exam.py separately before describing a changed program as verified.
"""
from pathlib import Path
import hashlib
import html
import json
import fitz

ROOT = Path(__file__).resolve().parents[2]
EXAM = ROOT / 'Complier/Code/exam'
NOTES = ROOT / 'Complier/Notes/Exam'
REVIEW = ROOT / 'Complier/Review'
NAME = 'Compiler - Ch1-Ch3 考試 C++ 程式集'

SPECS = [
    dict(stem='html_parser', title='HTML parser 與標籤配對', note='HTML parser 考試實作',
         basis='使用者表示歷屆出過 HTML parser；尚無原題全文。由 Ch1 scanner/parser、Ch2 CFG/AST 延伸。',
         source='[[Compiler-Ch1-p011-p020#PPT p.017｜Scanner 與 Parser]]；[[Compiler-Ch2-p001-p011#PPT p.006｜Context-free grammar 是一組產生式]]',
         pages='Ch1 p.17；Ch2 p.6–11、p.15；歷屆 HTML 題未附頁碼',
         mode='--check（預設）／--tokens／--tree／--text',
         contract='stdin 全部內容為一份 HTML fragment。預設輸出 VALID／INVALID，兩種判定均 exit 0。--tokens 只分詞；--tree 配對後輸出縮排樹；--text 配對後串接原始 TEXT，不自動加末尾換行。非 check 模式遇錯時 stdout 為空、stderr 診斷、exit 1。',
         algorithm='游標先辨認 START／END／TEXT／COMMENT／DOCTYPE；屬性引號內的 > 不結束標籤。arena 保存樹，stack 保存未關閉的 START；END 必須等於 stack 頂端；EOF 要回 document root。VOID／自閉合元素不 push。',
         limits='考試子集：ASCII 名稱轉小寫；boolean、單雙引號／無引號屬性；短 DOCTYPE html；13 個 void elements；script/style/title/textarea 讀到匹配結束標籤。一般元素必須顯式關閉；<custom/> 依本版類 XML 政策關閉。沒有瀏覽器錯誤修復、可省略 end tag、namespace/template 特殊 DOM、完整 script tokenizer、DTD、內容模型或 entity 解碼；註解以第一個 --> 結束；名稱限字母／_／: 開頭，後接字母數字／-／_／:。允許空 fragment／多個根及任意 DOCTYPE 位置。',
         pitfalls='<a><b></a></b> 即使數量相同也非法；<br> 不 push，</br> 拒絕。<p a=x/> 的 / 屬於值 x/，p 仍未關閉；<p a=x /> 才自閉合。--text 保留空白、CRLF、&amp; 和 script/style 來源文字，也不替 <br> 加換行，不等於畫面可見文字。',
         adapt='只檢查 tag 配對時保留 START/END 的 stack。若一行一案，把 main 的整份讀取改為外層 getline，但跨行 HTML 必須仍當一案。tag 數／深度在 parse 的 push/pop 更新，路徑由 nodes.children 走訪。VALID/INVALID 字樣只改 main。',
         example='<P>x</p><br> → VALID；<p title="a>b">x</p> → VALID；<a><b></a></b> → INVALID。',
         extra='HTML 分類、void 名單與屬性規則以 [WHATWG HTML syntax](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) 核對（2026-10-14）。標準 HTML 一般元素的 self-closing slash／可省略標籤有不同語意，本版明示為考試子集。'),
    dict(stem='expression', title='運算式 AST、後序式與求值', note='運算式 parser 考試實作',
         basis='Ch2 parser／AST 的常見延伸；括號、乘除、一元正負不在原 ac 文法。',
         source='[[Compiler-Ch2-p012-p022#PPT p.015｜Parsing 與 recursive descent]]；[[Compiler-Ch2-p023-p035#PPT p.028｜Fig 2.9 ac 程式的 AST]]', pages='Ch2 p.15、p.27–28；擴充運算子為補充',
         mode='--postfix（預設）／--ast／--eval',
         contract='每行一個完整運算式，無案例數。預設每行印空白分隔的 postfix；--ast 每行印一棵 S-expression；--eval 只接受常數，印 15 位有效數字。空白行非法，完全空的輸入表示零案例。任一案例失敗不發出任何暫存輸出，stderr 診斷、exit 1。',
         algorithm='Shunting-yard：value stack 保存 AST 索引，operator stack 保存待處理運算子。* / 高於 + -；二元同優先序用 >= 彈出以實現左結合；一元 neg/pos 從右向左結合。apply 建立父節點，arena 按子先父後排列，可直接輸出 postfix 與求值。',
         limits='支援 + - * /、括號、一元正負、小數與 e/E。ID 採 [A-Za-z_][A-Za-z_0-9]*，只供 AST/postfix；求值沒有變數環境。沒有 =、%、^、函式、隱含乘法。long double 拒絕零除／非有限值，但非精確有理數，顯示會捨入。',
         pitfalls='a+b*c 的根是 +；100-30-1 得 69；8/2/2 得 2；1+-2 合法，2(3) 非法。postfix neg 是一元指令，不等於二元 -。括號決定結構，不留 AST 節點。',
         adapt='只畫 AST 用 --ast；只求值把 main 預設改 --eval。求值變數要在 evaluate 葉節點加入符號表。新增 ^ 必須另定右結合及相對 unary minus 的優先序，不能只加入運算子字串。',
         example='a+b*c → a b c * +／(+ a (* b c))；(2+3)*4 → 20；-2*-3 → 6。',
         extra='文法：expr → term {(+|- ) term}；term → unary {(*|/) unary}；unary → (+|-) unary | primary；primary → number | ID | (expr)。採迴圈與 arena，長加法鏈不依賴深層函式遞迴。'),
    dict(stem='lexer', title='Scanner、註解與 longest match', note='Scanner 與註解考試實作',
         basis='Ch3 token／identifier／comment／string／longest match 的常見延伸。',
         source='[[Compiler-Ch3-p001-p010#PPT p.003｜Token type、lexeme 與 attribute]]；[[Compiler-Ch3-p011-p020#PPT p.015｜Identifier 的完整規則與底線限制]]；[[Compiler-Ch3-p011-p020#PPT p.016｜日期、註解、字串與 John 的 regex]]', pages='Ch3 p.3、p.15–16、p.20', mode='無參數',
         contract='stdin 整份來源到 EOF。每行 KIND "lexeme"，std::quoted 轉義引號／反斜線，末行 EOF。KW／ID／NUM／STRING／CHAR／OP／PUNCT；空白與 //、/* */ 不回傳 token。任何錯誤使 stdout 為空、stderr 診斷、exit 1。',
         algorithm='先略過空白／註解，再分類 ID、數字、引號 literal、運算子。ID 全部讀完才查 keyword set，所以 ifx 不拆成 if+x。三字元運算子先於二字元，再單字元；string 的 escaped quote 不結束 literal。',
         limits='補充 C-like lexer，非完整 C/C++。ID [A-Za-z_][A-Za-z_0-9]* 與教材的底線限制不同。NUM 允許 .5、10.、e/E；沒有 hex/octal 語意、suffix、raw string、preprocessor、行拼接。CHAR 只容一個 byte／簡單兩字元 escape，不解碼 hex／Unicode escape；STRING 保留詞素，不完整驗證 C escape 意義。block comment 不巢狀。',
         pitfalls='=／==，/／//／/*，keyword／longer ID 都要分清。exponent 以外正負號為 OP。字串內 /* 或 // 是文字。12abc 切成 NUM 12、ID abc 是否為合法敘述，還要由 parser 判斷。',
         adapt='keyword 改 keywords；多字元運算子改 ops 並維持長到短。若題目要求教材 ID，須在 ID 後驗證每個 _ 後至少一個 alnum、首字元為字母。要位置時集中於游標前進更新行欄，CRLF 算一次換行。',
         example='int sum=12; → 5 tokens；ifx==1 → ID、OP ==、NUM；x<<=2 的 <<= 是一個 OP。',
         extra='此版 floatx 為一個 ID；ac_homework 的單字母規格則為 floatdcl + id x。不要混用兩種語言契約。'),
    dict(stem='nfa_to_dfa', title='通用 epsilon-NFA → DFA', note='通用 NFA DFA 考試實作',
         basis='Ch3 子集構造直接延伸：由固定 HW5 圖改為讀 stdin 的任意轉移表。',
         source='[[Compiler-Ch3-p041-p050#PPT p.042｜Subset construction 的核心不變量]]；[[Compiler-Ch3-p041-p050#PPT p.046｜Revised Fig 3.23 演算法與九個 marker]]', pages='Ch3 p.42、p.46–50', mode='--check（預設）／--trace／--table',
         contract='n m start k；k 個 final states；alphabet 字串；m 行 from symbol to。states 0..n-1，# 代表 epsilon，不在 alphabet。其後每行完整待辨識字串，空行為 epsilon，預設 ACCEPT/REJECT。--trace 印每一步 NFA 集合；--table 只印完整 DFA，不處理後面案例。',
         algorithm='起點 closure({start})；對集合 S、每個 c 計算 closure(move(S,c))。新集合加入 worklist，以 map 去重；空集合也建為 sink。辨識同時計算 direct NFA 與 DFA，確認結果一致。',
         limits='n≤256、m≤65536、DFA≤4096 subsets，超過明確失敗。子集構造最壞會指數成長。alphabet 為非空、不重複、非空白的單 byte 字元字串，不含 #；純 epsilon 語言可用未使用的 dummy alphabet 字元。沒有 RE→Thompson NFA parser 或最小化。',
         pitfalls='closure 要到固定點，不止一層；每次 move 後再 closure；集合含任一 final 即接受。接受狀態仍有外出邊，不能提早停止。編號依 alphabet 發現順序，與教材 A/B 不必相同。',
         adapt='1 起算 states 可輸入時減 1；多起點改 initial closure 集合；只求辨識可刪 construct，直接保留 closure/move/direct simulation。需要 Unicode 字母表則改 symbol 表示，不能按 UTF-8 byte 當一個字元。',
         example='配套是 (bc)*d 的 NFA 改成 0 起算；d/bcd/bcbcd 接受，空字串/bc/bd/bcdd 拒絕。',
         extra='用 std::set 處理多於 32 個 states；每個 DFA state×alphabet 都列出，包括 sink。'),
    dict(stem='ll1', title='FIRST／FOLLOW／SELECT／LL(1)', note='Predict 與 LL1 考試實作',
         basis='Ch2 predict set 的補充工具；FIRST/FOLLOW 的正式名稱預告於 Ch4，列為較低優先的延伸。',
         source='[[Compiler - Predict set 與 recursive descent]]；[[Compiler-Ch2-p012-p022#PPT p.018｜Predict set：{id} 與 {print}]]；[[Compiler-Ch2-p023-p035#PPT p.023｜Stmts 的 predict set 怎麼算]]', pages='Ch2 p.18–24；FIRST/FOLLOW 正式名稱為補充', mode='--table（預設）／--check',
         contract='第一行 P（1..1000），接 P 行 LHS -> RHS，符號空白分隔，一行一個 alternative，# 單獨表示 epsilon。第一 LHS 為 start；所有 LHS 為 nonterminal，其他 RHS 為 terminal。$ 保留 EOF，不寫進 grammar。預設印 FIRST/FOLLOW/SELECT、所有非空 table cells、LL1 YES/NO；--check 讀後續每行 terminal tokens，補 $，印 ACCEPT/REJECT；空行測 epsilon。',
         algorithm='反覆聯集到 FIRST 固定，再求 start FOLLOW={$} 與各 suffix 的 FIRST／nullable 直到 FOLLOW 固定。SELECT=FIRST(RHS) 去 epsilon；nullable 時加 FOLLOW(LHS)。同格多規則為 CONFLICT；recognizer 用非遞迴 stack。',
         limits='不自動消除左遞迴／left factoring；非 LL(1) 不等於 ambiguous。--check 遇 conflict 報錯；最多 1,000,000 parsing steps。缺少 table cell 表示 error。RHS 名称是否為 nonterminal 由 LHS 集合決定，拼錯名稱會被當 terminal。',
         pitfalls='epsilon 不放 FOLLOW 或輸入；SELECT epsilon 分支加 FOLLOW；FOLLOW 看整個 suffix。ac 的 Prog → Dcls Stmts $ 應輸入 Prog → Dcls Stmts，本工具已補 EOF。# 不可與其他 RHS 並列，| 必須拆成多行。',
         adapt='只求 FIRST/FOLLOW 可刪 table／recognizer；要求全矩形表格則補印缺格為 error。解析來源 expression 先由 lexer 把實際數字映射為 num token，再送 --check。',
         example='num + num 接受；num + 拒絕；S → S a／S → b 會列 conflict。',
         extra='較低準備優先度：這是 predict 的通用延伸，不能宣稱 FIRST/FOLLOW 正式考試範圍已確認。'),
    dict(stem='stack_vm', title='Stack VM 與最小 interpreter', note='堆疊機 Interpreter 考試實作',
         basis='Ch1 compiler/interpreter、Ch2 dc stack code 的補充練習；instruction 名稱是本版定義，不是 dc。',
         source='[[Compiler-Ch1-p011-p020#PPT p.012｜Compiler 與 Interpreter 的兩階段差別]]；[[Compiler-Ch2-p036-p046#PPT p.036｜Code generation：由根往葉走訪 AST]]', pages='Ch1 p.12–14；Ch2 p.36–38', mode='無參數',
         contract='每行一指令到 EOF：PUSH number、LOAD name、STORE name、ADD/SUB/MUL/DIV/NEG、DUP、PRINT。空行略過。STORE pop 保存；LOAD 複製；PRINT pop 並印 15 位有效數字。EOF 可留剩餘 stack。錯誤時整份 PRINT 暫存不發出，stderr 診斷、exit 1。',
         algorithm='vector 是 stack、map 是 variables；二元先 pop 右 b，再左 a，做 a op b。NEG 只需一項；DUP 複製頂端。PUSH 必須完整轉換為有限 long double，零除／underflow／undefined LOAD 都拒絕。',
         limits='沒有跳躍、條件、函式、地址、型別分析、字串、註解或分號。非任意精度整數／dc。本版 PRINT 會 pop，與 GNU dc 的 p 不 pop 不同。名稱 [A-Za-z_][A-Za-z_0-9]*。',
         pitfalls='8 2 SUB 得 6，DIV 得 4；不可顛倒 pop 順序。LOAD 未定義值不能默認 0。輸出數值是 interpreter 執行結果，不是 compiler 產出的 target code。',
         adapt='postfix 數字→PUSH，+/-/*//→ADD/SUB/MUL/DIV，neg→NEG，pos→忽略，最後 PRINT。若仿 dc p，把 PRINT 的 pop 改成先檢查 stack 非空再讀 back。',
         example='配套算 x=100，再加 30+1 得 131；PUSH 2／DUP／MUL／NEG／PRINT 得 -4。',
         extra='演示 compiler → IR → interpreter 時，expression 的 --postfix 是 IR 入口；本 VM 不直接讀 C/C++ 或 ac 來源。'),
]

def build_notes():
    NOTES.mkdir(parents=True, exist_ok=True)
    for spec in SPECS:
        source = EXAM / (spec['stem'] + '.cpp')
        sample, answer = source.with_suffix('.in').read_text(), source.with_suffix('.expected').read_text()
        body = f'''---
title: "Compiler - {spec['note']}"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "{spec['source']}"
source_pages: "{spec['pages']}"
---

# Compiler - {spec['note']}

> [!abstract] 題型定位
> {spec['basis']} 以下為 **C++ 實作（補充）**；[[Complier/Code/exam/{spec['stem']}.cpp|單檔原碼]] · [[{NAME}|回程式集]]。

## 契約與模式

`{spec['mode']}`

{spec['contract']}

## 演算法與易錯點

{spec['algorithm']}

{spec['pitfalls']}

> [!note] 支援範圍
> {spec['limits']}

## 考場修改位置

{spec['adapt']}

{spec['extra']}

## 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/{spec['stem']}.cpp -o /tmp/{spec['stem']}
/tmp/{spec['stem']} < Complier/Code/exam/{spec['stem']}.in
```

輸入：

```text
{sample}```

預設輸出：

```text
{answer}```

其他測例：{spec['example']}

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

## 完整 C++17 程式

```cpp
{source.read_text()}```
'''
        (NOTES / ('Compiler - ' + spec['note'] + '.md')).write_text(body)
    rows = '\n'.join(f"| {i:02} | {s['title']} | [[Compiler - {s['note']}|說明與完整 code]] | `{s['stem']}.cpp` |" for i, s in enumerate(SPECS, 1))
    index = f'''---
title: "{NAME}"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement, source/user-provided]
chapter: [1, 2, 3]
source: "使用者提供 HTML parser 歷屆線索；Ch1–3 教材與既有作業筆記"
source_pages: "Ch1 p.12–19；Ch2 p.6–38、p.39–46；Ch3 p.3、p.15–20、p.42–60；延伸題非確認考題"
---

# {NAME}

> [!tip] 考場手寫優先用短版
> [[Compiler - Ch1-Ch3 考場短版 C++|八題考場短版]]：未加中文註解時五份為 839 → 400 行；保留原功能版本供 token／tree／DFA 表等題型。

> [!abstract] 八份完整程式，依題目選用
> 新增六份，保留原本 ac 與 HW5 NFA／DFA 兩份，均有 `main()`、只用標準 C++17、stdin/stdout、Linux 编譯指令與 CRLF 測例。程式採 ponytail：直接函式、標準容器、沒有外部套件或通用 framework。[[Complier/Review/Compiler-Ch1-Ch3-Cpp-Exam-Pack.pdf|A4 列印 PDF]] · [[Complier/Review/Compiler-Ch1-Ch3-Cpp-Exam-Pack.html|離線 HTML]] · [[Compiler - Ch1-Ch3 作業完整 C++17 實作|原作業兩份]]。

[[Compiler - 知識庫首頁|回首頁]]

## 題型證據與準備順序

**已知線索**：使用者在 2026-10-14 表示歷屆出過 HTML parser，但未附原題與 I/O。既有 [[Compiler - 第二次小考題目紀錄]] 有 CFG 與 AST 題；[[Compiler - 第一次小考題目與標準答案]] 有 token、compiler/interpreter、語法／語意及平台相容題。Ch2/Ch3 實際作業包含 scanner 擴充、parse tree／AST／產碼、NFA→DFA。

**下面是準備優先度，不是出題機率，也不是取得的考卷**：先 HTML 與 scanner，接運算式 AST 與原 ac 作業，再 NFA／DFA；stack VM 為產碼／直譯練習，FIRST/FOLLOW/LL(1) 為較低優先的補充（正式術語預告於 Ch4）。

| # | 題型 | 說明入口 | 單檔 |
|---|---|---|---|
{rows}
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

各 `.cpp` 都是**独立程式**，只編譯選中的一份，不能全部連結造成多個 main。試題若沒有命令列參數，就改 main 的預設模式／固定 HW5 題號；不要往 stdout 印提示、debug、額外 table 或 EOF，除非題目要求。測例數 T、空白行是否是案例、VALID/INVALID/YES/NO 字樣與精度，全部依原題改。

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
'''
    index = index.replace('Linux 编譯', 'Linux 編譯').replace('**独立程式**', '**獨立程式**')
    (REVIEW / (NAME + '.md')).write_text(index)

def pack_specs():
    result = [{**s, 'source_path': EXAM / (s['stem'] + '.cpp')} for s in SPECS]
    result += [dict(stem='ac_homework', title='ac 作業完整 compiler', source_path=ROOT/'Complier/Code/ch02/ac_homework.cpp',
                    contract='stdin 整份 ac；預設 dc 產碼，--tokens／--parse-tree／--ast／--typed-ast／--check；--fold 折疊整數加法。',
                    limits='原 ac：一個小寫字母 ID、宣告在敘述前、+ -，無括號／乘除／註解；帶 exponent 一律 float。exponent 絕對值≤10000。',
                    adapt='模式在 main；token 規格在 scan；int2float 在 check；產碼在 generate。完整說明見原作業筆記。'),
               dict(stem='automata_homework', title='固定 HW5(a)/(d) NFA／DFA', source_path=ROOT/'Complier/Code/ch03/automata_homework.cpp',
                    contract='5a 辨識 (a|(bc)*d)+；5d 辨識 (bc)*d；一行一案，空行為 epsilon。--table 印原 NFA 邊與完整 DFA。',
                    limits='只含兩題固定 NFA；32-bit 集合只供 states 1..12；需要任意轉移表時選 nfa_to_dfa。',
                    adapt='DOMjudge 不傳參數時，main 固定 5a／5d，再改題目要求的 ACCEPT/REJECT。')]
    return result

def build_html(specs, filename='Compiler-Ch1-Ch3-Cpp-Exam-Pack.html', intro=None):
    pieces = [f'<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>{NAME}</title>',
              '<style>@page{size:A4;margin:14mm}body{max-width:1000px;margin:30px auto;padding:0 24px;color:#151515;font:15px/1.6 sans-serif}h1{font-size:28px}h2{border-top:2px solid #222;padding-top:18px}a{color:#254363}pre{font:12px/1.5 monospace;white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #ddd;padding:14px}.source{counter-reset:line}.line{display:block;min-height:1.5em;padding-left:4em;position:relative}.line:before{counter-increment:line;content:counter(line);position:absolute;left:0;color:#888;user-select:none}@media print{body{margin:0;padding:0;font-size:10pt}h2{break-before:page}pre{font-size:8.6pt;line-height:1.35;border:0;padding:0}.line{break-inside:avoid}a{color:inherit}}</style>',
              f'<h1>{NAME}</h1><p>{html.escape(intro or "2026-10-14 · 8 份標準 C++17 完整程式 · HTML 由使用者歷屆線索優先準備，其他延伸非確認考題。Linux 交叉編譯成功，未驗證 Linux 實跑／DOMjudge Accepted。")}</p><ol>']
    for s in specs: pieces.append(f'<li><a href="#{s["stem"]}">{html.escape(s["title"])} — {s["source_path"].name}</a></li>')
    pieces.append('</ol><p>只编譯選中的一份。先對齊 I/O、案例分隔、預設模式、精度；PDF 目錄可查頁碼。</p>')
    for s in specs:
        pieces.append(f'<h2 id="{s["stem"]}">{html.escape(s["title"])}</h2>')
        for key, label in [('contract','契約'),('limits','範圍'),('adapt','考場改法')]: pieces.append(f'<p><b>{label}：</b>{html.escape(s[key])}</p>')
        for suffix, label in [('.in','輸入'),('.expected','預設輸出')]:
            pieces.append(f'<h3>{label}</h3><pre>{html.escape(s["source_path"].with_suffix(suffix).read_text())}</pre>')
        if s['stem']=='automata_homework': pieces.append('<p>這組 .in/.expected 需 5a 參數。</p>')
        pieces.append(f'<h3>完整 {s["source_path"].name}</h3><pre class="source" data-source="{s["stem"]}">')
        pieces.append(''.join('<span class="line">'+html.escape(line)+'</span>' for line in s['source_path'].read_text().splitlines()))
        pieces.append('</pre>')
    pieces.append('</html>')
    (REVIEW/filename).write_text('\n'.join(pieces).replace('只编譯','只編譯'))

def build_pdf(specs, filename='Compiler-Ch1-Ch3-Cpp-Exam-Pack.pdf', intro=None, checklist=None):
    doc = fitz.open()
    width, height = fitz.paper_size('a4')
    page = None; y = 0; chapter = ''
    records = []
    def mixed_runs(text, mono=False):
        runs=[]
        for c in text:
            font=('cour' if mono else 'helv') if ord(c)<128 else 'china-ts'
            if runs and runs[-1][0]==font: runs[-1]=(font,runs[-1][1]+c)
            else: runs.append((font,c))
        return runs
    def mixed_width(text,size,mono=False):
        return sum(fitz.get_text_length(run,fontname=font,fontsize=size) for font,run in mixed_runs(text,mono))
    def mixed_text(target,x,baseline,text,size,mono=False):
        for font,run in mixed_runs(text,mono):
            target.insert_text((x,baseline),run,fontsize=size,fontname=font)
            x+=fitz.get_text_length(run,fontname=font,fontsize=size)
    def new_page():
        nonlocal page, y
        page = doc.new_page(width=width,height=height); y = 60
        page.insert_text((30,28), 'Compiler Ch1-Ch3 | C++17 exam reference',fontsize=9,fontname='helv')
        mixed_text(page,30,43,chapter,9)
    def line(text, font='china-ts', size=9.3, leading=14, number=None):
        nonlocal y
        if y + leading > height - 38: new_page()
        x = 57 if font=='cour' else 30
        if number is not None: page.insert_text((30,y),str(number),fontsize=7,fontname='cour',color=(.45,.45,.45))
        if font in ('china-ts','cour'): mixed_text(page,x,y,text,size,mono=font=='cour')
        else: page.insert_text((x,y),text,fontsize=size,fontname=font)
        y += leading
    def paragraph(text, font='china-ts', size=9.3, leading=14):
        current = ''
        available = width - (57 if font=='cour' else 30) - 30
        for c in text:
            measured=mixed_width(current+c,size,mono=font=='cour') if font in ('china-ts','cour') else fitz.get_text_length(current+c,fontname=font,fontsize=size)
            if measured>available:
                line(current,font,size,leading); current=''
            current += c
        line(current,font,size,leading)
    chapter = '使用方式與目錄'; new_page()
    paragraph(NAME, size=16, leading=25)
    paragraph('2026-10-14｜完整八份 C++17｜只用標準函式庫')
    paragraph('HTML 為使用者歷屆線索；其他為課程／作業延伸，非出題機率。')
    paragraph(intro or '151 項新程式檢查＋sanitizer；Linux 編譯成功，尚未 Linux 實跑。')
    toc_y = y+12
    chapter = '考場先確認'; new_page()
    for text in checklist or ['只編譯選中的一個 .cpp；每份各有 main，不能一起連結。',
                 '先讀案例數 T、EOF／空白行分隔規則、輸出字樣與精度。',
                 'judge 不傳命令列參數時，直接改 main 的預設 mode。',
                 'HTML：一份可能跨行；引號內 > 不是 tag 結尾；END 要配 stack top。',
                 'HTML：本版顯式配對，不含瀏覽器 optional end tag／錯誤修復／entity 解碼。',
                 'Scanner：先長運算子，再短；完整 ID 後查 keyword；註解不處理字串內符號。',
                 'AST：* / 高於 + -；二元同級左結合；unary neg 與二元 minus 分開。',
                 'ac：原作業仍是單字母 ID、+ -、先宣告，目標是 dc 而非數值。',
                 'NFA：closure 到固定點；move 後 closure；接受後仍讀完整字串。',
                 'LL(1)：epsilon 分支加 FOLLOW；衝突不能偷偷選第一條；此工具為補充。',
                 'VM：先 pop 右 b、再左 a，做 a op b；本版 PRINT 會 pop。',
                 '程式長行在 PDF 視覺換行，行號只印原行首；提交以原 .cpp 為準。',
                 '完整契約與測例請看 Obsidian 的程式集及各題筆記。']:
        paragraph(text); y += 5
    for i, s in enumerate(specs,1):
        chapter=f'{i:02} | {s["title"]} | {s["source_path"].name}'
        new_page(); start_page=len(doc)
        for key,label in [('contract','契約'),('limits','範圍'),('adapt','改法')]: paragraph(label+'：'+s[key]); y+=5
        paragraph('Compile: g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror '+s['source_path'].name,font='cour',size=8.6,leading=12)
        if s['stem']=='automata_homework': paragraph('下列配套範例使用參數 5a。')
        for suffix,label in [('.in','輸入'),('.expected','預設輸出')]:
            paragraph(label+'：')
            for raw in s['source_path'].with_suffix(suffix).read_text().splitlines(): paragraph(raw,font='cour',size=8.6,leading=11.5)
            y+=5
        paragraph('完整程式：'+s['source_path'].name); y+=4
        count = 0
        source_start = None
        for count, raw in enumerate(s['source_path'].read_text().splitlines(),1):
            chunks=[]; current=''
            for c in raw:
                if mixed_width(current+c,8.6,mono=True)>width-57-30:
                    chunks.append(current); current=''
                current+=c
            chunks.append(current)
            for part, chunk in enumerate(chunks):
                line(chunk,font='cour',size=8.6,leading=11.7,number=count if part==0 else None)
                if source_start is None: source_start=(len(doc),y-11.7)
        records.append({'stem':s['stem'],'start_page':start_page,'end_page':len(doc),'source_start_page':source_start[0],'source_start_y':source_start[1],'source_lines':count,'source_sha256':hashlib.sha256(s['source_path'].read_bytes()).hexdigest()})
    cover = doc[0]  # Adding pages invalidates earlier PyMuPDF Page handles.
    for i,(s,r) in enumerate(zip(specs,records)):
        mixed_text(cover,30,toc_y+i*26,f'{i+1:02}  {s["title"]}  …… p.{r["start_page"]}–{r["end_page"]}',10)
    doc.set_toc([[1,s['title'],r['start_page']] for s,r in zip(specs,records)])
    for i,p in enumerate(doc): p.insert_text((30,height-20),f'{i+1} / {len(doc)}',fontsize=8,fontname='helv')
    doc.set_metadata({'title':NAME,'author':'Compiler course reference','subject':'Complete C++17 programs; exam subsets explicitly documented'})
    path=REVIEW/filename; doc.save(path,garbage=4,deflate=True)
    print('PDF',len(doc),'A4 pages;',len(records),'complete sources')
    return {'pdf_pages':len(doc),'pdf_source_records':records}

if __name__ == '__main__':
    build_notes(); specs=pack_specs(); build_html(specs)
    metadata=build_pdf(specs)
    (REVIEW/'cpp-exam-pack-layout.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
