// One expression per line; shunting yard builds AST, postfix, or evaluates constants.
// Grammar: expr=term{(+|-)term}; term=unary{(*|/)unary}; unary=(+|-)unary|primary.
#include <cmath>
#include <iomanip>
#include <iostream>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

bool digit(char c) { return c >= '0' && c <= '9'; }
bool letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_'; }
bool space(char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n'; }
int priority(char op) { return op == '~' || op == '`' ? 3 : op == '*' || op == '/' ? 2 : 1; }
struct Node { string value; int left, right; };
struct Expression {
    vector<Node> nodes;
    int root = -1;
    explicit Expression(const string& s) {
        vector<int> values;
        vector<char> ops;
        const auto apply = [&] {
            const char op = ops.back(); ops.pop_back();
            const bool unary = op == '~' || op == '`';
            if (values.size() < (unary ? 1u : 2u)) throw runtime_error("missing operand");
            const int right = values.back(); values.pop_back();
            int left = -1;
            if (!unary) { left = values.back(); values.pop_back(); }
            nodes.push_back({op == '~' ? "neg" : op == '`' ? "pos" : string(1, op), left, right});
            values.push_back(static_cast<int>(nodes.size()) - 1);
        };
        bool need_value = true;
        for (size_t p = 0; p < s.size();) {
            if (space(s[p])) { ++p; continue; }
            const auto start = p;
            if (digit(s[p]) || (s[p] == '.' && p + 1 < s.size() && digit(s[p + 1])) || letter(s[p])) {
                if (!need_value) throw runtime_error("missing operator");
                if (letter(s[p])) { ++p; while (p < s.size() && (letter(s[p]) || digit(s[p]))) ++p; }
                else {
                    while (p < s.size() && digit(s[p])) ++p;
                    if (p < s.size() && s[p] == '.') { ++p; while (p < s.size() && digit(s[p])) ++p; }
                    if (p < s.size() && (s[p] == 'e' || s[p] == 'E')) {
                        ++p; if (p < s.size() && (s[p] == '+' || s[p] == '-')) ++p;
                        if (p == s.size() || !digit(s[p])) throw runtime_error("missing exponent digits");
                        while (p < s.size() && digit(s[p])) ++p;
                    }
                }
                nodes.push_back({s.substr(start, p - start), -1, -1});
                values.push_back(static_cast<int>(nodes.size()) - 1); need_value = false;
                continue;
            }
            char op = s[p++];
            if (op == '(') {
                if (!need_value) throw runtime_error("missing operator before '('");
                ops.push_back(op); continue;
            }
            if (op == ')') {
                if (need_value) throw runtime_error("missing operand before ')'");
                while (!ops.empty() && ops.back() != '(') apply();
                if (ops.empty()) throw runtime_error("unmatched ')'");
                ops.pop_back(); continue;
            }
            if (string("+-*/").find(op) == string::npos) throw runtime_error("invalid expression character");
            if (need_value) {
                if (op != '+' && op != '-') throw runtime_error("missing operand");
                ops.push_back(op == '-' ? '~' : '`'); continue;
            }
            while (!ops.empty() && ops.back() != '(' && priority(ops.back()) >= priority(op)) apply();
            ops.push_back(op); need_value = true;
        }
        if (need_value) throw runtime_error("empty/incomplete expression");
        while (!ops.empty()) { if (ops.back() == '(') throw runtime_error("unmatched '('"); apply(); }
        if (values.size() != 1) throw runtime_error("invalid expression");
        root = values.back();
    }
    long double evaluate() const {
        vector<long double> values(nodes.size());
        for (size_t i = 0; i < nodes.size(); ++i) {
            const auto& n = nodes[i];
            if (n.right == -1) {
                istringstream input(n.value); input.imbue(locale::classic());
                if (!(input >> values[i]) || input.peek() != char_traits<char>::eof()) throw runtime_error("evaluation requires numeric constants");
            } else if (n.left == -1) values[i] = n.value == "neg" ? -values[n.right] : values[n.right];
            else {
                const auto a = values[n.left], b = values[n.right];
                if (n.value == "+") values[i] = a + b;
                else if (n.value == "-") values[i] = a - b;
                else if (n.value == "*") values[i] = a * b;
                else { if (b == 0) throw runtime_error("division by zero"); values[i] = a / b; }
            }
            if (!isfinite(values[i])) throw runtime_error("non-finite numeric result");
        }
        return values[root] == 0 ? 0 : values[root];
    }
    void postfix(ostream& out) const {
        // All nodes were appended after their children, in left-to-right order.
        for (size_t i = 0; i < nodes.size(); ++i) out << (i ? " " : "") << nodes[i].value;
        out << '\n';
    }
    void ast(ostream& out) const {
        vector<pair<int, char>> pending{{root, 0}};
        while (!pending.empty()) {
            const auto item = pending.back(); pending.pop_back();
            if (item.second) { out << item.second; continue; }
            const auto& n = nodes[item.first];
            if (n.right == -1) { out << n.value; continue; }
            out << '(' << n.value;
            pending.push_back({0, ')'}); pending.push_back({n.right, 0}); pending.push_back({0, ' '});
            if (n.left != -1) { pending.push_back({n.left, 0}); pending.push_back({0, ' '}); }
        }
        out << '\n';
    }
};
int main(int argc, char** argv) {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    try {
        const string mode = argc == 1 ? "--postfix" : argv[1];
        if (argc > 2 || (mode != "--postfix" && mode != "--ast" && mode != "--eval")) throw runtime_error("usage: expression [--postfix|--ast|--eval]");
        ostringstream output; output.imbue(locale::classic()); output << setprecision(15);
        string line;
        while (getline(cin, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            const Expression expr(line);
            if (mode == "--eval") output << expr.evaluate() << '\n';
            else if (mode == "--ast") expr.ast(output);
            else expr.postfix(output);
        }
        if (cin.bad()) throw runtime_error("input read failed");
        cout << output.str(); return cout ? 0 : 1;
    } catch (const exception& e) { cerr << "error: " << e.what() << '\n'; return 1; }
}
