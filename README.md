# Lattice Circuit Simulator

これは，格子の各辺に抵抗が，頂点とGNDの間にコンデンサが配置された大規模なRC回路網（格子回路）をシミュレーションするスクリプト群です．
回路シミュレーションにはLTspiceを利用しており，シミュレーションのためのネットリストを生成・変更・LTspiceサブプロセスによるシミュレーション実行・ログファイルのパースなどの機能を提供します．
目的は材料の触覚センサ利用のためのシミュレーションですので，7x7のグリッド状の電極が想定され，電極間のグリッド数（あるいは端の電極から回路の端までのグリッド数）を与えることで全体の格子回路を生成します．
7x7の電極の内，中央は電圧源に接続され，その他48個の電極が観測点です．
詳しくは以降を参照してください．

# Demo
注）デモはconfig.ymlが実行環境に合わせて適切に設定されていることを前提とします．config.yml自体の説明はconfig.yml内のコメントを参照してください．

レポジトリをクローンして移動
```
$ git clone https://github.com/BSL-Kyutech/LatticeCircuit.git
$ cd LatticeCircuit
```

電極間グリッド数を3とした時の電極ノード番号を確認
 ```
 $ python suggest_setup.py 3
 ```

電極間グリッド数を3とした時のシミュレーション用ネットリストを生成
 ```
 $ python generate_base_netlist.py 3 > base.net
 ```

LTspiceのサブプロセスを立ち上げ，シミュレーションを実行（接触するx位置，y位置，力を0～1で表現した時，それぞれ0.1, 0.2, 0.3と設定）
```
$ python simulate.py -s --X=0.1 --Y=0.2 --F=0.3
```

# Features
- 回路シミュレーションにはLTspiceを利用します
- LTspiceで作図できない回路規模をシミュレーションするため，ネットリスト（.netファイル）をスクリプトで生成します
- ベースとなるネットリストのパラメータ値を書き換えることで，接触に伴う電気的特性の変化を表現します
- 接触による圧抵抗効果・圧電効果は，接触位置を中心とした等分散二次元ガウス分布を接触力で重み付けして表現します
- シミュレーション結果は，各電極における電圧値と，与えた接触位置・力となります．

# Requirement

- Numpy
- PyYAML

# Usage

## `suggest_setup`

```
usage: suggest_setup.py [-h] M
```

- 引数
  1. `M`:電極間のグリッドの数．
- オプション引数
  1. `-h`: ヘルプ表示
- 戻り値（標準出力）
  1. 電極位置に相当するノード番号
  1. 全体の格子サイズ．総ノード数
  1. 入出力のノード番号（電極位置のノード番号を入出力に分けたもの）

## `generate_base_netlist`

```
usage: generate_base_netlist.py [-h] [--R R] [--C C] [--V V] [--F F] [--D D]
                                [-s] [-p]
                                M
```

- 引数
  1. `M`:電極間のグリッドの数．
- オプション引数
  1. `-h`: ヘルプ表示
  1. `--R`: 抵抗値の指定 [kOhm]．指定しない場合のデフォルトは10kOhm
  1. `--C`: 静電容量の指定 [nF]．指定しない場合のデフォルトは1nF
  1. `--V`: 入力電圧（振幅）の指定 [V]．指定しない場合のデフォルトは1V
  1. `--F`: 入力電圧（周波数）の指定 [Hz]．指定しない場合のデフォルトはFalse．その場合，スタート時にV[V]になる2D周期のPULSE電圧が印加される
  1. `--D`: シミュレーション時間の指定 [msec]．指定しない場合のデフォルトは100msec
  1. `-s`: 入力電圧にSINE電圧を選択．--Fに値が渡されたときに有効化される
  1. `-p`: 入力電圧にPULSE電圧を選択．--Fに値が渡されたときに有効化される
- 戻り値（標準出力）
  1. ネットリスト（ファイル保存はDemoに示したようにリダイレクトを使用すること）

### 備考
 - エラーは標準エラー出力に出力される．
 - コンデンサでGNDに接続されるため，現状，入力電圧に変化がないと電流が流れない．他の設定も考えられるようにするべきか．


## `simulate.py`
```
usage: simulate.py [-h] [-g] [--Dp DP] [--Df DF] [-s] [--X X] [--Y Y] [--F F]
```

- 引数なし
- オプション引数
  1. `-h`: ヘルプ表示
  1. `-g`: x位置，y位置，力をそれぞれ0.1～0.9の範囲でグリッド状にシミュレーションするためのフラグ
  1. `--Dp`: 位置に関して何分割するかの指定．`-g` 指定時のみ有効．指定しない場合のデフォルトは3
  1. `--Df`: 力のに関して何分割するかの指定．`-g` 指定時のみ有効．指定しない場合のデフォルトは3
  1. `-s`: x位置，y位置，力をそれぞれ指定して１つの接触条件についてシミュレーションするためのフラグ
  1. `--X`: x位置の指定．`-s` 指定時のみ有効．指定しない場合のデフォルトは0.5
  1. `--Y`: y位置の指定．`-s` 指定時のみ有効．指定しない場合のデフォルトは0.5
  1. `--F`: 力の指定．指定しない場合のデフォルトは0.5
- 戻り値（標準出力）
  1. シミュレーションを行った接触条件のリスト
  1. 各電極の電圧情報

### 備考
 - 結果の表示方法を切り替えるオプション引数を作り，データセットとしてファイル保存できるようにする必要あり．

## `sim7x7.py`

上記`simulate.py`を実装するためのモジュールです．上記スクリプトを利用せず，自身でシミュレーションコードを書く場合に利用してください．

このモジュールは，実行環境に依存する変数をconfig.ymlで与えることとしています．config.ymlで定義する変数は以下の通りです．
1. ltspice: 'LTspiceの実行ファイルの絶対パス'
1. working_dir: 'ベースとなるネットリストファイルが保存されたディレクトリの絶対パス'
1. delimiter: '実行環境におけるパスの区切り文字．Winなら\，その他は/'
1. base_netlist: 'ペーストなるネットリストファイルの名前'
補足）working_dirには，シミュレーション時にtmp.netという抵抗・静電容量の変化を与えたネットリストの一時ファイル，および，シミュレーションによる中間ファイルが生成されます．

# Note

(2021/4/21時点)
7x7の電極中央に電圧を印加した際の，残りの48個の電極での（定常状態における最大）電圧を計測することとしています．使用しているのは，LTspiceのTRANコマンドです．このコマンドは設定された時間の過渡応答をシミュレーションするコマンドで，この時間幅の最後から20%の時間幅を定常状態と見なしています．netlistファイルは，LTspiceを立ち上げてopenすることで個別にシミュレーションをすることや，電圧プロファイルをプロットすることができるので，最後から20%の時間幅において定常状態となることを確認することをお勧めします．あまりにも長い時間の過渡応答シミュレーションは，多くの時間・メモリを消費することに繋がるので注意してください．
