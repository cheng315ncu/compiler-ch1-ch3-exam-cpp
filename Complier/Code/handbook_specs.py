"""Handbook source specs: the eight exam programs and their handbook edit recipes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "Complier/Code"
SPECS = [
 dict(stem="html_check", title="HTML 標籤配對", source_path=CODE/"01-HTML標籤配對/html_check.cpp",
      contract="整份 stdin 為一個 HTML fragment；只印 VALID／INVALID，兩種判定皆 exit 0。stack 保存未關閉標籤，END 必須配 top；空輸入合法。",
      limits="保留原版 check 的屬性驗證、註解、DOCTYPE html、13 個 void 與 script/style/textarea/title raw text；名稱不分 ASCII 大小寫。明示關閉，普通元素 <x/> 採本題子集自閉合；非 browser DOM，不省略 end tag、不解碼 entity。",
      adapt="改 main 的輸出字樣；一行一案才改成 getline 外層。配對時累積 stack.size() 可求最大深度。若要 token／tree／text，使用原 html_parser.cpp 的相應模式。"),
 dict(stem="expression", title="遞迴下降運算式", source_path=CODE/"02-遞迴下降運算式/expression.cpp",
      contract="一行一式；常數 MODE=eval（預設求值）、postfix 或 ast，修改這一行選題。+ - * /、括號、一元正負、十進位及 e/E；二元左結合。錯誤 stderr、exit 1，整份 stdout 暫存。",
      limits="eval 使用 long double、15 位有效數字，拒絕零除／非有限數／變數；ID 僅用於 postfix/ast。嵌套括號與一元鏈深度 <=256；AST 字串拼接最壞 O(n²)。長加減鏈用 while，不占深遞迴。",
      adapt="只求值可刪 postfix 與 ast 相關行；只畫 AST 可刪 number 的計算。若嵌套超過 256 或 AST 很長，原版 iterative expression.cpp 保留相同運算規則。"),
 dict(stem="lexer", title="Scanner：沿用現有短程式", source_path=CODE/"03-Scanner與註解/lexer.cpp",
      contract="整份 stdin；印 KW/ID/NUM/STRING/CHAR/OP/PUNCT 與帶引號 lexeme，最後 EOF。忽略 // 與非巢狀 /* */。長運算子先比，完整 ID 再查 keyword。",
      limits="C-like 補充，非完整 C/C++；ID [A-Za-z_][A-Za-z_0-9]*；number 支援 .5、10.、e/E；CHAR 單 byte 或單 escape。",
      adapt="keyword 改 keywords；運算子改 ops；輸出改最後兩行。沿用原本順序掃描的邏輯，追加中文註解；不新增架構。"),
 dict(stem="nfa_check", title="NFA 直接判定字串", source_path=CODE/"04-NFA判定字串/nfa_check.cpp",
      contract="n m start k；k 個接受 state；alphabet；m 條 from symbol to；其後一行一字串。state=0..n-1，#=epsilon，空行=空字串。印 ACCEPT／REJECT。",
      limits="n<=256，m<=65536；只做 closure(move(states,c)) 的 NFA 模擬，不產 DFA 表。不再因完整 DFA 超過 4096 states 而失敗。",
      adapt="字串辨識就用這份；若題目明確要求 subset construction／DFA 表／集合 trace，改用原 nfa_to_dfa.cpp，勿用字串判定代替表格作答。"),
 dict(stem="hw5_check", title="HW5 固定四狀態 DFA", source_path=CODE/"05-HW5固定DFA/hw5_check.cpp",
      contract="一行一字串，空行拒絕；HW5A=true 辨識 (a|(bc)*d)+，改 false 辨識 (bc)*d。印 ACCEPT／REJECT，不需命令列參數。",
      limits="只有固定兩個語言；0=start、1=剛讀 b、2=剛讀 bc、3=accept、-1=dead。這是精簡的辨識 DFA，不是投影片子集構造的原始 state sets。",
      adapt="HW5A 常數選題；改 ACCEPT/REJECT 字樣。若要求原 NFA 邊、epsilon closure 或 subset DFA 表，用 automata_homework.cpp 5a/5d --table。"),
 dict(stem="ac_dc", title="ac 邊解析邊產 dc", source_path=CODE/"06-ac產dc/ac_dc.cpp",
      contract="整份 stdin 為 ac 程式；f/float、i/int 宣告在前，p 印變數，單字母 ID，加減左結合。保留重複／未宣告／float→int 檢查，正確時只印 dc code。",
      limits="支援小數與 lowercase e signed exponent；帶 . 或 e 就是 float。精確移動小數點，exponent 絕對值及 mantissa 長度 <=10000；無括號／乘除／註解。print 使用 l<變數>/p/si 形式。",
      adapt="int→float 時印 5 k；assign 後印 0 k。value 直接回 leaf code 與型別，主迴圈直接產碼，沒有樹走訪。題目要求 parse tree／AST／常數摺疊時，用原 ac_homework.cpp 的相應模式。"),
 dict(stem="stack_vm", title="Stack VM：沿用現有短程式", source_path=CODE/"07-StackVM/stack_vm.cpp",
      contract="一行一指令：PUSH、LOAD、STORE、ADD/SUB/MUL/DIV、NEG、DUP、PRINT；PRINT/STORE pop。long double，15 位有效數字；錯誤 stderr、exit 1，暫存 stdout。",
      limits="無條件／跳躍／函式；只做 stack interpreter，不是 dc。LOAD 未定義、underflow、div0 拒絕。",
      adapt="先 pop 右 b，再左 a，算 a op b；PRINT 若題目要求不 pop，就改讀 stack.back()。沿用原本直接執行流程，追加中文註解。"),
 dict(stem="ll1", title="LL(1)：較低優先補充", source_path=CODE/"08-LL1/ll1.cpp",
      contract="P 條產生式，一行 A -> X Y，# 單獨為 epsilon；預設印 FIRST/FOLLOW/SELECT、table 與 conflict。--check 判定其後每行 token sequence。",
      limits="通用表格功能需要固定點、nullable suffix 與衝突檢查；保留原本固定點演算法，追加中文註解。P<=1000；不消除左遞迴或做 left factoring。正式 FIRST/FOLLOW 範圍未確認。",
      adapt="若已知題目固定文法，只寫對應 recursive descent 更好記；若要求任意 CFG 的 FIRST/FOLLOW，保留本版以免刪掉 nullable 的必要處理。DOMjudge 不傳 args 時固定 main 的 mode。"),
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
   ('增加保留字', ['const set<string> keywords'], '在 keywords 名單加入 "switch", "case" 等題目指定字。'),
   ('增加多字元運算子', ['const vector<string> ops'], '在 ops 名單加入所需運算子；維持較長字串先列。這裡只分詞，不增加 parser 的運算規則。'),
   ('lexeme 不加引號', ['output << kind <<', 'output << "\\"\\n";'], 'output << kind << \' \' << s.substr(start, p - start) << \'\\n\';'),
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
   ('PRINT 保留 stack 頂端', ['} else if (op == "PRINT")'], '} else if (op == "PRINT") {\n    if (stack.empty()) throw runtime_error("stack underflow");\n    const auto value = stack.back();\n    output << (value == 0 ? 0 : value) << \'\\n\';\n}'),
   ('固定小數點後 2 位', ['output << setprecision'], '把 output << setprecision(15); 改成 output << fixed << setprecision(2);。'),
   ('PRINT 指令改名為 OUT', ['} else if (op == "PRINT")'], '把該行 op == "PRINT" 改成 op == "OUT"。'),
  ]),
 'll1': dict(
  question='計算任意 CFG 的 FIRST/FOLLOW/SELECT 與 LL(1) 表，或用表判定 token 序列（延伸題）。',
  logic='FIRST 與 FOLLOW 反覆合併至固定點；nullable RHS 將 FOLLOW 加進 SELECT。用 SELECT 填表，同格多條規則就是 conflict；解析用 stack 與 lookahead 查表。# 單獨代表 ε。',
  edits=[
   ('judge 不傳參數，只判定字串', ['const string mode ='], 'const string mode = argc == 1 ? "--check" : argv[1];'),
   ('只印 FIRST 與 FOLLOW', ['for (size_t i = 0; i < rules.size(); ++i) { cout << "SELECT', 'cout << (ll1 ?'], '刪除這段 SELECT / table / LL1 輸出；FIRST/FOLLOW 兩行不刪，前面的集合計算不刪。'),
   ('字串判定輸出 YES / NO', ['cout << (accepted && pos == words.size()'], '將 "ACCEPT\\n" / "REJECT\\n" 改成 "YES\\n" / "NO\\n"。'),
  ]),
}
