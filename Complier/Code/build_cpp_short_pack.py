#!/usr/bin/env python3
"""Build the source lookup guide; generate the optional source PDF with --pdf."""
import hashlib
import json
import build_cpp_exam_pack as pack
ROOT = pack.ROOT
SHORT = ROOT / "Complier/Code/exam/short"
NAME = "Compiler - Ch1-Ch3 考場短版 C++"
INTRO = "610 項檢查＋sanitizer；Linux 交叉編譯成功，Linux 實跑／DOMjudge Accepted 未驗證。"
SPECS = [
 dict(stem="html_check", title="HTML 標籤配對", source_path=SHORT/"html_check.cpp",
      contract="整份 stdin 為一個 HTML fragment；只印 VALID／INVALID，兩種判定皆 exit 0。stack 保存未關閉標籤，END 必須配 top；空輸入合法。",
      limits="保留原版 check 的屬性驗證、註解、DOCTYPE html、13 個 void 與 script/style/textarea/title raw text；名稱不分 ASCII 大小寫。明示關閉，普通元素 <x/> 採本題子集自閉合；非 browser DOM，不省略 end tag、不解碼 entity。",
      adapt="改 main 的輸出字樣；一行一案才改成 getline 外層。配對時累積 stack.size() 可求最大深度。若要 token／tree／text，使用原 html_parser.cpp 的相應模式。"),
 dict(stem="expression", title="遞迴下降運算式", source_path=SHORT/"expression.cpp",
      contract="一行一式；常數 MODE=eval（預設求值）、postfix 或 ast，修改這一行選題。+ - * /、括號、一元正負、十進位及 e/E；二元左結合。錯誤 stderr、exit 1，整份 stdout 暫存。",
      limits="eval 使用 long double、15 位有效數字，拒絕零除／非有限數／變數；ID 僅用於 postfix/ast。嵌套括號與一元鏈深度 <=256；AST 字串拼接最壞 O(n²)。長加減鏈用 while，不占深遞迴。",
      adapt="只求值可刪 postfix 與 ast 相關行；只畫 AST 可刪 number 的計算。若嵌套超過 256 或 AST 很長，原版 iterative expression.cpp 保留相同運算規則。"),
 dict(stem="lexer", title="Scanner：沿用現有短程式", source_path=ROOT/"Complier/Code/exam/lexer.cpp",
      contract="整份 stdin；印 KW/ID/NUM/STRING/CHAR/OP/PUNCT 與帶引號 lexeme，最後 EOF。忽略 // 與非巢狀 /* */。長運算子先比，完整 ID 再查 keyword。",
      limits="C-like 補充，非完整 C/C++；ID [A-Za-z_][A-Za-z_0-9]*；number 支援 .5、10.、e/E；CHAR 單 byte 或單 escape。",
      adapt="keyword 改 keywords；運算子改 ops；輸出改最後兩行。沿用原本順序掃描的邏輯，追加中文註解；不新增架構。"),
 dict(stem="nfa_check", title="NFA 直接判定字串", source_path=SHORT/"nfa_check.cpp",
      contract="n m start k；k 個接受 state；alphabet；m 條 from symbol to；其後一行一字串。state=0..n-1，#=epsilon，空行=空字串。印 ACCEPT／REJECT。",
      limits="n<=256，m<=65536；只做 closure(move(states,c)) 的 NFA 模擬，不產 DFA 表。不再因完整 DFA 超過 4096 states 而失敗。",
      adapt="字串辨識就用這份；若題目明確要求 subset construction／DFA 表／集合 trace，改用原 nfa_to_dfa.cpp，勿用字串判定代替表格作答。"),
 dict(stem="hw5_check", title="HW5 固定四狀態 DFA", source_path=SHORT/"hw5_check.cpp",
      contract="一行一字串，空行拒絕；HW5A=true 辨識 (a|(bc)*d)+，改 false 辨識 (bc)*d。印 ACCEPT／REJECT，不需命令列參數。",
      limits="只有固定兩個語言；0=start、1=剛讀 b、2=剛讀 bc、3=accept、-1=dead。這是精簡的辨識 DFA，不是投影片子集構造的原始 state sets。",
      adapt="HW5A 常數選題；改 ACCEPT/REJECT 字樣。若要求原 NFA 邊、epsilon closure 或 subset DFA 表，用 automata_homework.cpp 5a/5d --table。"),
 dict(stem="ac_dc", title="ac 邊解析邊產 dc", source_path=SHORT/"ac_dc.cpp",
      contract="整份 stdin 為 ac 程式；f/float、i/int 宣告在前，p 印變數，單字母 ID，加減左結合。保留重複／未宣告／float→int 檢查，正確時只印 dc code。",
      limits="支援小數與 lowercase e signed exponent；帶 . 或 e 就是 float。精確移動小數點，exponent 絕對值及 mantissa 長度 <=10000；無括號／乘除／註解。print 使用 l<變數>/p/si 形式。",
      adapt="int→float 時印 5 k；assign 後印 0 k。value 直接回 leaf code 與型別，主迴圈直接產碼，沒有樹走訪。題目要求 parse tree／AST／常數摺疊時，用原 ac_homework.cpp 的相應模式。"),
 dict(stem="stack_vm", title="Stack VM：沿用現有短程式", source_path=ROOT/"Complier/Code/exam/stack_vm.cpp",
      contract="一行一指令：PUSH、LOAD、STORE、ADD/SUB/MUL/DIV、NEG、DUP、PRINT；PRINT/STORE pop。long double，15 位有效數字；錯誤 stderr、exit 1，暫存 stdout。",
      limits="無條件／跳躍／函式；只做 stack interpreter，不是 dc。LOAD 未定義、underflow、div0 拒絕。",
      adapt="先 pop 右 b，再左 a，算 a op b；PRINT 若題目要求不 pop，就改讀 stack.back()。沿用原本直接執行流程，追加中文註解。"),
 dict(stem="ll1", title="LL(1)：較低優先補充", source_path=ROOT/"Complier/Code/exam/ll1.cpp",
      contract="P 條產生式，一行 A -> X Y，# 單獨為 epsilon；預設印 FIRST/FOLLOW/SELECT、table 與 conflict。--check 判定其後每行 token sequence。",
      limits="通用表格功能需要固定點、nullable suffix 與衝突檢查；保留原本固定點演算法，追加中文註解。P<=1000；parse<=1000000 步；不消除左遞迴或做 left factoring。正式 FIRST/FOLLOW 範圍未確認。",
      adapt="若已知題目固定文法，只寫對應 recursive descent 更好記；若要求任意 CFG 的 FIRST/FOLLOW，保留本版以免刪掉 nullable 的必要處理。DOMjudge 不傳 args 時固定 main 的 mode。"),
]
CHECKLIST = [
 "直接攜帶 .cpp 原檔；依題目選一份編譯，每份獨立 main，不能一起連結。",
 "只字串判定：HTML 用 html_check，NFA 用 nfa_check，固定 HW5 用 hw5_check。",
 "輸出 AST/postfix：expression 第一行 MODE 改 ast/postfix；eval 的變數不合法。",
 "ac 產碼：ac_dc 保留型別檢查與精確 decimal；要樹／摺疊改用原完整版本。",
 "Scanner、VM、LL(1) 沿用直接流程；中文註解增加閱讀長度，不增加執行步驟。",
 "HTML 引號內 > 不結束 tag；<p a=x/> 的 slash 屬於 value，p 仍未關閉。",
 "HW5(a) accept state 可接下一個 a/b/d；HW5(d) accept 後再讀字元就拒絕。",
 "案例數 T、EOF、空行、大小寫、輸出字樣、精度一律對齊原題。沒有原題就不能保證 Accepted。",
 "所有程式只用標準 C++17。getline 字串題移除尾端 CR；整份 source 把 CR 視為空白。",
 "直接修改 .cpp 並提交；完整版本仍保留 token/tree/text/DFA table 功能。",
]

