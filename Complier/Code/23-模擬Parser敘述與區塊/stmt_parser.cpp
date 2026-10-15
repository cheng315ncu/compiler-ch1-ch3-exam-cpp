// 模擬 ParserTest：if／else、while、{ } 區塊的 Recursive-Descent；合法才逐行印「種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { ID, NUM, IF, ELSE, WHILE, PRINT, ASSIGN, PLUS, LPR, RPR, LBR, RBR, SEMI, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    if (isalpha(c) || c == '_') {
        // 先讀完整個字再查 keyword：iff、whilex 都是 ID。
        while (pos < src.size() && (isalnum((unsigned char)src[pos]) || src[pos] == '_')) ++pos;
        const string w = src.substr(start, pos - start);
        token = w == "if" ? IF : w == "else" ? ELSE : w == "while" ? WHILE : w == "print" ? PRINT : ID;
    } else if (isdigit(c)) {
        while (pos < src.size() && isdigit((unsigned char)src[pos])) ++pos;
        token = NUM;
    } else if (c == '=') token = ASSIGN;
    else if (c == '+') token = PLUS;
    else if (c == '(') token = LPR;
    else if (c == ')') token = RPR;
    else if (c == '{') token = LBR;
    else if (c == '}') token = RBR;
    else if (c == ';') token = SEMI;
    else token = INVALID;
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

// expr -> atom { PLUS atom }；atom -> ID | NUM
bool expr() {
    if (!match(ID) && !match(NUM)) return false;
    while (match(PLUS)) if (!match(ID) && !match(NUM)) return false;
    return true;
}
bool stmt();
// stmts -> stmt stmts | λ：token 屬於 FIRST(stmt) 才繼續；λ 之後由呼叫端查 RBR 或 END。
bool stmts() {
    while (token == ID || token == PRINT || token == IF || token == WHILE || token == LBR)
        if (!stmt()) return false;
    return true;
}
bool stmt() {
    if (match(ID)) return match(ASSIGN) && expr() && match(SEMI);
    if (match(PRINT)) return expr() && match(SEMI);
    if (match(WHILE)) return match(LPR) && expr() && match(RPR) && stmt();
    if (match(LBR)) return stmts() && match(RBR);
    // dangling else：else 一律接給最近的 if（看到 ELSE 就吃，不回頭）。
    if (match(IF)) return match(LPR) && expr() && match(RPR) && stmt() && (!match(ELSE) || stmt());
    return false;
}

int main() {
    const char* names[] = {"ID", "NUM", "IF", "ELSE", "WHILE", "PRINT", "ASSIGN", "PLUS", "LPR", "RPR", "LBR", "RBR", "SEMI"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    if (!stmts() || token != END) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
