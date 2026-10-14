// Generic epsilon-NFA. Header: n m start k; k finals; alphabet; m edges.
// States 0..n-1. Edge symbol '#' means epsilon. Then one complete word per line.
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using States = set<int>;
struct NFA {
    int start = 0;
    States finals;
    string alphabet;
    vector<map<char, States>> edges;
    States closure(States states) const {
        vector<int> pending(states.begin(), states.end());
        while (!pending.empty()) {
            const int s = pending.back(); pending.pop_back();
            const auto it = edges[s].find('#');
            if (it != edges[s].end()) for (int next : it->second) if (states.insert(next).second) pending.push_back(next);
        }
        return states;
    }
    States move(const States& states, char c) const {
        States result;
        for (int s : states) {
            const auto it = edges[s].find(c);
            if (it != edges[s].end()) result.insert(it->second.begin(), it->second.end());
        }
        return result;
    }
    bool accepts(const States& states) const { for (int s : states) if (finals.count(s)) return true; return false; }
};
struct DFA { vector<States> states; vector<vector<int>> next; };
DFA construct(const NFA& nfa) {
    DFA dfa; map<States, int> ids;
    const auto record = [&](const States& states) {
        const auto it = ids.find(states);
        if (it != ids.end()) return it->second;
        // ponytail: subset construction can be exponential; fail explicitly above this study ceiling.
        if (dfa.states.size() >= 4096) throw runtime_error("DFA exceeds 4096 states");
        const int id = static_cast<int>(dfa.states.size());
        ids[states] = id; dfa.states.push_back(states); dfa.next.emplace_back(nfa.alphabet.size(), 0);
        return id;
    };
    record(nfa.closure({nfa.start}));
    for (size_t i = 0; i < dfa.states.size(); ++i) for (size_t c = 0; c < nfa.alphabet.size(); ++c) {
        const int target = record(nfa.closure(nfa.move(dfa.states[i], nfa.alphabet[c])));
        dfa.next[i][c] = target;
    }
    return dfa;
}
void print_set(const States& states) {
    cout << '{'; bool first = true;
    for (int s : states) { if (!first) cout << ','; cout << s; first = false; }
    cout << '}';
}
int main(int argc, char** argv) {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    try {
        const string mode = argc == 1 ? "--check" : argv[1];
        if (argc > 2 || (mode != "--check" && mode != "--table" && mode != "--trace")) throw runtime_error("usage: nfa_to_dfa [--check|--table|--trace]");
        NFA nfa; int n, m, k;
        if (!(cin >> n >> m >> nfa.start >> k) || n < 1 || n > 256 || m < 0 || m > 65536 || k < 0 || k > n)
            throw runtime_error("invalid NFA header (n<=256, m<=65536)");
        const auto valid = [&](int s) { return s >= 0 && s < n; };
        if (!valid(nfa.start)) throw runtime_error("invalid start state");
        for (int i = 0, s; i < k; ++i) {
            if (!(cin >> s) || !valid(s) || !nfa.finals.insert(s).second) throw runtime_error("invalid/duplicate final state");
        }
        if (!(cin >> nfa.alphabet) || nfa.alphabet.find('#') != string::npos ||
            set<char>(nfa.alphabet.begin(), nfa.alphabet.end()).size() != nfa.alphabet.size()) throw runtime_error("invalid alphabet");
        nfa.edges.resize(static_cast<size_t>(n));
        for (int i = 0; i < m; ++i) {
            int from, to; string symbol;
            if (!(cin >> from >> symbol >> to) || !valid(from) || !valid(to) || symbol.size() != 1 ||
                (symbol != "#" && nfa.alphabet.find(symbol[0]) == string::npos)) throw runtime_error("invalid edge");
            nfa.edges[from][symbol[0]].insert(to);
        }
        string line; getline(cin, line);
        if (line.find_first_not_of(" \t\r") != string::npos) throw runtime_error("words must start on the next line");
        const auto dfa = construct(nfa);
        if (mode == "--table") {
            cout << "DFA start=0 states=" << dfa.states.size() << '\n';
            for (size_t i = 0; i < dfa.states.size(); ++i) {
                cout << i << ' '; print_set(dfa.states[i]);
                cout << (nfa.accepts(dfa.states[i]) ? " accept" : " reject");
                for (size_t c = 0; c < nfa.alphabet.size(); ++c) cout << ' ' << nfa.alphabet[c] << "->" << dfa.next[i][c];
                cout << '\n';
            }
        } else while (getline(cin, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            int state = 0; States nstates = nfa.closure({nfa.start}); bool valid_word = true;
            if (mode == "--trace") { print_set(nstates); }
            for (char c : line) {
                const auto index = nfa.alphabet.find(c);
                if (index == string::npos) { valid_word = false; if (mode == "--trace") cout << " --invalid--> {}"; break; }
                state = dfa.next[state][index]; nstates = nfa.closure(nfa.move(nstates, c));
                if (mode == "--trace") { cout << " --" << c << "--> "; print_set(nstates); }
            }
            if (valid_word && nfa.accepts(nstates) != nfa.accepts(dfa.states[state])) throw runtime_error("NFA/DFA mismatch");
            if (mode == "--trace") cout << ' ';
            cout << (valid_word && nfa.accepts(dfa.states[state]) ? "ACCEPT\n" : "REJECT\n");
        }
        if (cin.bad()) throw runtime_error("input read failed");
        return cout ? 0 : 1;
    } catch (const exception& e) { cerr << "error: " << e.what() << '\n'; return 1; }
}
