import requests
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from prompts_data import diseaseGenPrompt
from os import getenv
from dotenv import load_dotenv
import json

load_dotenv()
llm=HuggingFaceEndpoint(repo_id="meta-llama/Meta-Llama-3-8B-Instruct",task="chat-completion",huggingfacehub_api_token=getenv("HUGGINGFACE_API_TOKEN"),max_new_tokens=1000)
model=ChatHuggingFace(llm=llm)

url = "http://localhost:11434/api/generate"

disease_dict={}
def diseaseSelecter():
    prompt=diseaseGenPrompt(disease_dict)

    response=model.invoke(prompt)
    response=json.loads(response.content)
    response=response["disease"]

    if response in disease_dict:
        disease_dict[response]+=1
    else:
        disease_dict[response]=1


    return response

print(diseaseSelecter())

def scenarioGen(disease):
    
    pass

# payload_gemma = {
#     "model": "gemma4",
#     "prompt": "Patient has chest pain and sweating. Ask ONE next relevant question.",
#     "stream": False
# }

# response = requests.post(url, json=payload)

# print(response.json()["response"])
