# AISupBOT - Discord GPT-3 Chat Bot
### Discord AI Chat Bot created using GPT-3

## How it works
### Voice channel
1. User joins voice channel
1. Bot greets user and explains how does conversation work using TTS
1. Bot records user audio for 5 seconds
1. Audio file is passed to Speech Recognition
1. Text received from Speech Recognition is added to chat log
1. Chat log is passed to GPT-3 API
1. GPT-3 API generates response
1. Response gets filter label assigned by GPT-3 API
1. If response gets filtered GPT-3 API generates new response
1. When response passed filter, bot adds it into chat log
1. Chat log gets send to discord chat log text channel (message gets edited every interaction to avoid spam)
1. Bot says response using TTS
1. After TTS finished bot goes back to **step 3**

* When user leaves voice channel chat log gets reseted and bot waits for another user to join

### Text channel
1. Bot recognizes command by prefix or slash command
1. Bot passes user input to GPT-3 API
1. GPT-3 API generates response
1. Response gets filter label assigned by GPT-3 API
1. If response gets filtered GPT-3 API generates new response
1. When response passed filter, bot replies to user with response

## Requirements
* Voice channel that bot auto-joins with user limit set to 2
* Text channel for chat log
* GPT-3 API Key
* Wit.ai API Key
* Discord Bot Token

## Limitations
* Can work on only one server at a time
* Can speak with only one user on a channel at a time

## Created using:
Tool|Function
-|-
[OpenAI GPT-3](https://openai.com/blog/openai-api/)| Filter and Responses
Modified version of [Sheepposu's](https://github.com/Sheepposu) [discord.py fork](https://github.com/Sheepposu/discord.py)|Recieving and saving discord audio
[gTTS](https://pypi.org/project/gTTS/)|Text to speech
[SpeechRecognition](https://pypi.org/project/SpeechRecognition/) | Converting user audio to text