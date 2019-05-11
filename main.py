import discord
import re
import random
import datetime

### 自作サブルーチンファイル ###
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

### ヘルプメッセージ ###
HELP_MSG =['``` ',
           '$[整数]d[整数] ダイスコードに従いダイスをふる',
           '$s[整数]d[整数] ダイスを降った後整列させ、期待値を表示する。',
           '$logs VCアクセスログおよびサーバータイムを表示する。',
           '$sw_ab アビス強化表を振ります',
           '$sw_ca[無しor整数] 整数の数だけ経歴表を振ります',
           '$sw_re 冒険に出た理由表を振ります',
           '$sw_[整数] 種族の初期値を3回生成する',
           '  人間：0,エルフ：1,ドワーフ：2,タビット：3',
           '  ルーンフォーク：4,ナイトメア：5,リカント：6,',
           '  リルドラケン：7,グラスランナー：8,メリア：9,',
           '  ティエンス：10,レプラカーン：11',
           '``` ']

if __name__ == '__main__':
            
    # クラスの呼び出し
    sw = SW.Swstat()
    Alog = accesslog.accesslog()
    DiceBot = dicebot.dicebot()
    calendar = google_calendar.google_calendar()
    client = discord.Client()        
    agenda_control = agenda_control.agenda_control()
    
    # 起動時のイベントハンドラ
    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        
    ### Auto動作 ###
    # pin留め時の動作
    @client.event
    async def on_message_edit(before, after):
        if before.pinned != after.pinned and client.get_channel(CH_AGENDA) == after.channel:
            pin_ms = await discord.abc.Messageable.pins(client.get_channel(CH_AGENDA))
            print(pin_ms)
            send_ms ='現在の募集中セッションは'+str(len(pin_ms))+'件だよ。参加してね。'
            await client.get_channel(CH_GENERAL).send(send_ms)
    

    # reaction付与時の動作
    @client.event
    async def on_reaction_add(reaction, user):
        if reaction.message.channel.id == CH_AGENDA:
            mes = reaction.message.content
            send_ms = agenda_control.date_separate(mes)
            dm = await user.create_dm()
            await dm.send(send_ms + "のセッションに参加申し込みしました")

    # reaction消去時
    @client.event
    async def on_reaction_remove(reaction, user):
        if reaction.message.channel.id == CH_AGENDA:
            mes = reaction.message.content
            send_ms = agenda_control.date_separate(mes)
            dm = await user.create_dm()
            await dm.send(send_ms + "のセッションの参加を取り消しました")


    ### Botへのコマンド送信時の動作 ###
    @client.event
    async def on_message(message):
        com = message.content
        
        ### ヘルプ
        # 各機能毎にヘルプつくって、そちらに誘導するよう変更すべきでは?
        # 今後各機能増やしていくときヘルプ作るのだるくなりそうなので (20190511所感)
        if re.match('\$help', com):
            await message.channel.send(HELP_MSG)

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

        # Alog系
        elif re.match('\$logs', com):
            send_ms = Alog.debug_print_str()
            await message.channel.send(send_ms)
            
        # Agenda管理系
        elif re.match('\@everyone', com):
            time = '0'
            send_ms = agenda_control.on_message_agenda_write(com)
            if send_ms == 0:
                await message.channel.send('error')
            else:
                startTime = agenda_control.time_format_change(send_ms[1])
                endTime = agenda_control.time_format_change(send_ms[2])
                title = agenda_control.name_create('test', send_ms[4])
                calendar.add_calendar_event(str(title), str(startTime), str(endTime))
                await message.channel.send('カレンダーを追加')

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

    client.run(TOKEN)