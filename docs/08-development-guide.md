# 開発ガイド

## 概要

この開発ガイドは、LangGraph Slide Generatorシステムの開発、テスト、デプロイメントに関する指示とベストプラクティスを提供します。このドキュメントは、開発環境のセットアップから本番環境へのデプロイまで、開発プロセス全体をカバーしています。

詳細なコード例や実装方法については、各項目ごとに詳細なドキュメントを参照してください。このガイドは主な概念と方針を示すことを目的としています。

## 目次

1. [開発環境セットアップ](#開発環境セットアップ)
2. [プロジェクト構造](#プロジェクト構造)
3. [コーディング規約](#コーディング規約)
4. [LangGraph開発](#langgraph開発)
5. [テスト](#テスト)
6. [パフォーマンス最適化](./08.1-performance-guide.md)
7. [エラー処理と例外管理](./08.2-error-handling.md)
8. [監視とロギング](./08.3-monitoring.md)
9. [セキュリティ考慮事項](./08.4-security.md)
10. [デプロイメント](./08.5-deployment.md)
11. [トラブルシューティング](./08.6-troubleshooting.md)

## 開発環境セットアップ

### 前提条件

- Python 3.9以上
- Node.js 18以上（Webインターフェイス用）
- Docker および Docker Compose（コンテナ化開発用）
- Git

### 初期セットアップ

1. リポジトリのクローン:

```bash
git clone https://github.com/organization/langgraph-slide-generator.git
cd langgraph-slide-generator
```

2. 仮想環境の作成とパッケージのインストール:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用パッケージ
```

3. 環境変数の設定:

```bash
cp .env.example .env
# エディタで.envファイルを開き、設定を編集
```

4. 開発サーバーの起動:

```bash
python -m src.main
```

### Docker環境

```bash
# Docker Composeを使用してすべてのサービスを起動
docker-compose up -d

# 特定のサービスのみを起動
docker-compose up -d api worker

# ログの確認
docker-compose logs -f api

# コンテナ内でのコマンド実行
docker-compose exec api bash
```

## プロジェクト構造

```
langgraph-slide-generator/
├── .github/                # GitHub Actions設定
├── docs/                   # ドキュメント
├── src/                    # ソースコード
│   ├── api/                # APIエンドポイント
│   ├── core/               # コア機能
│   │   ├── graph/          # LangGraphワークフロー定義
│   │   ├── image/          # 画像処理
│   │   ├── llm/            # LLM統合
│   │   └── html/           # HTML生成
│   ├── models/             # データモデル
│   ├── utils/              # ユーティリティ
│   └── web/                # Webインターフェイス
├── tests/                  # テスト
│   ├── unit/               # ユニットテスト
│   ├── integration/        # 統合テスト
│   └── data/               # テストデータ
├── scripts/                # ユーティリティスクリプト
├── templates/              # HTMLテンプレート
└── config/                 # 設定ファイル
```

## コーディング規約

### Python コーディングスタイル

- [PEP 8](https://www.python.org/dev/peps/pep-0008/)に準拠
- 型ヒントを使用（mypy互換）
- ドキュメンテーション文字列はGoogle形式
- 行の最大長は88文字（black準拠）

自動フォーマットとリンティングツール:

```bash
# コード整形
black src tests

# インポート整序
isort src tests

# リンティング
flake8 src tests

# 型チェック
mypy src
```

### 命名規則

- **クラス**: UpperCamelCase (`ImageProcessor`, `SlideGenerator`)
- **関数/メソッド**: snake_case (`process_image`, `generate_html`)
- **変数**: snake_case (`image_data`, `html_output`)
- **定数**: UPPER_CASE (`MAX_RETRY_COUNT`, `DEFAULT_TEMPLATE`)
- **プライベートメンバー**: 先頭にアンダースコア (`_internal_process`)

## LangGraph開発

### 状態定義

LangGraphワークフローの状態は、Pydanticモデルを使用して定義します：

- 明確な型ヒントを使用
- デフォルト値を適切に設定
- 状態遷移を追跡するためのステータスフィールドを含める
- 進捗状況を追跡するためのフィールドを含める

### グラフ定義

ワークフローグラフは以下の原則に従って定義します：

- 各ノードを明確に分離された機能単位として設計
- エラー処理のための条件付きエッジを含める
- 状態の変更を明示的に行い、副作用を最小限に抑える
- 各ノードの前後条件を明確に文書化

### ノード実装

各ノードは以下のパターンに従って実装します：

- 入力として現在の状態を受け取る
- 状態を直接変更せず、変更点を辞書として返す
- エラー処理を適切に行い、エラー状態を適切に設定
- 進捗状況を更新する

## テスト

### ユニットテスト

- 各コンポーネントを個別にテスト
- モックを使用して外部依存関係を分離
- 境界条件とエッジケースをカバー
- テストケースを明確に文書化

### 統合テスト

- コンポーネント間の連携をテスト
- エンドツーエンドのワークフローをテスト
- 実際のデータに近いテストデータを使用
- リアルな障害シナリオをシミュレート

### 実行方法

```bash
# すべてのテストを実行
pytest

# 特定のテストを実行
pytest tests/unit/test_image_processor.py

# 特定のテストケースを実行
pytest tests/unit/test_image_processor.py::TestImageProcessor::test_extract_text

# カバレッジレポートを生成
pytest --cov=src --cov-report=html
```

## 詳細ガイド

より詳細な実装ガイドラインについては、以下の文書を参照してください：

- [パフォーマンス最適化ガイド](./08.1-performance-guide.md)
- [エラー処理と例外管理](./08.2-error-handling.md)
- [監視とロギング](./08.3-monitoring.md)
- [セキュリティ考慮事項](./08.4-security.md)
- [デプロイメントガイド](./08.5-deployment.md)
- [トラブルシューティング](./08.6-troubleshooting.md)
