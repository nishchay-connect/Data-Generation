from DataPipeline import orchestrator
import random
import time
x=14

while x>0:
    orchestrator()
    time.sleep(5)
    x-=1