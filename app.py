import streamlit as st
import replicate
import os

# 페이지 설정
st.set_page_config(page_title="슈트 에이전시 AI 피팅", layout="wide")

# 제목
st.title("🕴️ 슈트 에이전시 가상 피팅 시스템")
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.header("설정 (Settings)")
    api_key = st.text_input("Replicate API Key를 입력하세요", type="password")
    st.info("비용은 1장당 약 40~50원입니다.")
    category = st.selectbox("피팅 부위", ["upper_body (상의)", "lower_body (하의)", "dresses (원피스/코트)"])

# 메인 화면
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 고객 사진")
    human_img = st.file_uploader("고객 전신 사진을 올려주세요", type=['png', 'jpg', 'jpeg'], key="human")
    if human_img:
        st.image(human_img, caption="고객 사진", use_container_width=True)

with col2:
    st.subheader("2. 정장 사진")
    garm_img = st.file_uploader("입힐 정장(누끼) 사진을 올려주세요", type=['png', 'jpg', 'jpeg'], key="garm")
    if garm_img:
        st.image(garm_img, caption="선택한 정장", use_container_width=True)

# 실행 버튼
if st.button("✨ 가상 피팅 시작 (Generate)"):
    if not api_key:
        st.error("왼쪽 사이드바에 API Key를 넣어주세요!")
    elif not human_img or not garm_img:
        st.error("사진 2장을 모두 올려주세요!")
    else:
        try:
            with st.spinner("AI가 옷을 입히는 중입니다... (약 20초 소요)"):
                os.environ["REPLICATE_API_TOKEN"] = api_key
                output = replicate.run(
                    "yisol/idm-vton:c871bb9b04660742b1153de56531647758ac45533797bb15620943147326b974",
                    input={
                        "human_img": human_img,
                        "garm_img": garm_img,
                        "garment_des": "suit",
                        "category": category.split(" ")[0],
                        "crop": False,
                        "seed": 42,
                        "steps": 30
                    }
                )
                st.success("완료되었습니다!")
                st.image(output, caption="피팅 결과", use_container_width=True)
        except Exception as e:
            st.error(f"에러가 발생했습니다: {str(e)}")
