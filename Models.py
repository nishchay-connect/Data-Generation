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
        return requests.post(url, json=modelInit("llama3.1:8b",prompt))
    
    def qwen3_5_4B(prompt):
        return requests.post(url, json=modelInit("qwen3.5:4b",prompt))
    
    def dolphin(prompt):
        return requests.post(url, json=modelInit("dolphin3:8b",prompt))
    
    def qwen3_5_9B(prompt):
        return requests.post(url, json=modelInit("qwen3.5:9b",prompt))
    
    def medgemma(prompt):
        return requests.post(url, json=modelInit("medgemma:4b",prompt))
    
    def gemma4(prompt):
        return requests.post(url, json=modelInit("gemma4",prompt))
    
    
    

