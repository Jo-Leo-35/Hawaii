# Hawaii Guide · Leo & Tyson

只包含歐胡島的公開旅行指南：Day 1–8、景點 Google Maps 按鈕、行前分工及官方參考連結。Leo 維護，Tyson 查看。頁面沿用原 travel-atlas 的山海主視覺、白底橘色、Phosphor 分類圖示、搜尋列與照片卡片；每日行程優先呈現，公開資料獨立整理。

## 修改行程：只改一個檔案

開啟 [`data/trip.json`](data/trip.json)，點 GitHub 的鉛筆按鈕。修改後保留 JSON 的引號、逗號與括號，提交到 `main`。

| 內容 | 欄位 |
| --- | --- |
| 每日標題、區域與交通 | `days` 內的 `title`、`area`、`transport` |
| 每日時段、景點與備註 | `days` 內的 `stops` |
| 每日景點與地圖 | `stops` 的 `placeId`，對應下方 `places` 的 `id` |
| 每日飯店 | `lodging`，填飯店在 `places` 的 `id`；換飯店日可填兩個 |
| 分工與進度 | `checklist` 內的 `owners`、`status`、`note` |
| 景點、美食、飯店與地址 | `places`；`mapUrl` 使用核對過的 Google Maps 地點頁，`image`／`imageAlt` 為已審查的本機照片 |
| 官方資源 | `resources` |

`owners` 只能使用 `Leo`、`Tyson`。`status` 可使用：

- `planned`：行程安排。
- `pending`：待確認。
- `confirmed`：已安排，確實確認後才使用。
- `optional`：候選備案。

範例景點：

```json
{
  "period": "下午",
  "name": "Kaimana Beach",
  "note": "散步與休息，依體力調整。",
  "status": "planned",
  "placeId": "kaimana"
}
```

首頁先顯示 Day 1–8。山海主圖的搜尋、六種分類和「查看全部收藏」可查閱景點；預設收藏顯示四個主要活動。

網站不提供訪客編輯，也不把個人瀏覽器的勾選當成共用進度。每個人看到的是已發布的資料版本。

同一分店的地址與地圖只在 `places` 維護一次，每日行程引用同一筆資料。新增地點時，先在 Google Maps 開啟地點頁、核對分店名稱和完整地址，再將 `/maps/place/` 網址填入 `mapUrl`，移除問號之後的帳號或追蹤參數。不要改回模糊的名稱搜尋，也不要貼私人收藏清單。地址和地圖應一起修改。

## 自動檢查與發布

提交後，GitHub 的 **Actions** 會檢查 JSON 格式、資料欄位及基本公開資料界線，成功後發布 GitHub Pages。若檢查失敗，原本已上線版本會保留；到 Actions 查看錯誤，修正後再提交。

首次啟用：repository 的 **Settings → Pages → Source** 選 **GitHub Actions**。需要時可從 Actions 手動執行 **Validate and publish Hawaii Guide**。

網站網址：<https://Jo-Leo-35.github.io/Hawaii/>。

## 公開資料界線

- 用 Day 1–8，不放實際出遊日期、航班或私人接送位置。經授權公開 Stay Hotel Waikiki 與 Hilton Garden Inn Waikiki Beach 的名稱、公共地址及相對住宿日。
- 僅用 Leo／Tyson 代稱；不放 Email、電話、證件、個人入境／投保結果。
- 不放訂單編號、付款資訊、QR code、私人憑證或附件。
- Google 地圖連結指向核對過的公開地點頁，不使用個人收藏清單、Google 日曆、雲端文件或帶有帳號／訂單參數的連結。
- 官方資源網址只允許檢查器列出的公開網站；要增加新官方網站，可審查後更新 `scripts/validate.py` 的 `ALLOWED_HOSTS`。
- 不從私人日曆自動同步資料。發布前仍需人工確認文案沒有其他可識別的私人資訊。

新 repository 以乾淨的提交歷史開始；沒有帶入原 repository 的原始行程資料、試算表、備份、部署設定或 Git 歷史。

飯店與活動入口交叉核對：[Stay Hotel 地址](https://www.stayhotelwaikiki.com/contact-and-location)、[Hilton Garden Inn 位置](https://www.hilton.com/en/hotels/hnlkugi-hilton-garden-inn-waikiki-beach/hotel-location/)、[GoJump 地址](https://gojump-hawaii.com/contact)、[Kualoa Ranch 入口](https://www.kualoa.com/contact-and-direction)。Kualoa 的地圖採用官網所連結的門牌位置，避免把園區中心當成入口。海豚活動指向 Waiʻanae 港口，並非 Waikiki 辦公室。

## 本機檢查與預覽

只需要 Python 3，不需要 Node、API key、資料庫或付費地圖服務。

```sh
python3 scripts/test_validation.py
python3 scripts/build.py
python3 -m http.server 8080 --directory dist
```

部署內容由明確的檔案清單產生在 `dist/`，不會把整個工作目錄打包。

程式碼：MIT License；圖片不隨程式碼授權。Phosphor Icons 授權保留在 `assets/icons/LICENSE.txt`。照片來源與授權見 [`CREDITS.html`](CREDITS.html)。
