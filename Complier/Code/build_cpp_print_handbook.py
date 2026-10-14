#!/usr/bin/env python3
"""Build the complete A4 exam reference; reuse verified guides, never edit C++.
Run with /Volumes/D/graduate/presentation/.venv/bin/python.
Requires installed WeasyPrint and PyMuPDF.
"""
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile
import fitz
import handbook_specs as short
from cpp_handbook_examples import apply_variant, variants_for

ROOT = short.ROOT
REVIEW = ROOT / 'Complier/Review'
SLUG = 'Compiler-Ch1-Ch3-Print-Handbook'
TITLE = 'Compiler - Ch1-Ch3 考場列印手冊'
CHAPTER_TITLES = {
    1: ['編譯器定義與目標碼', 'Compiler／Interpreter 與編譯流程', 'Scanner C 實作與前後端',
        'Bootstrapping 與 T 圖', 'Optimizer：矩陣乘法', 'HW 4／8／11 與短答', '名詞速查與自測'],
    2: ['詞法、Token 與英文短答', '15 條 ac 文法、Predict 與 Parser', '推導、Parse Tree 與 AST',
        'Symbol Table、型別與錯誤', 'dc 產碼與 Stack Trace', 'HW 1／2／3 與 Scanner 擴充'],
    3: ['中英術語與階段速查', '六類題目解題步驟', 'CFG 與概念英文短答', 'AST 畫法與優先序',
        'RE、Identifier 與 Exponent', 'DFA／NFA 與 Scanner 行為', 'RE→NFA 與 (bc)*d',
        'NFA→DFA 子集構造', '(a|b)*abb 構造與追蹤', 'HW5(a) 完整表與短答'],
}


