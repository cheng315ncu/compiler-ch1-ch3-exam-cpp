// FIRST / FOLLOW / SELECT / LL(1) table. P productions, each "A -> X Y".
// One alternative per line; '#' alone is epsilon; '$' is reserved EOF.
// Start symbol = first LHS. --check reads whitespace-separated token sequences afterward.
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
// 符號採字串，所以 num、Expr、ExprTail 不必改成單字元代號。
using Set = std::set<std::string>;
struct Rule { std::string lhs; std::vector<std::string> rhs; };
// 計算整段 RHS 的 FIRST，不是只看第一字元。
// 如果前方可為 epsilon，還要繼續合併下一符號的 FIRST。
Set first_sequence(const std::vector<std::string>& rhs, std::size_t start, const std::map<std::string, Set>& first) {
    Set result;
    for (std::size_t i = start; i < rhs.size(); ++i) {
        // first 表只含 nonterminal；找不到表示 terminal，自己就是 FIRST。
        const auto it = first.find(rhs[i]);
        if (it == first.end()) { result.insert(rhs[i]); return result; }
        for (const auto& t : it->second) if (t != "#") result.insert(t);
        if (!it->second.count("#")) return result;
    }
    // 整段 RHS 都 nullable，或 suffix 是空串，FIRST 才包含 epsilon。
    result.insert("#"); return result;
}
// 只有集合真的增加才回傳 true；用這個旗標決定固定點迴圈能否停止。
bool merge(Set& target, const Set& source) { const auto before = target.size(); target.insert(source.begin(), source.end()); return target.size() != before; }
void print_set(const Set& s) { std::cout << '{'; bool first = true; for (const auto& t : s) { if (!first) std::cout << ','; std::cout << t; first = false; } std::cout << '}'; }
int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        const std::string mode = argc == 1 ? "--table" : argv[1];
        if (argc > 2 || (mode != "--table" && mode != "--check")) throw std::runtime_error("usage: ll1 [--table|--check]");
        int count; std::string line;
        if (!(std::cin >> count) || count < 1 || count > 1000) throw std::runtime_error("production count must be 1..1000");
        std::getline(std::cin, line);
        if (line.find_first_not_of(" \t\r") != std::string::npos) throw std::runtime_error("production starts on next line");
        std::vector<Rule> rules; Set nonterminals;
        // 一行一條 production、同一 LHS 的替代規則分開寫；不要直接輸入 |。
        for (int i = 0; i < count; ++i) {
            if (!std::getline(std::cin, line)) throw std::runtime_error("missing production");
            std::istringstream input(line); Rule rule; std::string arrow, symbol;
            if (!(input >> rule.lhs >> arrow) || arrow != "->" || rule.lhs == "#" || rule.lhs == "$" || rule.lhs == "|") throw std::runtime_error("expected A -> symbols");
            while (input >> symbol) {
                if (symbol == "$" || symbol == "|") throw std::runtime_error("reserved symbol; use one alternative per line");
                rule.rhs.push_back(symbol);
            }
            // 不允許省略 epsilon 記號；輸入空 RHS 必須明寫 #。
            if (rule.rhs.empty()) throw std::runtime_error("write # for epsilon");
            // # 只可單獨表示 epsilon；內部改用空 vector 表示空 RHS。
            if (rule.rhs.size() == 1 && rule.rhs[0] == "#") rule.rhs.clear();
            else for (const auto& s : rule.rhs) if (s == "#") throw std::runtime_error("epsilon must be alone");
            nonterminals.insert(rule.lhs); rules.push_back(std::move(rule));
        }
        // 先收齊所有 LHS 才知道 nonterminal，避免尚未讀到的規則被當 terminal。
        std::map<std::string, Set> first, follow;
        for (const auto& nt : nonterminals) { first[nt] = {}; follow[nt] = {}; }
        // FIRST 與 FOLLOW 都反覆掃規則到集合不再增加；支援循環相依。
        bool changed;
        do {
            changed = false;
            for (const auto& rule : rules) if (merge(first[rule.lhs], first_sequence(rule.rhs, 0, first))) changed = true;
        } while (changed);
        // 第一條 production 的 LHS 是 start；start 的 FOLLOW 包含 EOF $。
        follow[rules[0].lhs].insert("$");
        do {
            changed = false;
            for (const auto& rule : rules) for (std::size_t i = 0; i < rule.rhs.size(); ++i) {
                if (!nonterminals.count(rule.rhs[i])) continue;
                // 對 A -> α B β：把 FIRST(β) 去掉 epsilon 後加進 FOLLOW(B)。
                auto suffix = first_sequence(rule.rhs, i + 1, first);
                const bool nullable = suffix.erase("#") != 0;
                if (merge(follow[rule.rhs[i]], suffix)) changed = true;
                // β 可空時，再把 FOLLOW(A) 加進 FOLLOW(B)，不能漏掉這個傳播。
                if (nullable && merge(follow[rule.rhs[i]], follow[rule.lhs])) changed = true;
            }
        } while (changed);
        // SELECT = FIRST(RHS) 去 epsilon；若 RHS nullable，再加 FOLLOW(LHS)。
        std::vector<Set> select;
        std::map<std::pair<std::string, std::string>, std::vector<int>> table;
        bool ll1 = true;
        for (std::size_t i = 0; i < rules.size(); ++i) {
            auto s = first_sequence(rules[i].rhs, 0, first);
            if (s.erase("#")) merge(s, follow[rules[i].lhs]);
            select.push_back(s);
            // 表格同一格若有兩條 production 就是 conflict；不可隨便選第一條。
            for (const auto& token : s) { auto& cell = table[{rules[i].lhs, token}]; cell.push_back(static_cast<int>(i)); if (cell.size() > 1) ll1 = false; }
        }
        if (mode == "--table") {
            for (const auto& nt : nonterminals) {
                std::cout << "FIRST(" << nt << ")="; print_set(first[nt]); std::cout << " FOLLOW(" << nt << ")="; print_set(follow[nt]); std::cout << '\n';
            }
            for (std::size_t i = 0; i < rules.size(); ++i) { std::cout << "SELECT(" << i + 1 << ")="; print_set(select[i]); std::cout << '\n'; }
            for (const auto& cell : table) {
                std::cout << "M[" << cell.first.first << ',' << cell.first.second << "]=";
                for (std::size_t i = 0; i < cell.second.size(); ++i) std::cout << (i ? "," : "") << cell.second[i] + 1;
                if (cell.second.size() > 1) std::cout << " CONFLICT";
                std::cout << '\n';
            }
            std::cout << (ll1 ? "LL1 YES\n" : "LL1 NO\n");
        } else {
            // 只能用無衝突的 LL(1) 表做這份 predictive parser。
            if (!ll1) throw std::runtime_error("grammar has LL(1) conflicts");
            while (std::getline(std::cin, line)) {
                std::istringstream input(line); std::vector<std::string> words; std::string word;
                bool accepted = true;
                while (input >> word) { if (word == "$" || word == "#" || nonterminals.count(word)) accepted = false; words.push_back(word); }
                // 輸入自動補 EOF；解析 stack 初始是 $ 與 start，頂端在 vector 尾端。
                words.push_back("$"); std::vector<std::string> stack{"$", rules[0].lhs}; std::size_t pos = 0, steps = 0;
                while (accepted && !stack.empty()) {
                    // ponytail: a finite study budget prevents pathological expansion; raise for larger judges.
                    if (++steps > 1000000) throw std::runtime_error("parse exceeds 1000000 steps");
                    // vector 尾端就是 stack top；push RHS 的順序要反過來。
                    const auto top = stack.back(); stack.pop_back();
                    // terminal 必須匹配 lookahead，才前進輸入位置；nonterminal 只展開，不吃字元。
                    if (!nonterminals.count(top)) { if (top != words[pos]) accepted = false; else ++pos; }
                    else {
                        const auto it = table.find({top, words[pos]});
                        if (it == table.end()) { accepted = false; continue; }
                        // 選到的 RHS 要反向 push，讓最左符號先被 pop／處理。
                        const auto& rhs = rules[it->second[0]].rhs;
                        for (auto r = rhs.rbegin(); r != rhs.rend(); ++r) stack.push_back(*r);
                    }
                }
                // stack 用完且輸入也全用完才接受；只匹配前綴不算成功。
                std::cout << (accepted && pos == words.size() ? "ACCEPT\n" : "REJECT\n");
            }
        }
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
