# Git Commit & Push

## 目標
執行 git add、commit，並根據變更內容自動生成 commit message。若有遠端倉庫則繼續 push。

## 執行步驟

### 1. 確認變更內容
- 執行 `git status` 查看當前狀態
- 執行 `git diff --stat` 查看變更摘要

### 2. 暫存所有變更
- 執行 `git add .`

### 3. 生成 Commit Message
根據 `git diff --cached` 的內容，依照以下格式生成 commit message：

**開頭類型**
- `Feat:` 新增功能
- `Fix:` 修復問題
- `Test:` 測試相關
- `Refactor:` 重構程式碼
- `Doc:` 文件更新
- `Conf:` 設定變更
- `Style:` 程式碼格式調整
- `Chore:` 雜項任務
- `Perf:` 效能優化

**格式範例**
```
Feat: 新增使用者登入功能

- 實作登入表單驗證
- 新增 JWT token 處理
```

### 4. 執行 Commit
- 顯示生成的 commit message 讓使用者確認
- 執行 `git commit -m "..."`

### 5. 檢查遠端並 Push
- 執行 `git remote -v` 檢查是否有遠端倉庫
- 若有遠端，執行 `git push`
- 若 push 失敗，顯示錯誤訊息供使用者處理

### 6. 輸出格式

```
【變更摘要】
- X 個檔案變更
- 新增 XX 行，刪除 XX 行

【Commit Message】
[生成的 commit message]

【執行結果】
✅ Commit 完成：[commit hash 前 7 碼]
✅ Push 完成：[branch 名稱] → [remote/branch]
或
⚠️ 無遠端倉庫，僅完成本地 commit
```

## 注意事項
- Commit message 使用繁體中文撰寫
- 若變更內容涵蓋多種類型，選擇最主要的類型
- Push 失敗時（如衝突），提示使用者手動處理

