import speechToText
import gpt3

class AiResponse:
    def __init__(self):

        self.sr = speechToText.SpeechToText()

        self.gpt3 = gpt3.GPT3()

        self.latest_query = None

        self.filtered_responses_in_a_row = 0

    def GetAIResponse(self, query=None):
        #if query isn't passed
        if(query is None):
            query = self.sr.GetResponse() #recognize query from audio recording

            if(query is None): #if speech recognition can't recognize query
                query = "i can't understand"

        
        #pass input in lower caps
        query = query.lower()
        self.latest_query = query #make query public


        #get gpt3 response
        print("Passing to GPT-3")

        response = self.gpt3.get_response(query)
        print('GPT-3 response: ' + response)

        response_content_filter_label = self.gpt3.get_filter_label(response)
        print('GPT-3 response content filter label: ' + response_content_filter_label)


        #filter response if response is broken string or offensive
        FILTER = response == " ." or response == " " or response == "  " or response == "." or response is None or len(response) < 2 or response_content_filter_label == "2" or response_content_filter_label == "1"


        #get new response if response is filtered
        if(FILTER):
            print('Filtered response, getting new output.')

            self.filtered_responses_in_a_row += 1

            #reset chat log if bot is stuck in a rant
            if(self.filtered_responses_in_a_row > 5):
                self.gpt3.resset_chat_log()
                self.filtered_responses_in_a_row = 0

            return self.GetAIResponse(query) #get new response

        else:
            self.filtered_responses_in_a_row = 0 #reset filter counter

            #save interaction
            self.gpt3.add_response_to_chat_log(query, response)
            return(response)