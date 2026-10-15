// 模擬 ParserTest：課本 Ch2 ac 語言（Fig 2.1）Recursive-Descent；合法才逐行印「種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { FLOATDCL, INTDCL, PRINT, ID, ASSIGN, PLUS, MINUS, INUM, FNUM, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    // ac 的 id 只有一個小寫字母；f、i、p 保留給 floatdcl、intdcl、print。ab 是 ID a、ID b。
    if (c == 'f') token = FLOATDCL;
    else if (c == 'i') token = INTDCL;
    else if (c == 'p') token = PRINT;
    else if (islower(c)) token = ID;
    else if (isdigit(c)) {
        // inum [0-9]+；fnum [0-9]+\.[0-9]+：點後至少一位才吃點。
        while (pos < src.size() && isdigit((unsigned char)src[pos])) ++pos;
        token = INUM;
        if (pos + 1 < src.size() && src[pos] == '.' && isdigit((unsigned char)src[pos + 1])) {
            for (++pos; pos < src.size() && isdigit((unsigned char)src[pos]); ++pos) {}
            token = FNUM;
        }
    } else if (c == '=') token = ASSIGN;
    else if (c == '+') token = PLUS;
    else if (c == '-') token = MINUS;
    else token = INVALID;
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

// Val -> id | inum | fnum
bool val() { return match(ID) || match(INUM) || match(FNUM); }
// Stmt -> id assign Val Expr | print id；Expr -> (plus | minus) Val Expr | λ 寫成迴圈。
bool stmt() {
    if (match(PRINT)) return match(ID);
    if (!match(ID) || !match(ASSIGN) || !val()) return false;
    while (token == PLUS || token == MINUS) {
        next_token();
        if (!val()) return false;
    }
    return true;
}
// Prog -> Dcls Stmts $：Dcls 看 floatdcl／intdcl，Stmts 看 id／print，最後必須是 END。
bool prog() {
    while (token == FLOATDCL || token == INTDCL) { next_token(); if (!match(ID)) return false; }
    while (token == ID || token == PRINT) if (!stmt()) return false;
    return token == END;
}

int main() {
    const char* names[] = {"FLOATDCL", "INTDCL", "PRINT", "ID", "ASSIGN", "PLUS", "MINUS", "INUM", "FNUM"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    if (!prog()) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
