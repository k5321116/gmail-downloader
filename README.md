## セットアップと使用方法

### 事前準備 (Google Cloud Console)
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成。
2. **Gmail API** を有効化。
3. **OAuth 同意画面**を設定（外部/テストユーザーで自分のメアドを追加）。
4. **OAuth クライアント ID** (デスクトップアプリ) を作成し `credentials.json` を取得。

### 1. 準備
`credentials.json` をプロジェクトのルートディレクトリに配置します。

### 2. 認証（トークンの生成）
以下のコマンドを実行してブラウザでログインし、`token.pickle` を生成します。
```bash
python get_token.py
```

### 3. メイン処理の実行
認証完了後、以下のコマンドでメールの取得と添付ファイルの保存が行えます。
```bash
python main.py
```
