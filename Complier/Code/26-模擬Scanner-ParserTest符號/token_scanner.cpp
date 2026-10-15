// 模擬 ScannerTest：ParserTest 的 terminal（ID／STRLIT／LBR／RBR／DOT）逐字元串流切 token。
#include <cctype>
#include <iostream>
#include <string>
using namespace std;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int c = cin.get();
    while (c != EOF) {
        if (isspace(c)) { c = cin.get(); continue; }
        if (isalpha(c) || c == '_') {
            // ID 會多讀一個字元才知道結束；那個字元留在 c，下一輪處理。
            string id;
            while (c != EOF && (isalnum(c) || c == '_')) { id += char(c); c = cin.get(); }
            cout << "ID " << id << '\n';
            continue;
        }
        if (c == '"') {
            // STRLIT "[^"]*"：讀到下一個引號為止，中間可有空白與換行；題目保證有結尾引號。
            string str = "\"";
            while ((c = cin.get()) != EOF && c != '"') str += char(c);
            cout << "STRLIT " << str << "\"\n";
            c = cin.get();
            continue;
        }
        switch (c) {
            case '(': cout << "LBR\n"; break;
            case ')': cout << "RBR\n"; break;
            case '.': cout << "DOT\n"; break;
            // 題目保證沒有錯誤資料；遇到非法字元就停止，已印出的 token 保留。
            default: return 1;
        }
        c = cin.get();
    }
}
