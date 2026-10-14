// C-like exam lexer: identifiers, decimal/exponent, strings, comments, longest operators.
// Supplement identifier rule: [A-Za-z_][A-Za-z_0-9]* (not Ch3's restricted underscores).
#include <iomanip>
#include <iostream>
#include <iterator>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
// 採 ASCII 範圍比較，避免 signed char 直接傳給 cctype 造成問題。
bool digit(char c) { return c >= '0' && c <= '9'; }
// 此補充題的 ID 可用底線；不要直接套用到 Ch3 另有底線限制的原題。
bool letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_'; }
bool space(char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '\f' || c == '\v'; }
int main() {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        // 整份 source 讀到 EOF；不可用 cin >> s，否則空白後的內容會遺失。
        const std::string s{std::istreambuf_iterator<char>(std::cin), {}};
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        // 先讀完整 ID 再查這張表：intx 是 ID，不是 int 接 x。
        const std::set<std::string> keywords{"int","float","double","char","bool","void","if","else","while","for","return","print"};
        // Longest match：三字元運算子放在二字元前；單字元最後判斷。
        const std::vector<std::string> ops{"<<=",">>=","++","--","==","!=","<=",">=","&&","||","+=","-=","*=","/=","%=","<<",">>","->","&=","|=","^=","::"};
        // 只在完整掃描成功後輸出 token，避免非法尾端造成半份輸出。
        std::ostringstream output;
        for (std::size_t p = 0; p < s.size();) {
            if (space(s[p])) { ++p; continue; }
            // 註解先於 / 運算子；單行註解遇 CR 或 LF 都結束。
            if (s.compare(p, 2, "//") == 0) { while (p < s.size() && s[p] != '\r' && s[p] != '\n') ++p; continue; }
            // 區塊註解採非巢狀規則；找不到 */ 必須報錯。
            if (s.compare(p, 2, "/*") == 0) {
                const auto end = s.find("*/", p + 2);
                if (end == std::string::npos) throw std::runtime_error("unclosed block comment");
                p = end + 2; continue;
            }
            // start 記住 token 起點；結束位置 p 可用來直接切原始 lexeme。
            const auto start = p;
            std::string kind;
            // ID 一次讀到底，再分成 keyword / identifier，避免錯切前綴。
            if (letter(s[p])) {
                ++p; while (p < s.size() && (letter(s[p]) || digit(s[p]))) ++p;
                kind = keywords.count(s.substr(start, p - start)) ? "KW" : "ID";
            // 小數的點只有接數字才可當 number 起點；獨立 . 是 punctuation。
            } else if (digit(s[p]) || (s[p] == '.' && p + 1 < s.size() && digit(s[p + 1]))) {
                kind = "NUM";
                while (p < s.size() && digit(s[p])) ++p;
                if (p < s.size() && s[p] == '.') { ++p; while (p < s.size() && digit(s[p])) ++p; }
                // 指數的正負號屬於 number；一般 -12 的 - 仍是獨立 operator。
                if (p < s.size() && (s[p] == 'e' || s[p] == 'E')) {
                    ++p; if (p < s.size() && (s[p] == '+' || s[p] == '-')) ++p;
                    if (p == s.size() || !digit(s[p])) throw std::runtime_error("missing exponent digits");
                    while (p < s.size() && digit(s[p])) ++p;
                }
            // 進入 literal 後，// 與 /* 不再當作註解；只找未跳脫的配對引號。
            } else if (s[p] == '\'' || s[p] == '"') {
                const char quote = s[p++];
                // token 的類型與 lexeme 分開存；內容不需轉成執行期字串值。
                kind = quote == '"' ? "STRING" : "CHAR";
                int units = 0;
                while (p < s.size() && s[p] != quote) {
                    if (s[p] == '\r' || s[p] == '\n' || s[p] == '\0') throw std::runtime_error("newline/NUL in literal");
                    // 反斜線連同下一個字元一起吃掉；例如 \" 不會提早結束 string。
                    if (s[p] == '\\') {
                        ++p;
                        if (p == s.size() || s[p] == '\r' || s[p] == '\n' || s[p] == '\0') throw std::runtime_error("incomplete escape");
                    }
                    ++p; ++units;
                }
                if (p == s.size()) throw std::runtime_error("unclosed literal");
                ++p;
                // CHAR 只允許一個 byte 或一個簡單 escape；不是完整 C 字元常量規範。
                if (quote == '\'' && units != 1) throw std::runtime_error("character literal needs one character/escape");
            } else {
                // 先試完整多字元 operator，再退到單字元；不要用固定切兩字元的做法。
                for (const auto& op : ops) if (s.compare(p, op.size(), op) == 0) { p += op.size(); kind = "OP"; break; }
                if (kind.empty()) {
                    const char c = s[p++];
                    // 此處才退到單字元 operator，確保 += 不被切成 + 和 =。
                    if (std::string("+-*/%=<>!&|^~?:").find(c) != std::string::npos) kind = "OP";
                    else if (std::string("(){}[],;.").find(c) != std::string::npos) kind = "PUNCT";
                    else throw std::runtime_error("invalid byte at " + std::to_string(start));
                }
            }
            // std::quoted 是輸出包裝；lexeme 本身仍保留原始大小寫與引號。
            output << kind << ' ' << std::quoted(s.substr(start, p - start)) << '\n';
        }
        // 只有題目要求才保留額外 EOF token；考場可刪此行。
        output << "EOF\n";
        std::cout << output.str(); return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
