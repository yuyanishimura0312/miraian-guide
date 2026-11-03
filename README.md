# miraian-guide

未来庵（MIRAI-AN）へのアクセスガイドページ。住所・所要時間・道順の概念図・地図・写真・ご来訪時の注意を1ページにまとめた静的サイト。

## 公開URL

https://miraian.emerging-future.org

GitHub Pages（`main` ブランチのルート）で公開している。push すると公開が更新される。

## ファイル構成

```
miraian-guide/
├── index.html            ページ本体（単一ファイル。CSS と JS を内包）
├── assets/
│   ├── og-access.png     共有用画像（1200x630）。tools/og.html から生成
│   ├── miratuku-mark.png ミラツク CI シンボル（miraian-lp の正規ロゴを縮小）
│   ├── miratuku-logo.png 構造化データのロゴ
│   └── apple-touch-icon.png
├── tools/og.html         共有用画像の元
├── robots.txt / sitemap.xml / llms.txt
├── favicon.ico
└── CNAME
```

## デザイン（v2・2026-11-03 全面改訂）

- ミラツク正式CI（NOSIGNER 2011）。Web アクセント #783C28、地 #FAF8F5、文字 #1A1A1A。図の配色は CI 12色。赤白CI（#CC1400）は使わない
- 書体は姉妹ページ `miraian-lp`（journal.emerging-future.org/miraian/）と同じ Zen Kaku Gothic New / Archivo / IBM Plex Mono
- 構成: ヒーロー（庭の写真＋所在地カード）→ 所要時間 → 道順（概念図と手順が連動）→ ほかの来方 → 地図（押して読み込む）→ 写真（拡大表示つき）→ ご来訪の前に → 未来庵について → URL を送る
- 純黒・イタリックは使わない。文字のコントラストは WCAG AA 以上を目標とし、写真の上の文字には暗い下地を敷く（2026-11-03 の独立採点で写真上の文字が未達と指摘され是正）。prefers-reduced-motion で動きを止める

## SEO

- title / description / canonical / OGP / Twitter カード / geo メタ
- 構造化データ（JSON-LD）: NGO・Place（住所・座標・地図）・WebPage・BreadcrumbList
- robots.txt・sitemap.xml・llms.txt

## 共有用画像の作り直し

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
  --window-size=1200,630 --virtual-time-budget=6000 \
  --screenshot=assets/og-access.png "file://$PWD/tools/og.html"
```

## 注意事項

- 写真は Spacemarket CDN への直リンク。差し替えるときは `index.html` の `cdnspacemarket.com` の URL を自前の画像に変える
- 所要時間（出町柳駅から「徒歩約5分」・京大正門前から「徒歩2分」・京都駅から「約30分」）は 2026-11-04 に西村さんが確認した値。変えるときは下の5か所を揃える
- 事実を変えたら、本文・所要時間の帯・地図の横の一覧・構造化データ・llms.txt の5か所を揃える
