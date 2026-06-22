# pages/onboarding.py
import streamlit as st

# オンボーディング画面のメイン表示
st.title("📖 オンボーディング・基礎研修資料")

st.markdown("---")
st.markdown("### 🔰 研修コンテンツ（ここに自由に追記・編集してください）")

# サンプルコンテンツ
st.info("武田塾の基本理念や、インサイドセールスとしての心構えをここで学びます。")

with st.expander("1. 武田塾の4つの指導方針"):
    st.write("- 参考書による自学自習の徹底")
    st.write("- 完璧になるまで先に進まない")
    st.write("- 忘れることを前提とした進捗管理")
    st.write("- 一冊を完璧に、の勉強法")