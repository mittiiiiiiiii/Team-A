import streamlit as st          # Streamlitライブラリをインポート
import random                   # 乱数を生成するためのライブラリをインポート
import openai
from llama_index.llms.openai import OpenAI
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader


st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

# ゲームの状態を初期化または更新
if 'position' not in st.session_state:  # セッション状態にプレイヤーの位置がない場合
    st.session_state.position = 0         # プレイヤーの初期位置を0に設定
    st.session_state.count = 0            # サイコロを振った回数を0に設定
if 'game_over' not in st.session_state:  # セッション状態にゲーム終了フラグがない場合
    st.session_state.game_over = False    # ゲーム終了フラグをFalseに設定

def roll_dice():    # サイコロを振るアクション
    if not st.session_state.game_over:                  # ゲームが終了していない場合
        roll = random.randint(1, 6)                        # 1から6の間でランダムな数値を生成
        st.session_state.position += roll               # プレイヤーの位置を更新
        st.session_state.count += 1                     # サイコロを振った回数を更新

        if st.session_state.position >= 28:             # 外周のマス数を超えた場合
            st.session_state.game_over = True           # ゲーム終了フラグをTrueに設定
            st.success(f'一周してゴールに到達しました！おめでとうございます！ サイコロを振った回数は {st.session_state.count} です。')  # 成功メッセージを表示
        else:
            st.info(f'サイコロの目は {roll} です。現在の位置は {st.session_state.position} です。')  # 現在の位置とサイコロの目を表示

def get_display_board_style():  # ゲームボードのスタイルを定義
    return """
    <style>
        .board{
            display: grid;
            grid-template-columns: repeat(10, 50px);
            grid-template-rows: repeat(7, 50px);
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

        .even{
            background-color: yellow;
        }

        .test{
            background-color: red;
        }
    </style>
    """

# ゲームボードの表示
def display_board():
    board_html = get_display_board_style()    # スタイルを呼び出し
    board_html += "<div class='board'>"  # ゲームボードの開始
    outer_positions = list(range(10)) + list(range(19, 60, 10)) + list(range(69, 59, -1)) + list(range(50, 1, -10))   # 外周のマスを計算
    k = 0
    t = False

    for i in range(70):  # 7x10のグリッドでループ
        if i in outer_positions:  # 外周のマスの場合
            if outer_positions.index(i) == st.session_state.position and not st.session_state.game_over:  # プレイヤーの位置の場合
                board_html += "<div class='cell player'>P</div>"  # プレイヤーを表示
                if i == 10 or i == 20 or i == 30 or i == 40 or i == 50 or i == 60:
                    t = True
                if i == 19 or i == 39 or i == 59:
                    k += 1
            else:
                if i % 2 == 0:
                    if i % 10 == 0:
                        board_html += "<div class='cell test'></div>"
                    else:
                        board_html += "<div class='cell even'></div>"  # 偶数のマスを黄色で表示
                elif i % (19 + 20 * k) == 0:
                    board_html += "<div class='cell even'></div>"
                    k += 1
                else:
                    board_html += "<div class='cell'></div>"  # 通常のマスを表示
        else:
            board_html += "<div class='cell empty'></div>"  # 使用しないマスを表示
    if t:
        t = False
        k=5
        send(k)

    board_html += "</div>"  # ゲームボードの終了
    st.markdown(board_html, unsafe_allow_html=True)  # ゲームボードを表示

def send(k):
    print("send関数に渡されたkの値:", k)
    prompt = "現在のカードの枚数は{}枚です。勝負しましょう".format(k)
    print("生成されたプロンプト:", prompt)  # 生成されたプロンプトを確認
    response = st.session_state.chat_engine.chat(prompt + " ぜひ日本語でお答えください。")
    st.write(response.response)
    st.session_state.messages.append({"role": "assistant", "content": response.response})

st.button('サイコロを振る', on_click=roll_dice)  # サイコロを振るためのボタンを表示

display_board()  # ゲームボードの表示を更新

# ゲームのリセット
if st.button('ゲームをリセット'):  # ゲームをリセットするためのボタンを表示
    st.session_state.position = 0  # プレイヤーの位置を0にリセット
    st.session_state.game_over = False  # ゲーム終了フラグをFalseにリセット
    st.session_state.laps = 0  # 周回数を0にリセット
    st.session_state.count = 0  # サイコロを振った回数を0にリセット

    st.experimental_rerun()  # ページをプログラム的に再実行して、リセットを即座に反映

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは!ゲームのテストbotです!!"},
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader("data")
        docs = reader.load_data()

        llm = OpenAI(model="gpt-4", temperature=0.0, system_prompt="あなたは、日本語が達者であり、必ず日本語で質問い回答する。カードの枚数勝ち負けゲームの専門家です。")
        index = VectorStoreIndex.from_documents(docs)
        return index
    
def judge_win_or_lose(response_text):
    if "勝ち" in response_text or "勝ち" in response_text:
        return "勝ち"
    elif "負け" in response_text:
        return "負け"

index = load_data()
 
if "chat_engine" not in st.session_state.keys():
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt + " ぜひ日本語でお答えください。")
            st.write(response.response)
            
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)

            result = judge_win_or_lose(message)  # 勝ち、負けを判定
            st.write(f"判定結果: {result}")

            print("メッセージ:", message)