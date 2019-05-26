import re
<<<<<<< HEAD:agenda_control.py
import google_calendar
import datetime
=======
from .google_calendar import *
>>>>>>> narihara-dep:sandboxbot/agenda_control.py

calendar = google_calendar()

class agenda_control:

    SINGLE_AGENDA_NUM = 8  # 種別/開始/終了/システム/シナリオ名/ツール/募集人数/概要
    CANPANE_AGENDA_NUM = 6 # 種別/システム/シナリオ名/ツール/募集人数/概要
    ALWAYS_AGENDA_NUM = 6  # 種別/システム/シナリオ名/ツール/募集人数/概要

    DATABASE_NUM = SINGLE_AGENDA_NUM + 1# + 21 # 種別/システム/シナリオ名/ツール/募集人数/概要/GM名/PC1/PC1のキャラシ/PC2…/PC10のキャラシ

    DATABASE_COLUMN_START_TIME = 1
    DATABASE_COLUMN_END_TIME = 2
    DATABASE_COLUMN_CAPACITY = 7
    DATABASE_COLUMN_NOTES = 8
<<<<<<< HEAD:agenda_control.py
    
    AGENDA_STANDARD = '```\n@everyone\n｜　種　別　｜単発/キャンペーン/常時\n｜開始日時　｜2019/05/15 19:00:00 (半角で入力してください)\n｜終了日時　｜2019/05/15 23:00:00 (半角で入力してください)\n｜システム　｜SW2.5\n｜シナリオ名｜シナリオ名\n｜ツール　　｜どどんとふ\n｜募集人数　｜2\n｜　概　要　｜\n卓の説明、その他。\n```'
    
=======

    AGENDA_STANDARD = '```\n@everyone\n｜　種　別　｜単発/キャンペーン/常時\n｜開始日時　｜2019/05/15 19:00 (半角で入力してください)\n｜終了日時　｜2019/05/15 23:00 (半角で入力してください)\n｜システム　｜SW2.5\n｜シナリオ名｜シナリオ名\n｜ツール　　｜どどんとふ\n｜募集人数　｜2\n｜　概　要　｜\n卓の説明、その他。\n```'

>>>>>>> narihara-dep:sandboxbot/agenda_control.py
    AGENDA_ERR_MSG = ['以下の卓の投稿に失敗しました。\n','以下の投稿の編集結果のフォーマットが異なります、修正してください。','以下の投稿の卓は日付情報がフォーマットと異なります、修正してください。' ]
    AGENDA_ADD_ERROR = 0
    AGENDA_EDIT_ERROR = 1
    AGENDA_DATE_ERROR = 2

    CALENDAR_ADD = 0
    CALENDAR_DEL = 1

    def __init__(self):#インスタンス変数管理
    	pass

    # 日付を抽出し返信用メッセージを生成する機能
    def check_date_str(self, mes):
        str_list = re.findall('[０-９\d]+月[０-９\d]+日|[０-９\d]+[\/][０-９\d]+',mes)

        if str_list == []:
            send_ms = '開催日時不明'
        else:
            send_ms = str_list[0]

        return send_ms


    # Agenda形式チェック
    def on_message_agenda_write(self, mes):
        
        # データ保存用のリストを初期化
        database_row = [0] * self.DATABASE_NUM

        # 投稿文を|で分割
        arrMes = mes.split('｜')

        # データ分割数からAgendaの要素数を取得
        arrDataNum = (len(arrMes) - 1)/2

        # 投稿文とのフォーマットが異なる場合はエラー
        # 将来的にはキャンペーンや常時卓用の機能追加したい
        # 今は単発卓のみ
        #if (arrDataNum != self.SINGLE_AGENDA_NUM) and (arrDataNum != self.CANPANE_AGENDA_NUM) and (arrDataNum != self.ALWAYS_AGENDA_NUM):
        
        # 要素数から突発卓かを判定
        # 違う場合はFalseを返す
        if (arrDataNum != self.SINGLE_AGENDA_NUM):
            return bool(False)

        '''
        # キャンペーン投稿文の場合、開始/終了時間がないため、配列を増やす
        if arrDataNum == self.CANPANE_AGENDA_NUM:
            arrMes.insert(self.DATABASE_COLUMN_START_TIME,0) # 開始の挿入
            arrMes.insert(self.DATABASE_COLUMN_END_TIME,0) # 終了の挿入

        # 常時卓投稿文の場合、開始/終了時間がないため、配列を増やす
        if arrDataNum == self.ALWAYS_AGENDA_NUM:
            arrMes.insert(self.DATABASE_COLUMN_START_TIME,0) # 開始の挿入
            arrMes.insert(self.DATABASE_COLUMN_END_TIME,0) # 終了の挿入
        '''
        
        # 単発卓投稿文の場合、開始/終了時間がNULLの場合異常を返す
        if arrDataNum == self.SINGLE_AGENDA_NUM:
            if arrMes[self.DATABASE_COLUMN_START_TIME] == 0 or arrMes[self.DATABASE_COLUMN_END_TIME] == 0:
