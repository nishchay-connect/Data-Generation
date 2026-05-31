import requests
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint,HuggingFacePipeline
from prompts_data import diseaseGenPrompt,scenarioGenPrompt,docRolePrompt,patientRolePrompt,InitpatientRolePrompt
from os import getenv
from dotenv import load_dotenv
import json
from google import genai
from google.genai.errors import ClientError
from Models import LLM
import time
load_dotenv()

# llm=HuggingFaceEndpoint(repo_id="meta-llama/Meta-Llama-3-8B-Instruct",task="chat-completion",huggingfacehub_api_token=getenv("HUGGINGFACE_API_TOKEN"),max_new_tokens=1000)


# llm=HuggingFacePipeline.from_model_id(
#     model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
#     task="text-generation",
#     pipeline_kwargs=dict(temperature=0.2)
# )
# model=ChatHuggingFace(llm=llm)

# client=genai.Client(api_key=f"{getenv("GEMINI_API_KEY")}")


# url = "http://localhost:11434/api/generate"


doc_flag=False
patient_flag=True
memory={"S.no:":0,"dialogue":[]}
total_generation={"total_dialogues":0,"dialogues":[memory]}

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
def memoryUpdate(role,content):
    memory["dialogue"].append({"role":role,"content":content})

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

    def saveDialogue():
        global total_generation
        global memory

        with open("dialogue_dataset.json","r") as f:
            total_generation=json.load(f)
            total_generation["total_dialogues"]+=1
            memory["S.no:"]=total_generation["total_dialogues"]



        with open("dialogue_dataset.json","w") as f:
            
            total_generation["dialogues"].append(memory)

            json.dump(total_generation,f,indent=4)

for i in range(1,10):
    jsonFunc.saveDialogue()
    print(i,"dialogue added")

def diseaseSelecter():
    prompt=diseaseGenPrompt(disease_dict)

    try:
        print("selecting disease....")
        response=model.invoke(prompt)
        print(response)
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
        # response=client.models.generate_content(model="gemini-2.5-flash",
        #              contents=scenarioGenPrompt(disease,features))
        
        # response=json.loads(response.text)
        print("generating scenario....")

        response=model.invoke(scenarioGenPrompt(disease,features))
        response=json.loads(response.content)

        
        response=response["scenario"]
        featuresUpdate(response)
        return response
    
    except Exception as e:
        print(e,"still continuing")
        time.sleep(5)
        scenarioGen(disease)
# x=int(input("how many iter"))

# while x>0:
#     print(scenarioGen(diseaseSelecter()))
#     print(disease_dict)
#     print(features)
#     x-=1

# jsonFunc.appendDis()
# jsonFunc.appendFeat()

def doctorAgent(query):
    response = LLM.medgemma(query)
    response=json.loads(response)
    return response

def patientAgent(prompt):
   print("calling patientAgent....")
   response=LLM.gemma4(prompt)
   print(response)
   return response
    
def orchestrator():
    global doc_flag
    global patient_flag
    global memory

    # scenario=scenarioGen(diseaseSelecter())
    
    scenario={
    "disease": "migraine",
    "age": 27,
    "age_group":"young_adult",
    "sex": "female",
    "severity": "moderate",
    "duration": "2 days",
    "visible_symptoms": [
      "headache on one side",
      "sensitivity to light",
      "nausea"
    ],
    "hidden_symptoms": [
      "blurred vision before headache"
    ],
    "emotional_state": "frustrated",
    "communication_style": "impatient",
    "medical_history": [
      "previous migraine episodes during stress"
    ],
    "lifestyle_context": "working long hours with poor sleep recently",
    "patient_goal": "wants fast relief to continue work",
    "contradictions": [
      "initially says headache is normal but later admits pain is severe"
    ],
    "additional_notes": "patient minimizes symptoms initially"
  }

    turn=15
    while turn>0:

        if patient_flag:

            if memory=={}:
            
                prompt=InitpatientRolePrompt(scenario)
                response=patientAgent(prompt)
                break
        
            else:
                prompt=patientRolePrompt(scenario,memory)
                response=patientAgent(prompt)

            memoryUpdate("patient",response)
            doc_flag=True
            patient_flag=False
        
        if doc_flag:
            prompt=docRolePrompt(scenario,memory)
            response=doctorAgent(prompt)
            print(response)

            memoryUpdate("doctor",response)
            doc_flag=False
            patient_flag=True
        
        turn-=1
    memory={}

# orchestrator()

           


    
    






    



# print(response.json()["response"])
