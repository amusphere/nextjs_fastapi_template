# Contributor Guide
このリポジトリはフロントエンドとバックエンドの両方を含むリポジトリです。
それぞれのディレクトリは独立しており、フロントエンドとバックエンドの両方を同時に開発することができます。

## Development setup
- 基本的なセットアップ方法はルートにあるREADME.mdを参考にしてください。
- Codexにおけるセットアップはcodex-setup.shを実行することで行えます。

## Directory structure
基本的なディレクトリ構造はルートにあるREADME.mdを参考にしてください。
基本的に修正対象となるのは`Backend/`と`Frontend/`のディレクトリを下記に示すように分けているので、各ディレクトリの中を修正していく形になります。

### Backend
FastAPIをベースにしており、下記のようなレイヤーで構成されています。

- `routers/` : APIのルーティングを定義するレイヤー
- `models/` : リクエスト/レスポンスのスキーマを定義するレイヤー
- `repositories/` : データアクセスを行うレイヤー
- `services/` : ビジネスロジックを定義するレイヤー
- `utils/` : ユーティリティ関数を定義するレイヤー

## Frontend
Next.jsをベースにしており、下記のようなレイヤーで構成されています。

- `app/api/` : APIのルーティングを定義するレイヤー
- `app/(authed)/` : 認証が必要なルーティングを定義するレイヤー
- `app/auth/` : 認証関連のルーティングを定義するレイヤー
- `components/components/commons` : 共通コンポーネントを定義するレイヤー
- `components/components/forms` : フォームコンポーネントを定義するレイヤー
- `components/components/ui` : shadcn/uiのコンポーネントを定義するレイヤー (変更しないでください)
- `components/hooks/` : カスタムフックを定義するレイヤー
- `components/lib/` : shadcn/uiのライブラリ関数を定義するレイヤー (変更しないでください)
- `components/pages/` : ページコンポーネントを定義するレイヤー
- `types/` : TypeScriptの型を定義するレイヤー
- `utils/` : ユーティリティ関数を定義するレイヤー

## Lint and Format

### Backend
- blackを使用してコードの整形を行います。

### Frontend
- `npm run lint`でlintを実行します。

## Testing

### Backend
下記コマンドでサーバを起動させて、エンドポイントを叩いてテストを行います。

```bash
uv run fastapi dev --host 0.0.0.0 --port 8000
```

必要あればデータベースのマイグレーションを行います。

```bash
uv run alembic upgrade head
```

### Frontend
下記コマンドでサーバを起動させて、画面を確認しながらテストを行います。
この際backendのサーバも起動しておく必要があります。

```bash
npm run dev
```

また、ビルドコマンドでビルドが通るか確認します。

```bash
npm run build
```
