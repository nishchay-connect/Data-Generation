import requests

url="http://localhost:11434/api/generate"

def modelInit(model,prompt):

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False}
    return payload


class LLM():
    
    def llama3(prompt):
        return requests.post(url, json=modelInit("llama3.1:8b",prompt)).json()["response"]
    
    def qwen3_5_4B(prompt):
        return requests.post(url, json=modelInit("qwen3.5:4b",prompt)).json()["response"]
    
    def dolphin(prompt):
        return requests.post(url, json=modelInit("dolphin3:8b",prompt)).json()["response"]
    
    def qwen3_5_9B(prompt):
        return requests.post(url, json=modelInit("qwen3.5:9b",prompt)).json()["response"]
    
    def medgemma(prompt):
        return requests.post(url, json=modelInit("medgemma:4b",prompt)).json()["response"]
    
    def medgemma1_5(prompt):
        return requests.post(url, json=modelInit("medgemma1.5:4b",prompt)).json()["response"]
    
    def gemma4(prompt):
        return requests.post(url, json=modelInit("gemma4:e4B",prompt)).json()["response"]

#### testing outputs
   
# response = LLM.dolphin("hi")
# print(type(response))
# print(response.status_code)
# print(response.text)
# print(response.json())

# print(response.json()["response"])  
    