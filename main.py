from gmail_utils import GmailClient


def main():
    client = GmailClient()
    # 1. メッセージ一覧取得
    msg_ids = client.list_messages(max_results=3)
    if not msg_ids:
        print("メッセージが見つかりませんでした。")
        return
        
    for mid in msg_ids:
        print(f"\nID: {mid}")
        # 2. 件名表示
        client.get_message_detail(mid)
        # 3. 添付ファイル保存
        client.download_attachments(mid, save_dir='downloads')

if __name__ == '__main__':
    main()