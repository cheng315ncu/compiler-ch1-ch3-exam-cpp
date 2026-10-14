// Ch3 HW5(d)/(a): original NFA edges -> subset construction -> complete DFA.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;
using Set = uint32_t;
struct Edge { int from; char symbol; int to; };
struct NFA { string alphabet; int start, final; vector<Edge> edges; };
struct DFA { vector<Set> states; vector<vector<int>> next; };
Set bit(int state) { return Set{1} << state; }
Set move(const NFA& nfa, Set states, char symbol) {
    Set result = 0;
    for (const auto& e : nfa.edges) if ((states & bit(e.from)) && e.symbol == symbol) result |= bit(e.to);
    return result;
}
Set closure(const NFA& nfa, Set states) {
    while (true) {
        const Set next = states | move(nfa, states, '\0');
        if (next == states) return states;
        states = next;
    }
}
DFA construct(const NFA& nfa) {
    DFA dfa;
    const auto record = [&](Set states) {
        const auto it = find(dfa.states.begin(), dfa.states.end(), states);
        if (it != dfa.states.end()) return static_cast<int>(it - dfa.states.begin());
        dfa.states.push_back(states);
        dfa.next.emplace_back(nfa.alphabet.size(), 0);
        return static_cast<int>(dfa.states.size()) - 1;
    };
    record(closure(nfa, bit(nfa.start)));
    for (size_t i = 0; i < dfa.states.size(); ++i) {
        for (size_t c = 0; c < nfa.alphabet.size(); ++c) {
            const int target = record(closure(nfa, move(nfa, dfa.states[i], nfa.alphabet[c])));
            dfa.next[i][c] = target; // record may reallocate; assign afterward.
        }
    }
    return dfa;
}
bool accepts_nfa(const NFA& nfa, const string& word) {
    Set states = closure(nfa, bit(nfa.start));
    for (char c : word) {
        if (nfa.alphabet.find(c) == string::npos) return false;
        states = closure(nfa, move(nfa, states, c));
    }
    return (states & bit(nfa.final)) != 0;
}
bool accepts_dfa(const NFA& nfa, const DFA& dfa, const string& word) {
    int state = 0;
    for (char c : word) {
        const auto index = nfa.alphabet.find(c);
        if (index == string::npos) return false;
        state = dfa.next[state][index];
    }
    return (dfa.states[state] & bit(nfa.final)) != 0;
}
void print_set(Set states) {
    cout << '{'; bool first = true;
    for (int i = 1; i <= 12; ++i) if (states & bit(i)) {
        if (!first) cout << ',';
        cout << i; first = false;
    }
    cout << '}';
}
int main(int argc, char** argv) {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    try {
        if (argc < 2 || argc > 3 || (string(argv[1]) != "5d" && string(argv[1]) != "5a") ||
            (argc == 3 && string(argv[2]) != "--table"))
            throw runtime_error("usage: automata_homework 5d|5a [--table]");
        // ponytail: fixed homework NFAs fit 32 bits; use a dynamic set for >=32 states.
        const NFA nfa = string(argv[1]) == "5d"
            ? NFA{"bcd", 1, 6, {{1,0,2},{1,0,5},{2,'b',3},{3,'c',4},{4,0,2},{4,0,5},{5,'d',6}}}
            : NFA{"abcd", 1, 12, {{1,0,2},{2,0,3},{2,0,6},{3,'a',4},{4,0,5},{5,0,2},{5,0,12},
                {6,0,7},{6,0,10},{7,'b',8},{8,'c',9},{9,0,7},{9,0,10},{10,'d',11},{11,0,5}}};
        const auto dfa = construct(nfa);
        if (argc == 3) {
            cout << "NFA start=" << nfa.start << " final=" << nfa.final << '\n';
            for (const auto& edge : nfa.edges) cout << edge.from << ' ' << (edge.symbol ? string(1, edge.symbol) : "epsilon") << ' ' << edge.to << '\n';
            cout << "DFA start=0 states=" << dfa.states.size() << '\n';
            for (size_t i = 0; i < dfa.states.size(); ++i) {
                cout << i << ' '; print_set(dfa.states[i]);
                cout << ((dfa.states[i] & bit(nfa.final)) ? " accept" : " reject");
                for (size_t c = 0; c < nfa.alphabet.size(); ++c) cout << ' ' << nfa.alphabet[c] << "->" << dfa.next[i][c];
                cout << '\n';
            }
        } else {
            string word;
            while (getline(cin, word)) {
                if (!word.empty() && word.back() == '\r') word.pop_back();
                const bool result = accepts_dfa(nfa, dfa, word);
                if (result != accepts_nfa(nfa, word)) throw runtime_error("NFA/DFA disagreement");
                cout << (result ? "ACCEPT\n" : "REJECT\n");
            }
            if (cin.bad()) throw runtime_error("input read failed");
        }
        return cout ? 0 : 1;
    } catch (const exception& error) { cerr << "error: " << error.what() << '\n'; return 1; }
}
