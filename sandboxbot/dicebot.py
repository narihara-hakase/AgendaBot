import re
import random

class dicebot:
    # ダイスの振り方
    __THROW = 0
    __SORT  = 1

    def __init__(self):#インスタンス変数管理
    	pass
    
    # Diceを振る機能
    def dice_message(self, mode, num, sides):
        dice = []
        for s in range(0, num):
            dice.append(random.randint(1, sides))

        if mode == dicebot.__SORT:
            dice.sort()

        dice_num = map(str, dice)
        dice_num = ','.join(dice_num)
        dice_total = str(sum(dice))

        if mode == dicebot.__SORT:
            dice_mean = str(((sides + 1)) / 2 * num)
            send_ms = 'ころころ...' + '[' + dice_num + '] 合計:'+ dice_total + ' 期待値:' + dice_mean
        else:
            send_ms = 'ころころ...' + '[' + dice_num + '] 合計:'+ dice_total
        return send_ms

    # 定数返却機能
    def sort_mode(self):
        return dicebot.__SORT
    
    def throw_mode(self):
        return dicebot.__THROW
