import os, glob

#form hoge import * をディレクトリ内に適用する
__all__ = [
    os.path.split(os.path.splitext(file)[0])[1]
    for file in glob.glob(os.path.join(os.path.dirname(__file__), '[a-zA-Z0-9]*.py'))
]


'''
個別指定ならこんな感じで書く＝importが通る
from .accesslog import *
from .google_calendar import *
from .agenda_control import *
'''
