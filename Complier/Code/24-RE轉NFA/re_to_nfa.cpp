// RE → NFA（Thompson）。第一行是 RE，輸出 04 nfa_check／13 nfa_to_dfa 的輸入格式；
// 其後各行（測試字串）原樣接在後面，所以 ./main < x.in | ../04-NFA判定字串/main 可直接判定。
// RE 語法：| 聯集、串接、* + ? 後置、( ) 分組、# 是 λ，其他非空白字元都是字母；空白忽略。
#include <algorithm>
#include <cctype>
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

struct Frag { int s, f; };            // 每段 NFA 只有一個入口 s、一個出口 f
struct Edge { int from; char sym; int to; };
string re; size_t p = 0;
int n = 0; vector<Edge> edges; set<char> alphabet;

int state() { return n++; }
char peek() { return p < re.size() ? re[p] : '\0'; }
Frag alt();
// atom -> ( alt ) | # | 字元
Frag atom() {
    const char c = peek();
    if (c == '(') { ++p; Frag a = alt(); if (peek() != ')') throw runtime_error("missing )"); ++p; return a; }
    if (c == '\0' || string("|)*+?").find(c) != string::npos) throw runtime_error("expected symbol");
    ++p; Frag a{state(), state()};
    edges.push_back({a.s, c, a.f});
    if (c != '#') alphabet.insert(c);
    return a;
}
// post -> atom { * | + | ? }：新入口 s、新出口 f 包住 a。
Frag post() {
    Frag a = atom();
    for (char op; (op = peek()) == '*' || op == '+' || op == '?'; ++p) {
        Frag b{state(), state()};
        edges.push_back({b.s, '#', a.s}); edges.push_back({a.f, '#', b.f});
        if (op != '?') edges.push_back({a.f, '#', a.s});   // 重複邊：* 與 +
        if (op != '+') edges.push_back({b.s, '#', b.f});   // 零次旁路：* 與 ?
        a = b;
    }
    return a;
}
// cat -> post { post }：前段出口 λ 接後段入口。
Frag cat() {
    Frag a = post();
    while (peek() != '\0' && peek() != '|' && peek() != ')') { Frag b = post(); edges.push_back({a.f, '#', b.s}); a.f = b.f; }
    return a;
}
// alt -> cat { | cat }：新入口 λ 分到兩邊，兩個出口 λ 到新出口。
Frag alt() {
    Frag a = cat();
    while (peek() == '|') {
        ++p; Frag b = cat(), c{state(), state()};
        edges.insert(edges.end(), {{c.s, '#', a.s}, {c.s, '#', b.s}, {a.f, '#', c.f}, {b.f, '#', c.f}});
        a = c;
    }
    return a;
}

int main() {
    try {
        if (!getline(cin, re)) throw runtime_error("missing RE");
        re.erase(remove_if(re.begin(), re.end(), [](unsigned char c) { return isspace(c); }), re.end());
        Frag a = alt();
        if (p != re.size()) throw runtime_error("unexpected )");
        cout << n << ' ' << edges.size() << ' ' << a.s << " 1\n" << a.f << '\n';
        for (char c : alphabet) cout << c;
        cout << '\n';
        for (const auto& e : edges) cout << e.from << ' ' << e.sym << ' ' << e.to << '\n';
        cout << string(istreambuf_iterator<char>(cin), {});
    } catch (const exception& e) { cerr << "error: " << e.what() << '\n'; return 1; }
}
