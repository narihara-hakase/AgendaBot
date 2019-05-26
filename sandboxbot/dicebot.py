import re
import random

class dicebot:

    def __init__(self):#インスタンス変数管理
        self.dice_ary = []
        self.dice_num  = ""
        self.dice_total = ""
        self.dice_mean = ""

    # Diceを振る機能
    def dice_roll(self,num, sides):
        for s in range(0, num):
            self.dice_ary.append(random.randint(1, sides))
        self.dice_num = ','.join(map(str, self.dice_ary))
        self.dice_total = str(sum(self.dice_ary))
        self.dice_mean = str(((sides + 1)) / 2 * num)

    def dice_roll_str(self, num, sides):
        self.dice_roll(num, sides)
        send_ms = 'ころころ...' + '[' + self.dice_num + '] 合計:'+ self.dice_total
        return send_ms

    def dice_roll_sort_str(self, num, sides):
        self.dice_roll(num, sides)
        self.dice_ary.sort()
        send_ms = 'ころころ...' + '[' + self.dice_num + '] 合計:'+ self.dice_total + ' 期待値:' + self.dice_mean
        return send_ms
