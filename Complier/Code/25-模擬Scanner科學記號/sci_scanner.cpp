// 模擬 ScannerTest：科學記號 NUM 的 longest match＋退回最後接受位置；任何錯誤只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;

bool digit_at(const string& s, size_t p) { return p < s.size() && isdigit((unsigned char)s[p]); }
// 成功時 out 是全部 token；失敗回 false，呼叫端不印任何 token。
bool scan(const string& s, string& out) {
    size_t p = 0;
    while (p < s.size()) {
        unsigned char c = s[p];
        if (isspace(c)) { ++p; continue; }
        size_t start = p;
        if (isdigit(c)) {
            // NUM -> [0-9]+ (\.[0-9]+)? (e[+-]?[0-9]+)?
            // 每段完整才吃：12e、1.2e- 只到最後接受位置（12、1.2），剩下的 e、- 從頭再掃。
            while (digit_at(s, p)) ++p;
            if (s[p] == '.' && digit_at(s, p + 1)) { ++p; while (digit_at(s, p)) ++p; }
            if (p < s.size() && s[p] == 'e') {
                size_t q = p + 1;
                if (q < s.size() && (s[q] == '+' || s[q] == '-')) ++q;
                if (digit_at(s, q)) { p = q; while (digit_at(s, p)) ++p; }
            }
            out += "NUM " + s.substr(start, p - start) + '\n';
        } else if (isalpha(c) || c == '_') {
            while (p < s.size() && (isalnum((unsigned char)s[p]) || s[p] == '_')) ++p;
            out += "ID " + s.substr(start, p - start) + '\n';
        } else {
            const string ops = "+-*/()", names[] = {"PLUS", "MINUS", "MUL", "DIV", "LPR", "RPR"};
            // 單獨的 .（例如 .5、3.）不屬於任何 token。
            if (ops.find(c) == string::npos) return false;
            out += names[ops.find(c)] + '\n';
            ++p;
        }
    }
    return true;
}

int main() {
    string s(istreambuf_iterator<char>(cin), {}), out;
    cout << (scan(s, out) ? out : "invalid input\n");
}