def esc(value):
    return re.sub(r'([ \t]+)(?=\n)', lambda m: ''.join('&#32;' if c == ' ' else '&#9;' for c in m[0]),
                  html.escape(str(value)))


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>'+esc(h)+'</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(
        '<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows) + '</tbody></table>'


def front_matter(locations):
    rows = [[esc(s['title']), '<code>'+esc(str(s['source_path'].relative_to(ROOT / 'Complier/Code')))
             +'</code>', str(locations.get(s['stem'], '待排版'))] for s in short.SPECS]
    quick='；'.join(f'{label} p.{locations.get(key,"待排版")}' for key,label in [
        ('versions','版本／模式'),('io','Linux／I/O'),('diagnosis','除錯'),('quiz','小考英文短答')])
    return '''<section class="front" id="index"><h1>Compiler Ch1–3｜考場列印手冊</h1>
<p class="basis">黑白 A4 完整版 · 2026-10-14 · 八份註解程式的選檔／改題指南＋Ch1–3 三章完整速查表。</p>
<p>程式直接帶原始 .cpp；紙本用來找題型、看推導、核對輸入輸出及修改位置。本冊保留八題的完整題意、
基本測例、手動追蹤、40 個修改範例的改前／改後與執行結果，不需展開才能閱讀。</p>
<h2>A｜先選題，再開檔</h2>''' + table(['題型', 'Code 檔案（相對 Complier/Code/）', 'PDF 頁'], rows) + '<p><b>快速入口：</b>'+esc(quick)+'</p>' + '''
<p class="line-note">相同檔名也可能有不同版本：02-遞迴下降運算式/expression.cpp 是短版求值；
12-運算式parser完整版/expression.cpp 是完整版本，預設 postfix。以本表完整相對路徑選檔。</p>
<h2>如何使用這本手冊</h2><ol>
<li>圈出輸出要求：合法判定、Token、Tree、AST、Postfix、DFA 表、目標碼，或執行結果。</li>
<li>先看該題輸入規格與範圍，再用配套 .in／.expected 跑一次原版。</li>
<li>按原檔行號找到修改區塊；每個變體獨立套用，多項合併後重新找位置。</li>
<li>以題目樣例確認輸出，再加空字串、邊界、非法字元、巢狀與長輸入等測例。</li>
<li>需要手算時查章節附錄；教材頁碼、教材解答與補充標示照原版保留。</li></ol>
<p>程式長行在紙本僅作視覺折行，修改時以 .cpp 原檔對照。PDF 最底端 Print handbook N / TOTAL 是本冊連續頁碼；附錄原有 01 / 06 等是各章自身編號。
此 HTML 僅含前半部程式指南，三章完整內容已合併於 PDF。</p></section>'''


def chapter_index(locations):
    rows = []
    for chapter, titles in CHAPTER_TITLES.items():
        for i, title in enumerate(titles, 1):
            rows.append([f'Ch{chapter} · 原第 {i} 頁', esc(title), str(locations.get(f'ch{chapter}-{i}', '待排版'))])
    return '''<section class="front" id="chapter-index"><h2>章節內容索引：三章完整保留</h2>
<p>現有教材伴讀速查表全部納入；來源 PPT／教材頁碼与補充辨析保留在各頁。
HTML parser 的歷屆線索未附原卷，因此程式題標明模擬規格。
FIRST／FOLLOW／LL(1) 保留為較低優先延伸，正式範圍尚未確認。</p>'''.replace('頁碼与','頁碼與') + table(
        ['原章節頁', '內容', '本冊 PDF 頁'], rows) + '''
<p class="line-note">教材已有疑義：Ch2 p.34 未附引用圖、p.43 解答與型別規則的差異、
Scanner 小數位數及科學記號規則的差異，均沿用既有辨析。不要把補充版本當成教材逐字原解。</p></section>'''


def program_choice():
    rows = [
        ['HTML 只判斷合法', '01-HTML標籤配對/html_check.cpp', '無參數；VALID／INVALID'],
        ['HTML Token／Tree／Text', '11-HTML-parser完整版/html_parser.cpp', '--tokens／--tree／--text；預設 --check'],
        ['每行算式求值／Postfix／AST', '02-遞迴下降運算式/expression.cpp', 'MODE：eval／postfix／ast'],
        ['深巢狀／迭代式算式 Parser', '12-運算式parser完整版/expression.cpp', '--postfix（預設）／--ast／--eval'],
        ['C-like Token、字串、註解', '03-Scanner與註解/lexer.cpp', 'keywords／ops 清單可改'],
        ['教材 ac Scanner／Parse Tree／AST', '14-ac作業完整版/ac_homework.cpp', '--tokens／--parse-tree／--ast／--typed-ast'],
        ['ac 型別檢查／產 dc', '06-ac產dc/ac_dc.cpp', '只產 dc，不直接印數值'],
        ['ac 完整型別／摺疊／產碼', '14-ac作業完整版/ac_homework.cpp', '--check／--dc（預設）；可加 --fold'],
        ['給 NFA，僅判字串', '04-NFA判定字串/nfa_check.cpp', '無參數；# 是 epsilon'],
        ['給 NFA，產 DFA 表／集合追蹤', '13-NFA轉DFA完整版/nfa_to_dfa.cpp', '--table／--trace；預設 --check'],
        ['固定 HW5(a)／(d) 字串辨識', '05-HW5固定DFA/hw5_check.cpp', 'HW5A=true／false'],
        ['固定 HW5 原 NFA→subset DFA', '15-HW5-NFA-DFA作業完整版/automata_homework.cpp', '5a --table／5d --table'],
        ['Stack 指令執行', '07-StackVM/stack_vm.cpp', 'PRINT 會 pop；不是 dc'],
        ['通用 FIRST／FOLLOW／LL(1)', '08-LL1/ll1.cpp', '預設表格；--check 判 Token 序列'],
    ]
    return '''<section class="front" id="versions"><h2>同一題型，輸出要求不同就換版本</h2>
<p>以下路徑相對 Complier/Code/。短版能辨識字串，不代表它也會畫樹或列 DFA 表。
評測若不傳命令列參數，將 main 的預設模式改成題目需要的模式。</p>''' + table(
        ['題目要求', '原檔路徑', '模式／關鍵設定'], [[esc(a),'<code>'+esc(b)+'</code>',esc(c)] for a,b,c in rows]) + '''
<h3>HTML parser 先判斷題意</h3><ul>
<li><b>合法判定：</b>START 入 stack，END 配 top，EOF 為空；數量相同不保證巢狀正確。</li>
<li><b>列 Token：</b>分辨 START／END／TEXT／COMMENT；是否檢查配對看題目要求。</li>
<li><b>輸出樹：</b>stack 的 top 是新節點的 parent，要保留 children 與文字次序。</li>
<li><b>抽文字：</b>是否保留空白、跳過 script／style、解碼 entity、替 br 換行？現有 --text 串接來源 TEXT，未做這些轉換。</li>
<li><b>邊界：</b>引號內 &gt; 不切 Tag；註解另找 --&gt;；void 不入 stack。
本模擬子集以 &lt;x/&gt; 自閉合，不等於完整瀏覽器的 HTML 規則。</li></ul>
<p class="basis">程式的 I/O 與支援範圍就是使用條件。mock 題型可用來改題，實際輸入輸出仍按考卷。</p></section>'''


def input_output_notes():
    rows = [
        ['案例界線', '首行 T／每行一案／整份 EOF 一案／sentinel', '跨行 HTML、ac 不可誤用每行一案。'],
        ['空白與空行', '空行是 epsilon 案例，還是忽略？空白是內容，還是分隔？', 'NFA／HW5 空行要測；expression 空白行目前是錯誤。'],
        ['State 編號', '0..n-1，還是 1..n？', '1 起算要同步改 valid 與容器大小。'],
        ['大小寫', 'Tag、Keyword、Instruction 是否区分大小寫？', '只改允許的字元；literal 不可整份轉小寫。'],
        ['數字', '整數除法／浮點；小數位數／有效位數；e／E', 'fixed+setprecision(2) 是兩位小數；不加 fixed 是有效位數。'],
        ['輸出格式', 'YES／NO、Case 編號、分隔空白、EOF Token', '不印提示字、debug、額外的樹或表。'],
        ['錯誤案例', '印指定文字、拒絕單案，還是終止全部？', '多份原檔暫存 stdout，任一案錯誤會取消整份輸出。'],
        ['複雜度', '長度、巢狀深度、State 上限、Time Limit', '短 expression 深度上限 256；subset DFA 可能指數膨脹。'],
    ]
    return '''<section class="front" id="io"><h2>讀題與跨平台輸入輸出：逐項核對</h2>''' + table(
        ['核對項目','先圈題目敘述','本程式的易錯處'],[[esc(x.replace('区分','區分')) for x in r] for r in rows]) + '''
<h3>Linux／DOMjudge 編譯與執行</h3><pre>g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror html_check.cpp -o main
./main &lt; input.txt &gt; actual.txt
diff -u expected.txt actual.txt</pre>
<p>每份都有自己的 main()，選一份編譯，不要把所有 .cpp 同時連結。
使用標準 C++17；不加入 windows.h、conio.h、getch、gets、system("pause") 或 system("cls")。</p>
<h3>getline 與 CRLF</h3><p>getline 吃掉 LF，但最後可能留下 CR。
以下為片段，未單獨編譯；每次讀到一行後去掉<b>末尾</b> CR，不刪內容中所有空白。</p>
<pre>while (getline(cin, line)) {
    if (!line.empty() &amp;&amp; line.back() == '\\r') line.pop_back();
    // 處理一個案例；是否略過空行依題意。
}</pre>
<p>混用 cin &gt;&gt; T 和 getline 時，先讀完 T 所在行的剩餘內容，再讀第一案。
若空行代表合法案例，不用 cin &gt;&gt; ws，它會吞掉空行。</p>
<h3>模式、輸出與原碼行號</h3><p>行號對應 2026-10-14 含中文註解的原檔，八份共 806 行。
每個變體從原版獨立套用；插入程式後後面行號會位移，可搜尋「改前」字串重新定位。
範例裡 stdout：空／stderr／exit 1 是手冊說明，不是要印在 stdout 的文字。</p></section>'''


def diagnosis_notes():
    rows = [
        ['編譯錯誤', '先看第一個診斷：include、括號、引號、型別、選檔。', '原檔通過後，一次改一個區塊；使用 C++17。'],
        ['輸出多了／少了行', '檢查 T 與 EOF 是否混用、空行是否被跳過。', 'stdout 只留指定內容；Case 編號按題意起算。'],
        ['小數答案不同', '有效位數、fixed、小數位數與整數除法。', 'ac 精確十進位字串不可先轉 double 再印。'],
        ['配對／巢狀失敗', 'stack top、引號、void 與 raw text。', '測交錯關閉與含 > 的屬性。'],
        ['運算順序不同', '優先序、結合性與 stack pop 順序。', '100-30-1=69；8/2/2=2；先 pop 右 b 再左 a。'],
        ['NFA 判定不同', '初始 closure；move 後再 closure；讀完才看 final。', '測空字串、epsilon cycle、final 有外出邊。'],
        ['Runtime Error', '空 stack／越界／未定義變數／零除／深遞迴。', '先測最小合法輸入，再測允許邊界。'],
        ['Time Limit', '迴圈是否推進游標，epsilon 是否重複進 todo。', 'AST 字串拼接可能 O(n²)；深／長算式換完整迭代版。'],
    ]
    return '''<section class="front" id="diagnosis"><h2>出錯時依症狀找位置</h2>''' + table(
        ['現象','先檢查','最小定位方式'],[[esc(x) for x in r] for r in rows]) + '''
<h3>提交前的測例清單</h3><ol>
<li>全部題目樣例，逐 byte 比對輸出；空白、最後換行與 Case 字樣都要對。</li>
<li>最短合法例、空輸入／空案例，以及同類的最短非法例。</li>
<li>一層與多層巢狀；不平衡、交錯關閉；引號與 escaped quote。</li>
<li>最高優先序、同級左結合、負 operand、零值與整數／浮點混合。</li>
<li>多案連續輸入；每案游標、stack、輸出與深度等狀態要重設。</li>
<li>LF 與 CRLF 各測一次；只有空白的尾端也按題目規格處理。</li></ol>
<p class="basis">八份原檔已通過 610 項 native 檢查與 sanitizer；40 個修改範例另有 82 次樣例檢查。
這次只編製文件，核對來源與報告的 SHA-256，沒有修改程式，也未新增 DOMjudge Accepted 證據。</p></section>'''


def quiz_reference():
    original=(REVIEW/'Compiler - 第一次小考題目與標準答案.md').read_text()
    sections=re.split(r'\n## 第 \d 題｜',original)[1:]
    comments=[
        'Compiler 產出目標程式；Interpreter 執行程式而產出結果。不要用「一定逐行」或「完全不翻譯」當定義。',
        'Token kind 是類別，lexeme 是來源字串，attribute 是附帶資訊；int sum = 12; 有五個來源 tokens。',
        '分清原始碼與二進位執行檔。相同 x86 不等於相同 OS、ABI 或函式庫；可攜原碼在 Linux 重新編譯。',
        '用在 x86 執行、產生 ARM 程式的 C 交叉編譯器，編譯 javac 的 C 原碼。產出的 javac 在 ARM 跑，仍將 Java 翻成 bytecode；不是把 javac 的 bytecode 後端改成 ARM。',
        'Parser 檢查排列是否符合文法；語意分析檢查宣告、名稱與型別。a=; 是缺 operand；使用未宣告變數是語意錯誤。',
    ]
    parts=['<section class="front" id="quiz"><h2>小考原題與可直接作答的英文</h2>',
           '<p>第一次五題原文由使用者提供；英文答案是既有筆記依教材整理的參考答案，非教師公布的逐字解答。第二次小考只提供題意，AST 的原程式未附。</p>']
    assert len(sections)==5
    for n,(section,comment) in enumerate(zip(sections,comments),1):
        heading=section.splitlines()[0]
        question=re.search(r'> \[!question\] 題目原文\n> (.+)',section)[1]
        answer=re.search(r'> \[!success\] 英文標準答案\n> (.+)',section)[1]
        parts.append(f'<div class="qa"><h3>Quiz 1 · {n}｜{esc(heading)}</h3><p><b>原題：</b>{esc(question)}</p><p class="basis">{esc(answer)}</p><p>{esc(comment)}</p></div>')
    parts += ['<div class="qa"><h3>Quiz 2 · 1｜Why use CFG?</h3><p><b>原題：</b>Why use CFG (context free grammer) instead of others ?</p>',
              '<p class="basis">A context-free grammar can describe recursive and nested syntax, such as balanced parentheses and nested statements, beyond the expressive power of regular expressions. Its productions also provide structure for parsing and AST construction. Semantic constraints, such as declarations and types, are checked separately.</p>',
              '<p>補充參考答案：RE 適合 Token 模式；CFG 可描述遞迴與任意巢狀結構，又能交給 Parser 建樹。CFG 不能取代名稱／型別檢查。更多例子見 Ch3 附錄。</p></div>',
              '<div class="qa"><h3>Quiz 2 · 2｜畫短程式的 AST</h3><p><b>原題：</b>wrtie down the AST for a short code</p>',
              '<p>原程式未提供；以下另編練習：<code>a+b*c</code> → <code>(+ a (* b c))</code>；<code>100-30-1</code> → <code>(- (- 100 30) 1)</code>。</p>',
              '<ol><li>辨認最外層低優先序的運算子，作為根。</li><li>依優先序、括號與結合性切左右子樹。</li><li>AST 保留有意義的運算／宣告／敘述，不保留文法輔助節點與括號 token。</li><li>若要求 decorated AST，查 symbol table，由葉往根標型別，必要時加 int2float。</li></ol></div></section>']
    return ''.join(parts)


def build_html(locations, evidence):
    source=(REVIEW/'Compiler-Ch1-Ch3-Cpp-Short.html').read_text()
    style=re.search(r'<style>(.*?)</style>',source,re.S)[1]
    articles=re.findall(r'<article id=".*?</article>',source,re.S)
    assert len(articles)==8
    for i,(spec,tested) in enumerate(zip(short.SPECS,evidence['results'])):
        assert spec['stem']==tested['stem']
        rows=[]
        for n,v in enumerate(tested['variants'],1):
            labels=['–'.join(map(str,e['lines'])) for e in v['edits']]
            rows.append([esc(v['title']),esc('；'.join(labels)),f'<a href="#{spec["stem"]}-change-{n}">修改範例 {n:02}（後文）</a>'])
        articles[i]=re.sub(r'<div class="table-wrap"><table>.*?</table></div>',
                           lambda m: table(['題目要求','原檔行號','完整改法'],rows),articles[i],flags=re.S)
        articles[i]=articles[i].replace('<details ', '<details open ')
        articles[i]=articles[i].replace('（點此展開）','').replace('在下方展開','在後文列出')
        articles[i]=articles[i].replace('改後（可直接貼）','改後（對照修改）')
        articles[i]=articles[i].replace('短改法見表格，詳細改前／改後與測例','表格列修改索引，詳細改前／改後與測例')
    overrides='''
@page{size:A4;margin:13mm 13mm 16mm}
body{background:#fff;color:#111;max-width:1100px;font-family:"PingFang TC","Noto Sans CJK TC",sans-serif}
.front{border-bottom:1px solid #aaa;margin-bottom:24px;padding-bottom:20px}details>div{display:block!important}
.qa{break-inside:avoid}summary{cursor:default}.basis{background:#f5f5f5}
@media print{body{font-size:10.5pt;line-height:1.6}article,.front{break-before:page;break-after:auto;border:0;padding:0;margin:0}
.front:first-child{break-before:auto}h1{font-size:21pt}h2{font-size:15pt}h3{font-size:11.5pt}
table{font-size:9pt;line-height:1.5}th,td{padding:6px 7px}thead{display:table-header-group}tr{break-inside:avoid}
p,li{orphans:3;widows:3}h2,h3,h4,summary{break-after:avoid}pre,code{font-size:8.5pt;line-height:1.5}
.sample,.changes{display:grid;grid-template-columns:1fr 1fr;gap:4mm;break-inside:avoid}
.sample>div,.changes>div{min-width:0}.edit{padding:8px 0;break-inside:avoid}summary{font-size:10.5pt}
.logic{grid-template-columns:minmax(0,1fr) 76mm}.line-note{font-size:9pt}.diagram-container{overflow:visible}a{color:#111}}
'''
    parts=['<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           '<title>Compiler Ch1–3｜完整考場列印指南</title><style>',style,overrides,'</style></head><body>',
           front_matter(locations),chapter_index(locations),program_choice(),input_output_notes(),diagnosis_notes(),quiz_reference(),
           *articles,'</body></html>']
    rendered='\n'.join(parts)+'\n'
    for before,after in [('#fafaf7','#fff'),('#f4f4f1','#f4f4f4'),('#f0f0ed','#f0f0f0')]:
        rendered=rendered.replace(before,after)
    path=REVIEW/(SLUG+'.html');path.write_text(rendered)
    return path


def compact(text):
    return re.sub(r'\s+','',text)


def grayscale_copy(source):
    """Known chapter PDFs use RGB page operators and hex text; preserve fonts exactly."""
    doc=fitz.open(source)
    number=rb'[-+]?(?:\d+\.?\d*|\.\d+)'
    rgb=re.compile(rb'(?<!\S)('+number+rb')\s+('+number+rb')\s+('+number+rb')\s+(rg|RG)\b')
    count=0
    for page in doc:
        assert not page.get_images() and not page.get_xobjects(), 'Unexpected image or Form color space'
        for xref in page.get_contents():
            stream=doc.xref_stream(xref)
            assert not re.search(rb'\b(?:sc|SC|scn|SCN|cs|CS|k|K)\b',stream), 'Unexpected color operator'
            assert not re.search(rb'\)\s*Tj',stream), 'Unexpected literal-text encoding'
            def gray(match):
                channels=[float(match[i]) for i in [1,2,3]]
                assert all(0<=x<=1 for x in channels)
                value=sum(x*w for x,w in zip(channels,[.299,.587,.114]))
                return f'{value:.6f} '.encode()+(b'g' if match[4]==b'rg' else b'G')
            updated,n=rgb.subn(gray,stream);count+=n
            assert not re.search(rb'\b(?:rg|RG)\b',updated)
            doc.update_stream(xref,updated)
    return doc,count


def locate_guide(doc):
    texts=[compact(p.get_text()) for p in doc]
    probes={'index':'CompilerCh1–3｜考場列印手冊','chapter-index':'章節內容索引：三章完整保留',
            'versions':'同一題型，輸出要求不同就換版本','io':'讀題與跨平台輸入輸出：逐項核對',
            'diagnosis':'出錯時依症狀找位置','quiz':'小考原題與可直接作答的英文'}
    probes.update({s['stem']:f'{i:02} '+s['title'] for i,s in enumerate(short.SPECS,1)})
    result={}
    for key,probe in probes.items():
        found=[i+1 for i,t in enumerate(texts) if compact(probe) in t[:180]]
        assert len(found)==1,(key,found)
        result[key]=found[0]
    for chapter,titles in CHAPTER_TITLES.items():
        start=len(doc)+sum(len(CHAPTER_TITLES[n]) for n in range(1,chapter))+1
        result.update({f'ch{chapter}-{i}':start+i-1 for i in range(1,len(titles)+1)})
    return result


def build_note(locations, pages):
    text=f'''---
title: "{TITLE}"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "八份註解原檔、40 個已驗證變體、Quiz 1／2 紀錄與 Ch1–3 完整速查表"
source_pages: "各章原有 PPT 頁碼保留在合併 PDF；本冊頁碼另列於下"
---

# {TITLE}

> [!abstract] 可直接列印的完整版本
> [[Complier/Review/{SLUG}.pdf|完整 A4 PDF]]：{pages} 頁，雙面約 {(pages+1)//2} 張；黑白、連續頁碼與書籤。[[Complier/Review/{SLUG}.html|前半部程式指南 HTML]] 可離線閱讀；三章完整速查表已合併於 PDF。

程式直接攜帶 `.cpp`；紙本提供選檔、完整題意、輸入輸出、解題追蹤、3 張流程圖、40 個修改範例的改前／改後及測例。八份原碼未修改，不在紙本重抄整份程式。附錄收錄 Ch1 7 頁、Ch2 6 頁、Ch3 10 頁，全部保留。

## 查找入口

| 內容 | 本冊 PDF 頁 |
|---|---:|
'''
    for key,label in [('index','選檔索引'),('chapter-index','三章內容索引'),('versions','完整版本與模式'),('io','跨平台與 I/O'),('diagnosis','除錯與提交前測例'),('quiz','小考原題與英文參考答案')]:
        text+=f'| {label} | {locations[key]} |\n'
    for s in short.SPECS:
        relative=s['source_path'].relative_to(ROOT)
        text+=f'| {s["title"]} · [[{relative}|原碼]] | {locations[s["stem"]]} |\n'
    text+='\n## 三章速查表頁碼\n\n| 原章節頁 | 主題 | 本冊 PDF 頁 |\n|---|---|---:|\n'
    for chapter,titles in CHAPTER_TITLES.items():
        for i,title in enumerate(titles,1):text+=f'| Ch{chapter} 原第 {i} 頁 | {title} | {locations[f"ch{chapter}-{i}"]} |\n'
    text+='''
## 來源與證據界線

- [[Compiler - Ch1-Ch3 考場短版 C++]]：八題輸入輸出與註解原檔。
- [[Compiler - 第一次小考題目與標準答案]]：五題原文與教材整理的參考答案，非教師逐字解答。
- [[Compiler - 第二次小考題目紀錄]]：CFG／AST 兩題，原 AST 程式未附，手冊算式例另標補充。
- Ch1／Ch2／Ch3 原速查 PDF 全頁纳入；保留教材頁碼、來源／補充分界與已知疑義，原檔不改。
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
'''.replace('全頁纳入','全頁納入')
    (REVIEW/(TITLE+'.md')).write_text(text.rstrip()+'\n')


def main():
    evidence=json.loads((REVIEW/'cpp-handbook-examples.json').read_text())
    assert evidence['variant_builds']==40 and evidence['checks']==82
    for spec,tested in zip(short.SPECS,evidence['results']):
        path=spec['source_path'];digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==tested['source_sha256']
        for recipe,saved in zip(variants_for(spec,short.HANDBOOK[spec['stem']]['edits']),tested['variants']):
            changed,edits=apply_variant(path.read_text(),recipe)
            assert edits==saved['edits'] and hashlib.sha256(changed.encode()).hexdigest()==saved['changed_sha256']
    with tempfile.TemporaryDirectory(prefix='compiler-print-') as scratch:
        scratch=Path(scratch);guide_path=scratch/'guide.pdf';locations={}
        for turn in range(3):
            source=build_html(locations,evidence)
            subprocess.run(['weasyprint',str(source),str(guide_path)],check=True,capture_output=True)
            guide=fitz.open(guide_path);current=locate_guide(guide)
            if current==locations:break
            locations=current;guide.close()
        else:raise ValueError('Page index did not stabilize')
        book=fitz.open();book.insert_pdf(guide);guide_pages=len(guide)
        sources=[]
        for chapter in [1,2,3]:
            source=ROOT/f'Complier/Lessons/Chapter {chapter}/Compiler-Ch{chapter}-cheatsheet.pdf'
            original=fitz.open(source);converted,color_ops=grayscale_copy(source)
            assert len(original)==len(converted)==len(CHAPTER_TITLES[chapter])
            for a,b in zip(original,converted):assert compact(a.get_text())==compact(b.get_text()),(chapter,a.number)
            start=len(book)+1;book.insert_pdf(converted)
            sources.append(dict(chapter=chapter,source=str(source.relative_to(ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                pages=len(original),start=start,end=len(book),grayscale_text_exact=True,grayscale_color_ops=color_ops))
            original.close();converted.close()
        toc=[]
        for key,label in [('index','選檔索引'),('chapter-index','章節內容索引'),('versions','版本與模式'),
                          ('io','跨平台與 I/O'),('diagnosis','除錯與測例'),('quiz','小考原題與英文參考答案')]:
            toc.append([1,label,locations[key]])
        for i,spec in enumerate(short.SPECS,1):toc.append([1,f'{i:02} {spec["title"]}',locations[spec['stem']]])
        for chapter,titles in CHAPTER_TITLES.items():
            toc.append([1,f'附錄 Ch{chapter} 完整速查表',locations[f'ch{chapter}-1']])
            for i,title in enumerate(titles,1):toc.append([2,f'{i:02} {title}',locations[f'ch{chapter}-{i}']])
        for i,page in enumerate(book,1):
            page.insert_text((25,page.rect.height-12),f'Print handbook {i} / {len(book)}',fontsize=8,fontname='helv',color=(0,0,0))
        book.set_toc(toc);book.set_metadata({'title':TITLE,'author':'Compiler course exam preparation','subject':'Ch1–3 full print reference and source modification guide'})
        target=REVIEW/(SLUG+'.pdf');book.save(target,garbage=4,deflate=True)
        book.close();book=fitz.open(target)
        build_note(locations,len(book))
        overflows=[]
        for page in book:
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        x0,y0,x1,y1=span['bbox']
                        if not (0<=x0<=x1<=page.rect.width+.5 and 0<=y0<=y1<=page.rect.height+.5):
                            overflows.append(dict(page=page.number+1,text=span['text'],bbox=span['bbox']))
        assert not overflows,overflows[:10]
        full_text='\n'.join(p.get_text() for p in book)
        assert '\ufffd' not in full_text
        flat=compact(full_text);snippets=0;samples=0
        for tested in evidence['results']:
            for variant in tested['variants']:
                for edit in variant['edits']:
                    for field in ['before','after']:
                        if edit[field]:assert compact(edit[field]) in flat,(tested['stem'],variant['title'],field)
                        snippets+=1
            for case in [tested['fixture'],*tested['samples'],*[v['example'] for v in tested['variants']]]:
                for field in ['input','output','stderr']:
                    if case[field]:assert compact(case[field]) in flat,(tested['stem'],field,case[field])
                samples+=1
        color_items=0
        for page in book:
            for drawing in page.get_drawings():
                for field in ['color','fill']:
                    color=drawing.get(field)
                    # MuPDF maps DeviceGray to RGB with tiny float rounding differences.
                    if color:assert max(color)-min(color)<.001,(page.number,field,color)
                    color_items+=bool(color)
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        c=span['color'];channels=[(c>>shift)&255 for shift in [16,8,0]]
                        assert max(channels)==min(channels),(page.number,span['text'],c)
        assert len(book.get_toc())==len(toc)
        assert all(abs(p.rect.width-595.28)<1 and abs(p.rect.height-841.89)<1 for p in book)
        report=dict(pages=len(book),duplex_sheets=(len(book)+1)//2,guide_pages=guide_pages,appendix_pages=23,
                    sources=sources,page_index=locations,bookmarks=len(toc),source_hashes_unchanged=True,
                    variant_patch_records_checked=40,existing_example_checks=82,diagrams=3,
                    chapter_text_roundtrips=23,code_snippets_present=snippets,sample_cases_present=samples,
                    grayscale_vector_items_checked=color_items,grayscale_all_text=True,
                    a4_all_pages=True,all_text_within_page=True,
                    no_replacement_characters=True,visual_review_pending=True,browser_ui_verified=False,
                    sha256={suffix:hashlib.sha256((REVIEW/(SLUG+suffix)).read_bytes()).hexdigest() for suffix in ['.pdf','.html']})
        (REVIEW/'cpp-print-handbook-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(f'Built {len(book)} A4 pages: {guide_pages} guide + 23 full chapter pages; {len(toc)} bookmarks.')
        guide.close();book.close()


if __name__=='__main__':
    main()
