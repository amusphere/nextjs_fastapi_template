# AIアシスタント - 動的ハブアンドスポーク アーキテクチャ

## 概要

このAIアシスタントは、動的なハブアンドスポーク形式で複数のサービス統合を提供するシステムです。ユーザーの自然言語でのリクエストを解析し、適切なアクションを決定・実行します。

## 動的スポーク読み込みシステム

### 新機能
- **完全動的読み込み**: spokesフォルダから自動的にスポークを検出・読み込み
- **プラグイン形式**: 新しいスポークはフォルダを追加するだけで利用可能
- **ゼロ設定デプロイ**: コード変更なしで新しいサービス統合を追加
- **BaseSpoke インターフェース**: 統一されたスポーク実装基準

### アーキテクチャ

#### ハブ（Hub）
- **`OperatorHub`**: 動的スポーク設定を読み込み、プロンプト解析を実行
- **`DynamicSpokeManager`**: スポークの自動検出・インスタンス化・実行管理
- **`SpokeRegistry`**: ロードされたスポークの登録・管理
- **`DynamicSpokeLoader`**: スポークファイルの動的インポート

#### スポーク（Spokes）
各スポークは独立したフォルダ構造で管理：

```
app/services/ai/spokes/
├── google_calendar/
│   ├── actions.json    # アクション定義
│   └── spoke.py       # GoogleCalendarSpoke実装
├── slack/              # 将来追加予定
│   ├── actions.json
│   └── spoke.py
└── email/              # 将来追加予定
    ├── actions.json
    └── spoke.py
```

### 新しいスポークの追加手順

1. **フォルダ作成**: `spokes/` 以下に新しいフォルダを作成
2. **actions.json**: アクション定義ファイルを作成
3. **spoke.py**: `BaseSpoke`を継承したクラスを実装
4. **自動検出**: システム再起動で自動的に利用可能

#### 例: 新しいスポークの実装

```python
# spokes/my_service/spoke.py
from ...spoke_interface import BaseSpoke
from ...models import SpokeResponse

class MyServiceSpoke(BaseSpoke):
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> SpokeResponse:
        # アクション実行ロジック
        pass

    @classmethod
    def get_supported_actions(cls) -> list[str]:
        return ["my_action_1", "my_action_2"]
```

### 主要コンポーネント

```
app/services/ai/
├── models.py              # データモデル定義
├── operator.py            # 動的ハブ（OperatorHub）
├── prompt_generator.py    # 動的プロンプト生成
├── executor.py            # アクション実行エンジン（動的対応）
├── orchestrator.py        # 統合レイヤー
├── logger.py              # ログ機能
├── exceptions.py          # 例外定義
└── spokes/               # 動的スポーク
    ├── spoke_interface.py # BaseSpoke抽象クラス
    ├── spoke_system.py    # 統合スポークシステム
    └── google_calendar/   # Google Calendarスポーク
        ├── actions.json   # アクション定義
        └── spoke.py      # スポーク実装
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
