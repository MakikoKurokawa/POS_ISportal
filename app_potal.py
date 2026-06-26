import streamlit as st

# --- ページ基本設定（一番最初に書く必要があります） ---
st.set_page_config(
    page_title="POS_ISポータル",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 古いバージョンでも動くようにセッション状態（ログイン管理）を自作する
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================================
# 🔒 ログインしていない場合の処理（メニューは一切作らない！）
# =========================================================================
if not st.session_state.logged_in:
    st.write("POS ISポータル")
    st.write("利用するにはGoogleアカウントでログインしてください。")
    
    if st.button("Googleアカウントでログイン"):
        st.session_state.logged_in = True
        st.rerun()
    
    # 💡 重要：ここで処理を完全にストップさせます。
    # この下にある st.navigation にたどり着かせないことで、メニューの表示を完全に防ぎます。
    st.stop()


# =========================================================================
# 🔓 【ここから下はログイン成功後】本編コード ＆ メニュー作成
# =========================================================================

# 🚀 データの管理ボタン（サイドバーの中に配置）
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 データの管理")

if st.sidebar.button("最新情報に更新"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# --- 各ページの表示ロジック（関数呼び出し用） ---
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


# 🧭 ナビゲーション定義（ログインした人だけにメニューを生成する）
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
