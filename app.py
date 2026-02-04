import streamlit as st
import replicate
import os
from PIL import Image, ImageOps
import io

# 페이지 기본 설정
st.set_page_config(page_title="슈트 에이전시 AI 피팅", layout="wide")

# 제목
st.title("🕴️ 슈트 에이전시 가상 피팅 시스템")
st.markdown("---")

# --- 기능 함수: 사진 회전 문제 해결 ---
def load_image(image_file):
    img = Image.open(image_file)
    # 휴대폰 사진의 회전 정보(EXIF)를 확인해서 똑바로 세움
    img = ImageOps.exif_transpose(img)
    return img

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("설정 (Settings)")
    api_key = st.text_input("Replicate API Key를 입력하세요", type="password", help="r8_로 시작하는 키 전체를 입력하세요")
    if not api_key:
        st.warning("⚠️ API Key를 입력해야 작동합니다.")
    st.info("비용은 1장당 약 40~50원입니다.")
    category = st.selectbox("피팅 부위", ["upper_body (상의)", "lower_body (하의)", "dresses (원피스/코트)"])

# --- 메인 화면 구성 ---
col1, col2 = st.columns(2)

# 변수 초기화
human_bytes = None
garm_bytes = None

with col1:
    st.subheader("1. 고객 사진")
    human_file = st.file_uploader("고객 전신 사진을 올려주세요", type=['png', 'jpg', 'jpeg'], key="human")
    if human_file:
        # 사진을 읽어서 강제로 똑바로 세움
        human_img = load_image(human_file)
        st.image(human_img, caption="고객 사진 (자동 회전됨)", use_container_width=True)
        
        # AI에게 보낼 형태로 변환
        buf = io.BytesIO()
        human_img.save(buf, format="PNG")
        human_bytes = buf.getvalue()

with col2:
    st.subheader("2. 정장 사진")
    garm_file = st.file_uploader("입힐 정장(누끼) 사진을 올려주세요", type=['png', 'jpg', 'jpeg'], key="garm")
    if garm_file:
        # 사진을 읽어서 강제로 똑바로 세움
        garm_img = load_image(garm_file)
        st.image(garm_img, caption="선택한 정장 (자동 회전됨)", use_container_width=True)
        
        # AI에게 보낼 형태로 변환
        buf = io.BytesIO()
        garm_img.save(buf, format="PNG")
        garm_bytes = buf.getvalue()

# --- 실행 버튼 ---
if st.button("✨ 가상 피팅 시작 (Generate)"):
    if not api_key:
        st.error("왼쪽 사이드바에 API Key를 넣어주세요!")
    elif not human_bytes or not garm_bytes:
        st.error("사진 2장을 모두 올려주세요!")
    else:
        try:
            with st.spinner("AI가 옷을 입히는 중입니다... (약 20초 소요)"):
                os.environ["REPLICATE_API_TOKEN"] = api_key
                
                # AI 모델 실행
                output = replicate.run(
                    "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4",
                    input={
                        "human_img": io.BytesIO(human_bytes),
                        "garm_img": io.BytesIO(garm_bytes),
                        "garment_des": "suit",
                        "category": category.split(" ")[0],
                        "crop": False,
                        "seed": 42,
                        "steps": 30,
                        "force_dc": False,
                        "mask_only": False
                    }
                )
                
                st.success("완료되었습니다!")
                
                # 결과 출력
                if isinstance(output, list):
                    st.image(str(output[0]), caption="피팅 결과", use_container_width=True)
                else:
                    st.image(str(output), caption="피팅 결과", use_container_width=True)
                    
        except Exception as e:
            st.error(f"에러가 발생했습니다: {str(e)}")
