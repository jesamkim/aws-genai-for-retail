import os
from langchain.llms.bedrock import Bedrock
#from langchain import PromptTemplate
from langchain.prompts import PromptTemplate

def get_llm():
    
    model_kwargs = { #Claude
        "max_tokens_to_sample": 1024,
        "temperature": 0,
        "top_k": 250, 
        "top_p": 1,
        "stop_sequences":["\n\nHuman:"]
    }
    
    
    llm = Bedrock(
        credentials_profile_name=os.environ.get("AWS_PROFILE"), #AWS 자격 증명에 사용할 프로필 이름을 설정합니다(기본값이 아닌 경우)
        region_name=os.environ.get("AWS_DEFAULT_REGION"), #리전 이름을 설정합니다(기본값이 아닌 경우)
        endpoint_url=os.environ.get("BEDROCK_ENDPOINT_URL"), #엔드포인트 URL 설정(필요한 경우)
        model_id="anthropic.claude-v2", #파운데이션 모델 설정하기
        #model_id="anthropic.claude-instant-v1", #파운데이션 모델 설정하기
        model_kwargs=model_kwargs) #Claude의 속성을 구성합니다.
    
    return llm
    
def get_prompt(keyword, productType):
    template = """
    \n\nHuman: 
    <keywords> 뚜껑이 달린 퇴비화 가능한 컵, 아이스 커피 컵, 빨대없는 뚜껑, \
    뚜껑이 달린 생분해성 컵, 생분해 성 컵, 커피, 스무디, 음료, 이동 중, 일회용 컵, 친환경, 식물 기반</keywords>
    <command> 위에 나열된 keywords를 사용하여 일회용 컵에 대한 설명을 작성하세요.</command>
    \n\nAssistant: 편리함과 친환경이 드디어 만났습니다! \
    뚜껑이 있는 일회용 스무디 컵은 100% 식물로 만들어집니다. \
    산업 퇴비 시설로 가져가세요.이 퇴비화 가능한 차가운 컵은 모든 종류의 음료에 적합합니다.\
    재사용 가능한 빨대는 훌륭하지만 휴대하기에는 번거롭습니다. \
    스냅 오픈 뚜껑이 있는 빨대 없는 컵은 적당한 크기의 빨대 구멍이 있습니다. \
    새지 않는 텀블러는 아침에 스무디를 마실 때 사용하면 지구에도 좋을지 모르지만 \
    세척하는 데 시간이 더 걸립니다. 저희도 이해합니다, \
    저희도 여기 지구에 살고 있으니까요.\
    대신에 컴포저블 컵을 사용해보시는 건 어떨까요? \
    회사, 학교, 운전할 때 식물성 컵을 가지고 다니세요.
    
    \n\nHuman:
    <keywords> ${keyword}</keywords>
    <command> 위에 나열된 ${keyword}를 사용하여 ${productType}에 대한 설명을 작성하세요 $는 빼고 작성하세요.</command>
    \n\nAssistant:
    """
    prompt_template = PromptTemplate.from_template(template)
    prompt = prompt_template.format(keyword=keyword, productType=productType)
    return prompt

def get_text_response(keyword, productType):
    llm = get_llm()
    prompt = get_prompt(keyword, productType)
    return llm.predict(prompt)
    
    
#import quicklist_lib_kr as glib
import streamlit as st

st.set_page_config(page_title="Amazon.com 셀러를 위한 Product Listing Tool")
st.title("Amazon.com 셀러를 위한 Product Listing Tool")

keyword = st.text_input("키워드")
productType = st.text_input("프로덕트 타입")
go_button = st.button("Go", type="primary")

if go_button:

    with st.spinner("Working"):
        response_content = get_text_response(keyword=keyword, productType=productType)
        st.write(response_content)
