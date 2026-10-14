// Tiny stack interpreter. One instruction per line; long double arithmetic.
// PUSH number, LOAD name, STORE name, ADD/SUB/MUL/DIV/NEG, DUP, PRINT.
#include <cmath>
#include <iomanip>
#include <iostream>
#include <locale>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
// 變數名稱首字元是字母或底線，其後才可出現數字。
bool name_valid(const std::string& name) {
    if (name.empty()) return false;
    for (std::size_t i = 0; i < name.size(); ++i) {
        const char c = name[i];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_' || (i && c >= '0' && c <= '9'))) return false;
    }
    return true;
}
int main() {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    try {
        // 用 vector.back 當 stack 頂端；沒有固定容量，不必自寫 linked list。
        std::vector<long double> stack;
        // vars 存變數；LOAD 不使用下標默認 0，未定義必須拒絕。
        std::map<std::string, long double> vars;
        // 顯示 15 位有效數字；資料仍保留 long double，不先轉 double。
        std::ostringstream output; output.imbue(std::locale::classic()); output << std::setprecision(15);
        // 共用 pop 先檢查空 stack，避免對空 vector 呼叫 back。
        const auto pop = [&] { if (stack.empty()) throw std::runtime_error("stack underflow"); const auto value = stack.back(); stack.pop_back(); return value; };
        std::string line; int line_number = 0;
        while (std::getline(std::cin, line)) {
            ++line_number;
            // 每行一條指令：先讀 op，再檢查需要的參數和多餘參數。
            std::istringstream input(line); input.imbue(std::locale::classic());
            std::string op, arg, extra;
            if (!(input >> op)) continue;
            // PUSH/LOAD/STORE 恰好需要一個參數；ADD 等不可多帶 argument。
            const bool needs_arg = op == "PUSH" || op == "LOAD" || op == "STORE";
            if (needs_arg && !(input >> arg)) throw std::runtime_error("missing argument at line " + std::to_string(line_number));
            if (input >> extra) throw std::runtime_error("extra argument at line " + std::to_string(line_number));
            // 數字必須完整解析且有限；1abc 不可偷偷讀成 1。
            if (op == "PUSH") {
                std::istringstream number(arg); number.imbue(std::locale::classic()); long double value;
                if (!(number >> value) || number.peek() != std::char_traits<char>::eof() || !std::isfinite(value)) throw std::runtime_error("invalid finite number");
                stack.push_back(value);
            } else if (op == "LOAD" || op == "STORE") {
                if (!name_valid(arg)) throw std::runtime_error("invalid variable name");
                // STORE 移走頂端存入變數；LOAD 只複製已存在的變數值。
                if (op == "STORE") vars[arg] = pop();
                else { const auto it = vars.find(arg); if (it == vars.end()) throw std::runtime_error("undefined variable " + arg); stack.push_back(it->second); }
            // 本題 PRINT 會 pop；題目若要像 dc 的 p 不 pop，改成讀 back 而不移除。
            } else if (op == "PRINT") { const auto value = pop(); output << (value == 0 ? 0 : value) << '\n'; }
            // NEG 是一元指令，只取一個值；不能與 SUB 的兩個 operand 混用。
            else if (op == "NEG") { const auto value = pop(); stack.push_back(-value); }
            // DUP 把頂端變成兩份；這裡先 pop 再 push 兩次，淨增加一項。
            else if (op == "DUP") { const auto value = pop(); stack.push_back(value); stack.push_back(value); }
            else if (op == "ADD" || op == "SUB" || op == "MUL" || op == "DIV") {
                // postfix 先取右 operand b，再取左 a；8 2 SUB 必須得到 6。
                const auto b = pop(), a = pop(); long double result;
                if (op == "ADD") result = a + b;
                else if (op == "SUB") result = a - b;
                else if (op == "MUL") result = a * b;
                else { if (b == 0) throw std::runtime_error("division by zero"); result = a / b; }
                // 即使 operand 有限，乘法仍可能溢位；結果也要檢查。
                if (!std::isfinite(result)) throw std::runtime_error("non-finite result");
                stack.push_back(result);
            } else throw std::runtime_error("unknown instruction " + op);
        }
        if (std::cin.bad()) throw std::runtime_error("input read failed");
        // 所有 PRINT 暫存到最後；後面有錯誤時不輸出半份執行結果。
        std::cout << output.str(); return std::cout ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 1; }
}
