// Exam HTML subset: explicit nesting, attributes, comments, void/raw elements.
// Not a browser's error-recovering WHATWG tree builder. C++17, no dependencies.
#include <iostream>
#include <iterator>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

bool space(char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f'; }
bool letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }
bool name_char(char c) { return letter(c) || (c >= '0' && c <= '9') || c == '-' || c == '_' || c == ':'; }
std::string lower(std::string s) { for (char& c : s) if (c >= 'A' && c <= 'Z') c = static_cast<char>(c + ('a' - 'A')); return s; }
std::string quoted(const std::string& text) {
    std::string result = "\"";
    for (char c : text) {
        if (c == '\n') result += "\\n";
        else if (c == '\r') result += "\\r";
        else if (c == '\t') result += "\\t";
        else { if (c == '\\' || c == '"') result += '\\'; result += c; }
    }
    return result + '"';
}
const std::set<std::string> void_tags{"area","base","br","col","embed","hr","img","input","link","meta","source","track","wbr"};
const std::set<std::string> raw_tags{"script","style","textarea","title"};
struct Token { std::string kind, value; std::vector<std::pair<std::string, std::string>> attrs; bool closed = false; };

std::vector<Token> tokenize(const std::string& s) {
    std::vector<Token> result;
    std::size_t p = 0;
    std::string raw;
    const auto fail = [&](const std::string& why) { throw std::runtime_error(why + " at byte " + std::to_string(p)); };
    const auto skip_space = [&] { while (p < s.size() && space(s[p])) ++p; };
    const auto name = [&] {
        const auto start = p;
        if (p == s.size() || !(letter(s[p]) || s[p] == '_' || s[p] == ':')) fail("expected name");
        while (p < s.size() && name_char(s[p])) ++p;
        return lower(s.substr(start, p - start));
    };
    while (p < s.size()) {
        if (!raw.empty()) {
            const auto start = p;
            auto end = s.find("</", p);
            while (end != std::string::npos) {
                auto after = end + 2 + raw.size();
                if (lower(s.substr(end + 2, raw.size())) == raw) {
                    while (after < s.size() && space(s[after])) ++after;
                    if (after < s.size() && s[after] == '>') break;
                }
                end = s.find("</", end + 2);
            }
            if (end == std::string::npos) fail("unclosed raw-text element " + raw);
            if (end != start) result.push_back({"TEXT", s.substr(start, end - start), {}, false});
            p = end; raw.clear();
        }
        if (s[p] != '<') {
            const auto start = p;
            while (p < s.size() && s[p] != '<') ++p;
            result.push_back({"TEXT", s.substr(start, p - start), {}, false});
            continue;
        }
        if (s.compare(p, 4, "<!--") == 0) {
            const auto end = s.find("-->", p + 4);
            if (end == std::string::npos) fail("unclosed comment");
            result.push_back({"COMMENT", s.substr(p + 4, end - p - 4), {}, false});
            p = end + 3; continue;
        }
        if (lower(s.substr(p, 9)) == "<!doctype") {
            p += 9;
            if (p == s.size() || !space(s[p])) fail("expected whitespace after DOCTYPE");
            skip_space();
            if (name() != "html") fail("only DOCTYPE html is supported");
            skip_space();
            if (p == s.size() || s[p] != '>') fail("invalid DOCTYPE");
            ++p; result.push_back({"DOCTYPE", "html", {}, false}); continue;
        }
        ++p;
        const bool closing = p < s.size() && s[p] == '/';
        if (closing) ++p;
        Token t{closing ? "END" : "START", name(), {}, false};
        if (closing) {
            skip_space();
            if (p == s.size() || s[p] != '>') fail("invalid end tag");
            ++p; result.push_back(std::move(t)); continue;
        }
        std::set<std::string> seen;
        while (true) {
            const auto before = p; skip_space();
            if (p == s.size()) fail("unclosed start tag");
            if (s[p] == '>') { ++p; break; }
            if (s[p] == '/' && p + 1 < s.size() && s[p + 1] == '>') { p += 2; t.closed = true; break; }
            if (p == before) fail("attributes require separating whitespace");
            const auto key = name();
            if (!seen.insert(key).second) fail("duplicate attribute " + key);
            const auto after_name = p; skip_space();
            std::string value;
            if (p < s.size() && s[p] == '=') {
                ++p; skip_space();
                if (p == s.size()) fail("missing attribute value");
                if (s[p] == '\'' || s[p] == '"') {
                    const char quote = s[p++];
                    const auto start = p, end = s.find(quote, p);
                    if (end == std::string::npos) fail("unclosed attribute quote");
                    value = s.substr(start, end - start); p = end + 1;
                } else {
                    const auto start = p;
                    while (p < s.size() && !space(s[p]) && s[p] != '>') {
                        if (s[p] == '"' || s[p] == '\'' || s[p] == '<' || s[p] == '=' || s[p] == '`') fail("invalid unquoted attribute");
                        ++p;
                    }
                    if (p == start) fail("empty unquoted attribute");
                    value = s.substr(start, p - start); // Slash in an unquoted value belongs to the value.
                }
            } else p = after_name;
            t.attrs.push_back({key, value});
        }
        // Supplement policy: XML-style <custom/> closes custom/normal elements too.
        t.closed = t.closed || void_tags.count(t.value) != 0;
        if (!t.closed && raw_tags.count(t.value)) raw = t.value;
        result.push_back(std::move(t));
    }
    return result;
}
struct Node { Token token; std::vector<int> children; };
std::vector<Node> parse(const std::vector<Token>& tokens) {
    std::vector<Node> nodes{{{"DOCUMENT", "", {}, false}, {}}};
    std::vector<int> stack{0};
    for (const auto& token : tokens) {
        if (token.kind == "END") {
            if (stack.size() == 1 || nodes[stack.back()].token.value != token.value)
                throw std::runtime_error("mismatched end tag " + token.value);
            stack.pop_back();
        } else {
            const int id = static_cast<int>(nodes.size());
            nodes.push_back({token, {}});
            nodes[stack.back()].children.push_back(id);
            if (token.kind == "START" && !token.closed) stack.push_back(id);
        }
    }
    if (stack.size() != 1) throw std::runtime_error("unclosed element " + nodes[stack.back()].token.value);
    return nodes;
}
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    const std::string mode = argc == 1 ? "--check" : argv[1];
    bool classify = false;
    try {
        if (argc > 2 || (mode != "--check" && mode != "--tokens" && mode != "--tree" && mode != "--text"))
            throw std::runtime_error("usage: html_parser [--check|--tokens|--tree|--text]");
        const std::string source{std::istreambuf_iterator<char>(std::cin), {}};
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        classify = true;
        if (source.find('\0') != std::string::npos) throw std::runtime_error("invalid input");
        const auto tokens = tokenize(source);
        std::ostringstream output;
        if (mode == "--tokens") {
            for (const auto& t : tokens) {
                output << t.kind << ' ' << quoted(t.value);
                if (t.kind == "START") output << (t.closed ? " closed" : " open");
                for (const auto& attr : t.attrs) output << ' ' << attr.first << '=' << quoted(attr.second);
                output << '\n';
            }
        } else {
            const auto nodes = parse(tokens);
            if (mode == "--check") output << "VALID\n";
            else if (mode == "--text") {
                for (const auto& n : nodes) if (n.token.kind == "TEXT") output << n.token.value;
            } else {
                // ponytail: iterative arena traversal; no recursive depth limit.
                std::vector<std::pair<int, int>> pending{{0, 0}};
                while (!pending.empty()) {
                    const auto item = pending.back(); pending.pop_back();
                    const auto& n = nodes[item.first];
                    output << std::string(static_cast<std::size_t>(item.second) * 2, ' ') << n.token.kind << ' ' << quoted(n.token.value) << '\n';
                    for (const auto& attr : n.token.attrs) output << std::string(static_cast<std::size_t>(item.second + 1) * 2, ' ') << '@' << attr.first << '=' << quoted(attr.second) << '\n';
                    for (auto it = n.children.rbegin(); it != n.children.rend(); ++it) pending.push_back({*it, item.second + 1});
                }
            }
        }
        std::cout << output.str(); return std::cout ? 0 : 1;
    } catch (const std::exception& e) {
        if (mode == "--check" && classify) { std::cout << "INVALID\n"; return std::cout ? 0 : 1; }
        std::cerr << "error: " << e.what() << '\n'; return 1;
    }
}
