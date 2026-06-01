from prompts_data import Prompt
from dotenv import load_dotenv
import json
from google import genai
from google.genai.errors import ClientError
from Models import LLM
from TTS import GenAudio
import random
import time
import datetime
from os import getenv

## added +100 value to child feature to skip child case generation 

load_dotenv()

client=genai.Client(api_key=f"{getenv("GEMINI_API_KEY_1")}")

doc_flag=False
patient_flag=True
memory={"conversation_id":0,
        
        "source":"synthetic",

        "turns":0,

        "disease":"",

        "scenario":{},

        "dialogue":[],

        "readiness_turn":-1,

        "model_used":"gemma4",

        "annotator_confidence (%)":0,

        "language":"en",

        "generated_on":"",

        "usable":1,

        "annotator_id":""

        }
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
  },
  "doctor_profile":{"government_MBBS":0,
                     "private_MBBS":0, 
                     "private_specialist":0, 
                     "rural_PHC":0,
                     "urban_PHC":0
      
 }
}
def logging(content):
    with open("logs.txt",'a') as f:
        f.write(content)

def memoryUpdate(role,content,turn_id):
    memory["dialogue"].append({"turn_id":turn_id,"role":role,"content":content,"annotation_data":{

                "label": 0,
    "current_diagnosis": "",
    "diagnostic_confidence": 0,
    "diagnosis_changed": False,
    "emergency_detected": False}})

def featuresUpdate(response):
    sex=response["sex"]
    age_group=response["age_group"]
    severity=response["severity"]

    doctor_profile=response["doctor_profile"]["type"]
    print(doctor_profile)


    features["sex"][sex]+=1
    features["age_group"][age_group]+=1
    features["severity"][severity]+=1
    features["doctor_profile"][doctor_profile]+=1

class jsonFunc():

    def appendDis():
        with open("disease.json","w") as f:
            json.dump(disease_dict,f,indent=4)

    def appendFeat():
        with open("features.json","w") as f:
            json.dump(features,f,indent=4)

    def loadDis():
        with open("disease.json","r") as f:
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
            memory["conversation_id"]=total_generation["total_dialogues"]



        with open("dialogue_dataset.json","w") as f:
            
            total_generation["dialogues"].append(memory)

            json.dump(total_generation,f,indent=4)


def diseaseSelecter():
    prompt=Prompt.diseaseGenPrompt(disease_dict)

    try:
        print("selecting disease....")
        logging("selecting disease....\n")
        start_d=time.perf_counter()

        response=LLM.llama3(prompt)

        ### testing 2 models for task 
        # if model==0:
            # response=LLM.qwen3_5_4B(prompt)   ## taking a lot of time around 150-160 sec

        # elif model==1:
        #     response=LLM.llama3(prompt)

        response=json.loads(response)
        response=response["disease"]

        
# add disease count verification if req---->
        # if response in disease_dict:
        #     if disease_dict[response]>=3:
        #         response=diseaseSelecter()

        if response in disease_dict:
            disease_dict[response]+=1
            memory["disease"]=response

        else:
            disease_dict[response]=1
            memory["disease"]=response

        end_d=time.perf_counter()
        logging(str(end_d-start_d)+'\n')
        return response

    except json.JSONDecodeError:

        response=diseaseSelecter()
        return response

def scenarioGen(disease):

    start_s=time.perf_counter()

    while True:

        try:

            print("generating scenario....")
            logging("generating scenario....")


            response=client.models.generate_content(model="gemini-2.5-flash",
                        contents=Prompt.scenarioGenPrompt(disease,features))
            response=response.text

            # response=json.loads(response.text)
    # not adequate quality and variation like gemini ,likely using gemini
            # response=LLM.dolphin(Prompt.scenarioGenPrompt(disease,features))

            response=json.loads(response)
            response=response["scenario"]
            featuresUpdate(response)
            memory["scenario"]=response

            end_s=time.perf_counter()
            logging(str(end_s-start_s)+'\n')
            
            return response
        
        except Exception as e:
            print(e,"still continuing")
            time.sleep(8)

def doctorAgent(query):
   
    start_d=time.perf_counter()
    while True:
        print("calling doctor agent...")
        logging("calling doctor agent...")
        try:
            
            response = LLM.gemma4(query)
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()
            response=json.loads(response)
            response=response["content"]
            print(response)
            # GenAudio.male(response)

            end_d=time.perf_counter()
            logging(str(end_d-start_d)+'\n')
            return response

        
        except json.decoder.JSONDecodeError:
            continue

def patientAgent(prompt):
    start_p=time.perf_counter()

    while True:

        print("calling patientAgent....")
        logging("calling patientAgent....")

        try :

            response=LLM.gemma4(prompt)
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()
            response=json.loads(response)
            response=response["content"]
            print(response)
            # GenAudio.female(response)

            end_p=time.perf_counter()
            logging(str(end_p-start_p)+'\n')

            return response

        except json.decoder.JSONDecodeError:
           continue
    
    
def orchestrator():
    start=time.perf_counter()
    
    global doc_flag
    global patient_flag
    global memory
    jsonFunc.loadDis()
    jsonFunc.loadFeat()
    
    scenario=scenarioGen(diseaseSelecter())

    turn=turnCalc(scenario)

    memory["turns"]=turn


    for i in range(1,turn+1):

        if patient_flag:

            if memory=={}:
            
                prompt=Prompt.InitpatientRolePrompt(scenario)
                response=patientAgent(prompt)

            else:
                prompt=Prompt.patientRolePrompt(scenario,memory,scenario["cultural_context"])
                response=patientAgent(prompt)

            memoryUpdate("patient",response,i)
            doc_flag=True
            patient_flag=False
        
        if doc_flag:
            prompt=Prompt.docRolePrompt(scenario,memory,scenario["doctor_profile"])
            response=doctorAgent(prompt)

            memoryUpdate("doctor",response,i)
            doc_flag=False
            patient_flag=True
    
        
    memory["generated_on"]=str(datetime.datetime.now())
    jsonFunc.saveDialogue()
    jsonFunc.appendDis()
    jsonFunc.appendFeat()
    
    end=time.perf_counter()
    logging("dialogue no : "+f"{memory['conversation_id']}"+"ended in...."+str(end-start)+'\n\n')

    print(end-start)

    memory={"conversation_id":0,
        
        "source":"synthetic",

        "turns":0,

        "disease":"",

        "scenario":{},

        "dialogue":[],

        "readiness_turn":-1,

        "model_used":"gemma4",

        "annotator_confidence (%)":0,

        "language":"en",

        "generated_on":"",

        "usable":1,

        "annotator_id":""

        }

def turnCalc(scenario):
    severity=scenario["severity"]

    if severity=="mild":
        turns=[9,10]
        turn=random.choice(turns)
    elif severity=="moderate":
        turns=[10,11]
        turn=random.choice(turns)
    elif severity=="severe":
        turns=[11,12]
        turn=random.choice(turns)
    return turn



    


           



    
    






    



