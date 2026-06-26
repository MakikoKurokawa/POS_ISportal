import streamlit as st

# --- ページ基本設定 ---
st.set_page_config(
    page_title="POS_ISポータル",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態（ログイン管理）
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================================
# 📑 ページ表示用の中身（関数）
# =========================================================================
def show_login():
    st.write("POS ISポータル")
    st.write("利用するにはGoogleアカウントでログインしてください。")
    if st.button("Googleアカウントでログイン"):
        st.session_state.logged_in = True
        st.rerun()

def show_home():
    st.title("🏠 ホーム ＆ 面談率PJ・各校舎からのお知らせ")
    st.info("📢 【重要なお知らせ】夏期講習（夏だけタケダ）のIS受付ディレクションが更新されました。")

def show_appsheet_manual():
    st.title("📱 AppSheet 操作手順マニュアル")

def show_script():
    st.title("📞 インサイドセールス・動的スクリプト")

def show_faq():
    st.title("🔍 FAQ ＆ カウンタートーク集")

def show_knowledge():
    st.title("📝 ナレッジ共有フォーム")

def show_dashboard():
    st.title("📊 本日の実績 ＆ Slack日報手動送信")


# =========================================================================
# 🧭 ルーティング制御（ログイン状態によってナビゲーションを「丸ごと」切り替える）
# =========================================================================

if not st.session_state.logged_in:
    # 🔒 ログイン前：別ファイルは一切読み込まず、ログイン画面「だけ」を定義する
    page_login = st.Page(show_login, title="🔐 ログインが必要です", default=True)
    pg = st.navigation([page_login], position="hidden") # position="hidden"でサイドバーごと消し去る
    pg.run()

else:
    # 🔓 ログイン後：ここで初めてキャンパスやオンボのファイルを読み込んでメニューを作る
    
    # 🚀 データの管理ボタン（サイドバー内）
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 データの管理")
    if st.sidebar.button("最新情報に更新"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    # メニューの定義
    page_home = st.Page(show_home, title="🏠 ホーム・戦略共有", default=True)
    page_onbo = st.Page("pages/onboarding.py", title="📖 オンボーディング・研修")
    page_campus = st.Page("pages/campus.py", title="🏫 校舎情報＆スケジュール")
    page_appsheet = st.Page(show_appsheet_manual, title="📱 AppSheet操作マニュアル")
    page_script = st.Page(show_script, title="📞 動的スクリプト")
    page_faq = st.Page(show_faq, title="🔍 FAQ・カウンタートーク")
    page_knowledge = st.Page(show_knowledge, title="📝 ナレッジ共有フォーム")
    page_dash = st.Page(show_dashboard, title="📊 実績ダッシュボード＆日報")

    pg = st.navigation([page_home, page_onbo, page_appsheet, page_script, page_faq, page_campus, page_knowledge, page_dash])
    pg.run()
