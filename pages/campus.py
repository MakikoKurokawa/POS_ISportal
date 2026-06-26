# pages/campus.py
import streamlit as st
import pandas as pd
import requests
from io import StringIO

# --- 🚨 スプレッドシートの共有URLを設定 🚨 ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNLGbIj6c_sWtQUqLBgywLhDH1dec1OkUr4mG21XRXWU7_DoMfIGrj-S3xyp_aDjSUmXJ4_ZvGitfz/pub?gid=628921947&single=true&output=csv"

# --- キャッシュによるデータ読み込み関数 ---
@st.cache_data
def load_campus_master_safe(url):
    try:
        csv_url = url
        response = requests.get(csv_url, timeout=5)
        if response.status_code == 200:
            # 💡 【対策】スプシの1行目が空白行だったりズレていても、
            # 自動的に「文字が入っている行」を列名として認識させる設定（header='infer'）
            df = pd.read_csv(StringIO(response.text), header='infer')
            
            # 列名の前後に目に見えないスペースが入っていたら綺麗に削る
            df.columns = df.columns.str.strip()
            
            # 💡 デバッグ用：万が一、列名がズレていた場合のために
            # 「校舎名」という列がどうしても見つからなければ、強制的に1行目を列名に再設定する
            if "校舎名" not in df.columns and len(df) > 0:
                df.columns = df.iloc[0].astype(str).str.strip()
                df = df[1:].reset_index(drop=True)
                
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# データの読み込み
df_campus = load_campus_master_safe(SPREADSHEET_URL)

# --- 信号機・行の色付けロジック ---

def style_campus_df(df):
    # 💡 【修正】画面の表（メイン一覧）に見せたい列「だけ」を順番通りに指定します
    # ※ここに書かれていない「校舎カレンダー」「カレンダーURL」「会議室①」「会議室②」は自動的に非表示になります！
    display_cols = [
        "エリア", 
        "校舎名", 
        "校舎名(ふりがな)", 
        "受付状況", 
        "中学生受付", 
        "中学生ディレクション", 
        "校舎ディレクション", 
        "担当者に関する備考欄", 
        "最寄り駅"
    ]
    
    # スプシに存在する列だけを安全に抜き出す
    available_cols = [c for c in display_cols if c in df.columns]
    sub_df = df[available_cols].copy()
    
    # 信号機（🔴や💛）による行の色付けルール
    def make_style(row):
        if "🔴" in str(row.get("受付状況", "")) or "❌" in str(row.get("中学生受付", "")):
            return ["background-color: #ffcccc; color: #330000; font-weight: bold;"] * len(row)
        elif "💛" in str(row.get("受付状況", "")) or "💛" in str(row.get("中学生受付", "")) or "📘" in str(row.get("中学生受付", "")):
            return ["background-color: #fff2cc; color: #332200; font-weight: bold;"] * len(row)
        return [""] * len(row)
        
    return sub_df.style.apply(make_style, axis=1)

# --- 画面のメイン表示処理 ---
st.title("🏫 校舎ステータス一覧 ＆ スケジュール調整")

if df_campus.empty:
    st.warning("スプレッドシートからデータが読み込めなかったため、一覧を表示できません。")
else:
    st.markdown("### 🚨 【即電対応】全校舎 受付・アクセス状況一覧")
    styled_df = style_campus_df(df_campus)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 📅 カレンダー一元確認 ＆ 詳細アクセス情報")
    
    col_select, _ = st.columns([1, 2])
    with col_select:
        campus_list = df_campus["校舎名"].dropna().tolist()
        selected_campus = st.selectbox("詳細スケジュールを確認する校舎を選択", campus_list)
        
    c_info = df_campus[df_campus["校舎名"] == selected_campus].iloc[0]
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"#### 📢 {selected_campus} のディレクション")
        st.error(f"**【全体受付状況】** {c_info.get('受付状況', '未設定')}\n\n👉 {c_info.get('校舎ディレクション', '特になし')}")
        st.warning(f"**【中学生の受付】** {c_info.get('中学生受付', '未設定')}\n\n👉 {c_info.get('中学生ディレクション', '特になし')}")
    with col_d2:
        st.markdown("#### 📱 アクセス・基本情報")
        st.success(f"""
        * **最寄り駅:** {c_info.get('最寄り駅', '未設定')} (開校: {c_info.get('開校時間', '未設定')} / 自習室: {c_info.get('自習室利用時間', '未設定')})
        * **面談可能時間:** {c_info.get('面談可能時間', '未設定')}
        * **住所:** {c_info.get('住所', '未設定')}
        """)
        col_btn1, col_btn2 = st.columns(2)
        if pd.notna(c_info.get('Googleマップ')) and str(c_info.get('Googleマップ')).startswith("http"):
            col_btn1.link_button("🗺️ Googleマップで開く", c_info['Googleマップ'], use_container_width=True)
        if pd.notna(c_info.get('HP')) and str(c_info.get('HP')).startswith("http"):
            col_btn2.link_button("🌐 公式HPの校舎ページ", c_info['HP'], use_container_width=True)

    st.markdown("---")
    st.markdown(f"### 👥 {selected_campus} スケジュール＆会議室 一元確認（特大合体ビュー）")
    
    if pd.notna(c_info.get('担当者に関する備考欄')) and str(c_info['担当者に関する備考欄']).strip() != "":
        st.warning(f"🚗 **【担当者に関する備考・移動注意】**\n\n{c_info['担当者に関する備考欄']}")

    combined_url = c_info.get("カレンダーURL")

    if pd.notna(combined_url) and str(combined_url).startswith("http"):
        st.caption("💡 複数のカレンダー・会議室の予定が1つの画面に重なって表示されています。")
        st.components.v1.iframe(str(combined_url).strip(), height=750, scrolling=True)
    else:
        st.info("この校舎の「カレンダーURL」列に有効なURLが登録されていません。スプレッドシートを確認してください。")
