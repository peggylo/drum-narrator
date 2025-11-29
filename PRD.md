# 鼓譜語音講解產生器 PRD

## 專案背景

使用者是盲人，正在學習爵士鼓。因看不到樂譜，需要老師口頭解釋譜面內容，耗時費力。

## 目標

開發一個工具，輸入鼓譜 PDF，自動產生口語化講解逐字稿，風格模仿老師的講解方式。

## 使用情境

1. **直接聆聽**：產出的逐字稿可用 TTS 朗讀給使用者聽
2. **互動問答**：逐字稿作為 GPTs 知識庫，使用者可語音提問特定段落

## 現有資源

| 檔案 | 說明 |
|------|------|
| sample/*.pdf | 範例樂譜 |
| sample/第一行.md 等 | 老師解釋樂譜的逐字稿 |
| 樂譜轉換原則.md | 初版轉換規則（需修正） |

## 技術架構

```
PDF 樂譜 → [Python] 轉圖片 → [Python + AI Vision API] 解析成 JSON → [Python] 生成逐字稿 → [GPTs] 口語互動
                                                                          ↑                    ↑
                                                                     穩定、規則化          自然、彈性
```

### 使用方式

```bash
python code/main.py --input ./input/Sugar.pdf --output ./output/
```

自動執行，產出至 `output/{樂譜名}_{YYYYMMDD_HHMM}/`：
1. PDF → 圖片
2. 圖片 → JSON
3. JSON → 講解稿

### 技術選型

- **PDF 轉圖片**：Python + pdf2image
- **AI Vision API**：OpenAI `gpt-4.1-mini`（成本低、足夠辨識鼓譜符號；如辨識不準再升級 `gpt-4.1`）
- **輸出 JSON**：結構化資料，穩定度高於純文字
- **規則轉換**：依據老師講解風格，將 JSON 轉成口語講解

## 可行性驗證結果

已用範例樂譜第一行測試：

| 項目 | 老師逐字稿 | AI 解析結果 | 符合 |
|------|------------|-------------|------|
| 休息小節數 | 4 小節 | 4 小節 | ✅ |
| 無 Hi-hat | 只有大小鼓 | 只有大小鼓 | ✅ |
| 基本節奏 | 懂、搭懂、嗯、搭 | 懂、搭懂、嗯、搭 | ✅ |
| 第四小節變化 | 懂懂、搭懂、嗯、搭 | 第一拍多一個大鼓 | ✅ |

---

# 檔案結構

```
drum/
├── code/
│   ├── main.py                      # 主程式（PDF轉圖片、Vision解析、逐字稿生成）
│   ├── parse_drum_sheet_prompt.md   # 樂譜解析 Prompt（被 main.py 讀取）
│   └── gpts_system_prompt.md        # GPTs System Prompt（手動放入 ChatGPT）
├── input/                           # 放置待處理的 PDF 樂譜
├── output/
│   └── {樂譜名}_{YYYYMMDD_HHMM}/    # 以樂譜名稱+時間戳命名
│       ├── images/
│       │   ├── page_1.png
│       │   └── page_2.png
│       ├── {樂譜名}.json
│       └── {樂譜名}_transcript.md
└── sample/                          # 範例資料（老師逐字稿、測試樂譜）
```

---

# 開發步驟

## 步驟 1：PDF 轉圖片

將 PDF 樂譜轉換為 PNG 圖片，供後續 AI Vision 解析使用。用範例樂譜測試。

產出：`code/main.py`（PDF 轉圖片功能）

## 步驟 2：樂譜解析 Prompt + 程式

撰寫 prompt 讓 AI Vision 看圖輸出 JSON，並實作呼叫 API 的程式：
- 定義 JSON schema（每小節打擊內容、段落標記、特殊標記）
- 呼叫 OpenAI Responses API（model: `gpt-4.1-mini`）

用範例樂譜測試，對照老師逐字稿驗證解析結果。

產出：`code/parse_drum_sheet_prompt.md`、`code/main.py`（Vision 解析功能）

## 步驟 3：逐字稿生成程式

用 Python 將 JSON 轉換成講解逐字稿：
- 讀取 `樂譜轉換原則.md` 作為規則來源
- 規則包含：口訣轉換、難點判斷、手法說明、銜接語句
- 同時修正/完善 `樂譜轉換原則.md` 的內容

選擇程式而非 AI 的原因：穩定優先，每次輸出一致。口語化處理留給 GPTs。

用範例樂譜測試，對照老師逐字稿驗證品質。

產出：`code/main.py`（逐字稿生成功能）、更新版 `樂譜轉換原則.md`

## 步驟 4：GPTs System Prompt

因使用者是盲人，全程使用語音對話，需針對此情境設計。

參考 `GPThostsample.md` 的框架結構，但簡化流程（專注「問答」情境）。

設計重點：
- **persona**：友善、簡潔、有耐心
- **core_principles**：回答簡短、用口訣描述、聽不懂時換方式說
- **response-patterns**：問特定小節、問手法、聽不懂時的回應
- **error-recovery**：處理模糊問題、引導使用者重新提問

產出：`code/gpts_system_prompt.md`（手動放入 ChatGPT GPTs）

---

# 未來優化項目

## 擴充樂譜測試

目前僅以單一範例樂譜作為開發與驗證範例。若目標是通用工具，需擴充測試範圍：

- **不同曲風**：搖滾、放克、拉丁等節奏型態差異大的樂譜
- **不同複雜度**：從簡單的基本節奏到複雜的過門與切分音
- **不同排版格式**：不同出版社或軟體產出的鼓譜可能有版面差異

完成核心功能後，可逐步蒐集更多樂譜進行測試，確保解析與講解的準確度。

