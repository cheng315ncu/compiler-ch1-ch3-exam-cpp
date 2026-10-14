# 11 HTML parser 完整版（check／tokens／tree／text）

| 項目 | 內容 |
|---|---|
| 程式 | [html_parser.cpp](html_parser.cpp) |
| 類型 | 完整功能版 |
| 測例 | [html_parser.in](html_parser.in) → [html_parser.expected](html_parser.expected) |
| 相關資料夾 | [01-HTML標籤配對](../01-HTML標籤配對/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror html_parser.cpp -o main
./main < html_parser.in | diff -u html_parser.expected -
```

## 筆記：Compiler - HTML parser 考試實作

> 原 `Complier/Notes/Exam/Compiler - HTML parser 考試實作.md`，已整份移到這裡。教材頁碼：Ch1 p.17；Ch2 p.6–11、p.15；歷屆 HTML 題未附頁碼。


> [!abstract] 題型定位
> 使用者表示歷屆出過 HTML parser；尚無原題全文。由 Ch1 scanner/parser、Ch2 CFG/AST 延伸。 以下為 **C++ 實作（補充）**；[單檔原碼](html_parser.cpp) · [[Compiler - Ch1-Ch3 考試 C++ 程式集|回程式集]]。

### 契約與模式

`--check（預設）／--tokens／--tree／--text`

stdin 全部內容為一份 HTML fragment。預設輸出 VALID／INVALID，兩種判定均 exit 0。--tokens 只分詞；--tree 配對後輸出縮排樹；--text 配對後串接原始 TEXT，不自動加末尾換行。非 check 模式遇錯時 stdout 為空、stderr 診斷、exit 1。

### 演算法與易錯點

游標先辨認 START／END／TEXT／COMMENT／DOCTYPE；屬性引號內的 > 不結束標籤。arena 保存樹，stack 保存未關閉的 START；END 必須等於 stack 頂端；EOF 要回 document root。VOID／自閉合元素不 push。

<a><b></a></b> 即使數量相同也非法；<br> 不 push，</br> 拒絕。<p a=x/> 的 / 屬於值 x/，p 仍未關閉；<p a=x /> 才自閉合。--text 保留空白、CRLF、&amp; 和 script/style 來源文字，也不替 <br> 加換行，不等於畫面可見文字。

> [!note] 支援範圍
> 考試子集：ASCII 名稱轉小寫；boolean、單雙引號／無引號屬性；短 DOCTYPE html；13 個 void elements；script/style/title/textarea 讀到匹配結束標籤。一般元素必須顯式關閉；<custom/> 依本版類 XML 政策關閉。沒有瀏覽器錯誤修復、可省略 end tag、namespace/template 特殊 DOM、完整 script tokenizer、DTD、內容模型或 entity 解碼；註解以第一個 --> 結束；名稱限字母／_／: 開頭，後接字母數字／-／_／:。允許空 fragment／多個根及任意 DOCTYPE 位置。

### 考場修改位置

只檢查 tag 配對時保留 START/END 的 stack。若一行一案，把 main 的整份讀取改為外層 getline，但跨行 HTML 必須仍當一案。tag 數／深度在 parse 的 push/pop 更新，路徑由 nodes.children 走訪。VALID/INVALID 字樣只改 main。

HTML 分類、void 名單與屬性規則以 [WHATWG HTML syntax](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) 核對（2026-10-14）。標準 HTML 一般元素的 self-closing slash／可省略標籤有不同語意，本版明示為考試子集。

### 編譯與已驗證範例

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror Complier/Code/11-HTML-parser完整版/html_parser.cpp -o /tmp/html_parser
/tmp/html_parser < Complier/Code/11-HTML-parser完整版/html_parser.in
```

輸入：

```text
<div id="main"><p title="a>b">Hello <b>world</b></p><br><img src=x><!--ok--></div>
```

預設輸出：

```text
VALID
```

其他測例：<P>x</p><br> → VALID；<p title="a>b">x</p> → VALID；<a><b></a></b> → INVALID。

整組六份程式已通過 151 項檢查、300 個 Fraction expression oracle、1,524 個隨機 NFA 字串；正常與 AddressSanitizer／UndefinedBehaviorSanitizer 均通過。Linux x86-64 交叉編譯成功；Linux 實跑／DOMjudge Accepted 未驗證。詳細結果見 `Complier/Review/cpp-exam-validation.json`。

### 完整 C++17 程式

完整程式就是同資料夾的 [html_parser.cpp](html_parser.cpp)。舊筆記內嵌的程式碼有幾份已與原檔不同步，為避免照抄到舊版本，這裡不再重複貼整份程式；以 .cpp 原檔為準。
