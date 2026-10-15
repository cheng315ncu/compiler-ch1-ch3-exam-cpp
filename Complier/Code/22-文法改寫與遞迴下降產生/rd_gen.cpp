// Grammar rewrite + recursive-descent generator. Input format is the same as 08 ll1.cpp:
// P, then P lines "A -> X Y" ('#' alone = epsilon, start = first LHS).
// Removes left recursion (direct and indirect), left-factors, then:
//   --grammar  prints the rewritten grammar in ll1.cpp input format (pipe into 08 for tables)
//   --code     (default) prints a compilable C++ recursive-descent parser for it
#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using Set = set<string>;
using Alts = vector<vector<string>>;   // 一個 nonterminal 的所有 RHS；空 RHS 代表 epsilon
map<string, Alts> g;
vector<string> order;                   // nonterminal 輸出順序：第一次出現的順序，新 A' 緊接在 A 後面

// 新 nonterminal：A → A' → A'' …，直到沒被用過。
string fresh(const string& a) {
    string t = a; do t += '\''; while (g.count(t));
    order.insert(find(order.begin(), order.end(), a) + 1, t);
    return t;
}
// A → A α | β  改成  A → β A'、A' → α A' | #。A → A 沒有意義，直接丟掉。
void remove_direct(const string& a) {
    Alts rec, base;
    for (const auto& r : g[a]) if (r != vector<string>{a}) (!r.empty() && r[0] == a ? rec : base).push_back(r);
    if (rec.empty()) { g[a] = base; return; }
    const auto t = fresh(a);
    for (auto& r : base) r.push_back(t);
    for (auto& r : rec) { r.erase(r.begin()); r.push_back(t); }
    rec.push_back({});
    g[a] = base; g[t] = rec;
}
// 課本演算法：依序處理 A_i，把 A_i → A_j γ（j < i）代入 A_j 的所有 RHS，再消直接左遞迴。
void remove_left_recursion() {
    const auto original = order;
    for (size_t i = 0; i < original.size(); ++i) {
        const auto& a = original[i];
        for (size_t j = 0; j < i; ++j) {
            Alts out;
            for (const auto& r : g[a]) {
                if (r.empty() || r[0] != original[j]) { out.push_back(r); continue; }
                for (auto d : g[original[j]]) { d.insert(d.end(), r.begin() + 1, r.end()); out.push_back(d); }
            }
            g[a] = out;
        }
        remove_direct(a);
    }
}
// A → α β1 | α β2 改成 A → α A'、A' → β1 | β2（α 取最長共同前綴）；A' 之後也會輪到。
void left_factor() {
    for (size_t k = 0; k < order.size(); ++k) {
        const auto a = order[k];
        for (size_t i = 0; i < g[a].size(); ++i) {
            const auto head = g[a][i];
            if (head.empty()) continue;
            Alts keep, tails; size_t len = head.size();
            for (const auto& r : g[a]) {
                if (r.empty() || r[0] != head[0]) { keep.push_back(r); continue; }
                size_t n = 0; while (n < len && n < r.size() && r[n] == head[n]) ++n;
                len = n; tails.push_back(r);
            }
            if (tails.size() < 2) continue;
            const auto t = fresh(a);
            for (auto& r : tails) r.erase(r.begin(), r.begin() + len);
            vector<string> factored(head.begin(), head.begin() + len); factored.push_back(t);
            // i 之前沒有同開頭的 RHS，所以合併後的規則放回位置 i。
            keep.insert(keep.begin() + i, factored);
            g[a] = keep; g[t] = tails;
        }
    }
}
// 以下 FIRST／FOLLOW／SELECT 與 08 ll1.cpp 同一套。
Set first_sequence(const vector<string>& rhs, size_t start, const map<string, Set>& first) {
    Set result;
    for (size_t i = start; i < rhs.size(); ++i) {
        const auto it = first.find(rhs[i]);
        if (it == first.end()) { result.insert(rhs[i]); return result; }
        for (const auto& t : it->second) if (t != "#") result.insert(t);
        if (!it->second.count("#")) return result;
    }
    result.insert("#"); return result;
}
bool merge(Set& target, const Set& source) { const auto before = target.size(); target.insert(source.begin(), source.end()); return target.size() != before; }
map<string, vector<Set>> select_sets() {
    map<string, Set> first, follow;
    for (const auto& a : order) { first[a] = {}; follow[a] = {}; }
    bool changed;
    do { changed = false; for (const auto& a : order) for (const auto& r : g[a]) if (merge(first[a], first_sequence(r, 0, first))) changed = true; } while (changed);
    follow[order[0]].insert("$");
    do {
        changed = false;
        for (const auto& a : order) for (const auto& r : g[a]) for (size_t i = 0; i < r.size(); ++i) {
            if (!g.count(r[i])) continue;
            auto suffix = first_sequence(r, i + 1, first);
            const bool nullable = suffix.erase("#") != 0;
            if (merge(follow[r[i]], suffix)) changed = true;
            if (nullable && merge(follow[r[i]], follow[a])) changed = true;
        }
    } while (changed);
    map<string, vector<Set>> sel;
    for (const auto& a : order) for (const auto& r : g[a]) { auto s = first_sequence(r, 0, first); if (s.erase("#")) merge(s, follow[a]); sel[a].push_back(s); }
    return sel;
}
string rhs_text(const vector<string>& r) { string s; for (const auto& x : r) s += (s.empty() ? "" : " ") + x; return s.empty() ? "#" : s; }
// E' → parse_E_p；其他非英數字元換成 _。
string fn(const string& a) { string s = "parse_"; for (unsigned char c : a) s += c == '\'' ? "_p" : isalnum(c) ? string(1, char(c)) : "_"; return s; }
string quote(const string& t) { string s = "\""; for (char c : t) { if (c == '"' || c == '\\') s += '\\'; s += c; } return s + '"'; }

