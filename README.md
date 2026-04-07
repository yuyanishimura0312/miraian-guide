# miraian-guide

未来庵（Miraian）へのアクセスガイドページ。住所・地図・交通案内・ギャラリーを1ページにまとめた静的サイト。

## 公開URL

https://miraian.emerging-future.org

## ファイル構成

```
miraian-guide/
├── index.html   # ページ本体（単一ファイル構成）
├── favicon.ico  # ファビコン
├── CNAME        # GitHub Pages カスタムドメイン設定
└── .gitignore
```

## 更新方法

`index.html` を直接編集し、GitHub にプッシュすると自動で公開が更新される。
GitHub Pages（`main` ブランチルート）でホスティングしている。

```bash
git add index.html
git commit -m "update: <変更内容>"
git push origin main
```

## 注意事項

- ギャラリー画像は現在 Spacemarket CDN の直リンクを使用している。
  画像の差し替えが必要な場合は `index.html` の `<img src="...">` を自前の画像パスに変更すること。
- 「徒歩約10分」などの所要時間は実際の現地状況に合わせて適宜更新すること。
