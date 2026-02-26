import os
import pickle
import base64
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build

class GmailAuthentication:
    def __init__(self, token_path='token.pickle'):
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):

        if not os.path.exists(self.token_path):
            raise FileNotFoundError(f"{self.token_path} が見つかりません。先に認証を完了させてください。")
        
        with open(self.token_path, 'rb') as token:
            creds = pickle.load(token)
        
        return build('gmail', 'v1', credentials=creds)

class GetMessageDetail:
    def __init__(self, auth_service):
        self.service = auth_service

    def validate_dates(self, date_from, date_to):
        try:
            # 1. 形式チェック (YYYY/MM/DD)
            start = datetime.strptime(date_from, "%Y/%m/%d")
            end = datetime.strptime(date_to, "%Y/%m/%d")
            
            # 2. 前後関係チェック
            if start > end:
                print("開始日が終了日より後の日付になっています。")
                return False
                
            # 3. 未来チェック
            if start > datetime.now() or end > datetime.now():
                print("未来の日付は指定できません。")
                return False

            print('OK')    
            return True
            
        except ValueError:
            print("日付は YYYY/MM/DD の形式で入力してください。")
            return False
    
    def get_message_id(self, DateFrom, DateTo):

        query = ""
        if DateFrom != None and DateFrom != "":
            query += "After:" + DateFrom + " "
        if DateTo != None and DateTo != "":
            query += "Before:" + DateTo + " "
        
        query += "has:attachment"

        results = self.service.users().messages().list(userId="me", maxResults=100, q=query).execute()
        messages = results.get("messages", [])

        message_id = []
        for msg in messages:
            message_id.append(msg['id'])

        return message_id
    
    def get_messagelist(self, DateFrom, DateTo):

        messagelist = []
        d_message = {}
        msg_id = self.get_message_id(DateFrom, DateTo)
        
        for i in range(len(msg_id)):
            d_message = {
                'ID': msg_id[i],
                'Attachments': []}
            
            message = self.service.users().messages().get(userId='me', id=msg_id[i], format='full').execute()

            #日付、差出人、件名を取得
            for haeder in message["payload"]["headers"]:
                if ('name', 'Date') in haeder.items():
                    d_message['Date'] = haeder['value']
                elif ('name', 'From') in haeder.items():
                    d_message['From'] = haeder['value']
                elif ('name', 'Subject') in haeder.items():
                    d_message['Subject'] = haeder['value']
            
            #添付ファイルの名前とIDを取得
            parts = message['payload'].get('parts', [])
            for part in parts:
                filename = part.get('filename')
                if filename:
                    body = part.get('body', {})
                    attachment_data = {
                        'filename': filename,
                        'attachmentId': body.get('attachmentId')
                    }
                    d_message['Attachments'].append(attachment_data)

            messagelist.append(d_message)
        return messagelist
    
    def get_messagelist_as_df(self, DateFrom, DateTo):
        messagelist = self.get_messagelist(DateFrom, DateTo)
        df = pd.DataFrame(messagelist)
        return df 

class AttachmentsDownloader:

    def __init__(self, auth_service, base_dir='downloads'):
        self.service = auth_service
        self.base_dir = base_dir

    def download_attachments(self, message_id, attachment_id, filename):
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)       
        attachment = self.service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()

        file_data = base64.urlsafe_b64decode(attachment['data'])
        file_path = os.path.join(self.base_dir, filename)

        with open(file_path, 'wb') as f:
            f.write(file_data)

    def download_all_from_df(self, df):
        if df.empty:
            print("ダウンロードするファイルがありません。")
            return
        
        for index, row in df.iterrows():
            message_id = row['ID']
            attachment_list = row['Attachments']
            for attach in attachment_list:
                attachment_id = attach['attachmentId']
                filename = attach['filename']
                self.download_attachments(message_id, attachment_id, filename)
            
class GmailClient:
    def __init__(self):
        self.auth = GmailAuthentication()
        self.auth_service = self.auth.service
        self.detail = GetMessageDetail(self.auth_service)
        self.downloader = AttachmentsDownloader(self.auth_service)
        self.current_df = pd.DataFrame()

    def search_attachments(self, date_from, date_to):
        """GUIの検索ボタンから呼ばれる関数"""
        # 日付のバリデーション（既存のロジックを活用）
        if not self.detail.validate_dates(date_from, date_to):
            return None
        
        # 検索実行
        self.current_df = self.detail.get_messagelist_as_df(date_from, date_to)
        return self.current_df

    def download_all(self):
        """GUIのダウンロードボタンから呼ばれる関数"""
        if self.current_df.empty:
            return False
        
        # 保持している検索結果(current_df)を使ってダウンロード
        self.downloader.download_all_from_df(self.current_df)
        return True
