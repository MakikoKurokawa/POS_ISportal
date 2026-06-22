# app_potal.py
import streamlit as st

# --- ページ基本設定 ---
st.set_page_config(
    page_title="POS_ISコックピット",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚀 修正：「スプシ最新化ボタン」は残したいので、ここでのキャッシュクリア用としてシンプルに記述
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 データの管理")
if st.sidebar.button("スプシの最新情報を取得", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# =========================================================================
# 各ページの表示ロジック
# =========================================================================

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
# 🧭 ナビゲーション
# =========================================================================
page_home = st.Page(show_home, title="🏠 ホーム・戦略共有", default=True)

# 🚀 切り分けたファイルを指定
page_onbo = st.Page("pages/onboarding.py", title="📖 オンボーディング・研修")
page_campus = st.Page("pages/campus.py", title="🏫 校舎情報＆スケジュール")

# 関数呼び出しのページ
page_appsheet = st.Page(show_appsheet_manual, title="📱 AppSheet操作マニュアル")
page_script = st.Page(show_script, title="📞 動的スクリプト")
page_faq = st.Page(show_faq, title="🔍 FAQ・カウンタートーク")
page_knowledge = st.Page(show_knowledge, title="📝 ナレッジ共有フォーム")
page_dash = st.Page(show_dashboard, title="📊 実績ダッシュボード＆日報")

st.sidebar.title("POS_ISコックピット 📞")
st.sidebar.caption("v1.11 (6/22更新)")
st.sidebar.markdown("---")

pg = st.navigation([page_home, page_onbo, page_appsheet, page_script, page_faq, page_campus, page_knowledge, page_dash])
pg.run()
