# pages/campus.py
import streamlit as st
import pandas as pd
import datetime
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# =========================================================================
# ⚙️ 1. 初期設定 & Google API 認証ロジック
# =========================================================================
# GoogleカレンダーAPIにアクセスするための設定（後ほどst.secretsに鍵を格納します）
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    try:
        # StreamlitのSecretsから認証情報を読み込む
        creds_dict = st.secrets["google_credentials"]
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        # 認証情報が未設定の場合はNoneを返し、画面上で警告を出す
        return None

service = get_calendar_service()

# =========================================================================
# 📊 2. スプレッドシートからのデータ読み込み
# =========================================================================
# 💡 ご自身のスプレッドシートのURLまたはIDに書き換えてください
# ※ 末尾を「/export?format=csv&gid=シートID」にすることで直接CSVとして読み込めます
# 1. 校舎一覧シートのURL（gid=0 は校舎一覧タブのシートIDに変更）
CAMPUS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1M9PwHaNywxZEd1LyKj76lMW82R05pDKUArc6Ni4LaUc/export?format=csv&gid=628921947"

# 2. 担当者マスタシートのURL（gid=11111 は担当者マスタタブのシートIDに変更）
STAFF_SHEET_URL = "https://docs.google.com/spreadsheets/d/1M9PwHaNywxZEd1LyKj76lMW82R05pDKUArc6Ni4LaUc/export?format=csv&gid=773023051"

@st.cache_data(ttl=60) # 1分間キャッシュ（現場のスプシ更新をすぐ反映するため）
def load_data():
    df_campus = pd.read_csv(CAMPUS_SHEET_URL)
    df_staff = pd.read_csv(STAFF_SHEET_URL)
    return df_campus, df_staff

try:
    df_campus, df_staff = load_data()
except Exception as e:
    st.error(f"スプレッドシートの読み込みに失敗しました。URLまたは共有設定を確認してください: {e}")
    st.stop()

# =========================================================================
# 📝 3. 担当者名のお掃除 & 自動パース（解析）ロジック
# =========================================================================
def clean_name(name_str):
    """末尾の『さん』『様』や不要なスペースを自動で削るお掃除関数"""
    if pd.isna(name_str):
        return ""
    name_str = str(name_str).strip()
    name_str = re.sub(r'(さん|様|氏|\s)+$', '', name_str)
    return name_str.strip()

def parse_staff_from_notes(notes, df_staff):
    """
    I列の備考欄から1行目を取り出し、優先度順に名前のリストを作成する。
    『佐藤亮（軽部>森内）』のような、カッコ内に入れ子で区切りがあるパターンや、
    『佐藤亮』➔『佐藤亮太』のような名字+名前の1文字欠けの部分一致にも完全対応。
    """
    if pd.isna(notes) or not str(notes).strip():
        return []
    
    # 1. 1行目（改行の手前まで）を抽出
    first_line = str(notes).split('\n')[0].strip()
    
    # 2. カッコの処理（中に区切り文字がある場合はカッコだけ外し、ただの補足ならカッコごと中身を消す）
    # 例：「佐藤亮（軽部>森内）」➔「佐藤亮 軽部>森内」に変換
    if any(sep in first_line for sep in ['＞', '>', '・', '＆', '&', '、', ',']):
        # カッコを半角スペースに置き換えて、後で区切り文字と一緒に分割できるようにする
        cleaned_line = re.sub(r'[\(（\)）]', ' ', first_line)
    else:
        # 単なる補足カッコ（例：佐藤（優））の場合はカッコと中身を消去
        cleaned_line = re.sub(r'[\(（].*?[\)）]', '', first_line)
    
    # 3. スペースや各種区切り文字で分割
    raw_names = re.split(r'＞|>|・|＆|&|、|,|\s+', cleaned_line)
    cleaned_input_names = [clean_name(name) for name in raw_names if name.strip()]
    
    # 4. マスタとの高度なあいまいマッチング
    df_staff_sorted = df_staff.copy()
    df_staff_sorted['clean_master_name'] = df_staff_sorted['担当者名'].apply(clean_name)
    df_staff_sorted['name_len'] = df_staff_sorted['clean_master_name'].str.len()
    df_staff_sorted = df_staff_sorted.sort_values(by='name_len', ascending=False)
    
    final_staff_names = []
    for input_name in cleaned_input_names:
        matched = False
        for _, row in df_staff_sorted.iterrows():
            master_name = row['clean_master_name']
            
            # ① 完全一致、または一方がもう一方に完全に含まれる場合
            # ②「佐藤亮」と「佐藤亮太」のように、入力がマスタの前方の一部に一致する場合（先頭2文字以上一致を条件にして誤判定を防ぐ）
            if (input_name in master_name) or (master_name in input_name) or \
               (len(input_name) >= 2 and master_name.startswith(input_name)) or \
               (len(master_name) >= 2 and input_name.startswith(master_name)):
                
                final_staff_names.append(row['担当者名'])
                matched = True
                break
        
        if not matched:
            final_staff_names.append(input_name)
            
    return final_staff_names
