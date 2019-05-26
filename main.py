### 汎用モジュールのインポート ###
import discord
import re
import random
import datetime
import asyncio
import time

import requests
import io
from PIL import Image
import argparse #コマンドラインコントロール
import json     #json処理


### 自作モジュールのインポート ###
#自作パッケージ内のすべてのモジュールをインポートする。import sandboxbot　を使用したい場合は__init__.pyに各ディレクトリを指定せよ
#グローバルの名前空間にロードするので名称の重複に注意せよ
from sandboxbot import *

# 起動オプション
parser = argparse.ArgumentParser(description='sandboxbot本体 helpは-h') #パーサ作るよ
parser.add_argument('--debug', action='store_false',help='指定なしでture(本番環境) 指定アリでfalse(テスト環境)')  # --debug指定なしでture(本番環境) 指定アリでfalse(テスト環境)
args = parser.parse_args()

#オプションに応じてjsonからbotパラメーターを引っ張る。
def get_bot_options(path):
    file = open(path, 'r', encoding="utf8")
    param_json = json.load(file)

    index = 1 if args.debug else 0
    bot_status = param_json['bot_status'][index] #辞書型で格納される
    file.close()

    return bot_status

json_path = './bot_options.json'
bot_options = get_bot_options(json_path)

### 定数宣言 ###
# BOTのトークン
TOKEN = bot_options["token"]

# DiscordのテキストChID
CH_GENERAL = bot_options["ch_general"]
CH_AGENDA  = bot_options["ch_agenda" ]
CH_BOT     = bot_options["ch_bot"    ]
CH_ADMIN   = bot_options["ch_admin"  ]

### インスタンスの生成 ###
sw = swbot.Swstat()
Alog = accesslog.accesslog()
DiceBot = dicebot.dicebot()
calendar = google_calendar.google_calendar()
client = discord.Client()
agenda_control = agenda_control.agenda_control()

