# 🌟 Eval Analyzer

一個基於 🎈 **Streamlit** 的互動式工具，用來分析 **[Twinkle Eval](https://github.com/ai-twinkle/Eval)** 格式的評估檔案（`.json` / `.jsonl`）。  

## 🌐 線上使用
- [Twinkle Eval Analyzer (Zeabur 部署)](https://twinkle-ai-eval-analyzer.zeabur.app/) (thanks @BbsonLin)
- [Eval Analyzer (GitHub Pages)](https://doggy8088.github.io/eval-analyzer/) (thanks @doggy8088)
- [Eval Analyzer (Streamlit Cloud)](https://ai-twinkle-eval-analyzer.streamlit.app/) (thanks @thliang01)

## 📌 功能特色

<p align="center">
  <img src="https://github.com/ai-twinkle/llm-lab/blob/main/courses/2025-0827-llm-eval-with-twinkle/assets/gpt-oss-120b-mmlu-eval-report.png?raw=1" width="100%"/><br/>
  <em>圖：gpt-oss-120b 在 MMLU 部分子集上的表現成績預覽</em>
</p>

- 支援上傳多個 **Twinkle Eval 檔案**（`json` / `jsonl`）。
- 自動解析評估結果，抽取：
  - `dataset`
  - `category`
  - `file`
  - `accuracy_mean`
  - `source_label`（模型名稱 + timestamp）
- 提供整體平均值的計算，缺漏時自動補足。
- 視覺化：
  - 各類別的柱狀圖（依模型分組對照）。
  - 可選擇排序方式（平均由高→低、平均由低→高、字母排序）。
  - 支援分頁顯示（自訂每頁顯示類別數量）。
  - 指標可切換為原始值或 0–100 比例。
- 支援 **CSV 匯出**（下載分頁結果）。

## 🚀 使用方式

### 1. 安裝環境
建議使用虛擬環境（如 `venv` 或 `conda`）：

```bash
pip install -r requirements.txt
```
### 2. 啟動應用程式
```bash
streamlit run app.py
```

### 3. 操作流程
1. 在左側 Sidebar 上傳一個或多個 **Twinkle Eval 檔案**。
2. 選擇要查看的資料集。
3. 設定排序方式、分頁大小、顯示比例（0–1 或 0–100）。
4. 查看圖表與資料表，並可下載 CSV。

## 📂 檔案格式要求
每份 json / jsonl 檔案需符合 Twinkle Eval 格式，至少包含以下欄位：

```json
{
  "timestamp": "2025-08-20T10:00:00",
  "config": {
    "model": { "name": "my-model" }
  },
  "dataset_results": {
    "datasets/my_dataset": {
      "average_accuracy": 0.85,
      "results": [
        {
          "file": "category1.json",
          "accuracy_mean": 0.9
        },
        {
          "file": "category2.json",
          "accuracy_mean": 0.8
        }
      ]
    }
  }
}
```
或者可以到 Twinkle AI [Eval logs](https://huggingface.co/collections/twinkle-ai/eval-logs-6811a657da5ce4cbd75dbf50) collections 下載範例。

## ⚠️ 檔案格式相容性注意事項

**重要提醒**：此工具目前支援特定的 JSON/JSONL 格式。來自外部資料集（如 Hugging Face 儲存庫）的檔案可能無法直接相容。

### 常見問題
- **缺少必要欄位**：缺少 `config` 或 `dataset_results` 欄位的檔案將無法載入
- **錯誤的檔案命名**：請使用 `results_*.json` 而非 `eval_results_*.jsonl` 格式
- **外部資料集格式**：來自其他工具或儲存庫的評估日誌可能使用不同的架構
- **欄位命名**：不同的欄位名稱（例如 `accuracy` vs `accuracy_mean`）可能導致解析錯誤

### 疑難排解
如果遇到「缺少必要欄位」錯誤：
1. 確認您的檔案包含所有必要的頂層欄位
2. 檢查巢狀物件是否遵循預期結構
3. 對於外部資料集，考慮建立轉換腳本或[提出議題](https://github.com/ai-twinkle/eval-analyzer/issues)請求格式支援

### 貢獻
我們歡迎支援額外格式的貢獻！請參閱我們的[貢獻指南](CONTRIBUTING.md)或提交功能請求。

## 📊 輸出範例

- **圖表**：顯示各模型在不同類別的 accuracy_mean 比較。
- **表格**：Pivot Table，行為類別，列為模型，值為 accuracy。
- **下載**：每頁結果可匯出成 CSV。

## 📄 License
MIT