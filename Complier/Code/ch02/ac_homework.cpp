// Ch2 HW1-3 / Ch3 HW3. C++17, stdin -> stdout; errors -> stderr, exit 1.
// One-letter ac identifiers are preserved. Full keywords use longest match.
#include <algorithm>
#include <array>
#include <iostream>
#include <iterator>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Token { std::string kind, text; std::size_t offset; };
bool digit(char c) { return c >= '0' && c <= '9'; }
bool space(char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '\v' || c == '\f'; }

std::vector<Token> scan(const std::string& source) {
    std::vector<Token> tokens;
    for (std::size_t p = 0; p < source.size();) {
        if (space(source[p])) { ++p; continue; }
        const auto start = p;
        std::string kind;
        const char c = source[p];
        if (digit(c)) {
            kind = "inum";
            while (p < source.size() && digit(source[p])) ++p;
            if (p < source.size() && source[p] == '.') {
                kind = "fnum";
                ++p;
                if (p == source.size() || !digit(source[p]))
                    throw std::runtime_error("lexical: digit required after decimal point at byte " + std::to_string(p));
                while (p < source.size() && digit(source[p])) ++p;
            }
            if (p < source.size() && source[p] == 'e') {
                kind = "fnum"; // Supplement: every exponent literal has float type.
                ++p;
                if (p < source.size() && (source[p] == '+' || source[p] == '-')) ++p;
                if (p == source.size() || !digit(source[p]))
                    throw std::runtime_error("lexical: digit required in exponent at byte " + std::to_string(p));
                while (p < source.size() && digit(source[p])) ++p;
            }
        } else {
            ++p;
            if (c == 'f') { kind = "floatdcl"; if (source.compare(start, 5, "float") == 0) p = start + 5; }
            else if (c == 'i') { kind = "intdcl"; if (source.compare(start, 3, "int") == 0) p = start + 3; }
            else if (c == 'p') kind = "print";
            else if (c >= 'a' && c <= 'z') kind = "id";
            else if (c == '=') kind = "assign";
            else if (c == '+') kind = "plus";
            else if (c == '-') kind = "minus";
            else throw std::runtime_error("lexical: invalid byte at " + std::to_string(start));
        }
        tokens.push_back({kind, source.substr(start, p - start), start});
    }
    tokens.push_back({"$", "", source.size()});
    return tokens;
}

// Exact decimal-point movement: never convert a source literal to double.
std::string decimal(std::string text) {
    constexpr int limit = 10000;
    const auto e = text.find('e');
    int exponent = 0;
    if (e != std::string::npos) {
        auto p = e + 1;
        const bool negative = text[p] == '-';
        if (text[p] == '+' || text[p] == '-') ++p;
        for (; p < text.size(); ++p) {
            if (exponent > (limit - (text[p] - '0')) / 10)
                throw std::runtime_error("codegen: exponent magnitude exceeds 10000");
            exponent = exponent * 10 + (text[p] - '0');
        }
        if (negative) exponent = -exponent;
        text.resize(e);
    }
    if (text.size() > static_cast<std::size_t>(limit))
        throw std::runtime_error("codegen: mantissa exceeds 10000 characters");
    auto dot = text.find('.');
    int point = static_cast<int>(dot == std::string::npos ? text.size() : dot) + exponent;
    if (dot != std::string::npos) text.erase(dot, 1);
    if (point <= 0) text = "0." + std::string(static_cast<std::size_t>(-point), '0') + text;
    else if (point >= static_cast<int>(text.size())) text.append(static_cast<std::size_t>(point) - text.size(), '0');
    else text.insert(static_cast<std::size_t>(point), ".");
    const auto first = text.find_first_not_of('0');
    if (first == std::string::npos) return "0";
    const auto keep = text[first] == '.' ? first - 1 : first;
    return text.substr(keep);
}

enum class Type { none, integer, floating };
struct Node { std::string label; std::vector<int> children; Type type = Type::none; };
using Tree = std::vector<Node>; // Arena indices remain valid across vector growth.
int node(Tree& tree, std::string label, std::vector<int> children = {}) {
    tree.push_back({std::move(label), std::move(children), Type::none});
    return static_cast<int>(tree.size()) - 1;
}

void print_tree(const Tree& tree, int root, std::ostream& out) {
    std::vector<int> pending{root};
    while (!pending.empty()) {
        const int id = pending.back(); pending.pop_back();
        if (id == -1) { out << ')'; continue; }
        if (id == -2) { out << ' '; continue; }
        const auto& n = tree[id];
        if (n.children.empty()) { out << n.label; continue; }
        out << '(' << n.label;
        pending.push_back(-1);
        for (auto it = n.children.rbegin(); it != n.children.rend(); ++it) {
            pending.push_back(*it); pending.push_back(-2);
        }
    }
    out << '\n';
}

