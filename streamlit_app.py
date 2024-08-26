import streamlit as st
from supabase import create_client, Client
import requests
import json

# Supabaseの設定
url = st.secrets["supabase"]["SUPABASE_URL"]
key = st.secrets["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Dify APIの設定
DIFY_API_URL = st.secrets["dify"]["API_URL"]
DIFY_API_KEY = st.secrets["dify"]["API_KEY"]

# 初期化: セッションステートにユーザー情報を保持
if "user" not in st.session_state:
    st.session_state.user = None
# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# ログイン処理を行う関数
def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            st.session_state.user = response.user
            st.success("ログインしました。")
        else:
            st.error("ログインに失敗しました。")
    except Exception as e:
        st.error(f"ログインに失敗しました: {e}")

# サインアップ処理を行う関数
def user_signup(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            st.session_state.user = response.user
            st.success("登録が完了しました。")
        else:
            st.error("登録に失敗しました。")
    except Exception as e:
        st.error(f"サインアップに失敗しました: {e}")

# DifyのチャットボットAPIに問い合わせる関数
def ask_dify_bot(prompt):
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {},  # 必要に応じて入力データをここに追加
        "query": prompt,  # ユーザーが入力したプロンプトをここに設定
        "response_mode": "streaming",  # 返答のモード（"streaming"または"blocking"）
        "conversation_id": "",  # 新しい会話の場合は空文字列、既存の会話IDがあればそれを指定
        "user": st.session_state.user.id,  # Supabaseから取得したユーザーIDを使用
        "files": []  # ファイルがある場合はここにリストとして追加
    }

    try:
        response = requests.post(DIFY_API_URL, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        full_response = ""
        response_area = st.empty()  # 空の要素を準備
        
        for chunk in response.iter_lines(decode_unicode=True):
            if chunk:
                if chunk.startswith('data:'):
                    data = json.loads(chunk[5:])
                    if data.get('event') == 'message':
                        full_response += data.get('answer')
                        response_area.markdown(full_response)  # 全体のレスポンスを表示
                    elif data.get('event') == 'message_end':
                        st.write("会話が終了しました。")
        
        # チャットログに追加
        st.session_state.chat_log.append({"name": "assistant", "msg": full_response})

    except requests.exceptions.HTTPError as e:
        st.error(f"チャットボットとの通信に失敗しました: {e}")
        st.write(response.json())
        return None

# チャットインターフェースを表示する関数
def chat_interface():
    user = st.session_state.user
    if user:
        st.write(f"Hello! {user.id}")
        st.write("妄想プロカメラマン（AI）があなたに最適なスチールカメラを提案します。  \nご予算、特徴、被写体などを入力してください。")
        prompt = st.chat_input("カメラについて聞いてください😎")
        
        # 過去のチャット履歴を表示
        for chat in st.session_state.chat_log:
            if isinstance(chat, dict):
                with st.chat_message(chat["name"]):
                    st.write(chat["msg"])
            else:
                print(f"Warning: Unexpected data type for chat: {type(chat)}")

        if prompt:
            with st.chat_message("user"):
                st.write(f"{prompt}")
                st.session_state.chat_log.append({"name": "user", "msg": prompt})
                
            with st.chat_message("assistant"):
                bot_response = ask_dify_bot(prompt)
                if bot_response:
                    # message = st.chat_message("assistant")
                    message.write(f"{bot_response}")

                    # セッションにチャットログを追加
                    # st.session_state.chat_log.append({"name": "assistant", "msg": bot_response})
                    st.session_state.chat_log.append({"name": "user", "msg": prompt})
                    st.session_state.chat_log.append({"name": "assistant", "msg": bot_response})

        # ログアウトボタン
        if st.button("ログアウト"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.success("ログアウトしました")

# ログインとサインアップ用のUIを表示する関数
def use_login():
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        login(email, password)
        st.rerun()

# メインコンテナの表示
with st.container():
    st.title("Streamlit AI Chat is :blue[Cool] :sunglasses:")
    
    if st.session_state.user:
        # ログイン済みならチャットインターフェースを表示
        chat_interface()
    else:
        # ログインしていない場合はログイン画面を表示
        use_login()