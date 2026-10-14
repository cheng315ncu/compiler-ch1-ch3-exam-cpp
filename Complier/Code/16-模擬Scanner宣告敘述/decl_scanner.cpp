// 模擬 ScannerTest：宣告／指定敘述。keyword 先讀完整 ID 再查表；數字分 INUM / FNUM。
#include <cctype>
#include <iostream>
#include <iterator>
#include <string>
using namespace std;
int main() {
    // FNUM 要看「. 後面是否為數字」需要兩字元 lookahead，所以整份讀進來比逐字元讀簡單。
    string s(istreambuf_iterator<char>(cin), {});
    size_t p = 0;
    auto digit = [&](size_t i) { return i < s.size() && isdigit((unsigned char)s[i]); };
    while (p < s.size()) {
        unsigned char c = s[p];
        if (isspace(c)) { ++p; continue; }
        size_t start = p;
        if (isalpha(c) || c == '_') {
            while (p < s.size() && (isalnum((unsigned char)s[p]) || s[p] == '_')) ++p;
            string w = s.substr(start, p - start);
            // 讀完整 ID 才查 keyword：intx 是 ID，不拆成 int + x。
            if (w == "int") cout << "INT\n";
            else if (w == "float") cout << "FLOAT\n";
            else if (w == "print") cout << "PRINT\n";
            else cout << "ID " << w << '\n';
        } else if (isdigit(c)) {
            // INUM -> 0 | [1-9][0-9]*：開頭 0 只吃一位，007 切成 INUM 0、INUM 0、INUM 7。
            ++p;
            if (c != '0') while (digit(p)) ++p;
            // FNUM -> INUM . [0-9]+：小數點後至少一位數字才算。
            bool fnum = p < s.size() && s[p] == '.' && digit(p + 1);
            if (fnum) for (++p; digit(p); ++p) {}
            cout << (fnum ? "FNUM " : "INUM ") << s.substr(start, p - start) << '\n';
        } else {
            ++p;
            switch (c) {
                case '=': cout << "ASSIGN\n"; break;
                case '+': cout << "PLUS\n";   break;
                case '-': cout << "MINUS\n";  break;
                case ';': cout << "SEMI\n";   break;
                // 題目保證沒有錯誤資料；非法字元直接結束。
                default: return 1;
            }
        }
    }
}
