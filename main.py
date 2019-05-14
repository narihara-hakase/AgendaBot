### 汎用モジュールのインポート ###
import discord
import re
import random
import datetime

### 自作モジュールのインポート ###
import swbot as SW
import accesslog
import dicebot
import google_calendar
import agenda_control

### 定数宣言 ###
# BOTのトークン
TOKEN = 'NTMyNTA3MDQzMDA1ODU3Nzky.XNGDNQ.G21CFz3yX_KR6Uvzj_6-PNA2k6Y'

# DiscordのテキストChID
CH_GENERAL = 576636764349923328
CH_AGENDA  = 576636894302175282
CH_BOT     = 576636917735489536
CH_ADMIN   = 577033215055888385

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

async def throw_message_date_changed():
    while True:
        if time.strftime('%H:%M:%S',time.localtime())=='00:00:00':
            pin_ms = await discord.abc.Messageable.pins(client.get_channel(CH_AGENDA))
            send_ms ='現在の募集中セッションは'+str(len(pin_ms))+'件だよ。参加してね。'
            await client.get_channel(CH_GENERAL).send(send_ms)
            sleep(5)

if __name__ == '__main__':
            
    ### インスタンスの呼び出し ###
    sw = SW.Swstat()
    Alog = accesslog.accesslog()
    DiceBot = dicebot.dicebot()
    calendar = google_calendar.google_calendar()
    client = discord.Client()        
    agenda_control = agenda_control.agenda_control()
    
    ### 起動時のイベントハンドラ ###
    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        
    ### reaction付与時のイベントハンドラ ###
    @client.event
    async def on_reaction_add(reaction, user):
        ### リアクションがアジェンダCHに付与されたとき
        if reaction.message.channel.id == CH_AGENDA:
            mes = reaction.message.content
            send_ms = agenda_control.date_separate(mes)
            dm = await user.create_dm()
            await dm.send(send_ms + "のセッションに参加申し込みしました")

    ### reaction消去時のイベントハンドラ ###
    @client.event
    async def on_reaction_remove(reaction, user):
        ### リアクションがアジェンダCHから消去されたとき
        if reaction.message.channel.id == CH_AGENDA:
            mes = reaction.message.content
            send_ms = agenda_control.date_separate(mes)
            dm = await user.create_dm()
            await dm.send(send_ms + "のセッションの参加を取り消しました")

    ### メッセージが編集されたときのイベントハンドラ ###
    @client.event
    async def on_message_edit(before, after):
        ### pin留めがアジェンダCHにておこなわれたとき
        if before.pinned != after.pinned and client.get_channel(CH_AGENDA) == after.channel:
            pin_ms = await discord.abc.Messageable.pins(client.get_channel(CH_AGENDA))
            send_ms ='現在の募集中セッションは'+str(len(pin_ms))+'件だよ。参加してね。'
            await client.get_channel(CH_GENERAL).send(send_ms)
        
        ### Agendaが編集されたとき
        else:
            com1 = before.content
            if re.match('\@everyone', com1):
                # Agendaの形式チェック
                send_ms = agenda_control.on_message_agenda_write(com1)
                # 形式が正しい投稿の場合、編集元の予定をカレンダーから削除
                # 投稿時、編集時にチェックしてるのでエラーの送信は不要
                if send_ms != 0:
                    author = str(after.author.nick)
                    ret = agenda_control.calendar_event_create(agenda_control.CALENDAR_DEL, send_ms, author)
                    ret = agenda_control.calendar_refresh(agenda_control.CALENDAR_DEL,ret[0], ret[1], ret[2])
                    
            com2 = after.content
            if re.match('\@everyone', com2):
                ret1 = 1
                ret2 = 1
                # 形式が正しい投稿の場合、編集結果の予定をカレンダーに追加
                send_ms = agenda_control.on_message_agenda_write(com2)
                if send_ms != 0:
                    author = str(after.author.nick)
                    ret1 = agenda_control.calendar_event_create(agenda_control.CALENDAR_ADD, send_ms, author)
                    if ret1 != 0:
                        ret2 = agenda_control.calendar_refresh(agenda_control.CALENDAR_ADD,ret1[0], ret1[1], ret1[2])
                # どこかでエラーが出た時
                if send_ms == 0 or ret1 == 0 or ret2 == 0:
                    # 投稿者への通知(編集エラー)
                    dm = await before.author.create_dm()
                    send_ms = agenda_control.error_message_create(agenda_control.AGENDA_EDIT_ERROR, com2)
                    await dm.send(send_ms)
            
    ### メッセージが削除された時のイベントハンドラ ###
    @client.event
    async def on_message_delete(message):
        com = message.content
        # @everyoneからはじまるメッセージが削除されたとき
        if re.match('\@everyone', com):
            # Agendaの形式で投稿されている文章かのチェック
            send_ms = agenda_control.on_message_agenda_write(com)
            # Agendaが削除された場合はカレンダーからイベントを削除
            if send_ms != 0:
                #author = str(message.author.name)
                author = str(message.author.nick)
                ret = agenda_control.calendar_event_create(agenda_control.CALENDAR_DEL, send_ms, author)
                agenda_control.calendar_refresh(agenda_control.CALENDAR_DEL, ret[0], ret[1], ret[2])

    ### メッセージ投稿時のイベントハンドラ ###
    @client.event
    async def on_message(message):
        com = message.content
        
        ### ヘルプ
        # 各機能毎にヘルプつくって、そちらに誘導するよう変更すべきでは?
        # 今後各機能増やしていくときヘルプ作るのだるくなりそうなので (20190511所感)
        if re.match('\$help', com):
            mes = ''
            for ele_help in HELP_MSG:
                mes = mes + ele_help + '\n'
            await message.channel.send(mes)

        ### ダイス系
        #ダイス(振るだけ)
        elif re.match('\$\d+d\d+', com):
            dice_cmd_list = re.findall('\d+',com)
            mode = DiceBot.throw_mode()
            send_ms = DiceBot.dice_message(mode, int(dice_cmd_list[0]),int(dice_cmd_list[1]))
            await message.channel.send(send_ms)

        # ダイス(ソートして振る)
        elif re.match('\$[sS]\d+d\d+', com):
            dice_cmd_list = re.findall('\d+',com)
            mode = DiceBot.sort_mode()
            send_ms = DiceBot.dice_message(mode, int(dice_cmd_list[0]),int(dice_cmd_list[1]))
            await message.channel.send(send_ms)

        ### SW-BOT系
        elif re.match('\$sw_\d+', com):
            send_ms = sw.roll_stat_str(com)
            await message.channel.send(send_ms)

        elif re.match('\$sw_ab', com):
            send_ms = sw.roll_abyss_str()
            await message.channel.send(send_ms)

        elif re.match('\$sw_ca\d*', com):
            send_ms = sw.roll_Career_str(com)
            await message.channel.send(send_ms)

        elif re.match('\$sw_re', com):
            send_ms = sw.roll_reason_str()
            await message.channel.send(send_ms)

        ### Alog系
        elif re.match('\$logs', com):
            send_ms = Alog.debug_print_str()
            await message.channel.send(send_ms)
            
        ### Agenda管理系
        elif re.match('\@everyone', com):
            if message.channel.id == CH_AGENDA:
                send_ms = agenda_control.on_message_agenda_write(com)
                # Agendaへの投稿が不正形式だった場合、その旨を投稿者にDMし投稿を削除
                if send_ms == 0:
                    dm = await message.author.create_dm()
                    send_ms = agenda_control.error_message_create(agenda_control.AGENDA_ADD_ERROR, com)
                    await dm.send(send_ms)
                    await message.delete()

                # Agendaへの投稿が正常に行われたとき、カレンダーにイベントを追加し、メッセージをピンどめする
                else:
                    ret1 = 1
                    ret2 = 1
                    author = str(message.author.nick)
                    
                    ret1 = agenda_control.calendar_event_create(agenda_control.CALENDAR_ADD, send_ms, author)
                    # 日付のエラーがないか確認
                    if ret1 != 0:
                        # カレンダーへの追加
                        ret2 = agenda_control.calendar_refresh(agenda_control.CALENDAR_ADD,ret1[0], ret1[1], ret1[2])
                    if ret1 == 0 or ret2 == 0:
                        # 投稿者への通知(日付エラー)
                        dm = await message.author.create_dm()
                        send_ms = agenda_control.error_message_create(agenda_control.AGENDA_DATE_ERROR, com)
                        await dm.send(send_ms)
                        await message.delete()
                    else:
                        # ピンどめ Botに権限がないとエラーになります。
                        await message.pin()

        #'''
        # 試験用(サーバ実装時はコメントアウト、絶対に残さないこと！)
        # メッセージの全削除
        if message.content == '/cleanup':
            await message.channel.purge()
        #'''
                
    client.run(TOKEN)