// 模擬 ParserTest：JSON 子集 Recursive-Descent；合法才逐行印「種類 原字串」，否則只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
enum Token { LCB, RCB, LSB, RSB, COLON, COMMA, STRING, NUMBER, TRUE, FALSE, NUL, END, INVALID };
string src;
size_t pos = 0, start = 0;
Token token;

bool digit(size_t i) { return i < src.size() && isdigit((unsigned char)src[i]); }

void next_token() {
    while (pos < src.size() && isspace((unsigned char)src[pos])) ++pos;
    start = pos;
    if (pos == src.size()) { token = END; return; }
    unsigned char c = src[pos++];
    if (c == '-' || isdigit(c)) {
        // NUMBER -> -?(0 | [1-9][0-9]*)：- 後一定要有數字；開頭 0 只吃一位。
        if (c == '-') {
            if (!digit(pos)) { token = INVALID; return; }
            c = src[pos++];
        }
        if (c != '0') while (digit(pos)) ++pos;
        token = NUMBER;
    } else if (c == '"') {
        size_t end = src.find('"', pos);
        token = end == string::npos ? INVALID : STRING;
        pos = end == string::npos ? src.size() : end + 1;
    } else if (isalpha(c)) {
        // 先讀完整個字再比對：truex、True 都不是 TRUE。
        while (pos < src.size() && isalpha((unsigned char)src[pos])) ++pos;
        string w = src.substr(start, pos - start);
        token = w == "true" ? TRUE : w == "false" ? FALSE : w == "null" ? NUL : INVALID;
    } else {
        const string marks = "{}[]:,";
        size_t i = marks.find(c);
        token = i == string::npos ? INVALID : Token(i);
    }
}

bool match(Token expected) {
    if (token != expected) return false;
    next_token();
    return true;
}

// value -> object | array | STRING | NUMBER | TRUE | FALSE | NULL
// object -> LCB (pair (COMMA pair)*)? RCB；pair -> STRING COLON value
// array  -> LSB (value (COMMA value)*)? RSB
bool value() {
    if (match(STRING) || match(NUMBER) || match(TRUE) || match(FALSE) || match(NUL)) return true;
    if (match(LCB)) {
        // 空物件只在下一個是 RCB 時成立；逗號後一定要再有 pair，所以 {"a":1,} 不合法。
        if (token != RCB)
            do if (!match(STRING) || !match(COLON) || !value()) return false; while (match(COMMA));
        return match(RCB);
    }
    if (match(LSB)) {
        if (token != RSB)
            do if (!value()) return false; while (match(COMMA));
        return match(RSB);
    }
    return false;
}

int main() {
    const char* names[] = {"LCB", "RCB", "LSB", "RSB", "COLON", "COMMA", "STRING", "NUMBER", "TRUE", "FALSE", "NULL"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    // 整份輸入必須剛好是一個 value。
    if (!value() || token != END) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token())
        cout << names[token] << ' ' << src.substr(start, pos - start) << '\n';
}
