import streamlit as st
from supabase import create_client, Client

# Supabaseの設定
url = st.secrets["supabase"]["SUPABASE_URL"]
key = st.secrets["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

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

# チャットインターフェースを表示する関数
def chat_interface():
    user = st.session_state.user
    if user:
        st.write(f"ユーザーID: {user.id}, メールアドレス: {user.email}")
        st.write("チャット画面")
        prompt = st.chat_input("Say something")
        if prompt:
            st.write(f"User has sent the following prompt: {prompt}")
            # AIチャットボットAPIとの連携などをここで実装

        # ログアウトボタン
        if st.button("ログアウト"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.success("ログアウトしました")
            st.experimental_rerun()  # ログアウト後に画面をリロード

# ログインとサインアップ用のUIを表示する関数
def use_login():
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")

    col1, col2 = st.columns([1, 1])  # 画面を2分割
    with col1:
        if st.button("登録"):
            user_signup(email, password)

    with col2:
        if st.button("ログイン"):
            login(email, password)

# メインコンテナの表示
with st.container():
    st.title("Streamlit AI Chat is :blue[Cool] :sunglasses:")
    
    if st.session_state.user:
        # ログイン済みならチャットインターフェースを表示
        chat_interface()
    else:
        # ログインしていない場合はログイン画面を表示
        use_login()