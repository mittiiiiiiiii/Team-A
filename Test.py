import streamlit as st          #Streamlitライブラリをインポート
import random                   #乱数を生成するためのライブラリをインポート

#ゲームの状態を初期化または更新
if 'position' not in st.session_state:  #セッション状態にプレイヤーの位置がない場合
    st.session_state.position=0         #プレイヤーの初期位置を0に設定
if 'game_over' not in st.session_state: #セッション状態にゲーム終了フラグがない場合
    st.session_state.game_over=False    #ゲーム終了フラグをFalseに設定

def roll_dice():    #サイコロを振るアクション
    if not st.session_state.game_over:                  #ゲームが終了していない場合
        roll=random.randint(1,6)                        #1から6の間でランダムな数値を生成
        st.session_state.position+=roll               #プレイヤーの位置を更新

        if st.session_state.position>=28:             #外周のマス数を超えた場合
            st.session_state.game_over=True           #ゲーム終了フラグをTrueに設定
            st.success('一周してゴールに到達しました！おめでとうございます！')  #成功メッセージを表示
        else:
            st.info(f'サイコロの目は {roll} です。現在の位置は {st.session_state.position} です。')  #現在の位置とサイコロの目を表示

def get_display_board_style():#ゲームボードのスタイルを定義
    return """
    <style>
        .board{
            display: grid;
            grid-template-columns: repeat(10,50px);
            grid-template-rows: repeat(7,50px);
            gap: 5px;
        }

        .cell{
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #333;
        }

        .player{
            background-color: #4CAF50;
        }

        .empty{
            border: none;
            background-color: white;
        }
    </style>
    """

#ゲームボードの表示
def display_board():
    board_html=get_display_board_style()#スタイルを呼び出し
    board_html+="<div class='board'>"  #ゲームボードの開始
    outer_positions=list(range(10))+list(range(19,60,10))+list(range(69,59,-1))+list(range(50,1,-10))#外周のマスを計算

    for i in range(70):  #7x10のグリッドでループ
        if i in outer_positions:  #外周のマスの場合
            if outer_positions.index(i)==st.session_state.position:  #プレイヤーの位置の場合
                board_html+="<div class='cell player'>P</div>"  #プレイヤーを表示
            else:
                board_html+="<div class='cell'></div>"  #通常のマスを表示
        else:
            board_html+="<div class='cell empty'></div>"  #使用しないマスを表示

    board_html+="</div>"  #ゲームボードの終了
    st.markdown(board_html,unsafe_allow_html=True)  #ゲームボードを表示

st.button('サイコロを振る',on_click=roll_dice)  #サイコロを振るためのボタンを表示

display_board()                         #ゲームボードの表示を更新

#ゲームのリセット
if st.button('ゲームをリセット'):          #ゲームをリセットするためのボタンを表示
    st.session_state.position=0         #プレイヤーの位置を0にリセット
    st.session_state.game_over=False    #ゲーム終了フラグをFalseにリセット
    st.session_state.laps=0             #周回数を0にリセット

    st.rerun() #ページをプログラム的に再実行して、リセットを即座に反映