# 01 HTML 標籤配對

| 項目 | 內容 |
|---|---|
| 程式 | [html_check.cpp](html_check.cpp) |
| 類型 | 優先使用（短版） |
| 測例 | [html_check.in](html_check.in) → [html_check.expected](html_check.expected) |
| 相關資料夾 | [11-HTML-parser完整版](../11-HTML-parser完整版/README.md) |

在本資料夾內編譯並跑測例：

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror html_check.cpp -o main
./main < html_check.in | diff -u html_check.expected -
```

## 題目內容

> 歷屆 HTML parser 是使用者提供的線索，未提供原考卷；以下是完整模擬題。

請撰寫程式讀入一份 HTML fragment，判斷所有非 void、非自閉合元素是否正確巢狀。開始標籤必須依相反順序關閉；END 名稱須與最內層未關閉元素相同。名稱不分 ASCII 大小寫。支援 boolean、單雙引號與無引號屬性、註解、短 DOCTYPE html；script/style/textarea/title 內容讀到匹配 END。多個根元素與空 fragment 均合法。

- **輸入規格**：stdin 全部內容到 EOF 是一個案例，可能跨行。普通元素必須顯式關閉；本模擬題將 &lt;x/> 視為自閉合。無額外案例數 T。
- **輸出規格**：合法印 VALID，否則印 INVALID，每次只印一行；這兩種分類都正常結束。
- **限制與適用範圍**：不是完整 browser DOM：不恢復錯誤、不省略 end tag、不解碼 entity、不檢查內容模型。這裡的「合法」指指定子集。

**Code 檔案名稱：**[`html_check.cpp`](html_check.cpp) （01-HTML標籤配對/html\_check.cpp）

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror html_check.cpp -o main
./main < input.txt
```

## 題目範例與邊界測例

**輸入**

```text
<div id="main"><p title="a>b">Hello <b>world</b></p><br><img src=x><!--ok--></div>
```

**輸出**

```text
VALID
```

### 邊界測例 01

**輸入**

```text
（空輸入）
```

**輸出**

```text
VALID
```

### 邊界測例 02

**輸入**

```text
<P>x</p><br>
```

**輸出**

```text
VALID
```

### 邊界測例 03

**輸入**

```text
<a><b></a></b>
```

**輸出**

```text
INVALID
```

### 邊界測例 04

**輸入**

```text
<p a="a>b">x</p>
```

**輸出**

```text
VALID
```

### 邊界測例 05

**輸入**

```text
<p a=x/>
```

**輸出**

```text
INVALID
```

### 邊界測例 06

**輸入**

```text
<p a=x />
```

**輸出**

```text
VALID
```

### 邊界測例 07

**輸入**

```text
<!-- unclosed
```

**輸出**

```text
INVALID
```

### 邊界測例 08

**輸入**

```text
<script>if(a<b){}</SCRIPT >
```

**輸出**

```text
VALID
```

## 邏輯與手動追蹤

START 入 stack；END 必須匹配頂端才 pop；EOF 時 stack 必須空。void 與自閉合標籤不入 stack；屬性引號內的 > 不結束標籤，註解與 raw text 另行跳過。

- &lt;a>&lt;b>x&lt;/b>&lt;/a>：\[\] → \[a\] → \[a,b\] → \[a\] → \[\]，接受。
- &lt;a>&lt;b>&lt;/a>&lt;/b>：讀 &lt;/a> 時 top 是 b，立即拒絕。
- &lt;p title="a>b">x&lt;/p>：引號中的 > 不切開 tag。
- &lt;p a=x/> 沒有關 p；&lt;p a=x /> 則已自閉合。

## 題目變動時：先查修改位置

行號以含註解的 .cpp 原檔為準。每個變體獨立套用；多項一起改時，重新定位，不要沿用位移後的行號。表格列修改索引，詳細改前／改後與測例在後文列出。

