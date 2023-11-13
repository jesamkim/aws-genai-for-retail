
import os
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

def get_llm():
    
    model_kwargs =  { #Anthropic 모델
        "max_tokens_to_sample": 8000,
        "temperature": 0, 
        "top_k": 250, 
        "top_p": 0.5, 
        "stop_sequences": ["\n\nHuman:"] 
    }
    
    llm = Bedrock(
        credentials_profile_name=os.environ.get("AWS_PROFILE"), #AWS 자격 증명에 사용할 프로필 이름을 설정합니다(기본값이 아닌 경우)
        region_name=os.environ.get("AWS_DEFAULT_REGION"), #리전 이름을 설정합니다(기본값이 아닌 경우)
        endpoint_url=os.environ.get("BEDROCK_ENDPOINT_URL"), #엔드포인트 URL 설정(필요한 경우)
        #model_id="anthropic.claude-v2", #파운데이션 모델 설정하기
        model_id="anthropic.claude-instant-v1", #파운데이션 모델 설정하기
        model_kwargs=model_kwargs) #Claude의 속성을 구성합니다.
    
    return llm

pdf_path = "uploaded_file.pdf"

def get_example_file_bytes(): #사용자가 기존 생성된 예제를 다운로드할 수 있도록 파일 바이트를 제공합니다.
    with open("2022-Shareholder-Letter-ko.pdf", "rb") as file:
        file_bytes = file.read()
    
    return file_bytes


def save_file(file_bytes): #업로드한 파일을 디스크에 저장하여 나중에 요약합니다.   
    with open(pdf_path, "wb") as f: 
        f.write(file_bytes)
    
    return f"Saved {pdf_path}"


def get_docs():
    
    loader = PyPDFLoader(file_path=pdf_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=4000, chunk_overlap=100 
    )
    docs = text_splitter.split_documents(documents=documents)
    
    return docs

def get_summary(return_intermediate_steps=False):
    
    map_prompt_template = "{text}\n\n위의 내용을 Korean으로 bullet point 3개로 요약합니다:"
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
    
    combine_prompt_template = "{text}\n\n위의 내용을 Korean으로 간결하게 bullet point 5개로 요약합니다:"
    combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
    
    llm = get_llm()
    docs = get_docs()
    
    chain = load_summarize_chain(
        llm, chain_type="map_reduce", 
        map_prompt=map_prompt, 
        combine_prompt=combine_prompt, 
        return_intermediate_steps=return_intermediate_steps,
        verbose=True
    )
    
    if return_intermediate_steps:
        return chain({"input_documents": docs}, return_only_outputs=True) #반환 구조를 chain.run(docs)와 일관성 있게 만들기
    else:
        return chain.run(docs)
