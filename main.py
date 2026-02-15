from gmail_utils import GmailClient
import pandas as pd

def main():
    client = GmailClient()
    
    # 1. まずは一覧を取得（デバッグ用に件数を絞る）
    print("--- 検索中 ---")
    df = client.get_messages_summary(max_results=5)
    
    if df.empty:
        print("該当するメールが見 tilかりませんでした。")
        return

    # pandasの表示設定（コンソールで見やすく）
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("\n--- 取得したメール一覧 ---")
    print(df[['ID', '日付', '件名', '添付ファイル数', 'ファイル名', '形式']])

    # 2. デバッグ：リストの「一番上」のメールを自動で選択してダウンロード処理に回す
    # (GUIではここをマウスでポチッと選ぶイメージ)
    target_id = df.iloc[0]['ID']
    target_subject = df.iloc[0]['件名']
    
    print(f"\n--- ダウンロード・デバッグ開始 ---")
    print(f"対象メール: {target_subject} (ID: {target_id})")
    
    # 3. download_attachments を実行
    # (実処理をコメントアウトしていても、関数内の print で挙動が確認できる)
    downloaded_files = client.download_attachments(target_id, save_dir='debug_downloads')
    
    print(f"\n[結果報告] {len(downloaded_files)} 件の処理候補がありました。")

if __name__ == '__main__':
    main()