# HTML only: four fields per problem; source lines are resolved at build time.
HANDBOOK = {
 'html_check': dict(
  question='讀入一份可跨行 HTML，判斷標籤是否正確巢狀，輸出 VALID / INVALID。',
  logic='START 入 stack；END 必須匹配頂端才 pop；EOF 時 stack 必須空。void 與自閉合標籤不入 stack；屬性引號內的 > 不結束標籤，註解與 raw text 另行跳過。',
  flow=[('讀取標籤', 'START / END'), ('入棧或配對出棧', 'push / top / pop'), ('檢查未關閉標籤', 'EOF: stack.empty()')],
  edits=[
   ('輸出 YES / NO', ['cout << (valid ?'], '將 "VALID\\n" / "INVALID\\n" 改成 "YES\\n" / "NO\\n"。'),
   ('一行一案', ['s.assign(istreambuf_iterator', 'cout << (valid ?'], '以此區塊替換這段；跨行一案時保留原版：\nwhile (getline(cin, s)) {\n    p = 0; bool valid = false;\n    try { valid = check(); } catch (const runtime_error&) {}\n    cout << (valid ? "VALID\\n" : "INVALID\\n");\n}\nif (cin.bad()) return 1;'),
   ('XML 式：br 等也須配對關閉', ['const set<string> empty', '"link","meta"'], '將兩行名單改成 const set<string> empty{};；<br/> 仍自閉合。'),
   ('求最大巢狀深度', ['size_t p = 0;', 'stack.push_back(tag);', 'cout << (valid ?'], '在 p 宣告後加 size_t deepest = 0;\npush 後加 if (stack.size() > deepest) deepest = stack.size();\n輸出行改為 if (valid) cout << deepest << "\\n"; else cout << "INVALID\\n";\n若同時改一行一案，每案開頭還需 deepest = 0;。'),
  ]),
 'expression': dict(
  question='每行一個運算式，求值、轉 postfix 或輸出 AST；含括號、+ - * / 與一元正負。',
  logic='expr 迴圈處理 + -，呼叫 term；term 迴圈處理 * /，呼叫 unary。unary 讀數字、變數或括號；同級二元由左往右合併。eval 不接受變數；括號／一元鏈嵌套上限 256。',
  flow=[('處理加減：低優先序', 'expr -> term'), ('處理乘除：高優先序', 'term -> unary'), ('處理一元、括號與葉節點', 'unary -> expr / value')],
  edits=[
   ('只輸出 postfix', ['const string MODE ='], 'const string MODE = "postfix";'),
   ('只輸出 AST', ['const string MODE ='], 'const string MODE = "ast";'),
   ('固定小數點後 2 位', ['ostringstream out; out << setprecision'], 'ostringstream out; out << fixed << setprecision(2);'),
   ('所有模式均禁止變數', ['bool id = letter(c);'], '在這行後插入 if (id) fail();；eval 原本已禁止。'),
  ]),
 'lexer': dict(
  question='讀入類 C 程式，跳過空白／註解，列出 token 類型及 lexeme。',
  logic='依序判定空白、註解、ID、number、literal、operator。讀完整 ID 才查 keyword；多字元 operator 由長到短比對；字串內的註解符號不當成註解。',
  edits=[
   ('增加保留字', ['const std::set<std::string> keywords'], '在 keywords 名單加入 "switch", "case" 等題目指定字。'),
   ('增加多字元運算子', ['const std::vector<std::string> ops'], '在 ops 名單加入所需運算子；維持較長字串先列。這裡只分詞，不增加 parser 的運算規則。'),
   ('lexeme 不加引號', ['output << kind <<'], 'output << kind << \' \' << s.substr(start, p - start) << \'\\n\';'),
   ('不要印 EOF', ['output << "EOF'], '刪除這一行。'),
  ]),
 'nfa_check': dict(
  question='讀 NFA 轉移表及多行字串，判定每個完整字串是否被接受。',
  logic='初始集合是 start 的 ε-closure。每讀一字元，先 move 再 ε-closure；讀完才檢查是否含接受狀態。空行代表空字串。這份只判定字串；要 DFA 表須用 nfa_to_dfa.cpp。',
  flow=[('建立初始可達集合', 'closure({start})'), ('逐字更新狀態集合', 'closure(move(states,c))'), ('檢查接受狀態交集', 'EOF: states & finals')],
  edits=[
   ('state 編號從 1 開始', ['auto valid = [n]', 'edges.resize(n);'], 'valid 行改成 auto valid = [n](int state) { return state >= 1 && state <= n; };\nresize 行改成 edges.resize(n + 1);；輸入 start、finals、edges 皆維持 1-based。'),
   ('epsilon 用 @', ["edges[from]['#']", "alphabet.find('#')", '(symbol != "#"'], '這三行的 \'#\' 與 "#" 改成 \'@\' 與 "@"。'),
   ('輸出 YES / NO', ['cout << (accepted ?'], '將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。'),
  ]),
 'hw5_check': dict(
  question='HW5(a) 辨識 (a|(bc)*d)+，或 HW5(d) 辨識 (bc)*d；每行一個字串。',
  logic='state 0 起始、1 剛讀 b、2 剛讀 bc、3 接受、-1 死狀態。1 只能接 c；2 只能接 b 或 d；HW5(a) 的 3 可接下一組，HW5(d) 的 3 再讀字元就拒絕。',
  edits=[
   ('改解 HW5(d)', ['const bool HW5A ='], 'const bool HW5A = false;'),
   ('輸出 YES / NO', ['cout << (state == 3 ?'], '將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。'),
   ('HW5(a) 外層 + 改成 *', ['cout << (state == 3 ?'], 'HW5A 保持 true；輸出條件 state == 3 改成 (state == 3 || word.empty())，使空字串也接受。'),
  ]),
 'ac_dc': dict(
  question='將 ac 程式翻譯成 dc code，檢查宣告與型別；含 i/f、int/float、加減與 p。',
  logic='scan 成 token；宣告填 types；value 回傳 leaf code 與是否 float。解析加減時直接輸出 postfix；int→float 印 5 k，assign 印 s<變數>，print 印 l<變數>/p/si。要樹或常數摺疊，用 ac_homework.cpp。',
  edits=[
   ('只允許 i / f 短宣告', ["if (kind == 'f' &&", "else if (kind == 'i' &&", "else if ((kind >= 'a'"], '刪除 float / int 完整字的兩行判定；第三行開頭 else if 改成 if。'),
   ('科學記號也接受 E', ["if (j < s.size() && s[j] == 'e')", "size_t e = text.find('e');", 'text.find_first_of(".e")'], '條件改成 if (j < s.size() && (s[j] == \'e\' || s[j] == \'E\')) {\nfind 改成 text.find_first_of("eE");\nfind_first_of(".e") 改成 find_first_of(".eE")。'),
   ('浮點運算 scale 改成 10', ['if (!left.second && right.second)', 'if (left.second && !right.second)', 'if (target_float && !left.second)'], '三行的 "5 k\\n" 都改成 "10 k\\n"；assignment 的 "0 k\\n" 保留。'),
  ]),
 'stack_vm': dict(
  question='執行 PUSH/LOAD/STORE、四則運算、NEG/DUP/PRINT 組成的堆疊指令。',
  logic='vector 當 stack，map 存變數。二元先 pop 右 b，再 pop 左 a，算 a op b；STORE 與 PRINT 都 pop。空 stack、未定義 LOAD、零除均報錯。',
  edits=[
   ('PRINT 保留 stack 頂端', ['} else if (op == "PRINT")'], '} else if (op == "PRINT") {\n    if (stack.empty()) throw std::runtime_error("stack underflow");\n    const auto value = stack.back();\n    output << (value == 0 ? 0 : value) << \'\\n\';\n}'),
   ('固定小數點後 2 位', ['output << std::setprecision'], '把 output << std::setprecision(15); 改成 output << std::fixed << std::setprecision(2);。'),
   ('PRINT 指令改名為 OUT', ['} else if (op == "PRINT")'], '把該行 op == "PRINT" 改成 op == "OUT"。'),
  ]),
 'll1': dict(
  question='計算任意 CFG 的 FIRST/FOLLOW/SELECT 與 LL(1) 表，或用表判定 token 序列（延伸題）。',
  logic='FIRST 與 FOLLOW 反覆合併至固定點；nullable RHS 將 FOLLOW 加進 SELECT。用 SELECT 填表，同格多條規則就是 conflict；解析用 stack 與 lookahead 查表。# 單獨代表 ε。',
  edits=[
   ('judge 不傳參數，只判定字串', ['const std::string mode ='], 'const std::string mode = argc == 1 ? "--check" : argv[1];'),
   ('只印 FIRST 與 FOLLOW', ['for (std::size_t i = 0; i < rules.size(); ++i) { std::cout << "SELECT', 'std::cout << (ll1 ?'], '刪除這段 SELECT / table / LL1 輸出；FIRST/FOLLOW 兩行不刪，前面的集合計算不刪。'),
   ('字串判定輸出 YES / NO', ['std::cout << (accepted && pos == words.size()'], '將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。'),
  ]),
}