# =========================================================================
# 📱 4. 画面レイアウト構築
# =========================================================================
st.title("🏢 校舎詳細・面談スケジュール登録")
st.caption("校舎ごとのカレンダー空き状況を確認し、その場で面談予約と会議室確保を行えます。")
st.markdown("---")

# 🏛️ 校舎選択プルダウン（スプシからユニークな校舎名を取得）
campus_options = df_campus['校舎名'].dropna().unique().tolist()
selected_campus = st.selectbox("📍 表示する校舎を選択してください", campus_options)

# 選択された校舎のデータを抽出
campus_data = df_campus[df_campus['校舎名'] == selected_campus].iloc[0]

# --- 💡 ここから『左側カレンダー・右側予約フォーム』の2カラム構成 ---
col_left, col_right = st.columns([1.3, 1.0])

with col_left:
    st.subheader(f"📅 {selected_campus}校 週間スケジュール")
    
    # 1. 担当者情報の自動回収と色割り当て
    staff_names = parse_staff_from_notes(campus_data.get('担当者に関する備考欄', '備考'), df_staff)
    
    # 優先度ごとの固定カラーコード（1番目:赤、2番目:青、3番目:緑）
    priority_colors = ["%23B1365F", "%232952A3", "%230D7813"]
    
# =========================================================================
    # 🎨 カレンダーURL合成処理（メールアドレス形式のみを許可して400エラーを防ぐ）
    # =========================================================================
    calendar_urls = []
    found_staff_info = [] # 予約フォームの選択肢用
    
    # 簡易メールアドレス判定用の正規表現
    def is_valid_email(email_str):
        if not email_str or pd.isna(email_str):
            return False
        return "@" in str(email_str)

    # 1. 担当者カレンダーIDの処理
    for idx, name in enumerate(staff_names):
        matched_rows = df_staff[df_staff['担当者名'].apply(clean_name) == name]
        
        if not matched_rows.empty:
            staff_id = str(matched_rows.iloc[0]['カレンダーID']).strip()
            # 💡 正しいメールアドレス形式の場合のみGoogleに送るURLに含める
            if is_valid_email(staff_id):
                color = priority_colors[idx] if idx < len(priority_colors) else "%235B5B5B"
                calendar_urls.append(f"&src={staff_id}&color={color}")
                found_staff_info.append({"name": name, "id": staff_id})
            else:
                st.warning(f"⚠️ 担当者「{name}」さんのカレンダーIDが正しいメールアドレス形式ではありません: {staff_id}")
        else:
            # 1行目に注意事項（バッファなど）が紛れ込んでマスタにない場合は、警告を出さずに無視するか、優しく警告します
            if name and not any(keyword in name for keyword in ["バッファ", "移動", "注意", "時間"]):
                st.warning(f"⚠️ 担当者マスタに「{name}」さんが登録されていません。")

    # 2. 会議室ID（K列・L列）の処理
    room_a_id = campus_data.get('会議室①') # 実際の列名に合わせて適宜修正してください
    room_b_id = campus_data.get('会議室②') # 実際の列名に合わせて適宜修正してください
    
    found_rooms = []
    if pd.notna(room_a_id) and is_valid_email(room_a_id):
        room_id_str = str(room_a_id).strip()
        calendar_urls.append(f"&src={room_id_str}&color=%23979797")
        found_rooms.append({"name": "会議室A", "id": room_id_str})
        
    if pd.notna(room_b_id) and is_valid_email(room_b_id):
        room_id_str = str(room_b_id).strip()
        calendar_urls.append(f"&src={room_id_str}&color=%23979797")
        found_rooms.append({"name": "会議室B", "id": room_id_str})

    # 3. Googleカレンダー埋め込みURLの合成
    base_embed_url = "https://calendar.google.com/calendar/embed?mode=DAY&wkst=1&hl=ja&ctz=Asia/Tokyo"
    
    # 💡 有効なカレンダーIDが1つもない場合は、ダミーとして表示可能な公式日本の祝日などを表示してエラーを回避
    if not calendar_urls:
        final_calendar_url = base_embed_url + "&src=ja.japanese%23holiday%40group.v.calendar.google.com&color=%232952A3"
        st.info("ℹ️ 現在、表示できる有効な担当者・会議室のカレンダーIDが登録されていません。")
    else:
        final_calendar_url = base_embed_url + "".join(calendar_urls)

    # 画面に重ね合わせカレンダーを表示
    st.components.v1.iframe(final_calendar_url, height=700, scrolling=True)
    
    # 🚨 スプシのI列の備考欄テキスト（バッファの注意書きなど）をそのまま下に綺麗に表示
    st.markdown("---")
    st.markdown("#### 📌 校舎・担当者に関する注意事項")
    notes_text = campus_data.get('担当者に関する備考欄', '備考')
    if pd.notna(notes_text):
        st.info(notes_text)

