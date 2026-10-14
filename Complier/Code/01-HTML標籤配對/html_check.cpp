// One HTML fragment -> VALID / INVALID. Explicit nesting, not browser recovery.
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
// 整份輸入保存在 s；p 是下一個尚未處理的 byte。只處理一份文件時不必重設 p。
string s;
size_t p = 0;
// 把 CR 與 LF 都視為空白，跨 Windows / Linux 的換行仍能解析。
bool space(char c) { return string(" \t\n\r\f").find(c) != string::npos; }
bool letter(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }
// 只轉 ASCII 大小寫：<DIV> 與 </div> 可配對，文字內容不會被改寫。
string lower(string t) { for (char& c : t) if (c >= 'A' && c <= 'Z') c += 'a' - 'A'; return t; }
// 統一用例外離開巢狀解析；不必在每層傳遞錯誤旗標。
void fail() { throw runtime_error("invalid HTML"); }
void skip() { while (p < s.size() && space(s[p])) ++p; }
// 讀 tag 或 attribute 名稱；先驗證第一字元，再讀完整名稱。
// 不能直接讀到空白：名稱內允許數字、-、_、:，但有自己的起始規則。
string name() {
    size_t start = p;
    if (p == s.size() || !(letter(s[p]) || s[p] == '_' || s[p] == ':')) fail();
    while (p < s.size() && (letter(s[p]) || (s[p] >= '0' && s[p] <= '9') ||
           s[p] == '-' || s[p] == '_' || s[p] == ':')) ++p;
    return lower(s.substr(start, p - start));
}
bool check() {
    // HTML void elements 沒有一般 end tag；它們不進 stack。
    // 本題另允許 <custom/> 自閉合，這是題目子集政策，非完整 browser 行為。
    const set<string> empty{"area","base","br","col","embed","hr","img","input",
                            "link","meta","source","track","wbr"};
    // raw text 中的 < 不一律是新 tag；要直接找對應的結束標籤。
    const set<string> raw{"script","style","textarea","title"};
    // stack 只保存「已開啟、尚未關閉」的 tag，由外層到內層排列。
    vector<string> stack;
    if (s.find('\0') != string::npos) fail();
    while (p < s.size()) {
        // 一般文字不影響巢狀關係，直接往後讀；遇到 < 才需要分類。
        if (s[p] != '<') { ++p; continue; }
        // 註解中的 <b> 不當成標籤；必須找到 -->，否則拒絕。
        if (s.compare(p, 4, "<!--") == 0) {
            size_t end = s.find("-->", p + 4);
            if (end == string::npos) fail();
            p = end + 3; continue;
        }
        // DOCTYPE 是宣告，不推入 stack；本版只接受短形式 <!DOCTYPE html>。
        if (lower(s.substr(p, 9)) == "<!doctype") {
            p += 9;
            if (p == s.size() || !space(s[p])) fail();
            skip(); if (name() != "html") fail(); skip();
            if (p == s.size() || s[p++] != '>') fail();
            continue;
        }
        ++p;
        // 剛跳過 <，下一字元 / 表示 end tag；不接受 < /a> 這種寫法。
        bool end_tag = p < s.size() && s[p] == '/';
        if (end_tag) ++p;
        string tag = name();
        // 結束標籤只能關閉最內層。例：<a><b></a> 不能先把 a 移除。
        if (end_tag) {
            skip();
            if (p == s.size() || s[p++] != '>' || stack.empty() || stack.back() != tag) fail();
            stack.pop_back(); continue;
        }
        // closed 表示不必再等待 end tag：void 或明示 />。
        bool closed = empty.count(tag);
        set<string> attrs;
        while (true) {
            // 每個 attribute 前要有空白；這個位置差用來拒絕 a="1"b="2"。
            size_t before = p; skip();
            if (p == s.size()) fail();
            if (s[p] == '>') { ++p; break; }
            if (s.compare(p, 2, "/>") == 0) { p += 2; closed = true; break; }
            // 同一個 start tag 不允許重複 attribute；名稱已轉小寫。
            if (p == before || !attrs.insert(name()).second) fail();
            // 沒有 = 的 attribute 是 boolean attribute；回到名稱尾端，讓下輪驗證空白。
            size_t after = p; skip();
            if (p == s.size() || s[p] != '=') { p = after; continue; }
            ++p; skip();
            if (p == s.size()) fail();
            // 引號內的 > 只是值的一部分；不可用第一個 > 草率切開 tag。
            if (s[p] == '\'' || s[p] == '"') {
                char quote = s[p++];
                size_t end = s.find(quote, p);
                if (end == string::npos) fail();
                p = end + 1;
            } else {
                size_t start = p;
                while (p < s.size() && !space(s[p]) && s[p] != '>') {
                    if (string("\"'<=`").find(s[p]) != string::npos) fail();
                    ++p;
                }
                // 無引號值至少有一個字元；a=x/> 的 / 是值的一部分，a=x /> 才自閉合。
                if (p == start) fail(); // Slash in an unquoted value is part of that value.
            }
        }
        if (closed) continue;
        // 一般未自閉合 START 才入 stack。求最大深度時就在這裡更新答案。
        stack.push_back(tag);
        if (raw.count(tag)) {
            // 只找完整對應的 end tag；</scriptx> 不可誤認成 </script>。
            size_t end = s.find("</", p);
            while (end != string::npos) {
                size_t after = end + 2 + tag.size();
                while (after < s.size() && space(s[after])) ++after;
                if (lower(s.substr(end + 2, tag.size())) == tag && after < s.size() && s[after] == '>') break;
                end = s.find("</", end + 2);
            }
            if (end == string::npos) fail();
            p = end;
        }
    }
    // 整份文件讀完仍有 tag 未關閉，就算沒有錯位 END 也要拒絕。
    return stack.empty();
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    // 以 EOF 當一案結尾，保留跨行 HTML；一行一案的題目需改這段。
    s.assign(istreambuf_iterator<char>(cin), {});
    // 讀取裝置失敗與文件語法非法不同：前者才用 exit 1。
    if (cin.bad()) { cerr << "input error\n"; return 1; }
    bool valid = false;
    // 語法錯誤也是分類結果 INVALID，所以這裡捕捉例外，不把它當程式崩潰。
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
    // 檢查輸出串流是否成功；不要印提示或 pause 訊息到 judge。
    return cout ? 0 : 1;
}
