
import sys
import os

import boto3
from langchain.retrievers import AmazonKendraRetriever
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock

def build_chain():

  session = boto3.Session(
      profile_name=os.environ.get("AWS_PROFILE")
  ) 
  boto3_bedrock = session.client(
    service_name='bedrock-runtime', 
    region_name=os.environ.get("AWS_DEFAULT_REGION"),
    endpoint_url=os.environ.get("BEDROCK_ENDPOINT_URL")
  ) 
    
  region = os.environ["AWS_REGION"]
  kendra_index_id = "{KENDRA_INDEX}" # Example: 65702b79-XXXX-XXXX-XXXX-9702f17fb994

  llm = Bedrock(model_id="anthropic.claude-v2", client=boto3_bedrock, model_kwargs={'max_tokens_to_sample':1000})
  
  retriever = AmazonKendraRetriever(
    index_id=kendra_index_id,
    region_name=os.environ.get("AWS_DEFAULT_REGION", None),
    top_k=3,
    attribute_filter = {
        "EqualsTo": {      
            "Key": "_language_code",
            "Value": {
                "StringValue": "ko"
            }
        }
    }
  )
  # prompt_template = """Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
  prompt_template = """Human: Use the following pieces of context to provide a concise answer to the question at the end. If the answer is not in the context, just say "시스템에 관련 내용을 찾을 수 없습니다.", don't try to make up an answer.

  {context}

  Question: {question}
  Assistant:"""

  PROMPT = PromptTemplate(
      template=prompt_template, input_variables=["context", "question"]
  )


  qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
  )

  return qa

def run_chain(chain, prompt: str):
  return chain({"query": prompt})