with col_right:
    st.subheader("📝 スケジュール登録フォーム")
    
    if service is None:
        st.warning("🔑 Google APIの認証情報が設定されていません。画面の閲覧は可能ですが、このフォームからの自動登録テストはスキップされます。")
    
    # 1. 担当者の選択（その校舎にいる人だけが自動抽出される）
    if found_staff_info:
        staff_options = [s["name"] for s in found_staff_info]
        selected_staff_name = st.selectbox("👤 担当者を選択", staff_options)
        selected_staff_id = next(s["id"] for s in found_staff_info if s["name"] == selected_staff_name)
    else:
        st.error("この校舎には有効な担当者が割り当てられていません。")
        selected_staff_id = None

    # 2. 会議室の選択（K列・L列にIDが入っている部屋だけが表示される）
    if found_rooms:
        room_options = ["部屋を指定しない"] + [r["name"] for r in found_rooms]
        selected_room_name = st.selectbox("🚪 抑える会議室を選択", room_options)
        selected_room_id = next((r["id"] for r in found_rooms if r["name"] == selected_room_name), None)
    else:
        st.caption("🔒 この校舎に登録されている会議室はありません（空欄のまま進みます）。")
        selected_room_id = None

    # 3. 日時と顧客名の入力
    appointment_date = st.date_input("📅 面谈日を選択", datetime.date.today())
    
    col_t1, col_t2 = st.columns(2)
    time_options = [f"{h:02d}:{m:02d}" for h in range(9, 22) for m in [0, 30]]
    with col_t1:
        start_time_str = st.selectbox("⏰ 開始時間", time_options, index=10) # デフォルト14:00
    with col_t2:
        end_time_str = st.selectbox("⏰ 終了時間", time_options, index=13) # デフォルト15:30
        
    customer_name = st.text_input("👤 顧客名（例：山田太郎）", placeholder="山田太郎")

    # 4. タイトルの自動生成プレビュー
    title_text = f"【受験相談＠{selected_campus}校】{clean_name(customer_name)}様"
    st.markdown(f"**生成されるタイトル:** `{title_text}`")
    
    # 5. 登録実行ボタン
    if st.button("📅 この内容でカレンダー・会議室を予約する", use_container_width=True, type="primary"):
        if not customer_name:
            st.error("❌ 顧客名を入力してください。")
        elif not selected_staff_id:
            st.error("❌ 担当者が選択されていないため予約できません。")
        else:
            # ISO形式の開始・終了日時文字列を作成
            start_datetime = f"{appointment_date}T{start_time_str}:00"
            end_datetime = f"{appointment_date}T{end_time_str}:00"
            
            # APIに送信する予定オブジェクトの作成（主催者のカレンダーに作り、担当者と会議室を招待する）
            event_body = {
                'summary': title_text,
                'start': {'dateTime': start_datetime, 'timeZone': 'Asia/Tokyo'},
                'end': {'dateTime': end_datetime, 'timeZone': 'Asia/Tokyo'},
                'attendees': [
                    {'email': selected_staff_id} # 担当者をゲスト招待
                ]
            }
            
            # 会議室も選択されていれば招待枠に追加
            if selected_room_id:
                event_body['attendees'].append({'email': selected_room_id})
            
            # Googleカレンダーへ送信実行
            if service:
                try:
                    event = service.events().insert(
                        calendarId='primary', # 主催者（現在ログイン中、またはAPIキーを持つ人）のメインカレンダー
                        body=event_body,
                        sendUpdates='all' # 招待相手に通知メールを飛ばす設定
                    ).execute()
                    st.success(f"🎉 予約が完了しました！\n担当者と会議室にカレンダー招待を送信しました。")
                except Exception as e:
                    st.error(f"Googleカレンダーへの登録中にエラーが発生しました: {e}")
            else:
                st.info("👍 (デモ実行) 認証キーが設定されると、上記の内容で担当者と会議室へ同時に招待状が送信されます。")
