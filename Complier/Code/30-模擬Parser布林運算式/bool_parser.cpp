// 模擬 ParserTest：布林運算式（or < and < not < 比較）Recursive-Descent；合法才逐行印「種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { OR, AND, NOT, ID, NUM, EQ, LT, GT, LPR, RPR, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    if (isalpha(c) || c == '_') {
        // 先讀完整個字再查 keyword：order、android 都是 ID。
        while (pos < src.size() && (isalnum((unsigned char)src[pos]) || src[pos] == '_')) ++pos;
        const string w = src.substr(start, pos - start);
        token = w == "or" ? OR : w == "and" ? AND : w == "not" ? NOT : ID;
    } else if (isdigit(c)) {
        while (pos < src.size() && isdigit((unsigned char)src[pos])) ++pos;
        token = NUM;
    } else if (c == '=' && pos < src.size() && src[pos] == '=') { ++pos; token = EQ; }   // 單獨的 = 不是 token
    else if (c == '<') token = LT;
    else if (c == '>') token = GT;
    else if (c == '(') token = LPR;
    else if (c == ')') token = RPR;
    else token = INVALID;
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

bool bexpr();
// rel -> operand relop operand；operand -> ID | NUM；relop -> EQ | LT | GT
bool operand() { return match(ID) || match(NUM); }
bool rel() { return operand() && (match(EQ) || match(LT) || match(GT)) && operand(); }
// bfactor -> NOT bfactor | LPR bexpr RPR | rel：( 一定開始括號內的 bexpr，因為 operand 不含括號。
bool bfactor() {
    if (match(NOT)) return bfactor();
    if (match(LPR)) return bexpr() && match(RPR);
    return rel();
}
// bterm -> bfactor { AND bfactor }
bool bterm() {
    if (!bfactor()) return false;
    while (match(AND)) if (!bfactor()) return false;
    return true;
}
// bexpr -> bterm { OR bterm }
bool bexpr() {
    if (!bterm()) return false;
    while (match(OR)) if (!bterm()) return false;
    return true;
}

int main() {
    const char* names[] = {"OR", "AND", "NOT", "ID", "NUM", "EQ", "LT", "GT", "LPR", "RPR"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    if (!bexpr() || token != END) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
