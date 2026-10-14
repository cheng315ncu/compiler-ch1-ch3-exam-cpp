// 模擬 ParserTest：成員存取、陣列索引與函式呼叫鏈；每個敘述以 ; 結尾。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { ID, NUM, STRLIT, DOT, COMMA, SEMI, LBR, RBR, LSB, RSB, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    if (isalpha(c) || c == '_') {
        while (pos < src.size() && (isalnum((unsigned char)src[pos]) || src[pos] == '_')) ++pos;
        token = ID;
    } else if (isdigit(c)) {
        while (pos < src.size() && isdigit((unsigned char)src[pos])) ++pos;
        token = NUM;
    } else if (c == '"') {
        // STRLIT -> "[^"]*"；沒有結尾的 " 就是 INVALID。
        size_t end = src.find('"', pos);
        token = end == string::npos ? INVALID : STRLIT;
        pos = end == string::npos ? src.size() : end + 1;
    } else {
        const string marks = ".,;()[]";
        size_t i = marks.find(c);
        token = i == string::npos ? INVALID : Token(DOT + i);
    }
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

bool call();
// arg -> call | STRLIT | NUM
bool arg() { return match(STRLIT) || match(NUM) || call(); }

// call -> ID tail；tail -> DOT ID tail | LSB NUM RSB tail | LBR args RBR tail | λ
bool call() {
    if (!match(ID)) return false;
    while (true) {
        if (match(DOT)) {
            if (!match(ID)) return false;
        } else if (match(LSB)) {
            if (!match(NUM) || !match(RSB)) return false;
        } else if (match(LBR)) {
            // args -> arg (COMMA arg)* | λ；λ 只在下一個 token 是 RBR 時成立，所以 f(,1) 不合法。
            if (token != RBR) {
                if (!arg()) return false;
                while (match(COMMA))
                    if (!arg()) return false;
            }
            if (!match(RBR)) return false;
        } else {
            return true;
        }
    }
}

int main() {
    const char* names[] = {"ID", "NUM", "STRLIT", "DOT", "COMMA", "SEMI", "LBR", "RBR", "LSB", "RSB"};
    src.assign(istreambuf_iterator<char>(cin), {});
    // program -> stmts；stmts -> call SEMI stmts | λ
    bool valid = true;
    for (next_token(); valid && token != END;) valid = call() && match(SEMI);
    if (!valid) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
