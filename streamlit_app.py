import streamlit as st
from supabase import create_client, Client
import requests

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
    
    # APIに送信するペイロードの設定
    payload = {
        "inputs": {},  # 必要に応じて入力データをここに追加
        "query": prompt,  # ユーザーが入力したプロンプトをここに設定
        "response_mode": "blocking",  # 返答のモード（"streaming"または"blocking"）
        "conversation_id": "",  # 新しい会話の場合は空文字列、既存の会話IDがあればそれを指定
        "user": st.session_state.user.id,  # Supabaseから取得したユーザーIDを使用
        "files": []  # ファイルがある場合はここにリストとして追加
    }
    
    try:
        response = requests.post(DIFY_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        # APIレスポンスから`answer`フィールドを取得
        response_data = response.json()
        answer = response_data.get("answer", "No response from bot.")
        
        return answer
    except requests.exceptions.HTTPError as e:
        st.error(f"チャットボットとの通信に失敗しました: {e}")
        st.write(response.json())  # エラーメッセージを表示
        return None

# チャットインターフェースを表示する関数
def chat_interface():
    user = st.session_state.user
    if user:
        # st.write(f"ユーザーID: {user.id}, メールアドレス: {user.email}")
        st.write(f"Hello! {user.id}")
        st.write("チャット画面")
        prompt = st.chat_input("カメラについて聞いてください😎")
        if prompt:
            with st.chat_message("user"):
                st.write(f"ユーザーの質問: {prompt}")
                bot_response = ask_dify_bot(prompt)
            if bot_response:
                message = st.chat_message("assistant")
                message.write(f"AIの応答: {bot_response}")

        # ログアウトボタン
        if st.button("ログアウト"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.success("ログアウトしました")
            # st.rerun()

# ログインとサインアップ用のUIを表示する関数
def use_login():
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        login(email, password)
        st.rerun()
    '''
    with st.form(key="form_login"):
        col1, col2 = st.columns([1, 1])  # 画面を2分割
        with col1:
            if st.form_submit_button("登録"):
                user_signup(email, password)
        with col2:'''
            

# メインコンテナの表示
with st.container():
    st.title("Streamlit AI Chat is :blue[Cool] :sunglasses:")
    
    if st.session_state.user:
        # ログイン済みならチャットインターフェースを表示
        chat_interface()
    else:
        # ログインしていない場合はログイン画面を表示
        use_login()