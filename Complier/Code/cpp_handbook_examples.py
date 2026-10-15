"""題目敘述與可直接替換的考場變體；所有行號依原檔重新定位。"""
PROMPTS = {
 'html_check': dict(
  basis='歷屆 HTML parser 是使用者提供的線索，未提供原考卷；以下是完整模擬題。',
  statement='請撰寫程式讀入一份 HTML fragment，判斷所有非 void、非自閉合元素是否正確巢狀。開始標籤必須依相反順序關閉；END 名稱須與最內層未關閉元素相同。名稱不分 ASCII 大小寫。支援 boolean、單雙引號與無引號屬性、註解、短 DOCTYPE html；script/style/textarea/title 內容讀到匹配 END。多個根元素與空 fragment 均合法。',
  input='stdin 全部內容到 EOF 是一個案例，可能跨行。普通元素必須顯式關閉；本模擬題將 <x/> 視為自閉合。無額外案例數 T。',
  output='合法印 VALID，否則印 INVALID，每次只印一行；這兩種分類都正常結束。',
  limits='不是完整 browser DOM：不恢復錯誤、不省略 end tag、不解碼 entity、不檢查內容模型。這裡的「合法」指指定子集。',
  trace=['<a><b>x</b></a>：[] → [a] → [a,b] → [a] → []，接受。','<a><b></a></b>：讀 </a> 時 top 是 b，立即拒絕。','<p title="a>b">x</p>：引號中的 > 不切開 tag。','<p a=x/> 沒有關 p；<p a=x /> 則已自閉合。'],
  samples=[('', 'VALID\n'),('<P>x</p><br>','VALID\n'),('<a><b></a></b>','INVALID\n'),('<p a="a>b">x</p>','VALID\n'),('<p a=x/>','INVALID\n'),('<p a=x />','VALID\n'),('<!-- unclosed','INVALID\n'),('<script>if(a<b){}</SCRIPT >','VALID\n')]),
 'expression': dict(
  basis='Ch2 recursive descent / AST 的延伸模擬題；乘除、括號與一元正負不在原 ac 文法。',
  statement='請讀入每行運算式，依通常優先序計算結果，或依題目指定改為 postfix / AST。一元正負優先於乘除，乘除優先於加減；同級二元左結合。括號可覆寫優先序。number 允許 .5、10.、十進位小數及 e/E 科學記號；ID 符合 [A-Za-z_][A-Za-z_0-9]*。求值模式不允許變數。',
  input='每行一個完整運算式到 EOF，沒有 T；完全空輸入是零案例，但空白行本身是非法運算式。',
  output='預設 eval：每行印 15 位有效數字的 long double 結果。postfix：以一個空白分隔 token。一元正負用 pos/neg。ast：印前序括號表示。',
  limits='嵌套括號／一元鏈最多 256；不支援 %、^、函式或隱含乘法。非法字元、缺 operand、零除、非有限值：stdout 空、stderr 訊息、exit 1。',
  trace=['100-30-1：先 100-30，再 -1，結果 69。','a+b*c：AST 是 (+ a (* b c))；postfix 是 a b c * +。','-2*-3：讀 2 → neg → 3 → neg → *，結果 6。','2(3) 並非隱含乘法，會因多餘內容拒絕。'],
  samples=[('1+2*3','7\n'),('(2+3)*4','20\n'),('100-30-1','69\n'),('8/2/2','2\n'),('-2*-3','6\n'),('.5+1e-2','0.51\n'),('1/0',None),('2(3)',None)]),
 'lexer': dict(
  basis='Ch3 scanner / longest match 的延伸模擬題。教材 HW3 要擴充 ac 的 f/float、i/int、scientific number；本份是一般 C-like token 題，規格不同。',
  statement='請對一份類 C 程式做詞彙分析，依序列出 keyword、identifier、number、string、char、operator 與 punctuation。忽略空白、單行 // 註解及非巢狀 /* */ 註解。先讀完整 identifier 再查保留字，operator 採最長匹配。quoted literal 中的註解符號不可當作註解，跳脫引號不得提早終止 literal。',
  input='整份 stdin 到 EOF；ID 可含底線；number 允許 .5、10.、e/E。keyword 名單及 operator 名單以檔案常數為準。',
  output='每個 token 一行：類型、空白、quoted 包裝的原始 lexeme；最後一行 EOF。',
  limits='不是完整 C/C++ lexer：沒有 preprocessing、raw string、數字 suffix 或完整字元 escape 語意；CHAR 只允許單 byte / 單簡單 escape。遇未閉註解／引號或非法 byte，exit 1 且 stdout 空。',
  trace=['intx：先讀四個字元，查 keyword 失敗，因此為 ID，不拆 int + x。','a>>=2：>>= 先於 >> / >，只有一個 operator token。','"//x"：整段是 STRING，// 不觸發註解。','-1e-2：前面的 - 是 OP，指數內的 - 是 NUM 的一部分。'],
  samples=[('intx >>= 2','ID "intx"\nOP ">>="\nNUM "2"\nEOF\n'),('int x; // hi\n','KW "int"\nID "x"\nPUNCT ";"\nEOF\n'),('"//x"','STRING "\\"//x\\""\nEOF\n'),('1e+',None),('/* unfinished',None)]),
 'nfa_check': dict(
  basis='Ch3 epsilon-closure 與 NFA 的字串判定模擬題；input 格式由這份手冊定義。',
  statement='給定帶 epsilon edge 的 NFA，請對每個完整輸入字串判定是否接受。NFA 在同一時刻可同時位於多個 state，且不用消耗字元也可沿 epsilon edge 移動。每讀一個字元，對全部當前 state 做 move，再做 epsilon-closure。所有字元用完後，只要集合含至少一個接受 state 就接受。',
  input='先讀 n m start k；再讀 k 個 final state；再讀 alphabet；接著 m 條 from symbol to。state 是 0..n-1；# 是 epsilon。其後每行一個字串，空行是 epsilon 案例。',
  output='每案一行 ACCEPT / REJECT。非法 alphabet 字元直接拒絕該字串；非法 NFA 描述則 stderr、exit 1。',
  limits='1<=n<=256、0<=m<=65536；alphabet 非空、無重複、不能含 #；只接受單 byte 符號。本份不輸出 subset DFA 表。',
  trace=['0 --#→ 1 --a→ 2(final)：初始 {0,1}；讀 a 後 {2}，接受。','epsilon cycle：set 去重，只有新 state 進 todo，所以 closure 不會卡住。','先碰 final 再走死：必須等字串讀完，不能中途接受。'],
  samples=[('3 2 0 1\n2\na\n0 # 1\n1 a 2\na\n\naa\nz\n','ACCEPT\nREJECT\nREJECT\nREJECT\n')]),
 'hw5_check': dict(
  basis='教材原題（Ch3 PPT p.55、p.58）：Write NFA, and then DFA that recognizes the tokens defined by the following regular expression；5(d)=(bc)*d，5(a)=(a|(bc)*d)+。以下字串 I/O 是另外定義的程式練習。',
  statement='請以 DFA 判定字串是否屬於 5(a) 或 5(d) 的語言。5(a) 是一段或多段 a 或 (bc)*d 的串接；5(d) 是零次或多次 bc 後接單一 d。所有字元必須用完才可接受。原作業若要求畫 NFA / subset DFA，另外用 automata_homework.cpp 的 --table；本短版只給辨識結果。',
  input='HW5A=true 選 5(a)，改 false 選 5(d)。其後每行一個字串到 EOF，沒有 T；空行代表空字串。',
  output='每案印 ACCEPT / REJECT。大小寫敏感，僅題目語言內的字母可接受。',
  limits='不支援任意正則表示式輸入；這是固定兩個語言的四個可達 state 加 dead state。',
  trace=['5(a)：a、d、ad、bcd、dd 接受；bc、空字串拒絕。','5(d)：d、bcd、bcbcd 接受；a、dd、bc 拒絕。','bcd：0 --b→ 1 --c→ 2 --d→ 3；最後在 3，接受。'],
  samples=[('\na\nd\nad\nbcd\nbc\ndd\nz\n','REJECT\nACCEPT\nACCEPT\nACCEPT\nACCEPT\nREJECT\nACCEPT\nREJECT\n')]),
 'ac_dc': dict(
  basis='教材原題（Ch2 PPT p.39–46）：HW1 對 i x x=100 x=x+30+1 p x 建 parse tree；HW2(a) 建 AST、(b) 判斷語意與所需語言變更、(c) 顯示產碼；HW3 讓 f/float、i/int 均可宣告，number 可帶 optionally signed exponent。本檔只解產碼與型別檢查部分。',
  statement='請把 ac 程式編譯為 dc stack code。所有宣告在敘述前，型別為 int / float；identifier 為一個小寫字母，i/f/p 是保留字。敘述為 id=val{(+|-)val} 或 p id。val 為 variable 或非負 number。加減左結合。檢查重複宣告、未宣告及 float→int 指定；int→float 可提升。科學記號用精確字串移動小數點轉為 dc 可讀的小數。',
  input='整份 stdin 到 EOF；沒有分號或 T。f 或 float、i 或 int 均可。小數的點後必須有數字，指數字母限 lowercase e，可有正負。',
  output='只印 dc target code，不直接印數值答案。非法 ac 時 stdout 空、stderr 訊息、exit 1。',
  limits='帶 . 或 e 的 number 在本實作一律 float；exponent 絕對值與 mantissa 長度 <=10000。無乘除、括號、unary、註解。短版無 parse tree / AST / folding，這些要求使用 ac_homework.cpp。教材對 HW2(b) 的 No 與型別規則有疑義，詳見既有作業校讀。',
  trace=['x=100：100 → sx → 0 k；p x：lx → p → si。','i a f b b=a+3.2：la → 5 k → 3.2 → +；提升必須在對應 operand 後。','123e-22 → 0.0000000000000000000123，不能先轉 double 再印。','i x x=1e0：數值雖為 1，來源型別是 float，所以拒絕指定給 int。'],
  samples=[('i x x=2 px','2\nsx\n0 k\nlx\np\nsi\n'),('f x x=1e-2 px','0.01\nsx\n0 k\nlx\np\nsi\n'),('i x x=1.2',None),('p x',None),('i x i x',None)]),
 'stack_vm': dict(
  basis='Ch1 interpreter / Ch2 dc 產碼的延伸模擬題；指令名稱由本題定義，不是 GNU dc。',
  statement='請執行 stack-based 虛擬機指令。PUSH number 把常數入 stack；STORE name pop 並保存；LOAD name 複製變數值。ADD/SUB/MUL/DIV 先取右 operand b，再取左 a，計算 a op b。NEG 取反，DUP 複製頂端，PRINT pop 並輸出。未知指令、未定義變數、underflow、零除或非有限值均視為錯誤。',
  input='每行一條指令到 EOF；空行忽略。PUSH/LOAD/STORE 恰有一個參數，其餘沒有參數；變數名採一般 ID 規則。',
  output='每次 PRINT 一行，15 位有效數字。整份成功後才發出累積輸出；任何錯誤 stdout 空、stderr 訊息、exit 1。',
  limits='long double，非任意精度；沒有跳躍、條件、函式或字串。EOF 可留未使用 stack；PRINT 與 dc p 的 pop 規則不同。',
  trace=['PUSH 8 / PUSH 2 / SUB / PRINT：8-2=6，不能算成 2-8。','PUSH 2 / DUP / MUL / NEG / PRINT：2*2 再取負，得 -4。','PRINT 後 stack 少一項；若題目要求保留，要改成 peek。'],
  samples=[('PUSH 8\nPUSH 2\nSUB\nPRINT\n','6\n'),('PUSH 2\nDUP\nMUL\nNEG\nPRINT\n','-4\n'),('PUSH 1\nPUSH 0\nDIV\nPRINT\n',None),('LOAD x\n',None),('PRINT\n',None)]),
 'll1': dict(
  basis='predict 的通用延伸模擬題；正式 FIRST/FOLLOW 術語預告於 Ch4，不能視為已確認 Ch1–3 考題。',
  statement='給定 CFG，請計算各 nonterminal 的 FIRST / FOLLOW、各 production 的 SELECT，並建立 LL(1) 解析表。FIRST / FOLLOW 必須反覆傳播至固定點。RHS 可空時將 LHS 的 FOLLOW 加入 SELECT。同格若有多條 production，列出 conflict，判定非 LL(1)。無衝突時另可用 predictive stack 判定 token 序列。',
  input='先讀 P（1..1000），再讀 P 行 A -> X Y。每行只含一條 alternative；# 必須單獨表示 epsilon，$ 保留為 EOF。start 是第一個 LHS。--check 模式才讀其後每行空白分隔的 token sequence。',
  output='預設列 FIRST/FOLLOW/SELECT、非空表格 cell、CONFLICT 與 LL1 YES/NO。--check 每案印 ACCEPT/REJECT；不由字串原始字元自動 tokenize。',
  limits='不消除左遞迴、不做 left factoring（要做用 22 rd_gen），也不判定任意 CFG 是否無歧義。有 LL(1) conflict 時不任選規則繼續。',
  trace=['S -> a S | #：FIRST(S)={#,a}、FOLLOW(S)={$}。','SELECT(S->#)={$}，所以 EOF 時才選 epsilon，而不是看到任何字元都選。','A -> B C：若 C nullable，FOLLOW(A) 也要傳給 FOLLOW(B)。','展開 S -> a S 時先 push S 再 push a，讓 a 先被處理。'],
  samples=[('2\nS -> a S\nS -> #\n','FIRST(S)={#,a} FOLLOW(S)={$}\nSELECT(1)={a}\nSELECT(2)={$}\nM[S,$]=2\nM[S,a]=1\nLL1 YES\n')]),
}


