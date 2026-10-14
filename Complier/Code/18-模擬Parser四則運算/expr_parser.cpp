// 模擬 ParserTest：四則運算式 Recursive-Descent；合法才逐行印「種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { NUM, ID, PLUS, MINUS, MUL, DIV, LPR, RPR, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    if (isdigit(c)) {
        // NUM -> 0 | [1-9][0-9]*：012 會切成 NUM 0、NUM 12，兩個 NUM 相鄰在文法上不合法。
        if (c != '0') while (pos < src.size() && isdigit((unsigned char)src[pos])) ++pos;
        token = NUM;
    } else if (isalpha(c) || c == '_') {
        while (pos < src.size() && (isalnum((unsigned char)src[pos]) || src[pos] == '_')) ++pos;
        token = ID;
    } else if (c == '+') token = PLUS;
    else if (c == '-') token = MINUS;
    else if (c == '*') token = MUL;
    else if (c == '/') token = DIV;
    else if (c == '(') token = LPR;
    else if (c == ')') token = RPR;
    else token = INVALID;
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

bool expr();
// factor -> NUM | ID | LPR expr RPR
bool factor() {
    if (match(NUM) || match(ID)) return true;
    return match(LPR) && expr() && match(RPR);
}
// term -> factor term_tail；term_tail -> (MUL | DIV) factor term_tail | λ，右遞迴寫成迴圈。
bool term() {
    if (!factor()) return false;
    while (token == MUL || token == DIV) {
        next_token();
        if (!factor()) return false;
    }
    return true;
}
// expr -> term expr_tail；expr_tail -> (PLUS | MINUS) term expr_tail | λ
bool expr() {
    if (!term()) return false;
    while (token == PLUS || token == MINUS) {
        next_token();
        if (!term()) return false;
    }
    return true;
}

int main() {
    const char* names[] = {"NUM", "ID", "PLUS", "MINUS", "MUL", "DIV", "LPR", "RPR"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    // 整份輸入必須剛好是一個 expr；後面還有東西（例如多的 RPR）也不合法。
    if (!expr() || token != END) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
