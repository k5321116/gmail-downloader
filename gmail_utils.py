import pickle
import base64
import os
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GmailClient:
    def __init__(self, token_path='token.pickle', debug=False):
        self.debug = debug
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        """認証を行い、Gmail APIサービスを構築する内部メソッド"""
        if not os.path.exists(self.token_path):
            raise FileNotFoundError(f"{self.token_path} が見つかりません。先に認証を完了させてください。")
        
        with open(self.token_path, 'rb') as token:
            creds = pickle.load(token)
        
        return build('gmail', 'v1', credentials=creds)

    def list_messages(self, max_results=5):
        """最新のメッセージIDリストを取得"""
        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        return [msg['id'] for msg in messages]
    
    def get_messages_summary(self, max_results=5):
        """メッセージの概要を取得し、pandasのDataFrameで返す"""
        msg_ids = self.list_messages(max_results=max_results)
        self.summary_data = []

        for mid in msg_ids:
            # メッセージ詳細を取得
            message = self.service.users().messages().get(userId='me', id=mid, format='full').execute()
            
            # ヘッダーから情報を抽出
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "（件名なし）")
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), "（日付不明）")
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "（差出人不明）")

            # 添付ファイルの有無と拡張子をチェック
            parts = message['payload'].get('parts', [])
            attachment = [p.get('filename') for p in parts if p.get('filename')]
            self.attachment_names = [os.path.splitext(f)[0].upper() for f in attachment]
            self.extensions = [os.path.splitext(f)[1].lower() for f in attachment]

            # 1件分のデータを辞書にまとめる
            self.summary_data.append({
                'ID': mid,
                '日付': date,
                '差出人': sender,
                '件名': subject,
                '添付ファイル数': len(attachment),
                'ファイル名': ", ".join(self.attachment_names),
                '形式': ", ".join(set(self.extensions)),
                'raw_data': message
            })

        # DataFrameに変換
        df = pd.DataFrame(self.summary_data)
        return df

    def download_attachments(self, message_id, save_dir='.'):
        """添付ファイルをダウンロードして保存"""
        msg_data = next((item for item in self.summary_data if item['ID'] == message_id), None)
        if not msg_data:
            print("データが見つかりません。先に get_messages_summary を実行してください。")
            return []
        parts = msg_data['raw_data']['payload'].get('parts', [])
        found_files = []

        # 保存先ディレクトリがなければ作成
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for part in parts:
            filename = part.get('filename')
            body = part.get('body', {})
            
            if filename and 'attachmentId' in body:
                print(f"  ... {filename} をダウンロード中 ...")
                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                sub_dir = ext.replace('.', '') if ext else 'others'
                target_dir = os.path.join(save_dir, sub_dir)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                print(f"  [保存] {filename} -> {sub_dir} フォルダ")
                '''
                file_path = os.path.join(target_dir, filename)
                if os.path.exists(file_path):
                    print(f"  [SKIP] {filename} は既に存在します")
                    found_files.append(f"{sub_dir}/{filename}")
                    continue
                attachment = self.service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=body['attachmentId']
                ).execute()

                file_data = base64.urlsafe_b64decode(attachment['data'])
                file_path = os.path.join(target_dir, filename)

                with open(file_path, 'wb') as f:
                    f.write(file_data)
                '''
                found_files.append(f"{sub_dir}/{filename}")
                
        if found_files:
            print(f"  [OK] 保存完了: {', '.join(found_files)}")
        else:
            print("  [-] 添付ファイルはありません。")
        
        return found_files