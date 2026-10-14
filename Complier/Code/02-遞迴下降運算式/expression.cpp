// One expression per line. Change MODE to "postfix" or "ast" for those tasks.
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
// 選一種題目輸出：eval=數值；postfix=後序式；ast=括號 AST。
// 精度設定是有效數字，並非固定小數位；固定小數位要另外使用 fixed。
const string MODE = "eval";
string s;
size_t p;
// 每次完成子運算後才記錄 operator，因此順序自然是左、右、根。
vector<string> postfix;
// 回傳目前子運算式的表示；只在選中的模式建立 AST 或計算 number。
struct Value { string ast; long double number; };
bool digit(char c) { return c >= '0' && c <= '9'; }
bool letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_'; }
void fail() { throw runtime_error("invalid expression"); }
// peek 先跳空白，所以每層文法不必重複處理空格與 CR。
void skip() { while (p < s.size() && string(" \t\r\n").find(s[p]) != string::npos) ++p; }
// EOF 以零字元回報；main 還會確認游標位置，拒絕內嵌 NUL。
char peek() { skip(); return p < s.size() ? s[p] : '\0'; }
Value expr(int depth);
// 遞迴下降（recursive descent）：每個函式對應一層優先序。
// 括號與連續一元正負會增加遞迴深度，長二元加減鏈則用迴圈。
Value unary(int depth) {
    // ponytail: nested parentheses/unary <= 256; use the iterative full version above that.
    if (depth > 256) fail();
    char c = peek();
    // 這裡出現的 + / - 位於 operand 前，是一元運算；-2 的 postfix 是 2 neg。
    if (c == '+' || c == '-') {
        ++p; Value v = unary(depth + 1);
        string op = c == '-' ? "neg" : "pos";
        postfix.push_back(op);
        if (MODE == "ast") v.ast = "(" + op + " " + v.ast + ")";
        if (c == '-') v.number = -v.number;
        return v;
    }
    // 括號內重新從 expr 開始；結束時必須消耗配對的 )。
    // 括號只控制結構，不會成為 AST 節點或 postfix operator。
    if (c == '(') {
        ++p; Value v = expr(depth + 1);
        if (peek() != ')') fail();
        ++p; return v;
    }
    size_t start = p;
    // 變數可以用於 AST / postfix；eval 沒有環境表，因此拒絕變數。
    bool id = letter(c);
    if (id) { while (p < s.size() && (letter(s[p]) || digit(s[p]))) ++p; }
    else {
        // 本題 number 允許 .5 與 10.；此規則與 ac 的必須有小數尾數不同。
        if (!digit(c) && !(c == '.' && p + 1 < s.size() && digit(s[p + 1]))) fail();
        while (p < s.size() && digit(s[p])) ++p;
        if (p < s.size() && s[p] == '.') { ++p; while (p < s.size() && digit(s[p])) ++p; }
        // e/E 後可有正負號，但必須至少一個數字；1e+ 不合法。
        if (p < s.size() && (s[p] == 'e' || s[p] == 'E')) {
            ++p; if (p < s.size() && (s[p] == '+' || s[p] == '-')) ++p;
            if (p == s.size() || !digit(s[p])) fail();
            while (p < s.size() && digit(s[p])) ++p;
        }
    }
    string text = s.substr(start, p - start);
    postfix.push_back(text);
    Value v{MODE == "ast" ? text : "", 0};
    // 數字必須完整轉換成功且為有限值；不能把 12abc 默默當作 12。
    if (MODE == "eval") {
        istringstream input(text);
        if (id || !(input >> v.number) || input.peek() != char_traits<char>::eof() || !isfinite(v.number)) fail();
    }
    return v;
}
// 先讀完右 operand，再合併左／右；op 的方向對減法、除法非常重要。
Value combine(Value a, char op, Value b) {
    postfix.push_back(string(1, op));
    // ponytail: AST strings can cost O(n^2); use the arena version for huge AST output.
    if (MODE == "ast") a.ast = "(" + string(1, op) + " " + a.ast + " " + b.ast + ")";
    if (MODE == "eval") {
        if (op == '+') a.number += b.number;
        if (op == '-') a.number -= b.number;
        if (op == '*') a.number *= b.number;
        // 除法的右 operand 不可是零；結果溢位成無限大也拒絕。
        if (op == '/') { if (b.number == 0) fail(); a.number /= b.number; }
        if (!isfinite(a.number)) fail();
    }
    // AST 不保留括號 token；節點的父子關係已記錄優先序。
    return a;
}
// term 只處理乘除，先完成高優先序，再交回 expr。
Value term(int depth) {
    Value v = unary(depth);
    while (peek() == '*' || peek() == '/') { char op = s[p++]; Value b = unary(depth); v = combine(v, op, b); }
    return v;
}
// while 每次用前次結果當左 operand，所以 100-30-1 是 (100-30)-1。
Value expr(int depth) {
    Value v = term(depth);
    while (peek() == '+' || peek() == '-') { char op = s[p++]; Value b = term(depth); v = combine(v, op, b); }
    return v;
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    // 先暫存所有答案；其中一行有錯時，不送出前面已算的部分答案。
    ostringstream out; out << setprecision(15);
    try {
        while (getline(cin, s)) {
            // 每行是一案，游標與 postfix 必須清空，不能沿用上一案。
            p = 0; postfix.clear(); Value v = expr(0);
            // 成功解析前綴不代表整行合法；2(3)、1abc 或多出的 ) 仍要拒絕。
            if (peek() != '\0' || p != s.size()) fail();
            if (MODE == "eval") out << (v.number == 0 ? 0 : v.number) << '\n';
            if (MODE == "ast") out << v.ast << '\n';
            if (MODE == "postfix") {
                for (size_t i = 0; i < postfix.size(); ++i) out << (i ? " " : "") << postfix[i];
                out << '\n';
            }
        }
        if (cin.bad()) fail();
        cout << out.str(); return cout ? 0 : 1;
    } catch (const exception& e) { cerr << e.what() << '\n'; return 1; }
}