struct Parser {
    const std::vector<Token>& tokens;
    std::size_t pos = 0;
    Tree parse, ast;
    std::vector<int> statements;
    explicit Parser(const std::vector<Token>& input) : tokens(input) {}
    bool at(const std::string& kind) const { return tokens[pos].kind == kind; }
    int take(const std::string& kind) {
        if (!at(kind)) throw std::runtime_error("syntax: expected " + kind + " at byte " + std::to_string(tokens[pos].offset));
        const auto t = tokens[pos++];
        if (kind == "$") return node(parse, "$");
        return node(parse, kind, {node(parse, t.text)});
    }
    std::pair<int, int> value() {
        const auto t = tokens[pos];
        if (t.kind != "id" && t.kind != "inum" && t.kind != "fnum")
            throw std::runtime_error("syntax: expected value at byte " + std::to_string(t.offset));
        const int leaf = node(ast, t.kind == "id" ? "id " + t.text : t.text);
        ast[leaf].type = t.kind == "inum" ? Type::integer : t.kind == "fnum" ? Type::floating : Type::none;
        return {node(parse, "Val", {take(t.kind)}), leaf};
    }
    int program() {
        std::vector<int> declarations, stmts;
        while (at("intdcl") || at("floatdcl")) {
            const auto kind = tokens[pos].kind;
            const int keyword = take(kind);
            const auto name = tokens[pos].text;
            const int id = take("id");
            declarations.push_back(node(parse, "Dcl", {keyword, id}));
            statements.push_back(node(ast, kind + " " + name));
        }
        while (!at("$")) {
            if (at("print")) {
                const int keyword = take("print");
                const auto name = tokens[pos].text;
                stmts.push_back(node(parse, "Stmt", {keyword, take("id")}));
                statements.push_back(node(ast, "print " + name));
                continue;
            }
            const auto name = tokens[pos].text;
            const int target = take("id"), assign = take("assign");
            const auto first = value();
            int expression = first.second;
            std::vector<std::pair<int, int>> tail;
            while (at("plus") || at("minus")) {
                const auto kind = tokens[pos].kind;
                const int op = take(kind);
                const auto next = value();
                tail.push_back({op, next.first});
                expression = node(ast, kind == "plus" ? "+" : "-", {expression, next.second});
            }
            int rest = node(parse, "Expr", {node(parse, "epsilon")});
            for (auto it = tail.rbegin(); it != tail.rend(); ++it) rest = node(parse, "Expr", {it->first, it->second, rest});
            stmts.push_back(node(parse, "Stmt", {target, assign, first.first, rest}));
            statements.push_back(node(ast, "=", {node(ast, "id " + name), expression}));
        }
        int dcls = node(parse, "Dcls", {node(parse, "epsilon")});
        for (auto it = declarations.rbegin(); it != declarations.rend(); ++it) dcls = node(parse, "Dcls", {*it, dcls});
        int seq = node(parse, "Stmts", {node(parse, "epsilon")});
        for (auto it = stmts.rbegin(); it != stmts.rend(); ++it) seq = node(parse, "Stmts", {*it, seq});
        return node(parse, "Prog", {dcls, seq, take("$")});
    }
};

void check(Tree& tree) {
    std::array<Type, 26> symbols{};
    const auto lookup = [&](char c) {
        const auto type = symbols[static_cast<std::size_t>(c - 'a')];
        if (type == Type::none) throw std::runtime_error(std::string("semantic: undeclared identifier ") + c);
        return type;
    };
    const auto promote = [&](int child) {
        if (tree[child].type == Type::floating) return child;
        const int converted = node(tree, "int2float", {child});
        tree[converted].type = Type::floating;
        return converted;
    };
    const auto count = tree.size();
    // Original nodes are in child-before-parent order. New conversion nodes
    // already have a type; never hold a vector reference while adding one.
    for (std::size_t i = 0; i < count; ++i) {
        const auto label = tree[i].label;
        if (label.rfind("intdcl ", 0) == 0 || label.rfind("floatdcl ", 0) == 0) {
            auto& entry = symbols[static_cast<std::size_t>(label.back() - 'a')];
            if (entry != Type::none) throw std::runtime_error("semantic: duplicate declaration " + label);
            entry = label[0] == 'i' ? Type::integer : Type::floating;
            tree[i].type = entry;
        } else if (label.rfind("id ", 0) == 0 || label.rfind("print ", 0) == 0) tree[i].type = lookup(label.back());
        else if (label == "+" || label == "-" || label == "=") {
            const int left = tree[i].children[0], right = tree[i].children[1];
            const auto lt = tree[left].type, rt = tree[right].type;
            if (label == "=" && lt == Type::integer && rt == Type::floating)
                throw std::runtime_error("semantic: cannot assign float to int " + tree[left].label);
            tree[i].type = label == "=" ? lt : (lt == Type::floating || rt == Type::floating ? Type::floating : Type::integer);
            if (tree[i].type == Type::floating) {
                if (label != "=") { const int c = promote(left); tree[i].children[0] = c; }
                const int c = promote(right); tree[i].children[1] = c;
            }
        }
    }
}

