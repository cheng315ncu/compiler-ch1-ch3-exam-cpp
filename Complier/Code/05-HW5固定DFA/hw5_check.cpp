// Fixed DFA for HW5(a), or HW5(d) after changing HW5A to false.
#include <iostream>
#include <string>
using namespace std;
// true 對應 (a|(bc)*d)+；false 對應 (bc)*d，不需命令列参數。
const bool HW5A = true;
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string word;
    // 空行是案例；不要用 >> word，否則 epsilon 測例會被略過。
    while (getline(cin, word)) {
        // getline 已吃掉 LF；CRLF 留下的尾端 CR 要移除。
        if (!word.empty() && word.back() == '\r') word.pop_back();
        // 0=start, 1=after b, 2=after bc, 3=accept, -1=dead.
        // 每行從起點重新開始；接受條件只看讀完後的 state。
        int state = 0;
        for (char c : word) {
            // 死狀態不可復活；字串剩餘內容已不可能改成接受。
            if (state == -1) break;
            // 剛讀 b 時只能接 c，才形成完整 bc；bd 或 ba 都拒絕。
            if (state == 1) state = c == 'c' ? 2 : -1;
            // 完整 bc 後可再接 b 開始另一組 bc，或接 d 結束該段。
            else if (state == 2) state = c == 'b' ? 1 : c == 'd' ? 3 : -1;
            // HW5(d) 只有一段；已讀終止 d 後再出現任何字元都拒絕。
            else if (state == 3 && !HW5A) state = -1;
            // 起點／HW5(a) 已接受處：a 或 d 可完成一段；b 進入等待 c。
            else state = c == 'b' ? 1 : c == 'd' || (HW5A && c == 'a') ? 3 : -1;
        }
        // 空字串保持 state 0，所以兩個原語言都拒絕 epsilon。
        cout << (state == 3 ? "ACCEPT\n" : "REJECT\n");
    }
    if (cin.bad()) { cerr << "input error\n"; return 1; }
    // stdout 僅包含每案答案；不印轉移表，除非題目另有要求。
    return cout ? 0 : 1;
}
