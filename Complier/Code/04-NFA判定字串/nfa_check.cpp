// n m start k; k finals; alphabet; m edges (from symbol to); words, one per line.
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
// 用 set 去重：NFA 同一時間可能在多個 state；不能只用一個 int。
using States = set<int>;
// edges[from][symbol] 保存全部可達 state；# 專門表示 epsilon。
vector<map<char, States>> edges;
void fail() { throw runtime_error("invalid NFA input"); }
// epsilon-closure：不用讀字元也能走的邊，必須一直追到固定點。
States closure(States states) {
    // todo 是待展開 state；只有新插入的 state 才進 todo，避免 epsilon cycle 無限迴圈。
    vector<int> todo(states.begin(), states.end());
    while (!todo.empty()) {
        int from = todo.back(); todo.pop_back();
        for (int to : edges[from]['#']) if (states.insert(to).second) todo.push_back(to);
    }
    return states;
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    try {
        // n=state 數，m=edge 數，start=起點，k=接受 state 數。
        int n, m, start, k;
        if (!(cin >> n >> m >> start >> k) || n < 1 || n > 256 || m < 0 || m > 65536 || k < 0 || k > n) fail();
        // state 使用 0-based；換成 1-based 時，也要把 edges 容量加一。
        auto valid = [n](int state) { return state >= 0 && state < n; };
        if (!valid(start)) fail();
        States finals;
        for (int i = 0, state; i < k; ++i) if (!(cin >> state) || !valid(state) || !finals.insert(state).second) fail();
        string alphabet;
        // alphabet 不能重複也不能含 epsilon 符號；每個輸入字元才有明確合法性。
        if (!(cin >> alphabet) || alphabet.find('#') != string::npos ||
            set<char>(alphabet.begin(), alphabet.end()).size() != alphabet.size()) fail();
        // 先按 n 配好容量，輸入每條 edge 時再驗證起終點索引。
        edges.resize(n);
        for (int i = 0; i < m; ++i) {
            int from, to; string symbol;
            if (!(cin >> from >> symbol >> to) || !valid(from) || !valid(to) || symbol.size() != 1 ||
                (symbol != "#" && alphabet.find(symbol[0]) == string::npos)) fail();
            // 同一 from / symbol 可以有多個 to；set 也會自動移除重複 edge。
            edges[from][symbol[0]].insert(to);
        }
        // 混用 >> 與 getline：先吃完轉移表最後一行，才開始讀案例。
        string word; getline(cin, word);
        if (word.find_first_not_of(" \t\r") != string::npos) fail();
        while (getline(cin, word)) {
            // 只去掉 CRLF 的尾端 CR；不要刪普通空白，因為空白可能是非法字元。
            if (!word.empty() && word.back() == '\r') word.pop_back();
            // 每案重新建立起始 closure；空行也需照樣檢查是否接受 epsilon。
            States states = closure({start});
            for (char c : word) {
                // 字母表外字元不接受；不嘗試跳過它以匹配剩餘前綴。
                if (alphabet.find(c) == string::npos) { states.clear(); break; }
                // move 收集目前所有 state 的 c 邊，不先挑某一條路。
                States next;
                for (int from : states) next.insert(edges[from][c].begin(), edges[from][c].end());
                // 讀一字元後再展開 epsilon；否則會漏掉先 c 再 epsilon 的路徑。
                states = closure(next);
            }
            // 必須讀完整字串才判定；中途碰到 final 但之後走死仍然拒絕。
            bool accepted = false;
            for (int state : states) if (finals.count(state)) accepted = true;
            cout << (accepted ? "ACCEPT\n" : "REJECT\n");
        }
        if (cin.bad()) fail();
        return cout ? 0 : 1;
    } catch (const exception& e) { cerr << e.what() << '\n'; return 1; }
}
