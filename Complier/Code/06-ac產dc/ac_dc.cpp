// ac -> dc, with type checks. No trees or constant folding in this short version.
#include <array>
#include <iostream>
#include <iterator>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using namespace std;
// kind 壓成一字元：i/f=宣告、p=print、v=單字母變數、n=number、$=EOF。
struct Token { char kind; string text; };
vector<Token> tokens;
size_t p = 0;
// 符號表（symbol table）直接用字母偏移；0 表示未宣告。
array<char, 26> types{}; // 0=undeclared, i=int, f=float.
void fail() { throw runtime_error("invalid ac program"); }
// 負數不作為 leaf literal；原 ac 要寫 0-數字，e 的負號則屬於 exponent。
bool digit(char c) { return c >= '0' && c <= '9'; }
// 先 tokenize 整份 ac；沒有分號，宣告與敘述的邊界由 token kind 判定。
void scan(const string& s) {
    for (size_t j = 0; j < s.size();) {
        if (string(" \t\r\n\v\f").find(s[j]) != string::npos) { ++j; continue; }
        size_t start = j;
        char kind = s[j];
        if (digit(s[j])) {
            kind = 'n';
            while (j < s.size() && digit(s[j])) ++j;
            // ac 小數要求點後有數字；1. 不合法，與 expression 補充文法不同。
            if (j < s.size() && s[j] == '.') {
                ++j; if (j == s.size() || !digit(s[j])) fail();
                while (j < s.size() && digit(s[j])) ++j;
            }
            // 科學記號 e 後可帶正負；即使 1e0 數值是整數，型別仍是 float。
            if (j < s.size() && s[j] == 'e') {
                ++j; if (j < s.size() && (s[j] == '+' || s[j] == '-')) ++j;
                if (j == s.size() || !digit(s[j])) fail();
                while (j < s.size() && digit(s[j])) ++j;
            }
        } else {
            ++j;
            // 保留教材一字母 ID 與最長 keyword 前綴：floatx 切 float + x。
            if (kind == 'f' && s.compare(start, 5, "float") == 0) j = start + 5;
            else if (kind == 'i' && s.compare(start, 3, "int") == 0) j = start + 3;
            else if ((kind >= 'a' && kind <= 'z') || kind == '=' || kind == '+' || kind == '-') {}
            else fail();
            if (kind >= 'a' && kind <= 'z' && kind != 'i' && kind != 'f' && kind != 'p') kind = 'v';
        }
        tokens.push_back({kind, s.substr(start, j - start)});
    }
    // 加入 EOF sentinel，parser 可一直查看下一個 token，不必另猜輸入是否結束。
    tokens.push_back({'$', ""});
}
// dc 不直接接受 e 記號；用字串移動小數點，避免 double 先捨入。
string decimal(string text) {
    int exponent = 0;
    size_t e = text.find('e');
    if (e != string::npos) {
        size_t j = e + 1;
        bool negative = text[j] == '-';
        if (text[j] == '+' || text[j] == '-') ++j;
        for (; j < text.size(); ++j) {
            // 限制 exponent 絕對值 10000，且累積前檢查，避免 int overflow 與巨大配置。
            if (exponent > (10000 - (text[j] - '0')) / 10) fail();
            exponent = exponent * 10 + text[j] - '0';
        }
        if (negative) exponent = -exponent;
        text.resize(e);
    }
    if (text.size() > 10000) fail();
    size_t dot = text.find('.');
    // point 是移除小數點後，新的小數位置：原位置加 exponent。
    int point = static_cast<int>(dot == string::npos ? text.size() : dot) + exponent;
    if (dot != string::npos) text.erase(dot, 1);
    // 往左超過頭：補 0. 與零；往右超過尾：補尾零；中間：插回小數點。
    if (point <= 0) text = "0." + string(-point, '0') + text;
    else if (point >= static_cast<int>(text.size())) text.append(point - text.size(), '0');
    else text.insert(point, ".");
    size_t first = text.find_first_not_of('0');
    if (first == string::npos) return "0";
    return text.substr(text[first] == '.' ? first - 1 : first);
}
// id 只接受單一小寫字母變數 token；i/f/p 已是保留字。
char id() {
    if (tokens[p].kind != 'v') fail();
    return tokens[p++].text[0];
}
// 查詢型別同時拒絕未宣告變數；沒有檢查變數是否曾賦值（沿用課程規則）。
bool floating(char c) { if (!types[c - 'a']) fail(); return types[c - 'a'] == 'f'; }
// leaf 回傳 pair：first 是 target code，second 是是否 float。
pair<string, bool> value() {
    if (tokens[p].kind == 'v') {
        char c = id(); return {"l" + string(1, c) + "\n", floating(c)};
    }
    if (tokens[p].kind != 'n') fail();
    string text = tokens[p++].text;
    // 帶 . 或 e 的 number 為 float；decimal 只改表示，不改數學值。
    return {decimal(text) + "\n", text.find_first_of(".e") != string::npos};
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    try {
        string source{istreambuf_iterator<char>(cin), {}};
        if (cin.bad()) fail();
        scan(source);
        // 即使前段已產碼，也先不送出；尾端型別／語法錯誤時整份 stdout 仍為空。
        ostringstream out;
        // 宣告必須全部在敘述前；同一變數宣告兩次會拒絕。
        while (tokens[p].kind == 'i' || tokens[p].kind == 'f') {
            char type = tokens[p++].kind, c = id();
            if (types[c - 'a']) fail();
            types[c - 'a'] = type;
        }
        // 因為沒有分號，一段加減後看到 id / p 就進入下一個 statement。
        while (tokens[p].kind != '$') {
            // dc 的 p 不 pop，所以印完用 si 移走頂端；i 不會與 ac 變數衝突。
            if (tokens[p].kind == 'p') {
                ++p; char c = id(); floating(c);
                out << 'l' << c << "\np\nsi\n"; continue;
            }
            char target = id(); bool target_float = floating(target);
            if (tokens[p++].kind != '=') fail();
            // 直接輸出 operand；不建 AST。迴圈左結合，所以 x-30-1 不會變成 x-(30-1)。
            auto left = value(); out << left.first;
            while (tokens[p].kind == '+' || tokens[p].kind == '-') {
                char op = tokens[p++].kind; auto right = value();
                // 左側已累積的 int 結果需要提升：先印 conversion，再印右側 code。
                if (!left.second && right.second) out << "5 k\n";
                out << right.first;
                // 右側 int 需要提升：先印右側 code，再印 conversion；順序不能顛倒。
                if (left.second && !right.second) out << "5 k\n";
                out << op << '\n'; left.second = left.second || right.second;
            }
            // float 不能指定給 int；int 指定給 float 可提升。全部成功才送出 out。
            if (!target_float && left.second) fail();
            if (target_float && !left.second) out << "5 k\n";
            // s<變數> pop 並存暫存器；assign 完把 scale 設回 0。
            out << 's' << target << "\n0 k\n";
        }
        cout << out.str(); return cout ? 0 : 1;
    } catch (const exception& e) { cerr << e.what() << '\n'; return 1; }
}
