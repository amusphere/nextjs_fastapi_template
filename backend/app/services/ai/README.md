# AIアシスタント - 動的ハブアンドスポーク アーキテクチャ

## 概要

このAIアシスタントは、動的なハブアンドスポーク形式で複数のサービス統合を提供するシステムです。ユーザーの自然言語でのリクエストを解析し、適切なアクションを決定・実行します。

## 🆕 動的スポーク設定システム

### 新機能
- **動的設定読み込み**: 各スポークのアクション定義をJSONファイルで管理
- **マルチスポーク対応**: Google Calendar、Slack、Emailなど複数サービスに対応
- **自動プロンプト生成**: スポーク設定に基づいてシステムプロンプトを動的生成

### アーキテクチャ

#### ハブ（Hub）
- **`OperatorHub`**: 動的スポーク設定を読み込み、プロンプト解析を実行
- **`SpokeConfigLoader`**: スポーク設定ファイルを動的に読み込み
- **`DynamicPromptGenerator`**: 設定に基づいてシステムプロンプトを自動生成

#### スポーク（Spokes）
各スポークは独立したフォルダ構造で管理：

```
app/services/ai/spokes/
├── google_calendar/
│   ├── actions.json    # アクション定義
│   ├── spoke.py       # 実装
│   └── __init__.py
├── slack/
│   ├── actions.json    # Slackアクション定義
│   └── (実装予定)
└── email/
    ├── actions.json    # Emailアクション定義
    └── (実装予定)
```

### 主要コンポーネント

```
app/services/ai/
├── models.py              # データモデル定義
├── operator.py            # 動的ハブ（OperatorHub）
├── spoke_config.py        # スポーク設定管理
├── prompt_generator.py    # 動的プロンプト生成
├── executor.py            # アクション実行エンジン
├── orchestrator.py        # 統合レイヤー
├── examples.py            # 使用例
└── spokes/               # 動的スポーク
    ├── google_calendar/  # Google Calendarスポーク
    ├── slack/           # Slackスポーク（設定のみ）
    └── email/           # Emailスポーク（設定のみ）
```

## 利用可能な機能

### 🗓️ Google Calendar
#### 1. カレンダーイベント取得
```
"今日の予定を教えて"
"来週のスケジュールを確認したい"
"明日から3日間の予定はどうなってる？"
```

#### 2. カレンダーイベント作成
```
"明日の午後2時から会議の予定を作成して"
"来週の金曜日に歓送迎会をスケジュールしたい"
"毎週月曜日の朝10時から定例会議を設定"
```

#### 3. カレンダーイベント更新
```
"明日の会議の時間を1時間遅らせて"
"プロジェクト会議の場所を会議室Bに変更"
```

#### 4. カレンダーイベント削除
```
"明日の会議をキャンセルして"
"金曜日の予定を削除したい"
```

### 💬 Slack（設定済み）
#### 1. メッセージ送信
```
"一般チャンネルに「おはようございます」を送信して"
"開発チームに進捗報告を投稿"
```

#### 2. チャンネル一覧取得
```
"Slackチャンネルの一覧を表示して"
"参加しているチャンネルを教えて"
```

#### 3. メッセージ履歴取得
```
"一般チャンネルの最新メッセージを確認"
"開発チームの過去10件のメッセージを表示"
```

### 📧 Email（設定済み）
#### 1. メール送信
```
"田中さんに会議の議事録をメールで送信"
"チーム全員に進捗報告をメールで共有"
```

#### 2. メール確認
```
"未読メールを確認して"
"受信箱の最新メールを表示"
```

#### 3. メール検索
```
"田中さんからのメールを検索"
"「会議」というキーワードでメールを探して"
```

### 4. カレンダーイベント削除
```
"明日の午後の会議をキャンセルして"
"来週の金曜日の予定を削除"
```

## API エンドポイント

### POST `/api/ai/process`

AIアシスタントにリクエストを送信して処理結果を取得

**リクエスト:**
```json
{
  "prompt": "今日の予定を教えてください",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**レスポンス:**
```json
{
  "success": true,
  "operator_response": {
    "analysis": "ユーザーは今日の予定を確認したいと要求しています",
    "confidence": 0.95,
    "actions_planned": 1
  },
  "execution_results": [
    {
      "success": true,
      "data": [...],
      "error": null,
      "metadata": {
        "total_events": 3,
        "period": "2024-01-15 to 2024-01-15"
      }
    }
  ],
  "summary": {
    "total_actions": 1,
    "successful_actions": 1,
    "failed_actions": 0,
    "success_rate": 1.0,
    "overall_status": "completed"
  }
}
```

### GET `/api/ai/actions`

利用可能なアクションタイプを取得

## 使用方法

### 1. 基本的な使用例

```python
from app.services.ai.orchestrator import process_ai_request

# 今日の予定を取得
result = process_ai_request(
    prompt="[USER_ID: 123] 今日の予定を教えてください"
)

print(f"成功: {result['success']}")
print(f"解析結果: {result['operator_response']['analysis']}")
```

### 2. APIを通じた使用

```bash
curl -X POST "http://localhost:8000/api/ai/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "明日の午後2時から会議の予定を作成してください",
    "max_tokens": 1000,
    "temperature": 0.7
  }'
```

### 3. サンプル実行

```bash
cd backend
python -m app.services.ai.examples
```

## 環境設定

### 必要な環境変数

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# 暗号化キー
ENCRYPTION_KEY=your_32_byte_hex_encryption_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### データベース設定

Google OAuthトークンの保存にはデータベースが必要です：

```bash
# マイグレーション実行
alembic upgrade head
```

## 拡張性

### 新しいスポークの追加

1. `app/services/ai/spokes/` に新しいスポークファイルを作成
2. `ActionType` enum に新しいアクションタイプを追加
3. `ActionExecutor` に新しいアクション実行ロジックを追加
4. オペレーターのシステムプロンプトを更新

例：
```python
# spokes/email.py
class EmailSpoke:
    async def send_email(self, request: EmailRequest) -> SpokeResponse:
        # メール送信ロジック
        pass
```

### 新しい機能の追加

- **Microsoft Calendar対応**: OutlookやTeamsカレンダーとの連携
- **リマインダー機能**: イベント前の通知設定
- **会議室予約**: 利用可能な会議室の検索・予約
- **参加者管理**: 会議参加者の自動招待
- **時間調整**: 参加者全員の空き時間から最適な時間を提案

## トラブルシューティング

### 認証エラー
- Google OAuth設定の確認
- 暗号化キーの確認
- データベース接続の確認

### プロンプト解析エラー
- OpenAI APIキーの確認
- プロンプトの形式確認
- LLMモデルの応答確認

### 実行エラー
- Google Calendar API権限の確認
- ユーザーの認証状態確認
- パラメータの形式確認

## セキュリティ

- OAuthトークンは暗号化してデータベースに保存
- APIアクセスは認証が必要
- ユーザーは自分のカレンダーのみアクセス可能
- 機密情報はログに出力されません

## パフォーマンス

- 非同期処理による高速応答
- 優先度によるアクションの順序制御
- エラー時の適切な処理継続
- LLMレスポンスのキャッシュ（今後実装予定）
