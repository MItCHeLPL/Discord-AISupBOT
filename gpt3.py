import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class GPT3:
    def __init__(self):
        #self.engine = "davinci"
        self.engine = "curie" #enough for chat, cheaper

        self.temperature = 0.9
        self.max_tokens = 30
        self.top_p = 1
        self.frequency_penalty = 0
        self.presence_penalty = 0.6

        self.start_chat_log = "Human: Hey, how are you doing?\nAI: I'm good! What would you like to chat about?\n " #default chat starting value
        self.chat_log = self.start_chat_log #logs whole conversation with given user

    #process text to assistant
    def get_response(self, query: str, frequency_penalty : int = 0):
        prompt = f'{self.chat_log}Human: {query}\nAI:' #pass formated query to ai

        response = openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=["\n", " Human:", " AI:"]
        )

        response_text = response['choices'][0]['text'] #get ai text response
        return str(response_text)


    #get filter label for ai response
    def get_filter_label(self, query: str):
        response = openai.Completion.create(
            engine="content-filter-alpha-c4",
            prompt = "<|endoftext|>"+query+"\n--\nLabel:",
            temperature=0,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            logprobs=10
        )

        output_label = response["choices"][0]["text"]
        return str(output_label)


    def add_response_to_chat_log(self, query, response):
        self.chat_log = f'{self.chat_log}Human: {query}\nAI: {response}\n' #add response and query to chat log


    def resset_chat_log(self):
        self.chat_log = self.start_chat_log