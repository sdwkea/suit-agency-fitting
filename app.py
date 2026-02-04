import streamlit as st
import replicate
import os
from PIL import Image, ImageOps
import io

# 페이지 설정
st.set_page_config(page_title="슈트 에이전시 AI 피팅", layout="wide")

# 제목
st.title("🕴️ 슈트 에이전시 가상 피팅 시스템")
st.markdown("---")

# --- 기능 함수: 사진 회전 문제 해결 ---
def load_image(image_file):
    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img) # 회전 정보 교정
    return img

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("설정 (Settings)")
    api_key = st.text_input("Replicate API Key를 입력하세요", type="password", help="r8_로 시작하는 키 전체를 입력하세요")
    if not api_key:
        st.warning("⚠️ API Key를 입력해야 작동합니다.")
    
    st.markdown("---")
    # 메뉴 선택
    category_label = st.radio(
        "어떤 옷을 입히시겠습니까?",
        ["수트 세트 (위아래 한벌)", "재킷/상의만 (Upper)", "바지/하의만 (Lower)"]
    )
    
    # AI 설정값 변환
    if "수트" in category_label:
        category = "dresses" # 위아래 한벌은 dresses로 설정해야 함
    elif "상의" in category_label:
        category = "upper_body"
    else:
        category = "lower_body"

# --- 메인 화면 구성 ---
col1, col2 = st.columns(2)
human_bytes = None
garm_bytes = None

with col1:
    st.subheader("1. 고객 사진")
    human_file = st.file_uploader("고객 전신 사진", type=['png', 'jpg', 'jpeg'], key="human")
    if human_file:
        human_img = load_image(human_file)
        st.image(human_img, caption="고객 사진", use_container_width=True)
        buf = io.BytesIO()
        human_img.save(buf, format="PNG")
        human_bytes = buf.getvalue()

with col2:
    st.subheader("2. 정장 사진")
    garm_file = st.file_uploader("입힐 수트(누끼/마네킹) 사진", type=['png', 'jpg', 'jpeg'], key="garm")
    if garm_file:
        garm_img = load_image(garm_file)
        st.image(garm_img, caption="선택한 수트", use_container_width=True)
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
            with st.spinner("AI가 수트를 입히는 중입니다... (약 30초 소요)"):
                os.environ["REPLICATE_API_TOKEN"] = api_key
                
                output = replicate.run(
                    "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4",
                    input={
                        "human_img": io.BytesIO(human_bytes),
                        "garm_img": io.BytesIO(garm_bytes),
                        "garment_des": "suit",
                        "category": category, 
                        "crop": False,
                        "seed": 42,
                        "steps": 40, # [수정됨] 50에서 허용 최대치인 40으로 수정
                        "force_dc": False,
                        "mask_only": False
                    }
                )
                
                st.success("완료되었습니다!")
                if isinstance(output, list):
                    st.image(str(output[0]), caption="피팅 결과", use_container_width=True)
                else:
                    st.image(str(output), caption="피팅 결과", use_container_width=True)
                    
        except Exception as e:
            st.error(f"에러가 발생했습니다: {str(e)}")
