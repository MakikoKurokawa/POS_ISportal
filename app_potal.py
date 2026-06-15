import streamlit as st
import pandas as pd

# --- ページ基本設定 ---
st.set_page_config(
    page_title="武田塾 ISコックピット",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 擬似マスターデータ（後にGoogleスプレッドシート連携に置き換え） ---
@st.cache_data
def load_mock_data():
    campus_data = {
        "校舎名": ["天王寺校", "大阪校", "梅田校", "京都校", "難波校"],
        "募集状況": ["🟢 受付中", "🔴 新規NG・定員寸前", "🟢 受付中", "🟢 受付中", "💛 残りわずか"],
        "中学生受付": ["中高一貫のみOK", "❌ 全面NG", "全員OK", "全員OK", "中高一貫のみOK"],
        "最寄り駅": ["天王寺駅", "大阪駅/梅田駅", "大阪梅田駅", "京都駅", "難波駅"],
        "徒歩": ["徒歩3分", "徒歩5分", "徒歩4分", "徒歩6分", "徒歩2分"],
        "駐輪場・駐車場": ["駐輪場あり / 近隣コインP", "なし（公共交通推奨）", "専用なし / 施設Pあり", "駐輪場あり", "近隣コインPのみ"],
        "誘導ディレクション / 特記事項": [
            "中高一貫の先取り学習のみ対応可",
            "🚨近隣の「天王寺校」または「難波校」へ誘導！",
            "中高生ともに余裕あり",
            "高校生メインで受付中",
            "定員間近のため面談枠タイト"
        ],
        "電話番号": ["06-1111-xxxx", "06-2222-yyyy", "06-3333-zzzz", "075-4444-aaaa", "06-5555-bbbb"],
        "住所": ["大阪市天王寺区...", "大阪市北区梅田...", "大阪市北区芝田...", "京都市下京区...", "大阪市中央区..."]
    }
    travel_data = {
        "出発校舎": ["大阪校", "大阪校", "天王寺校", "難波校"],
        "到着校舎": ["天王寺校", "梅田校", "大阪校", "大阪校"],
        "移動時間": [30, 15, 30, 20]
    }
    return pd.DataFrame(campus_data), pd.DataFrame(travel_data)

df_campus, df_travel = load_mock_data()

# --- 行の色付けロジック ---
def style_campus_df(df):
    def make_style(row):
        if "🔴" in row["募集状況"] or "❌" in row["中学生受付"]:
            return ["background-color: #ffcccc; color: #330000; font-weight: bold;"] * len(row)
        elif "💛" in row["募集状況"]:
            return ["background-color: #fff2cc; color: #332200;"] * len(row)
        return [""] * len(row)
    return df.style.apply(make_style, axis=1)


# =========================================================================
# 各ページの表示中身を関数として定義（st.navigationで呼び出すため）
# =========================================================================

def show_home():
    st.title("🏠 ホーム ＆ 戦略チームからの施策共有")
    st.info("📢 【重要なお知らせ】夏期講習（夏だけタケダ）のIS受付ディレクションが更新されました。")
    with st.expander("【2026/06/13】高3掘り起こし架電の優先順位について", expanded=True):
        st.write("過去にお問い合わせのあった「現高3生」への掘り起こしを強化します。")

def show_onboarding():
    st.title("📖 オンボーディング・基礎研修資料")
    st.caption("武田塾の「思想」をインプットし、説得力のある架電トークの土台を作ります。")
    onbo_tab1, onbo_tab_takeda, onbo_tab2, onbo_tab3 = st.tabs([
        "🏢 会社概要と事業内容", "🦅 【重要】武田塾の勉強法・コア思想", "🎯 ISの存在意義・重要KPI", "🎓 塾業界・受験制度の基礎"
    ])
    with onbo_tab1:
        st.subheader("武田塾のミッション：『日本初！授業をしない塾』")
        st.write("武田塾は、授業をせず「自学自習の徹底管理」によって逆転合格を専門とする個別指導塾です。")
    with onbo_tab_takeda:
        st.markdown("## 🦅 架電で絶対ブレないための「武田塾の4大本質」")
        st.write("①授業をしない理由、②一冊を完璧に、③4日進んで2日戻る、④参考書ルートの解説。")
    with onbo_tab2:
        st.subheader("🔥 インサイドセールス（IS）チームの存在意義")
    with onbo_tab3:
        st.subheader("🎓 塾業界知識と受験制度")

def show_appsheet_manual():
    st.title("📱 AppSheet 操作手順マニュアル")
    col_flow, col_step = st.columns([1, 2])
    with col_flow:
        st.markdown("### 🔄 顧客ステータス別の必須対応")
    with col_step:
        st.markdown("### 📸 画像でわかる！画面別操作説明")
        step = st.radio("確認したい操作手順を選択してください", ["Step1. 新規リストから顧客を選ぶ", "Step2. 架電ログを入力する", "Step3. 面談予約を確定させる"])
        st.image("https://via.placeholder.com/600x250.png?text=" + step.replace(" ", "+"))

def show_script():
    st.title("📞 インサイドセールス・動的スクリプト")
    tab1, _, _ = st.tabs(["👥 面談希望者向け", "📄 資料希望者向け", "🔄 過去問合せ掘り起こし"])
    with tab1:
        student_type = st.selectbox("生徒の学年を選択", ["高校3年生", "既卒生（浪人生）", "高校1・2年生"])
        st.info(f"「お問い合わせありがとうございます！武田塾です。{student_type}のこの時期ですと...」")

def show_faq():
    st.title("🔍 FAQ ＆ カウンタートーク集")
    search_query = st.text_input("🔍 検索窓")
    with st.expander("📦 サービス内容に関する懸念"):
        st.write("Q. 授業をしないなら、質問はどうするのですか？")

def show_campus_info():
    st.title("🏫 校舎ステータス一覧 ＆ スケジュール調整")
    st.markdown("### 🚨 【即電対応】全校舎 受付・アクセス状況一覧")
    styled_df = style_campus_df(df_campus)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.markdown("---")
    
    st.markdown("### 📅 カレンダー確認・移動時間シミュレーション")
    col_select, _ = st.columns([1, 2])
    with col_select:
        selected_campus = st.selectbox("詳細スケジュールを確認する校舎を選択", df_campus["校舎名"].tolist())
    
    c_info = df_campus[df_campus["校舎名"] == selected_campus].iloc[0]
    st.caption(f"📍 選択中: {selected_campus} （{c_info['最寄り駅']}{c_info['徒歩']} | TEL: {c_info['電話番号']}）")
    
    cam_tab1, cam_tab2 = st.tabs(["👤 担当者カレンダー", "🚪 校舎の会議室（リソース）"])
    with cam_tab1:
        st.code("Google Calendar iframe [担当A]\n14:00 (空き)", language="text")
    with cam_tab2:
        st.code(f"Google Calendar リソースiframe [{selected_campus} 面談室A]\n14:00-15:00 [空き]", language="text")

def show_knowledge():
    st.title("📝 ナレッジ共有フォーム")
    with st.form("knowledge_form"):
        st.text_area("① ターゲットの属性・課題")
        st.form_submit_button("ナレッジを投稿する")

def show_dashboard():
    st.title("📊 本日の実績 ＆ Slack日報手動送信")
    st.metric("架電人数", "20人")
    editable_report = st.text_area("日報内容（編集可能）", value="【架電数値報告】\n・架電人数：20人", height=150)
    if st.button("🚀 Slackに送信する"):
        st.success("📨 送信完了！")


# =========================================================================
# 🧭 ルーティングとナビゲーション定義 (どこをクリックしても遷移するメニュー)
# =========================================================================

# 1. 各メニューの定義（タイトル、アイコン、実行する関数を紐付け）
page_home = st.Page(show_home, title="🏠 ホーム・戦略共有", default=True)
page_onbo = st.Page(show_onboarding, title="📖 オンボーディング（武田塾知識）")
page_appsheet = st.Page(show_appsheet_manual, title="📱 AppSheet操作マニュアル")
page_script = st.Page(show_script, title="📞 動的スクリプト")
page_faq = st.Page(show_faq, title="🔍 FAQ・カウンタートーク")
page_campus = st.Page(show_campus_info, title="🏫 校舎情報＆スケジュール")
page_knowledge = st.Page(show_knowledge, title="📝 ナレッジ共有フォーム")
page_dash = st.Page(show_dashboard, title="📊 実績ダッシュボード＆日報")

# 2. サイドバー上部の固定ヘッダー表示
st.sidebar.title("武田塾 ISコックピット 📞")
st.sidebar.caption("v1.4 (クリックエリア最適化版)")
st.sidebar.write("👤 ログイン: `staff@takeda.tv`")
st.sidebar.markdown("---")

# 3. ナビゲーションの実行（これでサイドバーに文字幅いっぱいのメニューリンクが自動生成されます）
pg = st.navigation([
    page_home, 
    page_onbo, 
    page_appsheet, 
    page_script, 
    page_faq, 
    page_campus, 
    page_knowledge, 
    page_dash
])

# 4. 選択されたページの中身を実行
pg.run()
