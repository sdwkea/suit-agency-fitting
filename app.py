import streamlit as st
import replicate
import os

# 웹페이지 기본 설정
st.set_page_config(page_title="슈트에이전시 가상 피팅", layout="wide")

# 화면 상단 제목
st.title("🕴️ 슈트에이전시(Suit Agency) 가상 피팅 시스템")
st.markdown("고객님의 사진과 입히고 싶은 정장 사진을 업로드해주세요.")
st.markdown("---")

# --- 사이드바 (왼쪽 메뉴) 설정 ---
with st.sidebar:
    st.header("⚙️ 설정 (Settings)")
    
    # 1. API 키 입력창
    api_key = st.text_input("Replicate API Key를 입력하세요", type="password", help="r8_로 시작하는 키를 입력하세요.")
    if not api_key:
        st.warning("⚠️ API Key를 입력해야 작동합니다.")
        
    st.markdown("---")
    st.info("💡 **비용 안내:** 사진 생성 1회당 약 40~60원의 비용이 발생합니다.")

# --- 메인 화면 구성 ---
col1, col2 = st.columns(2)

# 왼쪽 컬럼: 고객 사진 업로드
with col1:
    st.subheader("📷 1. 고객 전신 사진 (Human)")
    human_img = st.file_uploader("고객의 정면 전신 사진을 올려주세요.", type=['png', 'jpg', 'jpeg'], key="human")
    if human_img:
        st.image(human_img, caption="업로드된 고객 사진", use_container_width=True)

# 오른쪽 컬럼: 정장 사진 업로드
with col2:
    st.subheader("🧥 2. 정장 사진 (Garment)")
    st.markdown("옷걸이에 걸린 옷이나 마네킹 컷 권장 (누끼 사진 베스트)")
    garm_img = st.file_uploader("입히고 싶은 정장 사진을 올려주세요.", type=['png', 'jpg', 'jpeg'], key="garm")
    if garm_img:
        st.image(garm_img, caption="선택한 정장", use_container_width=True)

st.markdown("---")

# --- 실행 버튼 및 결과 처리 ---
if st.button("✨ 가상 피팅 시작하기 (Generate)", type="primary"):
    if not api_key:
        st.error("❌ 왼쪽 사이드바에 'API Key'를 먼저 입력해주세요!")
    elif not human_img:
        st.error("❌ 고객 사진을 업로드해주세요!")
    elif not garm_img:
        st.error("❌ 입힐 정장 사진을 업로드해주세요!")
    else:
        try:
            with st.spinner("⏳ AI 재단사가 정장을 입혀보는 중입니다... (약 20~30초 소요)"):
                # 1. 환경변수에 API 키 설정
                os.environ["REPLICATE_API_TOKEN"] = api_key
                
                # 2. Replicate AI 모델 호출 (주소 수정됨: cuuupid/idm-vton)
                output = replicate.run(
                    "cuuupid/idm-vton:c871bb9b04660742b1153de56531647758ac45533797bb15620943147326b974",
                    input={
                        "human_img": human_img,
                        "garm_img": garm_img,
                        "garment_des": "suit", 
                        "category": "upper_body",
                        "crop": False,
                        "seed": 42, 
                        "steps": 30
                    }
                )
                
                # 3. 결과 이미지 출력
                st.success("🎉 피팅이 완료되었습니다!")
                st.image(output, caption="가상 피팅 결과물", use_container_width=True)
                
        except Exception as e:
            st.error(f"⚠️ 에러가 발생했습니다. API Key를 확인해주세요.\n에러 내용: {str(e)}")
