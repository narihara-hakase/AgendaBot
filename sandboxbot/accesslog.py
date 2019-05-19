import discord
import re
import datetime

class accesslog:
        def __init__(self):#インスタンス変数管理
            self.today = datetime.date.today().day
            self.unique_member_list = []

        def reset_val(self):
            self.today = datetime.date.today().day
            self.unique_member_list = []

        def add_member_list(self,member_tmp):
            #print(member_tmp.voice.voice_channel)
            if(member_tmp.voice.voice_channel != None  and  self.unique_member_list.count(member_tmp.name) == 0):
                self.unique_member_list.append(member_tmp.name)

        def is_update_time(self):
            now = datetime.date.today().day
            if (now != self.today):
                return True

        def print_logs_str(self):
            header = "本日のアクセス人数は[" + str( len(self.unique_member_list) ) + "]人でした。\r\n"
            member_table = "\r\n".join(self.unique_member_list)
            send_ms = header + member_table

            self.reset_val()
            return send_ms

        def debug_print_str(self):
            header = "本日現在までのアクセス人数は[" + str( len(self.unique_member_list) ) + "]人でした。\r\n"
            Stime = "サーバータイム:" +  str(datetime.datetime.today()) + "\r\n"
            member_table = "\r\n".join(self.unique_member_list)
            send_ms = Stime + header + member_table
            return send_ms