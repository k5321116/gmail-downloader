from gmail_utils import GmailClient
import pandas as pd

def main():
    client = GmailClient()
    print("--- 期間指定検索を開始 ---")
    df = client.get_messages_summary(
        after_date='2026/02/10', 
        before_date='2026/02/16'
    )
    
    if not df.empty:
        print(df[['日付', '件名', '形式']])
    else:
        print("指定された期間に添付ファイルのあるメールはありませんでした。")  
    
if __name__ == '__main__':
    main()