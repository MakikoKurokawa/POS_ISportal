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
        
        # 文字化け対策
        response = requests.get(csv_url, timeout=5)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df.columns = df.columns.str.strip()
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# データの読み込み
df_campus = load_campus_master_safe(SPREADSHEET_URL)

# --- 信号機・行の色付けロジック ＆ 表の見た目調整 ---
def style_campus_df(df):
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
    
    available_cols = [c for c in display_cols if c in df.columns]
    sub_df = df[available_cols].copy()
    
    # 🎨 空っぽのスタイル用の枠組みを作る
    style_df = pd.DataFrame("", index=sub_df.index, columns=sub_df.columns)
    
    for idx, row in sub_df.iterrows():
        status = str(row.get("受付状況", ""))
        jr_status = str(row.get("中学生受付", ""))
        
        # ルール①：受付状況が🔴や❌のときは、1行まるまる網掛け
        if "🔴" in status or "❌" in status:
            style_df.loc[idx] = "background-color: #ffcccc; color: #330000; font-weight: bold;"
        # 受付状況が💛などの警告色のときも、1行まるまる薄黄色
        elif "💛" in status:
            style_df.loc[idx] = "background-color: #fff2cc; color: #332200; font-weight: bold;"
            
        # ルール②：中学生受付が❌のときは、「中学生」に関する列だけ網掛け
        if "❌" in jr_status:
            jr_style = "background-color: #fce4d6; color: #c00000; font-weight: bold; border: 1px solid #c00000;"
            if "中学生受付" in style_df.columns:
                style_df.loc[idx, "中学生受付"] = jr_style
            if "中学生ディレクション" in style_df.columns:
                style_df.loc[idx, "中学生ディレクション"] = jr_style
        # 中学生受付が💛や📘のときも、中学生の列だけを薄黄色に
        elif "💛" in jr_status or "📘" in jr_status:
            jr_warn_style = "background-color: #fff2cc; color: #332200; font-weight: bold;"
            if "中学生受付" in style_df.columns:
                style_df.loc[idx, "中学生受付"] = jr_warn_style
            if "中学生ディレクション" in style_df.columns:
                style_df.loc[idx, "中学生ディレクション"] = jr_warn_style

    return sub_df.style.apply(lambda _: style_df, axis=None)


# --- 画面のメイン表示処理 ---
st.title("🏫 校舎ステータス一覧 ＆ スケジュール調整")

if df_campus.empty:
    st.warning("スプレッドシートからデータが読み込めなかったため、一覧を表示できません。")
else:
    st.markdown("### 🚨 【即電対応】全校舎 受付・アクセス状況一覧")
    
    styled_df = style_campus_df(df_campus)
    
    # 縦幅を2倍（height=600）にして表示
    st.dataframe(
        styled_df, 
        use_container_width=True, 
        hide_index=True,
        height=600
    )
    
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
        
        # 🪄 魔法： \n を <br> に変えて、標準的な狭い行間にします！
        k_direction = str(c_info.get('校舎ディレクション', '特になし')).replace('\n', '<br>')
        j_direction = str(c_info.get('中学生ディレクション', '特になし')).replace('\n', '<br>')
        
        # 💡 HTMLタグ（<br>）を認識させるために、unsafe_allow_html=True を仕込みます
        st.markdown(f'<div style="background-color: #ffcccc; color: #330000; padding: 15px; border-radius: 5px; font-weight: bold;">**【全体受付状況】** {c_info.get("受付状況", "未設定")}<br><br>👉 {k_direction}</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True) # すきま調整
        st.markdown(f'<div style="background-color: #fff2cc; color: #332200; padding: 15px; border-radius: 5px; font-weight: bold;">**【中学生の受付】** {c_info.get("中学生受付", "未設定")}<br><br>👉 {j_direction}</div>', unsafe_allow_html=True)
        
    with col_d2:
        st.markdown("#### 📱 アクセス・基本情報")
        
        # 🪄 各種情報の改行も <br> に統一
        station = str(c_info.get('最寄り駅', '未設定')).replace('\n', '<br>')
        address = str(c_info.get('住所', '未設定')).replace('\n', '<br>')
        open_time = str(c_info.get('開校時間', '未設定')).replace('\n', '<br>')
        study_time = str(c_info.get('自習室利用時間', '未設定')).replace('\n', '<br>')
        mendan_time = str(c_info.get('面談可能時間', '未設定')).replace('\n', '<br>')
        
        # 綺麗に枠に収めるためのHTML化
        st.markdown(f"""
        <div style="background-color: #d1e7dd; color: #0f5132; padding: 15px; border-radius: 5px;">
        📌 <b>最寄り駅:</b> {station}<br>
        (開校: {open_time} / 自習室: {study_time})<br><br>
        📌 <b>面談可能時間:</b> {mendan_time}<br><br>
        📌 <b>住所:</b> {address}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True) # すきま調整
        col_btn1, col_btn2 = st.columns(2)
        if pd.notna(c_info.get('Googleマップ')) and str(c_info.get('Googleマップ')).startswith("http"):
            col_btn1.link_button("🗺️ Googleマップで開く", c_info['Googleマップ'], use_container_width=True)
        if pd.notna(c_info.get('HP')) and str(c_info.get('HP')).startswith("http"):
            col_btn2.link_button("🌐 公式HPの校舎ページ", c_info['HP'], use_container_width=True)

    st.markdown("---")
    st.markdown(f"### 👥 {selected_campus} スケジュール＆会議室 一元確認（特大合体ビュー）")
    
    if pd.notna(c_info.get('担当者に関する備考欄')) and str(c_info['担当者に関する備考欄']).strip() != "":
        # 🪄 一番もどかしかった備考欄も <br> で普通の行間に！
        bikou = str(c_info['担当者に関する備考欄']).replace('\n', '<br>')
        st.markdown(f"""
        <div style="background-color: #fff3cd; color: #664d03; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107;">
        🚗 <b>【担当者に関する備考・移動注意】</b><br><br>
        {bikou}
        </div>
        """, unsafe_allow_html=True)
