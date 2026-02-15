import pickle
import base64
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GmailClient:
    def __init__(self, token_path='token.pickle'):
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

    def get_message_detail(self, message_id):
        """メッセージの情報を取得し、件名を表示"""
        message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        
        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "（件名なし）")
        
        print(f"件名: {subject}")
        return message

    def download_attachments(self, message_id, save_dir='.'):
        """添付ファイルをダウンロードして保存"""
        message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        parts = message['payload'].get('parts', [])
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