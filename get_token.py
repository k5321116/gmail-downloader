from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle

# スコープの定義（Gmailの全機能を使うためのスコープ）
SCOPES = ['https://mail.google.com/']

def main():
    # credentials.jsonはGCPからダウンロードしたファイル
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # 取得したトークンを保存しておく（token.pickleに保存）
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

if __name__ == '__main__':
    main()