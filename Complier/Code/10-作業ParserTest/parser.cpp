// ParserTest：Recursive-Descent 檢查整份輸入；合法才逐行印出「token 種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { ID, STRLIT, LBR, RBR, DOT, END, INVALID };
// 整份輸入保存在 src；[start, pos) 是目前 token 的原字串。題目未指定長度上限，用 string 自動擴充。
string src;
size_t pos = 0, start = 0;
Token token;

// Scanner：每次讀一個 token 放進 token。
void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }

    unsigned char c = src[pos++];
    if (isalpha(c) || c == '_') {
        // ID -> [A-Za-z_][A-Za-z0-9_]*
        while (pos < src.size() && (isalnum((unsigned char)src[pos]) || src[pos] == '_')) ++pos;
        token = ID;
    } else if (c == '"') {
        // STRLIT -> "[^"]*"：可跨行；找不到結尾的 " 就是 INVALID。
        size_t end = src.find('"', pos);
        token = end == string::npos ? INVALID : STRLIT;
        pos = end == string::npos ? src.size() : end + 1;
    } else if (c == '(') token = LBR;
    else if (c == ')') token = RBR;
    else if (c == '.') token = DOT;
    else token = INVALID;
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

// stmt -> STRLIT | ID (DOT ID | LBR stmt RBR)* | lambda
bool stmt() {
    if (token == STRLIT) return match(STRLIT);
    // stmt -> lambda：後面只能接 RBR 或輸入結尾。
    if (!match(ID)) return token == RBR || token == END;

    // primary_tail 的右遞迴改成迴圈。
    while (token == DOT || token == LBR) {
        if (token == DOT) {
            next_token();
            if (!match(ID)) return false;
        } else {
            next_token();
            if (!stmt() || !match(RBR)) return false;
        }
    }
    return true;
}

int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    const char* names[] = {"ID", "STRLIT", "LBR", "RBR", "DOT"};
    src.assign(istreambuf_iterator<char>(cin), {});
    if (cin.bad()) return 1;

    // 先檢查整份輸入：stmts -> stmt stmts | lambda。
    bool valid = true;
    next_token();
    while (token == ID || token == STRLIT) {
        if (!stmt()) { valid = false; break; }
    }

    if (!valid || token != END) {
        cout << "invalid input\n";
    } else {
        // 全部合法後才從頭重掃並輸出 token。
        pos = 0;
        for (next_token(); token != END; next_token())
            cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
    }
}