int main(int argc, char** argv) {
    try {
        const string mode = argc == 1 ? "--code" : argv[1];
        if (argc > 2 || (mode != "--code" && mode != "--grammar")) throw runtime_error("usage: rd_gen [--code|--grammar]");
        int count; string line;
        if (!(cin >> count) || count < 1) throw runtime_error("expected production count");
        getline(cin, line);
        for (int i = 0; i < count; ++i) {
            if (!getline(cin, line)) throw runtime_error("missing production");
            istringstream input(line); string lhs, arrow, symbol; vector<string> rhs;
            if (!(input >> lhs >> arrow) || arrow != "->") throw runtime_error("expected A -> symbols");
            while (input >> symbol) {
                if (symbol == "$" || symbol == "|") throw runtime_error("reserved symbol; use one alternative per line");
                rhs.push_back(symbol);
            }
            if (rhs.empty() || (rhs.size() > 1 && find(rhs.begin(), rhs.end(), "#") != rhs.end())) throw runtime_error("write # alone for epsilon");
            if (rhs[0] == "#") rhs.clear();
            if (!g.count(lhs)) order.push_back(lhs);
            g[lhs].push_back(rhs);
        }
        remove_left_recursion();
        left_factor();
        if (mode == "--grammar") {
            size_t n = 0; for (const auto& a : order) n += g[a].size();
            cout << n << '\n';
            for (const auto& a : order) for (const auto& r : g[a]) cout << a << " -> " << rhs_text(r) << '\n';
            return 0;
        }
        auto sel = select_sets();
        // 同一 nonterminal 的 SELECT 重疊 → 產出的程式會選錯分支，所以不產碼。
        bool ll1 = true;
        for (const auto& a : order) for (size_t i = 0; i < g[a].size(); ++i) for (size_t j = i + 1; j < g[a].size(); ++j)
            for (const auto& t : sel[a][i]) if (sel[a][j].count(t)) {
                cerr << "CONFLICT " << a << " on " << t << ": " << rhs_text(g[a][i]) << " | " << rhs_text(g[a][j]) << '\n';
                ll1 = false;
            }
        if (!ll1) throw runtime_error("rewritten grammar is not LL(1); see --grammar and 08 ll1.cpp");
        cout << "#include <iostream>\n#include <sstream>\n#include <string>\n#include <vector>\n\nusing namespace std;\n\n"
                "// token 來源：每行空白分隔；考試時把 tok()/match() 換成自己的 scanner。if 條件就是該規則的 SELECT。\n"
                "vector<string> toks; size_t pos = 0;\n"
                "string tok() { return pos < toks.size() ? toks[pos] : \"$\"; }\n"
                "bool match(const string& t) { if (tok() != t) return false; ++pos; return true; }\n";
        for (const auto& a : order) cout << "bool " << fn(a) << "();\n";
        for (const auto& a : order) {
            cout << "\nbool " << fn(a) << "() {\n";
            for (size_t i = 0; i < g[a].size(); ++i) {
                string cond, body;
                for (const auto& t : sel[a][i]) cond += (cond.empty() ? "" : " || ") + ("tok() == " + quote(t));
                for (const auto& s : g[a][i]) body += (body.empty() ? "" : " && ") + (g.count(s) ? fn(s) + "()" : "match(" + quote(s) + ")");
                cout << "    if (" << (cond.empty() ? "false" : cond) << ") return " << (body.empty() ? "true" : body)
                     << ";  // " << a << " -> " << rhs_text(g[a][i]) << '\n';
            }
            cout << "    return false;\n}\n";
        }
        cout << "\nint main() {\n"
                "    string line;\n"
                "    while (getline(cin, line)) {\n"
                "        istringstream in(line); toks.clear(); pos = 0;\n"
                "        for (string w; in >> w;) toks.push_back(w);\n"
                "        // 一定要停在 $：只吃掉前綴不算接受。\n"
                "        cout << (" << fn(order[0]) << "() && tok() == \"$\" ? \"ACCEPT\\n\" : \"REJECT\\n\");\n"
                "    }\n"
                "}\n";
        return cout ? 0 : 1;
    } catch (const exception& e) { cerr << "error: " << e.what() << '\n'; return 1; }
}
