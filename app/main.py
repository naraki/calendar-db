import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import mysql.connector
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

load_dotenv()

# 必要なスコープ（読み取り専用または読み書き）を設定
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  # 読み取り専用の場合

def get_calendar_service():
    creds = None
    # トークンファイルが存在すれば再利用
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # トークンがない、または期限切れの場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.jsonを使用して認証フローを実行
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 次回のためにトークンを保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Calendar APIサービスを構築
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_mysql_connection():
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
    }
    print(db_config)
    # 接続再試行用
    for _ in range(30):
        try:
            conn = mysql.connector.connect(**db_config)
            return conn
        except mysql.connector.Error:
            time.sleep(1)
    print("データベースへの接続に失敗しました")
    return None

def fetch_calendar_events(service, calendar_id='primary'):
    # 現在時刻から1ヶ月先までの予定を取得する例
    now = datetime.utcnow().isoformat() + 'Z' # UTCフォーマット
    
    print('Fetching upcoming events...')
    events_result = service.events().list(
        calendarId=calendar_id, 
        timeMin=now,
        maxResults=10, 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return events