def variants_for(spec, legacy):
    """每個變體都是明示、可試編的原碼替換；不改原檔。"""
    stem = spec['stem']; source = spec['source_path'].read_text()
    def line(anchor):
        found=[s for s in source.splitlines() if s.strip()==anchor]
        if not found: found=[s for s in source.splitlines() if anchor in s and not s.lstrip().startswith('//')]
        if len(found)!=1: raise ValueError((stem,anchor,found))
        return found[0]
    result=[]
    def add(title,patches,data,expected,args=()):
        result.append(dict(title=title,patches=patches,input=data,expected=expected,args=list(args)))
    def replace(anchor,new): return dict(action='replace',anchors=[anchor],text=new)
    def after(anchor,new): return dict(action='after',anchors=[anchor],text=new)
    def block(anchors,new): return dict(action='block',anchors=anchors,text=new)
    def output(anchor,data,expected):
        old=line(anchor);new=old.replace('VALID','YES').replace('INVALID','NO') if stem=='html_check' else old.replace('ACCEPT','YES').replace('REJECT','NO')
        # Replace INVALID first; otherwise VALID also changes inside INVALID.
        if stem=='html_check': new=old.replace('"INVALID\\n"','"NO\\n"').replace('"VALID\\n"','"YES\\n"')
        return [replace(anchor,new)],data,expected
    if stem=='html_check':
        a,d,e=output('cout << (valid ?', '<p/>','YES\n');add(legacy[0][0],a,d,e)
        add(legacy[1][0],[block(legacy[1][1],legacy[1][2].split('：\n',1)[1])],'<p/>\n<p>\n','VALID\nINVALID\n')
        add(legacy[2][0],[block(legacy[2][1],'const set<string> empty{};')],'<br></br>','VALID\n')
        add(legacy[3][0],[after('size_t p = 0;','size_t deepest = 0;'),after('stack.push_back(tag);','if (stack.size() > deepest) deepest = stack.size();'),replace('cout << (valid ?','if (valid) cout << deepest << "\\n"; else cout << "INVALID\\n";')],'<a><b></b></a>','2\n')
        t='int T; if (!(cin >> T) || T < 0) return 1;\ngetline(cin, s);\nif (s.find_first_not_of(" \\t\\r") != string::npos) return 1;\nfor (int tc = 0; tc < T; ++tc) {\n    if (!getline(cin, s)) return 1;\n    p = 0; bool valid = false;\n    try { valid = check(); } catch (const runtime_error&) {}\n    cout << (valid ? "VALID\\n" : "INVALID\\n");\n}\nif (cin.bad()) return 1;'
        add('首行 T，其後一行一案',[block(legacy[1][1],t)],'2\n<p/>\n<p>\n','VALID\nINVALID\n')
    elif stem=='expression':
        add(legacy[0][0],[replace('const string MODE =','const string MODE = "postfix";')],'a+b*c','a b c * +\n')
        add(legacy[1][0],[replace('const string MODE =','const string MODE = "ast";')],'a+b*c','(+ a (* b c))\n')
        add(legacy[2][0],[replace('ostringstream out; out << setprecision','ostringstream out; out << fixed << setprecision(2);')],'1/4','0.25\n')
        add(legacy[3][0],[after('bool id = letter(c);','if (id) fail();')],'x+1',None)
        old=line("if (op == '/')");add('每次除法結果向零截斷',[replace("if (op == '/')",old.replace('a.number /= b.number;','a.number = trunc(a.number / b.number);'))],'-7/2','-3\n')
    elif stem=='lexer':
        old=line('const set<string> keywords');add(legacy[0][0],[replace('const set<string> keywords',old.replace('{"int"','{"switch","case","int"'))],'switch case','KW "switch"\nKW "case"\nEOF\n')
        old=line('const vector<string> ops');add(legacy[1][0],[replace('const vector<string> ops',old.replace('"++"','"**","++"'))],'a**b','ID "a"\nOP "**"\nID "b"\nEOF\n')
        add(legacy[2][0],[block(legacy[2][1],legacy[2][2])],'int x','KW int\nID x\nEOF\n')
        add(legacy[3][0],[replace('output << "EOF','')],'int','KW "int"\n')
        add('不區分 keyword，全部列為 ID',[replace('kind = keywords.count','kind = "ID";')],'int x','ID "int"\nID "x"\nEOF\n')
    elif stem=='nfa_check':
        add(legacy[0][0],[replace('auto valid = [n]','auto valid = [n](int state) { return state >= 1 && state <= n; };'),replace('edges.resize(n);','edges.resize(n + 1);')],'2 1 1 1\n2\na\n1 a 2\na\nb\n','ACCEPT\nREJECT\n')
        edits=[replace(a,line(a).replace("'#'","'@'").replace('"#"','"@"')) for a in legacy[1][1]];add(legacy[1][0],edits,'3 2 0 1\n2\na\n0 @ 1\n1 a 2\na\n','ACCEPT\n')
        a,d,e=output('cout << (accepted ?', '2 1 0 1\n1\na\n0 a 1\na\n','YES\n');add(legacy[2][0],a,d,e)
        show='for (int state : states) cout << state << \' \';\ncout << \'\\n\';'
        add('印初始及每讀一字元後的 state 集合',[after('States states = closure({start});',show),after('states = closure(next);',show)],'3 2 0 1\n2\na\n0 # 1\n1 a 2\na\n','0 1 \n2 \nACCEPT\n')
        trim='size_t first = word.find_first_not_of(" \\t\\r");\nword = first == string::npos ? "" : word.substr(first, word.find_last_not_of(" \\t\\r") - first + 1);'
        add('忽略字串前後空白',[replace("if (!word.empty() && word.back() == '\\r')",trim)],'2 1 0 1\n1\na\n0 a 1\n  a \n','ACCEPT\n')
    elif stem=='hw5_check':
        add(legacy[0][0],[replace('const bool HW5A =','const bool HW5A = false;')],'d\ndd\nbcd\n','ACCEPT\nREJECT\nACCEPT\n')
        a,d,e=output('cout << (state == 3 ?', 'a\nb\n','YES\nNO\n');add(legacy[1][0],a,d,e)
        add(legacy[2][0],[replace('cout << (state == 3 ?',line('cout << (state == 3 ?').replace('state == 3 ?','(state == 3 || word.empty()) ?'))],'\na\nbc\n','ACCEPT\nACCEPT\nREJECT\n')
        add('ASCII 大小寫不敏感',[after("if (!word.empty() && word.back() == '\\r')","for (char& c : word) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';")],'BCD\nA\n','ACCEPT\nACCEPT\n')
        add('輸出 Case 1: 結果',[after('string word;','int case_no = 0;'),replace('cout << (state == 3 ?',line('cout << (state == 3 ?').replace('cout <<','cout << "Case " << ++case_no << ": " <<'))],'a\nb\n','Case 1: ACCEPT\nCase 2: REJECT\n')
    elif stem=='ac_dc':
        add(legacy[0][0],[replace(legacy[0][1][0],''),replace(legacy[0][1][1],''),replace(legacy[0][1][2],line(legacy[0][1][2]).replace('else if','if',1))],'i x x=1 px','1\nsx\n0 k\nlx\np\nsi\n')
        add(legacy[1][0],[replace(legacy[1][1][0],"if (j < s.size() && (s[j] == 'e' || s[j] == 'E')) {"),replace(legacy[1][1][1],'size_t e = text.find_first_of("eE");'),replace(legacy[1][1][2],line(legacy[1][1][2]).replace('".e"','".eE"'))],'f x x=1E-2 px','0.01\nsx\n0 k\nlx\np\nsi\n')
        edits=[replace(a,line(a).replace('5 k','10 k')) for a in legacy[2][1]];add(legacy[2][0],edits,'f x x=1 px','1\n10 k\nsx\n0 k\nlx\np\nsi\n')
        add('合法程式只輸出 OK',[replace('cout << out.str();','cout << "OK\\n"; return cout ? 0 : 1;')],'i x x=2 px','OK\n')
        add('assignment 後不要產生 scale reset',[replace("out << 's' << target",line("out << 's' << target").replace('\\n0 k\\n','\\n'))],'i x x=2 px','2\nsx\nlx\np\nsi\n')
    elif stem=='stack_vm':
        add(legacy[0][0],[replace(legacy[0][1][0],legacy[0][2])],'PUSH 2\nPRINT\nPRINT\n','2\n2\n')
        a=legacy[1][1][0];add(legacy[1][0],[replace(a,line(a).replace('output << setprecision(15);','output << fixed << setprecision(2);'))],'PUSH .25\nPRINT\n','0.25\n')
        a=legacy[2][1][0];add(legacy[2][0],[replace(a,line(a).replace('op == "PRINT"','op == "OUT"'))],'PUSH 8\nOUT\n','8\n')
        add('指令名稱忽略 ASCII 大小寫',[after('if (!(input >> op)) continue;',"for (char& c : op) if (c >= 'a' && c <= 'z') c -= 'a' - 'A';")],'push 2\nprint\n','2\n')
        add('PRINT 不移除值，DUP 後連續列印',[replace(legacy[0][1][0],legacy[0][2])],'PUSH 2\nDUP\nPRINT\nPRINT\n','2\n2\n')
    elif stem=='ll1':
        add(legacy[0][0],[replace(legacy[0][1][0],legacy[0][2])],'2\nS -> a S\nS -> #\na a\n\nb\n','ACCEPT\nACCEPT\nREJECT\n')
        add(legacy[1][0],[block(legacy[1][1],'')],'2\nS -> a S\nS -> #\n','FIRST(S)={#,a} FOLLOW(S)={$}\n')
        a,d,e=output(legacy[2][1][0],'2\nS -> a S\nS -> #\na\nb\n','YES\nNO\n');add(legacy[2][0],a,d,e,('--check',))
        a='follow[rules[0].lhs].insert';b='words.push_back("$");'
        add('指定 S 為 start，不使用第一個 LHS',[replace(a,line(a).replace('rules[0].lhs','"S"')),replace(b,line(b).replace('rules[0].lhs','"S"'))],'2\nA -> b\nS -> a\na\nb\n','ACCEPT\nREJECT\n',('--check',))
        add('只輸出是否為 LL(1)',[block(['for (const auto& nt : nonterminals) {', 'cout << (ll1 ?'], 'cout << (ll1 ? "LL1 YES\\n" : "LL1 NO\\n");')],'2\nS -> a S\nS -> #\n','LL1 YES\n')
    return result


def apply_variant(source, recipe):
    """一次從尾端改起，確保標示的是修改前原檔行號。"""
    original=source.splitlines();changes=[];records=[]
    for patch in recipe['patches']:
        positions=[]
        for anchor in patch['anchors']:
            found=[i for i,s in enumerate(original) if s.strip()==anchor]
            if not found: found=[i for i,s in enumerate(original) if anchor in s and not s.lstrip().startswith('//')]
            if len(found)!=1:raise ValueError((recipe['title'],anchor,found))
            positions.append(found[0])
        start=positions[0];end=positions[-1]+1
        if patch['action']=='after':start=end
        if patch['action'] in ('replace','after'):end=start+(patch['action']=='replace')
        before='\n'.join(original[positions[0]:positions[-1]+1])
        indent=original[positions[0]][:len(original[positions[0]])-len(original[positions[0]].lstrip())]
        replacement=[indent+s for s in patch['text'].splitlines()]
        changes.append((start,end,replacement))
        records.append(dict(lines=[i+1 for i in positions],action=patch['action'],before=before,after=patch['text']))
    result=original[:]
    for start,end,replacement in sorted(changes,reverse=True):result[start:end]=replacement
    return '\n'.join(result)+'\n',records
