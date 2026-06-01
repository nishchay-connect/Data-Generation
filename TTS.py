import pyttsx3

class GenAudio():

    def male(text):
        engine=pyttsx3.init()
        voices = engine.getProperty('voices')

        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()

    def female(text):
        engine=pyttsx3.init()
        voices = engine.getProperty('voices')

        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
# GenAudio.male("hi this")
# GenAudio.female("hello ")