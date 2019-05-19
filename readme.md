# Narihara bot feat X
すべてはSandBoxのために。
## Release版　起動方法
```
main.py
```
## Debug版　起動方法
```
main.py --debug
```
botのoptionは bot_options.json に書いてあるから見てね。

## 現在の機能
### ダイスを振る

|コマンド|機能|
|:-|:-|
|$[整数]d[整数] |ダイスコードに従いダイスをふる|
|$s[整数]d[整数] |ダイスを降った後整列させ、期待値を表示する。

 ### SWを遊ぶ
 |コマンド|機能|
 |:-|:-|
  |$sw_ab| アビス強化表を振ります'|
  |$sw_ca[無しor整数]| 整数の数だけ経歴表を振ります|
  |$sw_re| 冒険に出た理由表を振ります|
  |$sw_[整数]|種族の初期値を3回生成する|
```
  人間：0,エルフ：1,ドワーフ：2,タビット：3
  ルーンフォーク：4,ナイトメア：5,リカント：6
  リルドラケン：7,グラスランナー：8,メリア：9
  ティエンス：10,レプラカーン：11
  ```
  ### ログを解析する
  |コマンド|機能|
  |:-|:-|
  |$logs| VCアクセスログおよびサーバータイムを表示する|