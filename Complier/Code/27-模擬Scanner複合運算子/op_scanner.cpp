// 模擬 ScannerTest：複合運算子 longest match。串流版用 cin.peek() 看下一字元，符合才 get() 吃掉。
#include <cctype>
#include <iostream>
#include <string>
using namespace std;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    // 下一字元是 x 就吃掉並回傳 true；不是就不動（不能先 get 再退回）。
    auto next_is = [](char x) { if (cin.peek() != x) return false; cin.get(); return true; };
    for (int c; (c = cin.get()) != EOF;) {
        if (isspace(c)) continue;
        if (isdigit(c)) {
            // NUM -> 0 | [1-9][0-9]*，與 09 相同。
            string num(1, char(c));
            if (c != '0') while (isdigit(cin.peek())) num += char(cin.get());
            cout << "NUM " << num << '\n';
            continue;
        }
        switch (c) {
            // 兩字元的先試：+++ 是 INC PLUS，不是 PLUS INC。
            case '+': cout << (next_is('+') ? "INC\n" : next_is('=') ? "ADDASSIGN\n" : "PLUS\n"); break;
            case '-': cout << (next_is('-') ? "DEC\n" : next_is('=') ? "SUBASSIGN\n" : next_is('>') ? "ARROW\n" : "MINUS\n"); break;
            case '*': cout << (next_is('*') ? "POW\n" : "MUL\n"); break;
            case '=': cout << (next_is('=') ? "EQ\n" : "ASSIGN\n"); break;
            case '(': cout << "LPR\n"; break;
            case ')': cout << "RPR\n"; break;
            // 題目保證沒有錯誤資料；遇到非法字元就停止，已印出的 token 保留。
            default: return 1;
        }
    }
}
