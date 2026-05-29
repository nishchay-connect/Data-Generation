import requests
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from prompts_data import diseaseGenPrompt,scenarioGenPrompt,docRolePrompt,patientRolePrompt
from os import getenv
from dotenv import load_dotenv
import json
from google import genai
import time
# from google import 
load_dotenv()
llm=HuggingFaceEndpoint(repo_id="meta-llama/Meta-Llama-3-8B-Instruct",task="chat-completion",huggingfacehub_api_token=getenv("HUGGINGFACE_API_TOKEN"),max_new_tokens=1000)
model=ChatHuggingFace(llm=llm)

client=genai.Client(api_key=f"{getenv("GEMINI_API_KEY")}")


url = "http://localhost:11434/api/generate"

disease_dict={}
features={
  "sex": {
    "male": 0,
    "female": 0
  },

  "age_group": {
    "child": 0,
    "teen": 0,
    "young_adult": 0,
    "adult": 0,
    "elderly": 0
  },

  "severity": {
    "mild": 0,
    "moderate": 0,
    "severe": 0
  }
}

def featuresUpdate(response):
    sex=response["sex"]
    age_group=response["age_group"]
    severity=response["severity"]


    features["sex"][sex]+=1
    features["age_group"][age_group]+=1
    features["severity"][severity]+=1

class jsonFunc():

    def appendDis():
        with open("disease.json","w") as f:
            json.dump(disease_dict,f)

    def appendFeat():
        with open("features.json","w") as f:
            json.dump(features,f)

    def loadDis():
        with open("features.json","r") as f:
            global disease_dict
            disease_dict=json.load(f)

    def loadFeat():
        with open("features.json","r") as f:
            global features
            features=json.load(f)


def diseaseSelecter():
    prompt=diseaseGenPrompt(disease_dict)

    try:
        response=model.invoke(prompt)
        response=json.loads(response.content)
        response=response["disease"]

        if response in disease_dict:
            disease_dict[response]+=1
        else:
            disease_dict[response]=1
        

        return response

    except json.JSONDecodeError:
        diseaseSelecter()
    




def scenarioGen(disease):
    try:
        response=client.models.generate_content(model="gemini-2.5-flash",
                     contents=scenarioGenPrompt(disease,features))
        
        response=json.loads(response.text)
        response=response["scenario"]
        featuresUpdate(response)
        return response
    
    except Exception as e:
        print(e,"still continuing")
        time.sleep(5)
        scenarioGen(disease)
x=int(input("how many iter"))

while x>0:
    print(scenarioGen(diseaseSelecter()))
    print(disease_dict)
    print(features)
    x-=1

jsonFunc.appendDis()
jsonFunc.appendFeat()





    

# payload_gemma = {
#     "model": "gemma4",
#     "prompt": "Patient has chest pain and sweating. Ask ONE next relevant question.",
#     "stream": False
# }

# response = requests.post(url, json=payload)

# print(response.json()["response"])
