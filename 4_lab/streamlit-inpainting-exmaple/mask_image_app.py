import streamlit as st
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas
import io
import json
import mask_image_lib as glib

# 함수 정의는 모든 호출 뒤에 위치해야 합니다.
def convert_mask_data_to_image_bytes(mask_data, image_shape, stroke_width=50):
    # JSON 데이터에서 캔버스 객체 추출
    mask_data = mask_data.get('objects', []) if isinstance(mask_data, dict) else []
    # RGB 모드로 흰색 배경을 가진 마스크 이미지를 생성합니다.
    mask_image = Image.new("RGB", image_shape, (255, 255, 255))
    draw = ImageDraw.Draw(mask_image)

    for obj in mask_data:
        if obj.get('type') == 'path':
            path_data = obj.get('path')
            # 경로 데이터를 (x, y) 좌표 리스트로 변환
            path_tuples = [(float(p[1]), float(p[2])) for p in path_data if p[0] in ('L', 'M')]
            # 선 굵기에 따라 검은색 선을 그립니다.
            for i in range(len(path_tuples) - 1):
                draw.line([path_tuples[i], path_tuples[i + 1]], fill=(0, 0, 0), width=stroke_width)

    # 바이트로 변환합니다.
    mask_bytes = io.BytesIO()
    mask_image.save(mask_bytes, format='PNG')
    return mask_bytes.getvalue()



# Streamlit 페이지 설정
st.set_page_config(layout="wide", page_title="Bedrock-SDXL_v0.8-Inpainting-DEMO")

# 제목 설정
st.title("Bedrock-SDXL-Inpainting-DEMO")

# 세 개의 컬럼 생성
col1, col2, col3 = st.columns([2, 1, 2])  # col2는 마스크 표시용으로 더 작게 설정

# 이미지 로드
image = Image.open('../data/1_product.png').convert("RGB")

# 첫 번째 컬럼 (프롬프트 입력 및 캔버스)
with col1:
    st.subheader("이미지 프롬프트")
    prompt_text = st.text_area("프롬프트를 입력하세요:", height=100)
    
    # 캔버스 위젯 설정
    #stroke_width = st.slider("선 굵기:", 1, 50, 20)
    stroke_width = 50
    stroke_color = "#000000"  # 선 색 설정
    bg_color = "#ffffff"    # 배경색 설정
    drawing_mode = st.checkbox("그리기 모드", True)
    
    # 캔버스 위젯 생성
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=image,
        update_streamlit=True,
        height=657,
        width=512,
        drawing_mode="freedraw" if drawing_mode else "transform",
        key="canvas",
    )

# 두 번째 컬럼 (마스크 이미지 표시)
with col2:
    st.subheader("마스크 이미지")
    if canvas_result.json_data is not None:
        # 사용자가 설정한 선 굵기를 전달합니다.
        mask_bytes = convert_mask_data_to_image_bytes(canvas_result.json_data, image.size, stroke_width)
        st.image(mask_bytes, caption='마스크 이미지', use_column_width=True)
        
    prompt_strenth = st.slider("prompt_strenth", min_value=0.0, max_value=30.0, value=10.0, step=0.1, format='%.1f')
    generation_step = st.slider("Generation step", min_value=10, max_value=150, value=50, step=1)
    seed = st.slider("Seed", min_value=0, max_value=300, value=10, step=1)



# 세 번째 컬럼 (결과 표시)
with col3:
    st.subheader("결과")
    process_button = st.button("생성하기")
    
    if process_button:
        if not prompt_text or not canvas_result.json_data.get('objects'):
            st.warning("프롬프트와 마스크를 지정해주세요.")
        else:
            image_array = canvas_result.image_data
            if image_array is not None:
                image_pil = Image.fromarray(image_array.astype('uint8'), 'RGBA')
                image_bytes = io.BytesIO()
                image_pil.save(image_bytes, format='PNG')
                
                mask_bytes = convert_mask_data_to_image_bytes(canvas_result.json_data, image_pil.size)
                
                with st.spinner("이미지를 생성하는 중..."):
                    generated_image = glib.get_image_response(prompt_text, image, mask_bytes, prompt_strenth, generation_step, seed)
                
                st.image(generated_image, caption='생성된 이미지', use_column_width=True)
            else:
                st.error("이미지 데이터가 없습니다.")
