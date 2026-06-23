# 學校鬧鐘系統 (School Bell System)

依照學校上下課時間表，自動定時播放上課鈴與下課鈴的鬧鐘系統。本專案提供 **網頁版** 與 **Python 桌面版** 兩種實作。

---

## 📦 專案內容

| 版本 | 路徑 | 技術 | 說明 |
|------|------|------|------|
| 網頁版（主力） | [`index.html`](index.html) | HTML / CSS / JavaScript | 開啟即用的單檔網頁，設定儲存在瀏覽器 |
| 桌面版（已封存） | [`pybell/`](pybell/) | Python + CustomTkinter + Pygame | 早期的桌面實作，可打包為 `SchoolBell.exe`，目前已停止維護 |

> ⚠️ **本專案以網頁版 [`index.html`](index.html) 為主力。** Python 桌面版 [`pybell/`](pybell/) 為早期實作、功能與網頁版重複，現已停止維護，僅作封存保留。

---

## ⏰ 預設時間表

| 節次 | 上課 | 下課 |
|:----:|:----:|:----:|
| 第 1 節 | 08:20 | 09:10 |
| 第 2 節 | 09:15 | 10:05 |
| 第 3 節 | 10:15 | 11:05 |
| 第 4 節 | 11:10 | 12:00 |
| 第 5 節 | 13:20 | 14:10 |
| 第 6 節 | 14:15 | 15:05 |
| 第 7 節 | 15:15 | 16:05 |
| 第 8 節 | 16:10 | 17:00 |

---

## ✨ 主要功能

- **鬧鐘排程**：依 8 個上課與 8 個下課時間點準時觸發。
- **獨立 / 批次控制**：每節上下課鈴可單獨啟用或停用，並提供「全部啟用 / 停用」、「啟用所有上課 / 下課鈴」等快捷操作。
- **鈴聲管理**：
  - 支援「網路 URL」或「本機音訊檔案」作為鈴聲來源。
  - 上課與下課各自擁有獨立的播放清單。
  - 每個清單支援「順序播放」與「隨機播放」模式。
- **設定保存**：所有設定自動儲存，下次啟動自動載入（網頁版存於瀏覽器，桌面版存於 `config/settings.json`）。
- **即時狀態**：顯示目前時間與下一個即將響鈴的鬧鐘。
- **測試工具**：提供「立即測試下一個鬧鐘」與「手動停止鈴聲」。

---

## 🌐 網頁版使用方式

直接用瀏覽器開啟 [`index.html`](index.html) 即可，無需安裝。

> 版面為響應式 (RWD)，按鈕網格會依螢幕寬度自動調整為 8×2、4×4 或 2×8。

---

## 🖥️ 桌面版 (pybell) 使用方式（已封存）

> 此版本已停止維護，以下說明僅供參考。建議直接使用網頁版。

### 直接執行
執行 `dist/SchoolBell.exe` 即可啟動（若已建置）。

### 從原始碼執行

1. 安裝 Python 3.12+。
2. 安裝相依套件：
   ```bash
   pip install customtkinter==5.2.2 pygame==2.6.0 schedule==1.2.0 requests==2.32.5
   ```
3. 在專案根目錄執行：
   ```bash
   python pybell/main.py
   ```

### 重新打包成 .exe

```bash
pip install pyinstaller==6.8
pyinstaller --onefile --windowed --name SchoolBell pybell/main.py
```
建置完成的 `.exe` 會輸出於 `dist/` 目錄。

---

## 📁 目錄結構

```
bellring/
├─ index.html              # 網頁版（單檔）
├─ pybell/                 # Python 桌面版
│  ├─ main.py              # 主程式進入點
│  ├─ app/                 # 核心模組（排程、音訊、設定、UI…）
│  └─ config/settings.json # 設定檔
├─ SchoolBell.spec         # PyInstaller 打包設定
└─ README.md
```

> `build/`、`dist/`、`__pycache__/`、`logs/` 為建置與執行產物，已於 `.gitignore` 中排除，不納入版本控制。

---

*Powered by 皮卡賴*
