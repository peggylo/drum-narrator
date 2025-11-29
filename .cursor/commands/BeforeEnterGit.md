# Git 提交前檢查

## 目標
在 git commit 前，檢查是否有不宜進入版控的檔案，確保 `.gitignore` 設定完整。

## 執行步驟

### 1. 取得待提交檔案清單
- 執行 `git status --porcelain` 取得所有變更檔案
- 執行 `git diff --cached --name-only` 取得已暫存檔案

### 2. 分層級掃描問題

**🔴 禁止級（必須處理）**
- `.env`、`.env.*` 檔案
- 含有 API key、token、password、secret 的檔案內容
- 私鑰檔案：`.pem`、`.key`、`.p12`
- 依賴目錄：`node_modules/`、`venv/`、`__pycache__/`
- 建置產物：`dist/`、`build/`、`.next/`、`out/`

**🟡 警告級（建議排除）**
- 超過 10MB 的檔案
- IDE 設定：`.idea/`、`.vscode/settings.json`
- 系統檔案：`.DS_Store`、`Thumbs.db`
- Log 檔：`*.log`

**🔵 提醒級（僅供參考）**
- 1-10MB 的資源檔
- 暫存檔：`*.tmp`、`*.swp`

### 3. 檢查 .gitignore 設定
- 確認專案根目錄是否有 `.gitignore`
- 若發現禁止級項目未被忽略，建議應加入的規則

### 4. 輸出格式

```
【檢查結果】

🔴 禁止級問題（必須處理）
- [檔案路徑] - [問題說明]
→ 建議：加入 .gitignore 或移除敏感內容

🟡 警告級問題（建議處理）
- [檔案路徑] - [問題說明]
→ 建議：[處理建議]

🔵 提醒事項
- [檔案路徑] - [說明]

【.gitignore 建議】
若需新增規則，列出建議加入的內容

【結論】
✅ 可以安全提交 / ⚠️ 建議先處理上述問題
```

## 注意事項
- 禁止級問題發現時，明確提醒不要繼續 commit
- 若專案沒有 `.gitignore`，建議建立並提供常用模板
- 掃描敏感內容時，檢查變更檔案的實際內容（grep 關鍵字）

