import streamlit as st
from supabase import create_client

# Supabaseの設定
url = st.secrets["supabase"]["SUPABASE_URL"]
key = st.secrets["supabase"]["SUPABASE_KEY"]
supabase = create_client(url, key)
# 環境変数が正しく取得できているか確認
def check_supabase_config():
    # 環境変数が正しく取得できているか確認
    if not url or not key:
        return "SupabaseのURLまたはAPIキーが設定されていません。secrets.tomlファイルを確認してください。"
    else:
        return f"コネクトできています"

# 関数の呼び出しと結果の表示
result = check_supabase_config()

if "設定されていません" in result:
    st.error(result)
else:
    for line in result.split("\n"):
        st.write(line)
user = supabase.auth.get_user()

def login_signup():
    if user:
        # ログイン済み
        st.write(f"ユーザーID: {user['id']}, メールアドレス: {user['email']}")
        # チャット画面
        prompt = st.chat_input("Say something")
        if prompt:
            st.write(f"User has sent the following prompt: {prompt}")
        # ログアウトボタンなど、ログイン後の処理を追加
        if st.button("ログアウト"):
            # ログアウト処理
            supabase.auth.sign_out()
            st.success("ログアウトしました")
    else:
        # ログインしていない
        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")

        col1, col2 = st.columns([20, 80])  # 画面を2分割
        with col1:
            if st.button("登録"):
                # サインアップ
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                if not response.successful():
                    st.error(response.message)
                else:
                    st.success("登録が完了しました。")

        with col2:
            if st.button("ログイン"):
                # ログイン
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                if not response.successful():
                    st.error(response.message)
                else:
                    st.success("ログインしました。")

with st.container():
    st.title("_Streamlit_ is :blue[cool] :sunglasses:")
    login_signup()