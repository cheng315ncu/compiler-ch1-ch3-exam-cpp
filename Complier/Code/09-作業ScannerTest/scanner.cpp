// ScannerTest：把一條運算式切成 NUM / PLUS / MINUS / MUL / DIV / LPR / RPR，每個 token 一行。
#include <cctype>
#include <iostream>
#include <string>
using namespace std;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    // cin.get() 回傳 0..255 或 EOF，可直接交給 isspace / isdigit。
    int c = cin.get();
    while (c != EOF) {
        // 跳過空白、換行、tab；CR 也算空白，所以 CRLF 輸入不受影響。
        if (isspace(c)) { c = cin.get(); continue; }
        if (isdigit(c)) {
            // NUM -> 0 | [1-9][0-9]*：開頭 0 只吃一位，"012" 會切成 NUM 0、NUM 12。
            string num(1, char(c));
            c = cin.get();
            if (num != "0") while (isdigit(c)) { num += char(c); c = cin.get(); }
            cout << "NUM " << num << '\n';
            // c 已經是下一個未處理的字元，不能再讀一次。
            continue;
        }
        switch (c) {
            case '+': cout << "PLUS\n";  break;
            case '-': cout << "MINUS\n"; break;
            case '*': cout << "MUL\n";   break;
            case '/': cout << "DIV\n";   break;
            case '(': cout << "LPR\n";   break;
            case ')': cout << "RPR\n";   break;
            // 題目保證沒有錯誤資料；遇到非法字元就停止，已印出的 token 保留。
            default: return 1;
        }
        c = cin.get();
    }
}