def source_locations(spec, anchors):
    lines = spec['source_path'].read_text().splitlines()
    result = []
    for anchor in anchors:
        matches = [i for i, line in enumerate(lines, 1) if anchor in line and not line.lstrip().startswith('//')]
        if len(matches) != 1:
            raise ValueError(f"{spec['stem']}: ambiguous/missing anchor {anchor!r}: {matches}")
        result.append(matches[0])
    return result


def logic_figure(stem, nodes):
    import html
    # fit preset: 40px margins, 48px nodes, 40px gaps, bottom legend; black/white.
    slug = 'short-' + stem
    svg = [f'<div class="diagram-container"><svg viewBox="0 0 480 364" role="img" aria-labelledby="{slug}-title {slug}-desc">',
           f'<title id="{slug}-title">{html.escape(HANDBOOK[stem]["question"])}</title>',
           f'<desc id="{slug}-desc">{html.escape(HANDBOOK[stem]["logic"])}</desc>', '<defs>']
    for marker in ['arrow', 'arrow-accent', 'arrow-link']:
        svg.append(f'<marker id="{slug}-{marker}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#555"/></marker>')
    svg += ['</defs>', '<rect width="480" height="364" fill="#fafaf7"/>']
    for i in range(2):
        y = 88 + i * 88
        svg.append(f'<line x1="240" y1="{y}" x2="240" y2="{y+40}" stroke="#555"/>')
        svg.append(f'<polygon points="236,{y+32} 244,{y+32} 240,{y+40}" fill="#555"/>')
    for i, (name, sub) in enumerate(nodes):
        y = 40 + i * 88
        svg += [f'<rect x="80" y="{y}" width="320" height="48" rx="6" fill="#fafaf7"/>',
                f'<rect x="80" y="{y}" width="320" height="48" rx="6" fill="#fff" stroke="#222"/>',
                f'<text class="node" x="240" y="{y+21}" text-anchor="middle">{html.escape(name)}</text>',
                f'<text class="sub" x="240" y="{y+37}" text-anchor="middle">{html.escape(sub)}</text>']
    svg += ['<line x1="40" y1="296" x2="440" y2="296" stroke="#ddd"/>',
            '<text class="legend" x="40" y="316">方框：處理步驟　箭頭：執行順序或呼叫關係</text>', '</svg></div>']
    return ''.join(svg)


