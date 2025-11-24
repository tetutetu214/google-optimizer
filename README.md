# Vertex AI Prompt Optimizer ツール
Vertex AI Prompt Optimizerを使用したプロンプト最適化ツール。
Streamlit UIでプロンプトを入力し、改善提案をリアルタイムで確認できます。

## 機能
- **プロンプト最適化**: Vertex AI Prompt Optimizer (Zero-shot) による自動最適化
- **改善提案の可視化**: 変更前後の比較と改善理由を表示
- **日本語翻訳**: 改善理由を Gemini 2.0 Flash で日本語に自動翻訳
- **ストリーミング表示**: リアルタイムで最適化結果を段階的に表示
- **ファイル対応**: テキストファイル (.txt, .md) のアップロードに対応
- **ダウンロード機能**: 最適化されたプロンプトをファイルとして保存可能

## ディレクトリ構成
```
prompt-optimizer-tool/
├── .gitignore
├── README.md
├── requirements.txt
├── .env.example          # 環境変数のサンプル (作成してください)
├── backend/
│   └── optimizer.py      # PromptOptimizer クラス
└── frontend/
    └── app.py            # Streamlit UI
```

## 前提条件
- Python 3.12 以上
- Google Cloud プロジェクト
- Vertex AI API の有効化
- 適切な IAM 権限:
  - `roles/aiplatform.user` (Vertex AI User)
  - `roles/aiplatform.serviceAgent` (Vertex AI Service Agent)

## セットアップ
### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd prompt-optimizer-tool
```

### 2. 仮想環境の作成と有効化
```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env` ファイルをプロジェクトルートに作成:
```bash
# .env
PROJECT_ID=your-project-id
LOCATION=us-central1
```

または、`.env.example` をコピーして編集:
```bash
cp .env.example .env
# .env を編集
```

### 5. Google Cloud 認証
```bash
gcloud auth application-default login
```

## 使い方
### ローカルアプリケーションの起動
```bash
streamlit run frontend/app.py
```


### 基本的な使い方
1. **サイドバーで設定**
   - Google Cloud Project ID を入力 (または .env から自動読み込み)
   - Location を入力 (デフォルト: us-central1)

2. **プロンプト入力**
   - 「直接入力」: テキストエリアに直接入力
   - 「ファイルアップロード」: .txt または .md ファイルをアップロード

3. **最適化実行**
   - 「最適化実行」ボタンをクリック

4. **結果の確認**
   - 最適化されたプロンプトを確認
   - 改善提案の詳細を展開して確認
   - 必要に応じてダウンロード

## 参考リンク

| 種別 | リンク |
|------|--------|
| 公式ドキュメント | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-optimizer |
| Zero-shot Optimizer | https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/zero-shot-optimizer |
| GitHub サンプル | https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/prompts/prompt_optimizer/get_started_with_vertex_ai_prompt_optimizer.ipynb |
| 公式ブログ | https://cloud.google.com/blog/products/ai-machine-learning/announcing-vertex-ai-prompt-optimizer |
| 論文 (arXiv) | https://arxiv.org/pdf/2406.15708 |