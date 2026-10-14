// 模擬 ParserTest × HTML：OPEN / CLOSE / SELF / TEXT 四種 token，element 的開關標籤名稱必須相同。
#include <cctype>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
using namespace std;
enum Token { OPEN, CLOSE, SELF, TEXT, END, INVALID };
string src, value;  // value：標籤名稱，或整理過空白的文字
size_t pos = 0;
Token token;

void next_token() {
    // TEXT：到下一個 < 為止；istringstream 逐字讀再用單一空白接回，順便去頭尾、壓縮連續空白與換行。
    while (pos < src.size() && src[pos] != '<') {
        size_t end = min(src.find('<', pos), src.size());
        istringstream words(src.substr(pos, end - pos));
        pos = end;
        value.clear();
        for (string w; words >> w;) value += (value.empty() ? "" : " ") + w;
        // 全是空白就略過，不產生 token；文字中出現 > 不合法。
        if (value.empty()) continue;
        token = value.find('>') == string::npos ? TEXT : INVALID;
        return;
    }
    if (pos == src.size()) { token = END; return; }

    // 標籤：< /? [a-z]+ /? >，標籤內不允許空白或屬性。
    size_t p = pos + 1;
    bool close = p < src.size() && src[p] == '/';
    if (close) ++p;
    size_t name = p;
    while (p < src.size() && islower((unsigned char)src[p])) ++p;
    value = src.substr(name, p - name);
    bool self = !close && p < src.size() && src[p] == '/';
    if (self) ++p;
    if (value.empty() || p == src.size() || src[p] != '>') { token = INVALID; pos = src.size(); return; }
    pos = p + 1;
    token = close ? CLOSE : self ? SELF : OPEN;
}

bool content();
// element -> OPEN content CLOSE；CLOSE 的名稱必須等於 OPEN（語意檢查），<b><i></b></i> 不合法。
bool element() {
    string name = value;
    next_token();
    if (!content() || token != CLOSE || value != name) return false;
    next_token();
    return true;
}

// content -> element content | TEXT content | SELF content | λ
bool content() {
    while (true) {
        if (token == TEXT || token == SELF) next_token();
        else if (token == OPEN) { if (!element()) return false; }
        else return true;  // CLOSE / END / INVALID 交給呼叫端判斷
    }
}

int main() {
    const char* names[] = {"OPEN", "CLOSE", "SELF", "TEXT"};
    src.assign(istreambuf_iterator<char>(cin), {});
    next_token();
    // document -> content，最後必須停在 END；多出的 CLOSE 也不合法。
    if (!content() || token != END) { cout << "invalid input\n"; return 0; }
    pos = 0;
    for (next_token(); token != END; next_token()) cout << names[token] << ' ' << value << '\n';
}