def build_handbook_html():
    import html
    from cpp_handbook_examples import PROMPTS
    def esc(text):
        import re
        encoded = html.escape(text)
        return re.sub(r'([ \t]+)(?=\n)', lambda m: ''.join('&#32;' if c==' ' else '&#9;' for c in m[0]), encoded)
    evidence=json.loads((pack.REVIEW/'cpp-handbook-examples.json').read_text())
    examples={r['stem']:r for r in evidence['results']}
    pieces=['<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Compiler Ch1–3｜考場查題／改題指南</title>', '''<style>
*{box-sizing:border-box}body{max-width:1100px;margin:28px auto;padding:0 24px;color:#222;background:#fafaf7;font:15px/1.7 system-ui,"PingFang TC","Microsoft JhengHei",sans-serif}h1{font:30px/1.3 Georgia,"Noto Serif TC",serif;margin:0 0 12px}nav{display:flex;flex-wrap:wrap;gap:8px 18px;margin:20px 0}a{color:inherit;text-decoration:underline;text-underline-offset:3px}article{border-top:2px solid #888;padding:24px 0}h2{font-size:21px;margin:0 0 12px}h3{font-size:17px;margin:20px 0 8px}h4{font-size:15px;margin:10px 0}.basis{border-left:3px solid #555;padding:10px 16px;background:#f0f0ed}.file{margin:12px 0}code,pre{font-family:ui-monospace,"Menlo",monospace;font-size:13px}pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:0;padding:10px 12px;background:#f4f4f1;border:1px solid #ddd}code{overflow-wrap:anywhere}p{margin:8px 0}dl{margin:12px 0}dt{font-weight:600;margin-top:10px}dd{margin-left:0}.logic{display:grid;grid-template-columns:minmax(0,1fr) 480px;gap:20px;align-items:start}.diagram-container{width:100%;max-width:100%;min-width:0;overflow-x:auto}svg{display:block;width:100%;min-width:480px}.node{font:600 12px "Geist","Noto Sans TC","PingFang TC",sans-serif;fill:#222}.sub{font:9px "Geist Mono",ui-monospace,monospace;fill:#555}.legend{font:12px "Geist","Noto Sans TC","PingFang TC",sans-serif;fill:#555}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #ddd;text-align:left;vertical-align:top;padding:9px 10px}th{background:#eee}.line-note{font-size:13px;color:#555}.sample{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0}.sample p{font-size:13px;margin:0 0 4px}.edit{border-top:1px solid #ccc;padding:16px 0;break-inside:avoid}.changes{display:grid;grid-template-columns:1fr 1fr;gap:12px}.after{border-color:#555}details{margin:10px 0}summary{cursor:pointer;font-weight:600;padding:8px 0}details:not([open])>div{display:none}li{margin:5px 0}
@media(max-width:850px){body{padding:0 16px}.logic,.sample,.changes{grid-template-columns:minmax(0,1fr)}th,td{min-width:100px}}
@page{size:A4;margin:12mm}@media print{body{margin:0;padding:0;max-width:none;font-size:10pt;background:#fff}h1{font-size:18pt}nav{display:none}article{padding:12px 0}h2{font-size:14pt}h3{font-size:11pt}h4{font-size:10pt}.basis{padding:6px 10px}.logic{grid-template-columns:minmax(0,1fr) 80mm;gap:6mm}.diagram-container,.table-wrap{overflow-x:visible}svg{min-width:0}.node{font-size:16px}.sub{font-size:12px}table{font-size:9pt}code,pre{font-size:8pt}.line-note{font-size:8pt}.sample,.changes{grid-template-columns:1fr 1fr;gap:3mm}a{text-decoration:none}pre{padding:6px}.edit{break-inside:avoid}}
</style></head><body><h1>Compiler Ch1–3｜考場查題／改題指南</h1>''',
            '<p>考試直接攜帶八份含中文註解的 C++17 原檔。這份 HTML 用來查題目、檔名、解題邏輯與修改位置；完整程式請開啟各題的檔案連結。40 個修改範例與測例可展開查看。黑白離線版，行號對應目前原檔。</p>',
            '<nav aria-label="題目索引">']
    for i,spec in enumerate(SPECS,1):pieces.append(f'<a href="#{spec["stem"]}">{i:02} {esc(spec["title"].split("：")[0])}</a>')
    pieces.append('</nav>')
    def sample(data,label='輸入',outlabel='輸出'):
        out=data['output'] if data['exit']==0 else 'stdout：空\nstderr：'+data['stderr']+'exit 1'
        return f'<div class="sample"><div><p>{esc(label)}</p><pre>{esc(data["input"]) or "（空輸入）"}</pre></div><div><p>{esc(outlabel)}</p><pre>{esc(out)}</pre></div></div>'
    records=[]
    for i,spec in enumerate(SPECS,1):
        stem=spec['stem'];source=spec['source_path'];digest=hashlib.sha256(source.read_bytes()).hexdigest();tested=examples[stem]
        if digest!=tested['source_sha256']:raise ValueError(f'{stem}: run check_cpp_handbook.py after source changes')
        item=HANDBOOK[stem];prompt=PROMPTS[stem];href='../Code/'+str(source.relative_to(ROOT/'Complier/Code'))
        pieces += [f'<article id="{stem}"><h2>{i:02} {esc(spec["title"])}</h2>', '<h3>題目內容</h3>',f'<p class="basis">{esc(prompt["basis"])}</p>',f'<p>{esc(prompt["statement"])}</p>','<dl>']
        for key,label in [('input','輸入規格'),('output','輸出規格'),('limits','限制與適用範圍')]:pieces.append(f'<dt>{label}</dt><dd>{esc(prompt[key])}</dd>')
        pieces += ['</dl>',f'<p class="file"><b>Code 檔案名稱：</b><a href="{esc(href)}"><code>{source.name}</code></a> <small>（{esc(str(source.relative_to(ROOT/"Complier/Code")))}）</small></p>',f'<pre>g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror {source.name} -o main\n./main &lt; input.txt</pre>','<details class="examples"><summary>題目範例與邊界測例（點此展開）</summary><div>',sample(tested['fixture'])]
        for n,data in enumerate(tested['samples'],1):pieces.append(f'<h4>邊界測例 {n:02}</h4>'+sample(data))
        pieces.append('</div></details>')
        pieces.append('<h3>邏輯與手動追蹤</h3>')
        logic='<p>'+esc(item['logic'])+'</p><ul>'+''.join('<li>'+esc(t)+'</li>' for t in prompt['trace'])+'</ul>'
        pieces.append('<div class="logic"><div>'+logic+'</div>'+logic_figure(stem,item['flow'])+'</div>' if 'flow' in item else logic)
        pieces += ['<h3>題目變動時：先查修改位置</h3>','<p class="line-note">行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。短改法見表格，詳細改前／改後與測例在下方展開。</p>','<div class="table-wrap"><table><thead><tr><th>題目要求</th><th>修改行號</th><th>直接改法</th></tr></thead><tbody>']
        for n,v in enumerate(tested['variants'],1):
            labels=['–'.join(map(str,e['lines'])) if len(e['lines'])>1 else str(e['lines'][0]) for e in v['edits']]
            short_edits=[]
            for e in v['edits']:
                action='行後插入' if e['action']=='after' else '取代'
                short_edits.append(f'<p>{action}：</p><pre>{esc(e["after"]) or "（刪除此區塊）"}</pre>')
            pieces.append(f'<tr><td>{esc(v["title"])}<br><a href="#{stem}-change-{n}">展開完整範例</a></td><td>第 {"；".join(labels)} 行</td><td>{"".join(short_edits)}</td></tr>')
        pieces.append('</tbody></table></div>')
        for n,v in enumerate(tested['variants'],1):
            pieces += [f'<details class="edit" id="{stem}-change-{n}"><summary>{n:02} {esc(v["title"])}：改前／改後與測例</summary><div>']
            # Existing human guidance remains useful alongside exact replacements.
            guidance=next((text for title,_,text in item['edits'] if title==v['title']),None)
            if guidance:pieces.append('<p>'+esc(guidance)+'</p>')
            for e in v['edits']:
                lines='–'.join(map(str,e['lines']));instruction='在此行後插入' if e['action']=='after' else '用改後取代此行／區塊'
                pieces += [f'<p>第 {lines} 行：{instruction}</p>',f'<div class="changes"><div><p>改前（原碼）</p><pre>{esc(e["before"])}</pre></div><div><p>改後（可直接貼）</p><pre class="after">{esc(e["after"]) or "（刪除；不要貼這段提示文字）"}</pre></div></div>']
            if v['args']:pieces.append('<p>此變體執行參數：<code>./main '+esc(' '.join(v['args']))+'</code></p>')
            pieces += ['<p>已試編並執行的變體測例：</p>',sample(v['example']), '</div></details>']
        lines=source.read_text().splitlines()
        pieces.append('</article>')
        records.append(dict(stem=stem,source=str(source.relative_to(ROOT)),sha256=digest,source_lines=len(lines),variants=len(tested['variants'])))
    pieces.append('</body></html>');(pack.REVIEW/'Compiler-Ch1-Ch3-Cpp-Short.html').write_text('\n'.join(pieces))
    print('Source lookup guide:',8,'questions;',sum(len(v['variants']) for v in examples.values()),'compiled variants;',evidence['checks'],'sample checks; no duplicated full source')
    return records


