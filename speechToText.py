import speech_recognition as sr
import os
from os import path
from dotenv import load_dotenv

load_dotenv()

class SpeechToText:
    def __init__(self):
        self.wit_ai_key = os.getenv('WIT_AI_KEY')

        self.AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "audio/output.wav") #get recorder voice audio path

        self.r = sr.Recognizer()

        self.audio = None

    def __GetFile(self):
        with sr.AudioFile(self.AUDIO_FILE) as source:
            self.audio = self.r.record(source)  # read the entire audio file

    def GetGoogleResponse(self):
        try:
            response = self.r.recognize_google(self.audio)
            print("Google Speech Recognition response: " + response)
            return response
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return "I can't understand"
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return "I can't understand"


    def GetWitAIResponse(self):
        try:
            response = self.r.recognize_wit(self.audio, key=self.wit_ai_key)
            print("Wit.ai response: " + response)
            return response
        except sr.UnknownValueError:
            print("Wit.ai could not understand audio")
            return
        except sr.RequestError as e:
            print("Could not request results from Wit.ai service; {0}".format(e))
            return


    def GetResponse(self):
        self.__GetFile() #read audio file

        #get google response, if empty get witai response, if empty retrun "i can't understand"

        googleResponse = self.GetGoogleResponse()

        if(googleResponse != None):
            return googleResponse

        else:
            witAiResponse = self.GetWitAIResponse()
            if(witAiResponse != None and witAiResponse != " "):
                return witAiResponse
            else:
                return "i can't understand"