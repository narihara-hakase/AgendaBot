import re
from .google_calendar import *

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

    AGENDA_STANDARD = '```\n@everyone\n｜　種　別　｜単発/キャンペーン/常時\n｜開始日時　｜2019/05/15 19:00 (半角で入力してください)\n｜終了日時　｜2019/05/15 23:00 (半角で入力してください)\n｜システム　｜SW2.5\n｜シナリオ名｜シナリオ名\n｜ツール　　｜どどんとふ\n｜募集人数　｜2\n｜　概　要　｜\n卓の説明、その他。\n```'

    AGENDA_ERR_MSG = ['以下の卓の投稿に失敗しました。\n','以下の投稿の編集結果のフォーマットが異なります、修正してください。','以下の投稿の卓は日付情報がフォーマットと異なります、修正してください。' ]
    AGENDA_ADD_ERROR = 0
    AGENDA_EDIT_ERROR = 1
    AGENDA_DATE_ERROR = 2

    CALENDAR_ADD = 0
    CALENDAR_DEL = 1

    def __init__(self):#インスタンス変数管理
    	pass

    # 日付を抽出する機能
    def date_separate(self, mes):
        str_list = re.findall('[０-９\d]+月[０-９\d]+日|[０-９\d]+[\/][０-９\d]+',mes)

        if str_list == []:
            send_ms = '開催日時不明'
        else:
            send_ms = str_list[0]

        return send_ms


    def on_message_agenda_write(self, mes):
        arrMes = mes.split('｜')

        database_row = [0] * self.DATABASE_NUM
        arrDataNum = (len(arrMes) - 1)/2

        # 投稿文とのフォーマットが異なる場合はエラー
        # 将来的にはキャンペーンや常時卓用の機能をはやすけど、今は単発卓のみ
        #if (arrDataNum != self.SINGLE_AGENDA_NUM) and (arrDataNum != self.CANPANE_AGENDA_NUM) and (arrDataNum != self.ALWAYS_AGENDA_NUM):
        if (arrDataNum != self.SINGLE_AGENDA_NUM):
            return 0

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
        # 単発卓投稿文の場合、開始/終了時間がNULLの場合エラー
        if arrDataNum == self.SINGLE_AGENDA_NUM:
            if arrMes[self.DATABASE_COLUMN_START_TIME] == 0 or arrMes[self.DATABASE_COLUMN_END_TIME] == 0:
                return 0

        # データベース1行分のリストにデータをコピー
        # everyoneから始まる行が0、種別が1、種別の内容が2…と格納されている
        for i in range(self.DATABASE_NUM):
            if i == self.DATABASE_COLUMN_CAPACITY:
                # 募集人数を数値に変更
                database_row[i - 1] = int(arrMes[ i * 2 ])
            elif i == self.DATABASE_COLUMN_NOTES:
                # 概要は改行を含め全てそのまま格納
                database_row[i - 1] = arrMes[ i * 2 ]
            elif i == 0:
                # @everyoneは何もしない
                pass
            else:
                # 改行文字を削除
                database_row[i - 1] = arrMes[ i * 2 ].replace('\n', '')
        return database_row

    def time_format_change(self, mes):
        # mesは配列の1か2を渡すこと！
        # 時差をたすこと()
        try :
            result_time = str(mes).split(' ')
            result_ymd = result_time[0].split('/')
            result_hms = result_time[1].split(':')
            strTime = result_ymd[0] + '-' + result_ymd[1] + '-' + result_ymd[2] + 'T' + result_hms[0] + ':' + result_hms[1] + ':' + result_hms[2]
            retTime  = strTime.split('\n')
            return retTime[0]
        except :
            return 0

    def name_create(self, gm_name, system):
        mes = gm_name + '卓' + system
        return mes

    def error_message_create(self,mode,com):
        send_ms = self.AGENDA_ERR_MSG[mode] + '```' + com + '```' + '\n以下のフォーマットで投稿してください。\n' + self.AGENDA_STANDARD
        return send_ms

    def calendar_event_create(self, mode, send_ms, author):
        if send_ms[3] != '':
            title = self.name_create(author, send_ms[3])
        else:
            title = 0

        try:
            # 日付の検査
            if mode == self.CALENDAR_ADD:
                # カレンダーへのイベント追加
                startTime = self.time_format_change(send_ms[1])
                endTime = self.time_format_change(send_ms[2])
            else:
                # カレンダーへのイベント削除
                startTime = self.time_format_change(send_ms[1]) + '+09:00'
                endTime = self.time_format_change(send_ms[2]) + '+09:00'
            if title != 0 and startTime != 0 and endTime != 0:
                ret = [title, startTime, endTime]
            else:
                ret = 0
            return ret
        except:
            return 0

    def calendar_refresh(self, mode, title, startTime, endTime):
        try:
            if mode == self.CALENDAR_ADD:
                calendar.add_calendar_event(title, startTime, endTime)
            else:
                calendar.del_calendar_event(title, startTime, endTime)
            return 1
        except:
            return 0