def build_note():
    from cpp_handbook_examples import PROMPTS
    examples = {r["stem"]: r for r in json.loads((pack.REVIEW/"cpp-handbook-examples.json").read_text())["results"]}
    def case_block(data):
        if any(line.endswith((' ', '\t')) for line in data.splitlines()):
            return '```json\n' + json.dumps(data, ensure_ascii=False) + '\n```\n\n此 JSON 表示完整測試字串；`\\n` 是換行，尾端空白保留。\n\n'
        return '```text\n' + data + '```\n\n'
    text = f'''---
title: "{NAME}"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "既有 Ch1–3 作業實作與使用者 HTML parser 線索；短版為補充"
source_pages: "Ch2 p.15、p.36–46；Ch3 p.53–60；HTML 為使用者線索，LL(1) 為範圍未確認的補充"
---

# {NAME}

> [!abstract] 考場優先用這份
> 考試直接攜帶下列八份 `.cpp` 原檔，每份可獨立編譯。程式保留 **160 行追加的中文註解**，目前共 806 行。這份筆記與 [[Complier/Review/Compiler-Ch1-Ch3-Cpp-Short.html|HTML 查題／改題指南]] 提供題目、檔名、邏輯及修改行號；完整原碼請直接開檔。需要較完整功能時，查 [[Compiler - Ch1-Ch3 考試 C++ 程式集|原完整版]]。

先準備 HTML、Scanner、運算式、ac 與 HW5。LL(1) 放最後。以下每份的「範圍」就是適用條件，不能把不同 I/O 或題目要求當成已通過。

| 題型 | 行數 | 最短使用方式 |
|---|---:|---|
'''
    for s in SPECS:
        count = len(s['source_path'].read_text().splitlines())
        text += f"| {s['title']} | {count} | `{s['source_path'].name}` |\n"
    text += "\n## 考場先看\n\n" + "\n".join("- "+s for s in CHECKLIST)
    text += "\n\n## 驗證\n\n" + INTRO + "另有 200 個 HTML 新舊版比對、200 個獨立 Fraction 求值、97,222 個固定 DFA 字串及 768 個隨機 NFA 字串；完整報告見 `cpp-short-validation.json`。\n\n```sh\npython3 Complier/Code/check_cpp_short.py\npython3 Complier/Code/check_cpp_short.py --sanitize\n```\n"
    for s in SPECS:
        relative = s['source_path'].relative_to(ROOT)
        text += f"\n## {s['title']}\n\n[[{relative}|原始單檔]]\n\n"
        for key, label in [('contract','輸入輸出'),('limits','範圍'),('adapt','考場修改')]: text += f"**{label}**：{s[key]}\n\n"
        text += f"```sh\ng++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror {relative} -o /tmp/main\n/tmp/main < {relative.with_suffix('.in')}\n```\n\n"
        for suffix,label in [('.in','輸入'),('.expected','輸出')]: text += f"{label}：\n\n```text\n{s['source_path'].with_suffix(suffix).read_text()}```\n\n"
        prompt = PROMPTS[s['stem']]
        text += "### 完整題目（教材／模擬來源已區分）\n\n" + prompt['basis'] + "\n\n" + prompt['statement'] + "\n\n"
        for key, label in [('input','輸入'),('output','輸出'),('limits','範圍')]: text += f"**{label}**：{prompt[key]}\n\n"
        text += "### 手動追蹤\n\n" + "\n".join('- '+t for t in prompt['trace']) + "\n\n"
        text += "### 已試編修改範例\n\n"
        for variant in examples[s['stem']]['variants']:
            text += "#### " + variant['title'] + "\n\n"
            for edit in variant['edits']:
                where = '、'.join(map(str, edit['lines']))
                action = '在行後插入' if edit['action']=='after' else '取代這行／區塊'
                text += f"原檔第 {where} 行，{action}：\n\n```cpp\n{edit['after']}\n```\n\n"
            if variant['args']: text += "參數：`"+' '.join(variant['args'])+"`\n\n"
            example = variant['example']
            text += "輸入：\n\n" + case_block(example['input']) + "輸出：\n\n" + case_block(example['output'])
            if example['exit']: text += "stderr（exit 1）：\n\n```text\n"+example['stderr']+"```\n\n"
    (pack.REVIEW / (NAME+'.md')).write_text(text.rstrip()+'\n')

if __name__ == '__main__':
    pack.NAME = NAME
    import sys
    build_handbook_html()
    if '--html-only' in sys.argv:
        sys.exit(0)
    build_note()
    if '--pdf' in sys.argv:
        layout = pack.build_pdf(SPECS, 'Compiler-Ch1-Ch3-Cpp-Short.pdf', INTRO, CHECKLIST)
        (pack.REVIEW/'cpp-short-pack-layout.json').write_text(json.dumps(layout, ensure_ascii=False, indent=2)+'\n')
