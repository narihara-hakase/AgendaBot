import datetime
import pickle
import re
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class google_calendar:
    # カレンダーへのRW権限(スコープ)を変更する
    # 変更する際はtoken.pickleを削除してください。
    __SCOPES = ['https://www.googleapis.com/auth/calendar']

    # 変更する対象のカレンダー
    __CARENDAR_ID = 'digitallibraryforme@gmail.com'

    # 東京でのUTCとの誤差
    __ERR_UTC_TOKYO = 9

    # 時間の出力フォーマット
    __FORMAT_TIME = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self):#インスタンス変数管理
        pass

    def connect(self):
        ''' # token.pickleを初期作成する際は外すこと。
        creds = None
        # token.pickleファイルには、ユーザーのアクセストークンと更新トークンが格納されています。
        # 許可フローが最初に完了したときに自動的に作成されます。

        # token.pickleの読み込み
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # token.pickleの読み込み失敗時
        # 利用可能な（有効な）認証情報がない場合は、ユーザーにログインさせます。
        if not creds or not creds.valid:
            ## ここなんのしょりしてる？条件わかんね
            if creds and creds.expired and creds.refresh_token:
                # ブラウザのリフレッシュ
                creds.refresh(Request())

            # ブラウザで認証URLを開く
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()

            # 次回の実行のために資格情報を保存します
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        '''
        
        # token.pickleの読み込み'(token.pickleを作成する際はコメントアウトすること)
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

        # カレンダーAPIとの接続
        service = build('calendar', 'v3', credentials=creds)
        
        return service
    
    def add_calendar_event(self, summary, start_time, end_time):
        # APIとの接続
        service = self.connect()

        # カレンダ情報の格納
        body = {'summary': summary,
                'start': {  'dateTime': start_time,
                            'timeZone': 'Asia/Tokyo',
                         },
                'end':   {  'dateTime': end_time,
                            'timeZone': 'Asia/Tokyo',
                         },
                'attendees': '',
               }

        # カレンダへイベントの追加
        event = service.events().insert(
            calendarId=google_calendar.__CARENDAR_ID,
            body=body
        ).execute()
    
    def del_calendar_event(self, summary, start_time, end_time):
        # APIとの接続
        service = self.connect()

        # イベントIDの取得
        eventid = self.get_calendar_event(summary, start_time, end_time)
       
        # カレンダのイベントを削除
        service.events().delete(
            calendarId=google_calendar.__CARENDAR_ID,
            eventId=eventid
        ).execute()        
    
    def get_calendar_event(self, summary, start_time, end_time):
        # APIとの接続
        service = self.connect()

        eventid = 0
        page_token = None

        # カレンダーの取得
        while True:
            events = service.events().list(
                calendarId=google_calendar.__CARENDAR_ID,
                pageToken=page_token
            ).execute()
            
            # 日付データ文字(引数)を置換
            startTime = datetime.datetime.strptime(start_time,self.__FORMAT_TIME)
            endTime = datetime.datetime.strptime(end_time,self.__FORMAT_TIME)
            
            # イベントの検索
            for event in events['items']:
                start = event['start']
                end   = event['end']
                
                # 日付と卓名が一致したら、それを返却
                if event['summary'] == summary and datetime.datetime.strptime(start['dateTime'],self.__FORMAT_TIME) == startTime and datetime.datetime.strptime(end['dateTime'],self.__FORMAT_TIME) == endTime:
                    eventid = event['id']
                    break
            
            # 次イベントの取得
            page_token = events.get('nextPageToken')
        
            # 読むイベントがなくなったら終了
            if not page_token:
                break
        
        # idの返却
        return eventid
    
'''
メモ
        # カレンダー系(試験用)
        elif re.match('\$cadd1', com):
            calendar.add_calendar_event('test', '2019-05-11T21:00:00', '2019-05-11T23:00:00')
            send_ms = 'カレンダーを追加'
            await message.channel.send(send_ms)

        elif re.match('\$cadd2', com):
            calendar.add_calendar_event('test2', '2019-05-11T21:00:00', '2019-05-11T23:00:00')
            send_ms = 'カレンダーを追加'
            await message.channel.send(send_ms)

        elif re.match('\$cdel', com):
            calendar.del_calendar_event('test2', '2019-05-11T21:00:00+09:00', '2019-05-11T23:00:00+09:00')
            send_ms = 'カレンダーを削除'
            await message.channel.send(send_ms)
'''