// Generic epsilon-NFA. Header: n m start k; k finals; alphabet; m edges.
// States 0..n-1. Edge symbol '#' means epsilon. Then one complete word per line.
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using States = std::set<int>;
struct NFA {
    int start = 0;
    States finals;
    std::string alphabet;
    std::vector<std::map<char, States>> edges;
    States closure(States states) const {
        std::vector<int> pending(states.begin(), states.end());
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
struct DFA { std::vector<States> states; std::vector<std::vector<int>> next; };
DFA construct(const NFA& nfa) {
    DFA dfa; std::map<States, int> ids;
    const auto record = [&](const States& states) {
        const auto it = ids.find(states);
        if (it != ids.end()) return it->second;
        // ponytail: subset construction can be exponential; fail explicitly above this study ceiling.
        if (dfa.states.size() >= 4096) throw std::runtime_error("DFA exceeds 4096 states");
        const int id = static_cast<int>(dfa.states.size());
        ids[states] = id; dfa.states.push_back(states); dfa.next.emplace_back(nfa.alphabet.size(), 0);
        return id;
    };
    record(nfa.closure({nfa.start}));
    for (std::size_t i = 0; i < dfa.states.size(); ++i) for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) {
        const int target = record(nfa.closure(nfa.move(dfa.states[i], nfa.alphabet[c])));
        dfa.next[i][c] = target;
    }
    return dfa;
}
void print_set(const States& states) {
    std::cout << '{'; bool first = true;
    for (int s : states) { if (!first) std::cout << ','; std::cout << s; first = false; }
    std::cout << '}';
}
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        const std::string mode = argc == 1 ? "--check" : argv[1];
        if (argc > 2 || (mode != "--check" && mode != "--table" && mode != "--trace")) throw std::runtime_error("usage: nfa_to_dfa [--check|--table|--trace]");
        NFA nfa; int n, m, k;
        if (!(std::cin >> n >> m >> nfa.start >> k) || n < 1 || n > 256 || m < 0 || m > 65536 || k < 0 || k > n)
            throw std::runtime_error("invalid NFA header (n<=256, m<=65536)");
        const auto valid = [&](int s) { return s >= 0 && s < n; };
        if (!valid(nfa.start)) throw std::runtime_error("invalid start state");
        for (int i = 0, s; i < k; ++i) {
            if (!(std::cin >> s) || !valid(s) || !nfa.finals.insert(s).second) throw std::runtime_error("invalid/duplicate final state");
        }
        if (!(std::cin >> nfa.alphabet) || nfa.alphabet.find('#') != std::string::npos ||
            std::set<char>(nfa.alphabet.begin(), nfa.alphabet.end()).size() != nfa.alphabet.size()) throw std::runtime_error("invalid alphabet");
        nfa.edges.resize(static_cast<std::size_t>(n));
        for (int i = 0; i < m; ++i) {
            int from, to; std::string symbol;
            if (!(std::cin >> from >> symbol >> to) || !valid(from) || !valid(to) || symbol.size() != 1 ||
                (symbol != "#" && nfa.alphabet.find(symbol[0]) == std::string::npos)) throw std::runtime_error("invalid edge");
            nfa.edges[from][symbol[0]].insert(to);
        }
        std::string line; std::getline(std::cin, line);
        if (line.find_first_not_of(" \t\r") != std::string::npos) throw std::runtime_error("words must start on the next line");
        const auto dfa = construct(nfa);
        if (mode == "--table") {
            std::cout << "DFA start=0 states=" << dfa.states.size() << '\n';
            for (std::size_t i = 0; i < dfa.states.size(); ++i) {
                std::cout << i << ' '; print_set(dfa.states[i]);
                std::cout << (nfa.accepts(dfa.states[i]) ? " accept" : " reject");
                for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) std::cout << ' ' << nfa.alphabet[c] << "->" << dfa.next[i][c];
                std::cout << '\n';
            }
        } else while (std::getline(std::cin, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            int state = 0; States nstates = nfa.closure({nfa.start}); bool valid_word = true;
            if (mode == "--trace") { print_set(nstates); }
            for (char c : line) {
                const auto index = nfa.alphabet.find(c);
                if (index == std::string::npos) { valid_word = false; if (mode == "--trace") std::cout << " --invalid--> {}"; break; }
                state = dfa.next[state][index]; nstates = nfa.closure(nfa.move(nstates, c));
                if (mode == "--trace") { std::cout << " --" << c << "--> "; print_set(nstates); }
            }
            if (valid_word && nfa.accepts(nstates) != nfa.accepts(dfa.states[state])) throw std::runtime_error("NFA/DFA mismatch");
            if (mode == "--trace") std::cout << ' ';
            std::cout << (valid_word && nfa.accepts(dfa.states[state]) ? "ACCEPT\n" : "REJECT\n");
        }
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