| 題目要求 | 原檔行號 | 完整改法 |
|---|---|---|
| 輸出 YES / NO | 127 | [修改範例 01（後文）](#html_check-change-1) |
| 一行一案 | 121–127 | [修改範例 02（後文）](#html_check-change-2) |
| XML 式：br 等也須配對關閉 | 32–33 | [修改範例 03（後文）](#html_check-change-3) |
| 求最大巢狀深度 | 11；101；127 | [修改範例 04（後文）](#html_check-change-4) |
| 首行 T，其後一行一案 | 121–127 | [修改範例 05（後文）](#html_check-change-5) |

<a id="html_check-change-1"></a>

### 01 輸出 YES / NO：改前／改後與測例

將 "VALID\\n" / "INVALID\\n" 改成 "YES\\n" / "NO\\n"。

第 127 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    cout << (valid ? "VALID\n" : "INVALID\n");
```

**改後（對照修改）**

```cpp
    cout << (valid ? "YES\n" : "NO\n");
```

已試編並執行的變體測例：

**輸入**

```text
<p/>
```

**輸出**

```text
YES
```

<a id="html_check-change-2"></a>

### 02 一行一案：改前／改後與測例

以此區塊替換這段；跨行一案時保留原版： while (getline(cin, s)) { p = 0; bool valid = false; try { valid = check(); } catch (const runtime\_error&amp;) {} cout &lt;&lt; (valid ? "VALID\\n" : "INVALID\\n"); } if (cin.bad()) return 1;

第 121–127 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    s.assign(istreambuf_iterator<char>(cin), {});
    // 讀取裝置失敗與文件語法非法不同：前者才用 exit 1。
    if (cin.bad()) { cerr << "input error\n"; return 1; }
    bool valid = false;
    // 語法錯誤也是分類結果 INVALID，所以這裡捕捉例外，不把它當程式崩潰。
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
```

**改後（對照修改）**

```cpp
while (getline(cin, s)) {
    p = 0; bool valid = false;
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
}
if (cin.bad()) return 1;
```

已試編並執行的變體測例：

**輸入**

```text
<p/>
<p>
```

**輸出**

```text
VALID
INVALID
```

<a id="html_check-change-3"></a>

### 03 XML 式：br 等也須配對關閉：改前／改後與測例

將兩行名單改成 const set&lt;string> empty{};；&lt;br/> 仍自閉合。

第 32–33 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    const set<string> empty{"area","base","br","col","embed","hr","img","input",
                            "link","meta","source","track","wbr"};
```

**改後（對照修改）**

```cpp
const set<string> empty{};
```

已試編並執行的變體測例：

**輸入**

```text
<br></br>
```

**輸出**

```text
VALID
```

<a id="html_check-change-4"></a>

### 04 求最大巢狀深度：改前／改後與測例

在 p 宣告後加 size\_t deepest = 0; push 後加 if (stack.size() > deepest) deepest = stack.size(); 輸出行改為 if (valid) cout &lt;&lt; deepest &lt;&lt; "\\n"; else cout &lt;&lt; "INVALID\\n"; 若同時改一行一案，每案開頭還需 deepest = 0;。

第 11 行：在此行後插入

**改前（原碼）**

```cpp
size_t p = 0;
```

**改後（對照修改）**

```cpp
size_t deepest = 0;
```

第 101 行：在此行後插入

**改前（原碼）**

```cpp
        stack.push_back(tag);
```

**改後（對照修改）**

```cpp
if (stack.size() > deepest) deepest = stack.size();
```

第 127 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    cout << (valid ? "VALID\n" : "INVALID\n");
```

**改後（對照修改）**

```cpp
if (valid) cout << deepest << "\n"; else cout << "INVALID\n";
```

已試編並執行的變體測例：

**輸入**

```text
<a><b></b></a>
```

**輸出**

```text
2
```

<a id="html_check-change-5"></a>

### 05 首行 T，其後一行一案：改前／改後與測例

第 121–127 行：用改後取代此行／區塊

**改前（原碼）**

```cpp
    s.assign(istreambuf_iterator<char>(cin), {});
    // 讀取裝置失敗與文件語法非法不同：前者才用 exit 1。
    if (cin.bad()) { cerr << "input error\n"; return 1; }
    bool valid = false;
    // 語法錯誤也是分類結果 INVALID，所以這裡捕捉例外，不把它當程式崩潰。
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
```

**改後（對照修改）**

```cpp
int T; if (!(cin >> T) || T < 0) return 1;
getline(cin, s);
if (s.find_first_not_of(" \t\r") != string::npos) return 1;
for (int tc = 0; tc < T; ++tc) {
    if (!getline(cin, s)) return 1;
    p = 0; bool valid = false;
    try { valid = check(); } catch (const runtime_error&) {}
    cout << (valid ? "VALID\n" : "INVALID\n");
}
if (cin.bad()) return 1;
```

已試編並執行的變體測例：

**輸入**

```text
2
<p/>
<p>
```

**輸出**

```text
VALID
INVALID
```