### 直接実行モジュールの指定 ###
if __name__ == '__main__':

    ### インスタンスの生成 ###
    # discord.py
    client = discord.Client()
    # 自作：グーグルカレンダーの制御
    calendar = google_calendar.google_calendar()
    # 自作：Agendaの制御
    agenda_control = agenda_control.agenda_control()
    # 自作：ダイスを振る機能
    DiceBot = dicebot.dicebot()
    # 自作：SW2.0/2.5　キャラクター作成支援機能
    sw = SW.Swstat()
    # 自作：アクセスログ解析機能
    Alog = accesslog.accesslog()

    ### 起動時のイベントハンドラ ###
    @client.event
    async def on_ready():

        # botの情報をコンソール出力
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        print(f'運命はダイスに託された！\n{bot_options["code"]}起動！')
        asyncio.ensure_future(throw_message_date_changed())

    ### 時刻管理 ###
    async def throw_message_date_changed():
        while True:

            # デバッグプリント
            print('TIMER RUNNING BY INTERVAL A MINUTE')

            ### 現在時刻が00:00のとき
            if time.strftime('%H:%M',time.localtime())=='00:00':

                #! リアクション数が取得できるようになったならば、以下の処理は卓一覧出力にすること !#

                # 卓数の取得( = ピンどめの数の取得)
                pin_ms = await discord.abc.Messageable.pins(client.get_channel(CH_AGENDA))
                # 送信メッセージの生成
                send_ms ='現在の募集中セッションは'+str(len(pin_ms))+'件だよ。参加してね。'
                # メッセージの送信
                await client.get_channel(CH_GENERAL).send(send_ms)

            #60sスリープ asyncioでのスリープは他の処理を妨げないスレッド処理
            await asyncio.sleep(60)

    ### reaction付与時のイベントハンドラ ###
    @client.event
    async def on_reaction_add(reaction, user):

        ### リアクションがAgendaに付与されたとき
        if reaction.message.channel.id == CH_AGENDA:

            #投稿文の取得
            mes = reaction.message.content

            # 投稿文から開始日時の情報を取得
            #! Agendaのデータを格納する構造体が確定したら記述を変更すること !#
            send_ms = agenda_control.date_separate(mes)

            # リアクションをつけた人へのdmを作成
            dm = await user.create_dm()

            # dmの送信
            await dm.send(send_ms + "のセッションに参加申し込みしました")

    ### reaction消去時のイベントハンドラ ###
    @client.event
    async def on_reaction_remove(reaction, user):

        ### リアクションがAgendaから消去されたとき
        if reaction.message.channel.id == CH_AGENDA:

            # 投稿文の取得
            mes = reaction.message.content

            # 投稿文から開始日時の情報を取得
            #! Agendaのデータを格納する構造体が確定したら記述を変更すること !#
            send_ms = agenda_control.date_separate(mes)

            # リアクションをつけた人へのdmを作成
            dm = await user.create_dm()

            # dmの送信
            await dm.send(send_ms + "のセッションの参加を取り消しました")

    ### メッセージが編集されたときのイベントハンドラ ###
    @client.event
    async def on_message_edit(before, after):

        ### pin留めがAgendaにておこなわれたとき
        if before.pinned != after.pinned and client.get_channel(CH_AGENDA) == after.channel:

            #! リアクション数が取得できるようになったならば、以下の処理は卓一覧出力にすること !#

            # 卓数の取得( = ピンどめの数の取得)
            pin_ms = await discord.abc.Messageable.pins(client.get_channel(CH_AGENDA))
            # 送信メッセージの生成
            send_ms ='現在の募集中セッションは'+str(len(pin_ms))+'件だよ。参加してね。'
            # メッセージの送信
            await client.get_channel(CH_GENERAL).send(send_ms)

        ### Agendaが編集されたとき
        else:

            # 編集前のAgendaの投稿文を検査
            if re.match('\@everyone', before.content):

                # Agendaの形式チェック
                send_ms = agenda_control.on_message_agenda_write(before.content)

                # 形式が正しい投稿の場合、編集元の予定をカレンダーから削除
                # 投稿時、編集時にチェックしてるのでエラーの送信は不要
                if send_ms != bool(False):

                    # 投稿者のDiscord名を取得（鯖でのニックネーム)
                    author = str(before.author.nick)

                    # 編集前の卓の予定をカレンダーから消去するための情報を生成
                    ret = agenda_control.calendar_event_create(agenda_control.CALENDAR_DEL, send_ms, author)

                    # カレンダー消去用の情報の生成に成功したとき
                    if ret != bool(False):
                        # 編集前の卓の予定をカレンダーから削除
                        agenda_control.calendar_refresh(agenda_control.CALENDAR_DEL,ret[0], ret[1], ret[2])

            # 編集後のAgendaの投稿文を検査
            if re.match('\@everyone', after.content):
                ret1 = bool(True)
                ret2 = bool(True)

                # Agendaの形式チェック
                send_ms = agenda_control.on_message_agenda_write(after.content)

                # 形式が正しい投稿の場合、編集元の予定をカレンダーへ追加
                if send_ms != bool(False):

                    # 投稿者のDiscord名を取得（鯖でのニックネーム)
                    author = str(after.author.nick)

                    # 編集後の卓の予定をカレンダーへ追加するための情報を生成
                    ret1 = agenda_control.calendar_event_create(agenda_control.CALENDAR_ADD, send_ms, author)

                    # 情報の作成に成功したとき
                    if ret1 != bool(False):

                        # 編集後の卓の情報をカレンダーへ追加
                        ret2 = agenda_control.calendar_refresh(agenda_control.CALENDAR_ADD,ret1[0], ret1[1], ret1[2])

                # 1.編集結果の形式が不正
                # 2.編集後の卓の予定に誤りがある
                # 3.カレンダー操作が何らかの理由で失敗した 1~3のいづれかのとき
                if send_ms == bool(False) or ret1 == bool(False) or ret2 == bool(False):

                    # 投稿者にその旨をDMで通知

                    # dmの生成
                    dm = await before.author.create_dm()

                    # dmで送信するエラーメッセージの作成
                    send_ms = agenda_control.error_message_create(agenda_control.AGENDA_EDIT_ERROR, after.content)

                    # dmの送信
                    await dm.send(send_ms)

    ### メッセージが削除された時のイベントハンドラ ###
    @client.event
    async def on_message_delete(message):

        # 投稿文本文を取得
        com = message.content

        # @everyoneからはじまるメッセージが削除されたとき
        if re.match('\@everyone', com):

            # Agendaの形式チェック
            send_ms = agenda_control.on_message_agenda_write(com)

            # Agendaが削除された場合はカレンダーからイベントを削除
            if send_ms != bool(False):

                # 投稿者のDiscord名を取得（鯖でのニックネーム)
                author = str(message.author.nick)

                # 卓の予定をカレンダーから削除するための情報を生成
                ret = agenda_control.calendar_event_create(agenda_control.CALENDAR_DEL, send_ms, author)

                # 卓の予定をカレンダーから削除
                agenda_control.calendar_refresh(agenda_control.CALENDAR_DEL, ret[0], ret[1], ret[2])

    ### メッセージ投稿時のイベントハンドラ ###
    @client.event
    async def on_message(message):

        # 投稿文本文を取得
        com = message.content

        ### ヘルプ
        # 各機能毎にヘルプつくって、そちらに誘導するよう変更すべきでは?
        # 今後各機能増やしていくときヘルプ作るのだるくなりそうなので (20190511所感)
        if re.match('\$help', com):
            ### ヘルプメッセージ ###
            HELP_MSG =['``` ### ダイスを振る ###',
                       '$[整数]d[整数] ダイスコードに従いダイスをふる',
                       '$s[整数]d[整数] ダイスを降った後整列させ、期待値を表示する。',
                       '``` ',
                       '``` ### SWを遊ぶ ###',
                       '$sw_ab アビス強化表を振ります',
                       '$sw_ca[無しor整数] 整数の数だけ経歴表を振ります',
                       '$sw_re 冒険に出た理由表を振ります',
                       '$sw_[整数] 種族の初期値を3回生成する',
                       '  人間：0,エルフ：1,ドワーフ：2,タビット：3',
                       '  ルーンフォーク：4,ナイトメア：5,リカント：6,',
                       '  リルドラケン：7,グラスランナー：8,メリア：9,',
                       '  ティエンス：10,レプラカーン：11',
                       '``` ',
                       '``` ### ログを解析する ###',
                       '$logs VCアクセスログおよびサーバータイムを表示する。',
                       '``` ']

            mes = ''

            for ele_help in HELP_MSG:
                # ヘルプの配列を順番にmesへ格納
                mes = mes + ele_help + '\n'

            # ヘルプメッセージを入力されたCHへ送信
            await message.channel.send(mes)

        ### 自己紹介カード自動生成機能(作りかけで放置)
        elif re.match('\$avatar', com):

            # com送信者のアバター画像のurlを取得
            avatar_url = message.author.avatar_url
            # ヴェノーさん作の自己紹介カードの画像URL
            card_url = 'https://cdn.discordapp.com/attachments/425609740152995840/571361111325147185/712651fbc55cd866.png'

            # 各画像をimageオブジェクトに保存
            user_img = Image.open(io.BytesIO(requests.get(avatar_url).content))
            card_image = Image.open(io.BytesIO(requests.get(card_url).content))

            # アバター画像を自己紹介カードの枠内にペースト
            card_image.paste(user_img, (6,10))

            # 自己紹介カードの画像を保存
            card_image.save('test.png', quality=95)

            # 保存した画像をdiscordへ送信
            await message.channel.send('Hello', file=discord.File('test.png'))

            # 画像を削除
            #os.remove('test.png') # できない！なじぇ！！

        ### ダイス機能
        #ダイス(振るだけ)
        elif re.match('\$\d+d\d+', com):
            # 投稿メッセージの意味を解釈
            dice_cmd_list = re.findall('\d+',com)
            send_ms = DiceBot.dice_roll_str(int(dice_cmd_list[0]),int(dice_cmd_list[1]))
            await message.channel.send(send_ms)

        # ダイス(ソートして振る)
        elif re.match('\$[sS]\d+d\d+', com):
            # 投稿メッセージの意味を解釈
            dice_cmd_list = re.findall('\d+',com)
            send_ms = DiceBot.dice_roll_sort_str(int(dice_cmd_list[0]),int(dice_cmd_list[1]))
            await message.channel.send(send_ms)

        ### SW-BOT系
        # ステータス
        elif re.match('\$sw_\d+', com):
            send_ms = sw.roll_stat_str(com)
            await message.channel.send(send_ms)
        # アビスカース
        elif re.match('\$sw_ab', com):
            send_ms = sw.roll_abyss_str()
            await message.channel.send(send_ms)
        # 生まれ
        elif re.match('\$sw_ca\d*', com):
            send_ms = sw.roll_Career_str(com)
            await message.channel.send(send_ms)
        # 来歴
        elif re.match('\$sw_re', com):
            send_ms = sw.roll_reason_str()
            await message.channel.send(send_ms)

        ### Alog系
        elif re.match('\$logs', com):
            send_ms = Alog.debug_print_str()
            await message.channel.send(send_ms)

        ### Agenda管理系
        elif re.match('\@everyone', com):

            # Agendaにメッセージが投稿された時
            if message.channel.id == CH_AGENDA:

                # Agendaの形式チェック
                send_ms = agenda_control.on_message_agenda_write(com)

                # Agendaへの投稿が不正形式だった場合、その旨を投稿者にDMし、投稿文を削除
                if send_ms == bool(False):

                    # dmを生成
                    dm = await message.author.create_dm()

                    # エラーメッセージの生成
                    send_ms = agenda_control.error_message_create(agenda_control.AGENDA_ADD_ERROR, com)

                    # dmを送信
                    await dm.send(send_ms)

                    # 投稿文を削除
                    await message.delete()

                # Agendaへの投稿が正常に行われたとき、カレンダーにイベントを追加し、メッセージをピンどめする
                else:
                    ret1 = bool(True)
                    ret2 = bool(True)

                    # 投稿者のDiscord名を取得（鯖でのニックネーム)
                    author = str(message.author.nick)

                    ret1 = agenda_control.calendar_event_create(agenda_control.CALENDAR_ADD, send_ms, author)

                    # 情報の作成に成功したとき
                    if ret1 != bool(False):

                        # 卓の予定をカレンダーに追加
                        ret2 = agenda_control.calendar_refresh(agenda_control.CALENDAR_ADD,ret1[0], ret1[1], ret1[2])

                    # 1.投稿された卓の予定に誤りがある
                    # 2.カレンダー操作が何らかの理由で失敗した 1~2のいづれかのとき
                    # Agendaへの投稿が不正形式だった場合、その旨を投稿者にDMし、投稿文を削除
                    if ret1 == bool(False) or ret2 == bool(False):

                        # dmを生成
                        dm = await message.author.create_dm()

                        # エラーメッセージの生成
                        send_ms = agenda_control.error_message_create(agenda_control.AGENDA_DATE_ERROR, com)

                        # dmを送信
                        await dm.send(send_ms)

                        # 投稿文を削除
                        await message.delete()

                    # 卓の予定をカレンダーに追加できたとき
                    else:
                        # メッセージをピンどめする
                        #! botに権限がないとエラーになります !#
                        await message.pin()

        # 開催予定卓一覧の取得
        if re.match('\$list', com):

            arrSessionList = [] # セッション一覧格納用
            send_ms = ''        # メッセージ格納用

            # pin留めされたメッセージを取得
            pin_ms_list = await discord.abc.Messageable.pins(client.get_channel(CH_AGENDA))

            # pin留めされたメッセージの分析
            for pin_mes_line in pin_ms_list:

                # pin留めされたメッセージ本文を取得
                mes_content = pin_mes_line.content

                # メッセージの投稿者のニックネームを取得
                author = str(pin_mes_line.author.nick)

                # pin留めされたメッセージにつけられたリアクション数を取得
                pl_num = sum(reaction.count for riaction in pin_mes_line.reactions)
                print(pl_num)

                # メッセージのフォーマットを解析して配列化
                database_row = agenda_control.on_message_agenda_write(mes_content)

                # メッセージのフォーマットの開始日と今日の日付を比較
                ret = agenda_control.session_list_create(database_row, author, pl_num)

                # 今日よりもメッセージ内の開始日の日付が古い場合
                if ret == bool(False):

                    # メッセージのピンどめを解除
                    await pin_mes_line.unpin()

                # 今日よりもメッセージ内の開始日の日付が新しい場合
                else:
                    arrSessionList.append(ret)

            # 開始日でリストをソート
            arrSessionList.sort(key=lambda x: x[2]) # 開始日は3列目

            # 開催予定卓一覧を出力
            for mes_line in arrSessionList:

                # メッセージの生成
                send_ms = send_ms + str(mes_line[0]) + ' ' + str(mes_line[1]) + ' ' + str(mes_line[2]) + '/' + str(mes_line[3]) + ' ' + str(mes_line[4]) + '\n'

            # メッセージを送信
            await message.channel.send(send_ms)

        #'''
        # 試験用(サーバ実装時はコメントアウト、絶対に残さないこと！)
        # メッセージの全削除
        #if message.content == '/cleanup':
        #    await message.channel.purge()
        #'''

    client.run(TOKEN)
