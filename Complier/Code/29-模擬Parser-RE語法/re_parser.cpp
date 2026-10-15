// 模擬 ParserTest：Regular Expression 語法本身的 Recursive-Descent；合法才逐行印「種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { CHAR, OR, STAR, LPR, RPR, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    // CHAR 一次只有一個字元：ab 是 CHAR a、CHAR b（串接），不是一個 token。
    if (islower(c) || isdigit(c)) token = CHAR;
    else if (c == '|') token = OR;
    else if (c == '*') token = STAR;
    else if (c == '(') token = LPR;
    else if (c == ')') token = RPR;
    else token = INVALID;
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

bool re();
// factor -> atom star；star -> STAR star | λ；atom -> CHAR | LPR re RPR
bool factor() {
    if (!match(CHAR) && !(match(LPR) && re() && match(RPR))) return false;
    while (match(STAR)) {}
    return true;
}
// term -> factor term_tail；term_tail -> factor term_tail | λ：下一個是 FIRST(factor) = {CHAR, LPR} 才繼續串接。
bool term() {
    if (!factor()) return false;
    while (token == CHAR || token == LPR) if (!factor()) return false;
    return true;
}
// re -> term re_tail；re_tail -> OR term re_tail | λ
bool re() {
    if (!term()) return false;
    while (match(OR)) if (!term()) return false;
    return true;
}

int main() {
    const char* names[] = {"CHAR", "OR", "STAR", "LPR", "RPR"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    if (!re() || token != END) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
