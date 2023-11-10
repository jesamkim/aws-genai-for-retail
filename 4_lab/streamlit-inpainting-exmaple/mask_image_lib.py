# 필요한 라이브러리를 import 합니다.
import io
import os
import boto3
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
# Pillow 버전에 따라 ImageResampling을 다르게 가져올 수 있습니다.
try:
    from PIL import ImageResampling
except ImportError:
    # Pillow 버전이 낮아 ImageResampling을 직접 가져올 수 없는 경우
    # Image.Resampling으로 대체할 수 있습니다.
    from PIL.Image import Resampling as ImageResampling



# AWS 세션 설정
session = boto3.Session(
    profile_name=os.environ.get("BWB_PROFILE_NAME")
)

# Bedrock 클라이언트 생성
bedrock = session.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get("BWB_REGION_NAME"),
    endpoint_url=os.environ.get("BWB_ENDPOINT_URL")
)

# Stable Diffusion 모델 ID
bedrock_model_id = "stability.stable-diffusion-xl-v0"



# 응답 페이로드로부터 이미지를 추출하는 함수
def get_response_image_from_payload(response):
    payload = json.loads(response.get('body').read())
    images = payload.get('artifacts')
    image_data = base64.b64decode(images[0].get('base64'))
    return BytesIO(image_data)



# 이미지의 크기를 64의 배수로 조정하는 함수
def resize_image_to_model_compatible(image, base=64):
    # 이미지의 너비와 높이를 64의 배수로 조정
    new_width = ((image.width + base - 1) // base) * base
    new_height = ((image.height + base - 1) // base) * base
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_image




# 이미지 응답을 가져오는 함수
def get_image_response(prompt_content, image, mask_bytes, prompt_strenth, generation_step, seed):
    # 요청 바디 설정
    request_body = {
        "text_prompts": [{"text": prompt_content}],
        "cfg_scale": prompt_strenth,
        "seed": seed,
        "steps": generation_step,
        "mask_source": "MASK_IMAGE_BLACK"
    }

    # 원본 이미지 처리
    #image = Image.open(BytesIO(image_bytes))
    #image = Image.open('../data/1_product.png').convert("RGB")
    resized_image = resize_image_to_model_compatible(image)
    image_bytes_io = BytesIO()
    resized_image.save(image_bytes_io, format='PNG')
    encoded_image = base64.b64encode(image_bytes_io.getvalue()).decode('utf-8')
    request_body["init_image"] = encoded_image
    

    # 마스크 이미지 처리
    mask_image = Image.open(BytesIO(mask_bytes))
    resized_mask_image = resize_image_to_model_compatible(mask_image) # 수정된 부분
    mask_bytes_io = BytesIO()
    resized_mask_image.save(mask_bytes_io, format='PNG')
    encoded_mask_image = base64.b64encode(mask_bytes_io.getvalue()).decode('utf-8')
    request_body["mask_image"] = encoded_mask_image

    
    #print(request_body)
    
    # 모델 호출
    response = bedrock.invoke_model(body=json.dumps(request_body), modelId=bedrock_model_id)
    
    # 생성된 이미지 반환
    output = get_response_image_from_payload(response)
    return output

