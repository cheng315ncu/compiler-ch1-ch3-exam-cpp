// 模擬 ScannerTest：比較運算子 longest match＋兩種註解；任何錯誤只印 invalid input。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;

// 成功時 out 是全部 token；失敗回 false，呼叫端不印任何 token。
bool scan(const string& s, string& out) {
    // 兩字元運算子排在前面：<= 要先於 <，這就是 longest match。
    const pair<string, string> ops[] = {{"<=", "LE"}, {">=", "GE"}, {"==", "EQ"}, {"!=", "NE"},
                                        {"<", "LT"}, {">", "GT"}, {"=", "ASSIGN"},
                                        {"(", "LPR"}, {")", "RPR"}, {";", "SEMI"}};
    size_t p = 0;
    while (p < s.size()) {
        unsigned char c = s[p];
        if (isspace(c)) { ++p; continue; }
        // // 到行尾（或 EOF）；/* 到第一個 */，不巢狀，沒有結尾就是錯誤。
        if (s.compare(p, 2, "//") == 0) { p = s.find('\n', p); continue; }
        if (s.compare(p, 2, "/*") == 0) {
            size_t end = s.find("*/", p + 2);
            if (end == string::npos) return false;
            p = end + 2; continue;
        }
        size_t start = p;
        if (isalpha(c) || c == '_') {
            while (p < s.size() && (isalnum((unsigned char)s[p]) || s[p] == '_')) ++p;
            out += "ID " + s.substr(start, p - start) + '\n';
        } else if (isdigit(c)) {
            while (p < s.size() && isdigit((unsigned char)s[p])) ++p;
            out += "NUM " + s.substr(start, p - start) + '\n';
        } else {
            size_t i = 0;
            while (i < size(ops) && s.compare(p, ops[i].first.size(), ops[i].first) != 0) ++i;
            // 單獨的 ! 或 / 不是 token。
            if (i == size(ops)) return false;
            out += ops[i].second + '\n';
            p += ops[i].first.size();
        }
    }
    return true;
}

int main() {
    string s(istreambuf_iterator<char>(cin), {}), out;
    cout << (scan(s, out) ? out : "invalid input\n");
}
