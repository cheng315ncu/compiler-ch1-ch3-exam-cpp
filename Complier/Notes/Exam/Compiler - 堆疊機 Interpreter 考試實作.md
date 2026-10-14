---
title: "Compiler - 堆疊機 Interpreter 考試實作"
created: 2026-10-14
updated: 2026-10-14
tags: [type/exam-review, course/compiler, source/supplement]
chapter: [1, 2, 3]
source: "[[Compiler-Ch1-p011-p020#PPT p.012｜Compiler 與 Interpreter 的兩階段差別]]；[[Compiler-Ch2-p036-p046#PPT p.036｜Code generation：由根往葉走訪 AST]]"
source_pages: "Ch1 p.12–14；Ch2 p.36–38"
---

# Compiler - 堆疊機 Interpreter 考試實作

> [!abstract] 題型定位
> Ch1 compiler/interpreter、Ch2 dc stack code 的補充練習；instruction 名稱是本版定義，不是 dc。 以下為 **C++ 實作（補充）**；[[Complier/Code/exam/stack_vm.cpp|單檔原碼]] · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

## 契約與模式

`無參數`

每行一指令到 EOF：PUSH number、LOAD name、STORE name、ADD/SUB/MUL/DIV/NEG、DUP、PRINT。空行略過。STORE pop 保存；LOAD 複製；PRINT pop 並印 15 位有效數字。EOF 可留剩餘 stack。錯誤時整份 PRINT 暫存不發出，stderr 診斷、exit 1。

## 演算法與易錯點

vector 是 stack、map 是 variables；二元先 pop 右 b，再左 a，做 a op b。NEG 只需一項；DUP 複製頂端。PUSH 必須完整轉換為有限 long double，零除／underflow／undefined LOAD 都拒絕。

8 2 SUB 得 6，DIV 得 4；不可顛倒 pop 順序。LOAD 未定義值不能默認 0。輸出數值是 interpreter 執行結果，不是 compiler 產出的 target code。

> [!note] 支援範圍
> 沒有跳躍、條件、函式、地址、型別分析、字串、註解或分號。非任意精度整數／dc。本版 PRINT 會 pop，與 GNU dc 的 p 不 pop 不同。名稱 [A-Za-z_][A-Za-z_0-9]*。

## 考場修改位置

postfix 數字→PUSH，+/-/*//→ADD/SUB/MUL/DIV，neg→NEG，pos→忽略，最後 PRINT。若仿 dc p，把 PRINT 的 pop 改成先檢查 stack 非空再讀 back。

演示 compiler → IR → interpreter 時，expression 的 --postfix 是 IR 入口；本 VM 不直接讀 C/C++ 或 ac 來源。

## 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/exam/stack_vm.cpp -o /tmp/stack_vm
/tmp/stack_vm < Complier/Code/exam/stack_vm.in
```

輸入：

```text
PUSH 100
STORE x
LOAD x
PUSH 30
PUSH 1
ADD
ADD
STORE x
LOAD x
PRINT
```

預設輸出：

```text
131
```

其他測例：配套算 x=100，再加 30+1 得 131；PUSH 2／DUP／MUL／NEG／PRINT 得 -4。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

## 完整 C++17 程式

```cpp
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
```