std::string add_integer(std::string a, std::string b) {
    std::string sum;
    int carry = 0;
    while (!a.empty() || !b.empty() || carry) {
        int n = carry;
        if (!a.empty()) { n += a.back() - '0'; a.pop_back(); }
        if (!b.empty()) { n += b.back() - '0'; b.pop_back(); }
        sum.push_back(static_cast<char>('0' + n % 10)); carry = n / 10;
    }
    std::reverse(sum.begin(), sum.end());
    const auto first = sum.find_first_not_of('0');
    return first == std::string::npos ? "0" : sum.substr(first);
}

// Supplement: exact nonnegative integer + folding, matching HW2's x+31.
// Never reassociate subtraction or floating expressions.
void fold(Tree& tree) {
    const auto constant = [&](int id) { return tree[id].type == Type::integer && digit(tree[id].label[0]); };
    const auto count = tree.size();
    for (std::size_t i = 0; i < count; ++i) {
        if (tree[i].label != "+" || tree[i].type != Type::integer) continue;
        const int left = tree[i].children[0], right = tree[i].children[1];
        if (constant(left) && constant(right)) {
            tree[i].label = add_integer(tree[left].label, tree[right].label); tree[i].children.clear();
        } else if (tree[left].label == "+" && constant(tree[left].children[1]) && constant(right)) {
            const int before = tree[left].children[0], c = tree[left].children[1];
            const int sum = node(tree, add_integer(tree[c].label, tree[right].label));
            tree[sum].type = Type::integer;
            tree[i].children = {before, sum};
        }
    }
}

void generate(const Tree& tree, const std::vector<int>& statements, std::ostream& out) {
    for (const int root : statements) {
        std::vector<std::pair<int, bool>> pending{{root, false}};
        while (!pending.empty()) {
            const auto item = pending.back(); pending.pop_back();
            const auto& n = tree[item.first];
            if (!item.second) {
                pending.push_back({item.first, true});
                if (n.label == "=") pending.push_back({n.children[1], false});
                else for (auto it = n.children.rbegin(); it != n.children.rend(); ++it) pending.push_back({*it, false});
                continue;
            }
            if (n.label == "=") out << 's' << tree[n.children[0]].label.back() << "\n0 k\n";
            else if (n.label == "+" || n.label == "-") out << n.label << '\n';
            else if (n.label == "int2float") out << "5 k\n";
            else if (n.label.rfind("id ", 0) == 0) out << 'l' << n.label.back() << '\n';
            else if (n.label.rfind("print ", 0) == 0) out << 'l' << n.label.back() << "\np\nsi\n";
            else if (digit(n.label[0])) out << decimal(n.label) << '\n';
        }
    }
}

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        std::string mode = "--dc";
        bool optimize = false;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--fold") optimize = true;
            else if (arg == "--tokens" || arg == "--parse-tree" || arg == "--ast" || arg == "--typed-ast" || arg == "--check" || arg == "--dc") mode = arg;
            else throw std::runtime_error("usage: ac_homework [--tokens|--parse-tree|--ast|--typed-ast|--check|--dc] [--fold]");
        }
        if (optimize && (mode == "--tokens" || mode == "--parse-tree"))
            throw std::runtime_error("--fold requires --ast, --typed-ast, --check or --dc");
        // ponytail: whole-input scanning; use streaming if source files outgrow RAM.
        const std::string source{std::istreambuf_iterator<char>(std::cin), {}};
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        const auto tokens = scan(source);
        std::ostringstream output; // Publish only after the complete selected phase succeeds.
        if (mode == "--tokens") {
            for (const auto& t : tokens) output << t.kind << (t.text.empty() ? "" : " " + t.text) << '\n';
        } else {
            Parser parser(tokens);
            const int root = parser.program();
            if (mode == "--parse-tree") print_tree(parser.parse, root, output);
            else if (mode == "--ast" && !optimize) print_tree(parser.ast, node(parser.ast, "Prog", parser.statements), output);
            else {
                check(parser.ast);
                if (optimize) fold(parser.ast);
                if (mode == "--check") output << "OK\n";
                else if (mode == "--ast" || mode == "--typed-ast") print_tree(parser.ast, node(parser.ast, "Prog", parser.statements), output);
                else generate(parser.ast, parser.statements, output);
            }
        }
        std::cout << output.str();
        return std::cout ? 0 : 1;
    } catch (const std::exception& error) { std::cerr << "error: " << error.what() << '\n'; return 1; }
}