<<<<<<< HEAD:agenda_control.py
                return bool(False)
       
        # Agendaの各要素を格納
=======
                return 0

        # データベース1行分のリストにデータをコピー
>>>>>>> narihara-dep:sandboxbot/agenda_control.py
        # everyoneから始まる行が0、種別が1、種別の内容が2…と格納されている
        for i in range(self.DATABASE_NUM):
            
            # 募集人数を格納
            if i == self.DATABASE_COLUMN_CAPACITY:
                
                # 募集人数を数値に変更
                database_row[i - 1] = int(arrMes[ i * 2 ])
            
            # 概要を格納
            elif i == self.DATABASE_COLUMN_NOTES:
                
                # 概要は改行を含め全てそのまま格納
                database_row[i - 1] = arrMes[ i * 2 ]
                
            # @everyone行は無視
            elif i == 0:
                pass
            
            # それ以外の行は改行を消して格納
            else:
                # 改行文字を削除
                database_row[i - 1] = arrMes[ i * 2 ].replace('\n', '')
        
        # 格納したデータを戻す
        return database_row
<<<<<<< HEAD:agenda_control.py
    
    # カレンダー用の日付形式変更
=======

>>>>>>> narihara-dep:sandboxbot/agenda_control.py
    def time_format_change(self, mes):

        # 文字列操作に失敗したらexcept文へ飛ぶ
        try :
            
            # YMD Hmsと分割
            result_time = str(mes).split(' ')
            
            # Y M D を分割
            result_ymd = result_time[0].split('/')
            
            # H m sを分割
            result_hms = result_time[1].split(':')
            
            # 時間の結合
            strTime = result_ymd[0] + '-' + result_ymd[1] + '-' + result_ymd[2] + 'T' + result_hms[0] + ':' + result_hms[1] + ':' + result_hms[2]
            
            # 改行を削除（何故かこれをやらないとうごかない）
            retTime  = strTime.split('\n')
            
            # 変換結果を返す
            return retTime[0]
        
        # エラー時異常を返す
        except :
<<<<<<< HEAD:agenda_control.py
            return bool(False)
    
    # カレンダーの予定の名前を生成
=======
            return 0

>>>>>>> narihara-dep:sandboxbot/agenda_control.py
    def name_create(self, gm_name, system):
        
        # author卓system名 を生成
        mes = gm_name + '卓' + system
        
        # 生成名を返す
        return mes
<<<<<<< HEAD:agenda_control.py
    
    # 形式が異なるAgenda投稿者へのエラーメッセージ生成
=======

>>>>>>> narihara-dep:sandboxbot/agenda_control.py
    def error_message_create(self,mode,com):
        
        # エラーメッセージの生成
        send_ms = self.AGENDA_ERR_MSG[mode] + '```' + com + '```' + '\n以下のフォーマットで投稿してください。\n' + self.AGENDA_STANDARD
        return send_ms

    # カレンダーAPIを叩くための情報の生成
    def calendar_event_create(self, mode, send_ms, author):
        
        # システム名がNULLでない
        if send_ms[3] != '':
            # カレンダー名を生成
            title = self.name_create(author, send_ms[3])
        
        # システム名がNULL
        else:
<<<<<<< HEAD:agenda_control.py
            title = bool(False)
        
        # 開始/終了時刻の生成
        # 生成に失敗したらexcept文へ飛ぶ
=======
            title = 0

>>>>>>> narihara-dep:sandboxbot/agenda_control.py
        try:
            
            # カレンダーへ予定追加時
            if mode == self.CALENDAR_ADD:

                # 時刻の生成
                startTime = self.time_format_change(send_ms[1])
                endTime = self.time_format_change(send_ms[2])
            
            # カレンダーの予定削除時
            else:

                # 時刻の生成(削除時は時差の情報が必要)
                startTime = self.time_format_change(send_ms[1]) + '+09:00'
                endTime = self.time_format_change(send_ms[2]) + '+09:00'
            
            # APIを叩くための情報が不足しているとき
            if title == bool(False) or startTime == bool(False) or endTime == bool(False):
                
                # 異常も格納
                ret = bool(False)
            
            # APIを叩くための情報が揃っている時
            else:
                
                # 情報を戻り値に格納
                ret = [title, startTime, endTime]
                
            return ret
        
        # 時刻の生成でエラー発生時、異常を戻す
        except:
<<<<<<< HEAD:agenda_control.py
            return bool(False)
        
    # カレンダーへの操作処理を呼び出す
=======
            return 0

>>>>>>> narihara-dep:sandboxbot/agenda_control.py
    def calendar_refresh(self, mode, title, startTime, endTime):
        
        # カレンダーへの操作でエラーが発生した場合except文へ飛ぶ
        try:
            
            # カレンダーにイベントを追加
            if mode == self.CALENDAR_ADD:
                calendar.add_calendar_event(title, startTime, endTime)
            
            # カレンダーからイベントを削除
            else:
                calendar.del_calendar_event(title, startTime, endTime)
                
            # 正常を返す
            return bool(True)
        
        # カレンダーAPIを叩いた結果エラーが発生したとき
        # 異常を返す
        except:
            return bool(False)

    # 卓一覧リストを一行生成する
    def session_list_create(self, send_ms, author, pl_num):
        
        # author卓system　文字列を生成
        system = self.name_create(author, send_ms[3])
        
        # シナリオ名を取得
        title = send_ms[4]
        
        # 開始/終了日時を時間として取得
        startTime = datetime.datetime.strptime(self.time_for_discord(send_ms[1]), '%Y-%m-%d %H:%M:%S')
        endTime = datetime.datetime.strptime(self.time_for_discord(send_ms[2]), '%Y-%m-%d %H:%M:%S')
        
        # 参加人数 / 募集人数 文字列を生成
        player_num = str(pl_num) + ' / ' +str(send_ms[6])
        
        # 現在時刻を取得
        now = datetime.datetime.now()
        
        # 現在時刻より卓の開始日が過去の場合
        if startTime < now:
            return bool(False)
        
        # 現在時刻より卓の開始日が先の場合
        else:
            
            # 時刻を文字列に変換
            startTime = self.time_for_discord(send_ms[1])
            endTime = self.time_for_discord(send_ms[2])
            
            # 卓情報をリストに格納
            arrRet = [system, title, startTime, endTime, player_num]
            
            # 卓情報を戻す
            return arrRet
    
    # 卓一覧リスト用の時刻生成処理
    def time_for_discord(self, mes):
        # YMD Hmsと分割
        result_time = str(mes).split(' ')
        
        # Y M D と分割
        result_ymd = result_time[0].split('/')
        
        # H m s と分割
        result_hms = result_time[1].split(':')
        
        # 現在日時を文字列を結合して取得
        strTime = result_ymd[0] + '-' + result_ymd[1] + '-' + result_ymd[2] + ' ' + result_hms[0] + ':' + result_hms[1] + ':' + result_hms[2]
        
        # 改行を削除(念の為)
        retTime  = strTime.split('\n')
        
        # 時刻を返却
        return retTime[0]

