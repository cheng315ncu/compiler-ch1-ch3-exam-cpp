// Ch3 HW5(d)/(a): original NFA edges -> subset construction -> complete DFA.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Set = std::uint32_t;
struct Edge { int from; char symbol; int to; };
struct NFA { std::string alphabet; int start, final; std::vector<Edge> edges; };
struct DFA { std::vector<Set> states; std::vector<std::vector<int>> next; };
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
        const auto it = std::find(dfa.states.begin(), dfa.states.end(), states);
        if (it != dfa.states.end()) return static_cast<int>(it - dfa.states.begin());
        dfa.states.push_back(states);
        dfa.next.emplace_back(nfa.alphabet.size(), 0);
        return static_cast<int>(dfa.states.size()) - 1;
    };
    record(closure(nfa, bit(nfa.start)));
    for (std::size_t i = 0; i < dfa.states.size(); ++i) {
        for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) {
            const int target = record(closure(nfa, move(nfa, dfa.states[i], nfa.alphabet[c])));
            dfa.next[i][c] = target; // record may reallocate; assign afterward.
        }
    }
    return dfa;
}
bool accepts_nfa(const NFA& nfa, const std::string& word) {
    Set states = closure(nfa, bit(nfa.start));
    for (char c : word) {
        if (nfa.alphabet.find(c) == std::string::npos) return false;
        states = closure(nfa, move(nfa, states, c));
    }
    return (states & bit(nfa.final)) != 0;
}
bool accepts_dfa(const NFA& nfa, const DFA& dfa, const std::string& word) {
    int state = 0;
    for (char c : word) {
        const auto index = nfa.alphabet.find(c);
        if (index == std::string::npos) return false;
        state = dfa.next[state][index];
    }
    return (dfa.states[state] & bit(nfa.final)) != 0;
}
void print_set(Set states) {
    std::cout << '{'; bool first = true;
    for (int i = 1; i <= 12; ++i) if (states & bit(i)) {
        if (!first) std::cout << ',';
        std::cout << i; first = false;
    }
    std::cout << '}';
}
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        if (argc < 2 || argc > 3 || (std::string(argv[1]) != "5d" && std::string(argv[1]) != "5a") ||
            (argc == 3 && std::string(argv[2]) != "--table"))
            throw std::runtime_error("usage: automata_homework 5d|5a [--table]");
        // ponytail: fixed homework NFAs fit 32 bits; use a dynamic set for >=32 states.
        const NFA nfa = std::string(argv[1]) == "5d"
            ? NFA{"bcd", 1, 6, {{1,0,2},{1,0,5},{2,'b',3},{3,'c',4},{4,0,2},{4,0,5},{5,'d',6}}}
            : NFA{"abcd", 1, 12, {{1,0,2},{2,0,3},{2,0,6},{3,'a',4},{4,0,5},{5,0,2},{5,0,12},
                {6,0,7},{6,0,10},{7,'b',8},{8,'c',9},{9,0,7},{9,0,10},{10,'d',11},{11,0,5}}};
        const auto dfa = construct(nfa);
        if (argc == 3) {
            std::cout << "NFA start=" << nfa.start << " final=" << nfa.final << '\n';
            for (const auto& edge : nfa.edges) std::cout << edge.from << ' ' << (edge.symbol ? std::string(1, edge.symbol) : "epsilon") << ' ' << edge.to << '\n';
            std::cout << "DFA start=0 states=" << dfa.states.size() << '\n';
            for (std::size_t i = 0; i < dfa.states.size(); ++i) {
                std::cout << i << ' '; print_set(dfa.states[i]);
                std::cout << ((dfa.states[i] & bit(nfa.final)) ? " accept" : " reject");
                for (std::size_t c = 0; c < nfa.alphabet.size(); ++c) std::cout << ' ' << nfa.alphabet[c] << "->" << dfa.next[i][c];
                std::cout << '\n';
            }
        } else {
            std::string word;
            while (std::getline(std::cin, word)) {
                if (!word.empty() && word.back() == '\r') word.pop_back();
                const bool result = accepts_dfa(nfa, dfa, word);
                if (result != accepts_nfa(nfa, word)) throw std::runtime_error("NFA/DFA disagreement");
                std::cout << (result ? "ACCEPT\n" : "REJECT\n");
            }
            if (std::cin.bad()) throw std::runtime_error("input read failed");
        }
        return std::cout ? 0 : 1;
    } catch (const std::exception& error) { std::cerr << "error: " << error.what() << '\n'; return 1; }
}
