import re

class agenda_control:
    SINGLE_AGENDA_NUM = 8  # 種別/開始/終了/システム/シナリオ名/ツール/募集人数/概要
    CANPANE_AGENDA_NUM = 6 # 種別/システム/シナリオ名/ツール/募集人数/概要
    ALWAYS_AGENDA_NUM = 6  # 種別/システム/シナリオ名/ツール/募集人数/概要

    DATABASE_NUM = SINGLE_AGENDA_NUM + 1# + 21 # 種別/システム/シナリオ名/ツール/募集人数/概要/GM名/PC1/PC1のキャラシ/PC2…/PC10のキャラシ

    DATABASE_COLUMN_START_TIME = 1
    DATABASE_COLUMN_END_TIME = 2
    DATABASE_COLUMN_CAPACITY = 7
    DATABASE_COLUMN_NOTES = 8
    
    AGENDA_STANDARD = '以下のように記述してください。\n\n@everyone\n｜　種　別　｜単発/キャンペーン/常時\n｜開始日時　｜2019/05/15 19:00 (半角で入力してください、キャンペーン/常時の場合削除)\n｜終了日時　｜2019/05/15 23:00 (半角で入力してください、キャンペーン/常時の場合削除)\n｜システム　｜SW2.5\n｜シナリオ名｜シナリオ名\n｜ツール　　｜どどんとふ\n｜募集人数　｜2\n｜　概　要　｜\n卓の説明、その他。'
    
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
        if (arrDataNum != self.SINGLE_AGENDA_NUM) and (arrDataNum != self.CANPANE_AGENDA_NUM) and (arrDataNum != self.ALWAYS_AGENDA_NUM):
            return 0

        # キャンペーン投稿文の場合、開始/終了時間がないため、配列を増やす
        if arrDataNum == self.CANPANE_AGENDA_NUM:
            arrMes.insert(self.DATABASE_COLUMN_START_TIME,0) # 開始の挿入
            arrMes.insert(self.DATABASE_COLUMN_END_TIME,0) # 終了の挿入

        # 常時卓投稿文の場合、開始/終了時間がないため、配列を増やす
        if arrDataNum == self.ALWAYS_AGENDA_NUM:
            arrMes.insert(self.DATABASE_COLUMN_START_TIME,0) # 開始の挿入
            arrMes.insert(self.DATABASE_COLUMN_END_TIME,0) # 終了の挿入

        # データベース1行分のリストにデータをコピー
        # everyoneから始まる行が0、種別が1、種別の内容が2…と格納されている
        for i in range(self.DATABASE_NUM):
            if i == self.DATABASE_COLUMN_START_TIME or i == self.DATABASE_COLUMN_END_TIME:
                # 時間のフォーマット変更
                database_row[i - 1] = arrMes[ i * 2 ]
            elif i == self.DATABASE_COLUMN_CAPACITY:
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
        result_time = str(mes).split(' ')
        result_ymd = result_time[0].split('/')
        result_hms = result_time[1].split(':')
        strTime = result_ymd[0] + '-' + result_ymd[1] + '-' + result_ymd[2] + 'T' + result_hms[0] + ':' + result_hms[1] + ':' + result_hms[2]
        return strTime
    
    def name_create(self, gm_name, system):
        mes = gm_name + '卓' + system
        return mes
