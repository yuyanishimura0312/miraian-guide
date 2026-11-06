# miraian-guide

未来庵（MIRAI-AN）へのアクセスガイドページ。ミラツクの未来学研究の拠点・未来庵への行き方（住所・所要時間・OpenStreetMap 実データの道順地図・Google マップ・バスとお車・写真）と、未来庵の紹介・未来学入門講座の案内を1ページにまとめた静的サイト。

## 公開URL

https://miraian.emerging-future.org

GitHub Pages（`main` ブランチのルート）で公開している。push すると公開が更新される。

## 事実の正本

ページに書く事実（住所・座標・所要時間・バス系統・ロゴの扱い）は **`docs/FACTS.md`** だけから取る。ここに無い事実を足さない。
事実を変えたら、`docs/FACTS.md` → `tools/index.template.html`（本文・所要時間の帯・地図の横の一覧・JSON-LD・meta description）→ `llms.txt` → 本 README の順で揃え、`python3 tools/build_index.py` で `index.html` を作り直す。

## ファイル構成

```
miraian-guide/
├── index.html                 ページ本体（生成物。tools/build_index.py が作る。直接編集しない）
├── docs/FACTS.md              事実の正本
├── tools/
│   ├── index.template.html    ページの原稿（CSS と JS を内包。{{MAP_SVG}} に地図が入る）
│   ├── build_index.py         template + route-map.svg → index.html
│   ├── map/
│   │   ├── build_map.py       OpenStreetMap データから道順地図 SVG を生成（道路・経路・ピンの座標はここが正本）
│   │   ├── data/osm.json      Overpass 抽出（© OpenStreetMap contributors, ODbL）
│   │   └── out/route-map.svg  生成された地図（1000x653）／ route.json（距離）
│   ├── og.html                共有用画像の元
│   └── photos/
│       ├── fetch_drive.py     Google Drive の写真フォルダから一覧と縮小版を取得（取得物はリポジトリの外に置く）
│       ├── contact_sheet.py   全写真の一覧シート（選定用）
│       ├── selection.json     掲載する写真の正本（区分・キャプション・代替テキスト・Drive の出所）
│       ├── build_photos.py    selection.json → assets/photos/*.webp ＋ ギャラリーの HTML 断片
│       ├── test_gallery.py    絞り込み・拡大表示の動作確認（Playwright）
│       └── out/               生成物（manifest.json / gallery.html / counts.json）
├── assets/
│   ├── photos/                    掲載写真（WebP。build_photos.py の生成物。直接編集しない）
│   ├── miratuku-logo-h.png        正規ロゴ 横型（ヘッダー・フッター用。NOSIGNER 2011）
│   ├── miratuku-logo-h-white.png  同 白抜き（暗い地の上のヘッダー用）
│   ├── miratuku-mark.png / miratuku-logo.png / apple-touch-icon.png
│   └── og-access.png          共有用画像（1200x630）
├── robots.txt / sitemap.xml / llms.txt
├── favicon.ico
└── CNAME
```

## 作り直し

```bash
python3 tools/map/build_map.py     # 地図を作り直す（OSM データから）
python3 tools/photos/build_photos.py <縮小版の置き場>   # 写真を作り直す（selection.json を変えたとき）
python3 tools/build_index.py       # index.html を組み直す
python3 tools/photos/test_gallery.py http://127.0.0.1:<port>/   # 動作確認（リポジトリ直下を http.server で配信してから）
```

### 写真を差し替える・増やす

写真の元は Google Drive「未来庵」フォルダ（`1eSAIicK6Yal-XAItXnDmEc8I2E-lPJzb`。esse.miratuku@gmail.com で閲覧）。

1. `python3 -I tools/photos/fetch_drive.py list <一覧.json>` で一覧を作り、`fetch <一覧.json> <置き場> 2400` で縮小版を取る。元写真には1枚100MB級の PNG があるため Drive の縮小版を使い、縮小版の無いものだけ元を取得してその場で縮小・削除する
2. `contact_sheet.py` で一覧シートを作り、`selection.json` に載せる写真を足す。★`drive_id` は一覧から引く（手で打たない。初回は手打ちの40件中38件が誤っていた）
3. `build_photos.py` → `build_index.py` → `test_gallery.py`

★人が写っている写真と、竣工時の書籍・雑誌のスキャンは、本人の了承と権利が確認できるまで載せない（2026-11-07 の選定で除外）。

## デザイン（v3・2026-11-04）

- ミラツク正式CI（NOSIGNER 2011）。Web アクセント #783C28、地 #FAF8F5、文字 #1A1A1A。地図の配色は CI 12色。赤白CI（#CC1400）は使わない
- ロゴは正規ファイルから書き出した PNG をそのまま使う。生成・描き直し・色替え・種や渦の図柄の自作はしない
- 書体は姉妹ページ `miraian-lp`（journal.emerging-future.org/miraian/）と同じ Zen Kaku Gothic New / Archivo / IBM Plex Mono
- 構成（v4・2026-11-04）: ヒーロー（庭に開く和室の写真＋所在地カード）→ 導入（未来学研究の拠点としての位置づけ＋所要時間3項目）→ 01 道順（OSM 地図・手順・Google マップ補助）→ 02 バス・お車 → 03 写真（到着の目印になる4枚＋絞り込みと拡大表示のできるギャラリー。2026-11-07 追加）→ 04 未来庵について（暗面）→ 05 未来学入門講座（暗面の続き）→ フッター。左に索引列・右に本文の2列の編集的な版面
- 余白・寸法・色は `:root` のトークン（`--space-*` `--fs-*` ほか）から引く。純黒・イタリックは使わない。文字のコントラストは WCAG AA 以上。写真の上の文字には暗い下地を敷く。prefers-reduced-motion で動きを止める
- 390px 幅でもページ内ナビ（横スクロール）を残す。CDN 画像は 2x の srcset を持つ
- ギャラリーは 1100px 以上で5列、760px 以下では最初の12枚だけを出し「残りN枚を表示する」で開く（絞り込みで折りたたみに戻る。折りたたんだ写真は拡大表示の前後送りにも入らない）。到着の目印4枚のモザイクは5行で組む（2026-11-07 全体見直し）

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

- 写真はすべて自前の `assets/photos/`（2026-11-07 に Spacemarket CDN への直リンク4枚から移行）。正本は `tools/photos/selection.json`
- 所要時間（出町柳駅から徒歩約18分・京大農学部前から徒歩約5分・京都駅から市バス7系統で約35分の目安 ほか）は `docs/FACTS.md` が正本。ページ側には同じ値が ヒーローのカード・帯・道順の手順・バスの節・地図の横の一覧・JSON-LD・meta description に出ている
