# Frontend 開発ガイド（Next.js）

## 構成と原則

- App Router を採用。`app/` 配下でレイアウトとページを構成。
- 再利用コンポーネントは `components/components/{commons,forms,ui}` に配置。
  - `components/components/ui` と `components/lib` は shadcn/ui 生成物のため変更禁止。
- 型は `types/`、共通ロジックは `utils/`、フックは `components/hooks` に配置。

## ページの追加手順

1. `app/` 配下に新規ディレクトリ/ファイルを作成（必要に応じて `(authed)/` 配下）。
2. 必要なコンポーネントを `components/components` から組み合わせる。
3. API 呼び出しはバックエンドのエンドポイントに合わせて実装。

## ローカル起動

```bash
cd frontend
npm install
npm run dev
```

表示: http://localhost:3000

