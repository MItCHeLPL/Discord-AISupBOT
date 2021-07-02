import os
import asyncio
import random

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashCommandOptionType, SlashContext

import aiResponse
import saveVoice

from dotenv import load_dotenv
from gtts import gTTS as gtts

load_dotenv()

TEXT_PREFIXES = ['yoai ', 'yoai'] #recognize command prefix in chat

HELP_MESSAGE = '''Yo, I can think! I am alive! Ask me anything.
Join **AI Voice Channel** to talk with me!
Type "**yoai [query]**" and ask for anything!'''

INFO_MESSAGE = '''I'm created by M!tCheL: https://github.com/MItCHeLPL
I'm using OpenAI's GPT-3 to think and filter my responses
I'm using modified version of Sheepposu's discord.py fork to receive audio: https://github.com/Sheepposu/discord.py
I'm using Google Text To Speech to communicate
I'm using Google and Wit.ai Speech Recognition to understand you'''

INSTRUCTIONS = "I will listen to you for 5 seconds, after that I will respond to your input. After my response I will listen to you again. You can speak now."

HELLOS = ['hello', 'whats up?', 'How do you do?', 'Welcome', 'Hi', "Yo"] #tts greetings list

class AISupBOT(commands.Bot):
    """Responds to Discord User Queries"""

    def __init__(self, auto_join_guild, auto_join_vc, log_guild, log_textchannel):

        super(AISupBOT, self).__init__( #discord bot init
            command_prefix='yoai ',
            intents = discord.Intents().all(),
            owner_id=int(os.getenv('DISCORD_BOT_OWNER_ID'))
        )

        #voice input init
        self.vi = saveVoice.VoiceInput()

        #ai init
        self.ai = aiResponse.AiResponse()

        self.auto_join_guild = auto_join_guild
        self.auto_join_vc = auto_join_vc

        self.log_guild = log_guild
        self.log_textchannel = log_textchannel

        self.vc = None
        self.conversation = False #is bot currently in conversation
        self.latest_conversation_message = None

    #BODY
    #booted
    async def on_ready(self):
            print('Starting...')
            print('\nName: ')
            print(self.user.name)
            print('\nUser ID: ')
            print(self.user.id)
            print('\nStarted.')

            #Listening to: "yoai help" rich presence
            await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = 'yoai [query]'))

            print('\nConnected to:')
            for guild in client.guilds:
                print(guild.name)

                if(guild.id == self.auto_join_guild): #auto join guild
                    channel = discord.utils.get(guild.voice_channels, id=self.auto_join_vc) #get voice channel
                    
                    if(channel != None):
                        self.vc = await channel.connect() #connect to channel


    async def on_voice_state_update(self, member, before, after):
        if(self.voice_clients != [] and member.id != self.user.id): #if bot is in the same voice channel

            #ignore bools
            smute = ((before.self_mute == False and after.self_mute == True) or (before.self_mute == True and after.self_mute == False))
            mute = ((before.mute == False and after.mute == True) or (before.mute == True and after.mute == False))
            sdeaf = ((before.self_deaf == False and after.self_deaf == True) or (before.self_deaf == True and after.self_deaf == False))
            deaf = ((before.deaf == False and after.deaf == True) or (before.deaf == True and after.deaf == False))
            stream = ((before.self_stream == False and after.self_stream == True) or (before.self_stream == True and after.self_stream == False))
            video = ((before.self_video == False and after.self_video == True) or (before.self_video == True and after.self_video == False))

            #ignore
            if smute or mute or sdeaf or deaf or stream or video:
                return

            #somebody leaved/entered voice channel
            else:
                for server in self.voice_clients: #cycle through all servers

                    if(server.channel == after.channel): #connect
                        await self.StartConversation(member)

                    if(server.channel == before.channel): #leave
                        await self.StopConversation()

        #bot disconnects from the channel
        if member.id == self.user.id:
            if before.channel and not after.channel and self.voice_clients == []:
                for guild in client.guilds:
                    if(guild.id == self.auto_join_guild): #auto join guild
                        channel = discord.utils.get(guild.voice_channels, id=self.auto_join_vc) #get voice channel
                        
                        if(channel != None):
                            self.vc = await channel.connect() #connect to channel
        

    async def on_message(self, message):
        #ignore bots
        if message.author.bot:
            return

        #pass message in lower caps
        lower_content = message.content.lower()
        prefixList = list(filter(lower_content.startswith, TEXT_PREFIXES))
        
        # if message does not begin with an invocation prefix
        if prefixList == []:
            return
        else: #strip text from invocation
            print('\nRecognized text invocations: ' + str(prefixList))
            lower_content = lower_content[len(str(prefixList[0])):]
            print('Passed text input: ' + lower_content)

        #if asked for help
        if lower_content.find('help', 0, 4) != -1:
            print("Displayed help")
            await message.reply(HELP_MESSAGE)
            await message.add_reaction('✅') #bot understood message
            return

        #if asked for info
        if lower_content.find('info', 0, 4) != -1:
            print("Displayed info")
            await message.reply(INFO_MESSAGE)
            await message.add_reaction('✅') #bot understood message
            return

        #if asked to stop reading
        elif lower_content.find('stop', 0, 4) != -1:
            print("Stopped playing")
            await message.add_reaction('✅')
            if self.vc.is_playing():
                self.vc.stop()
            return
        
        else:
            #stop playing if doing so
            if self.vc.is_playing():
                self.vc.stop()

            ai_response = self.ai.GetAIResponse(lower_content)

            await message.reply(ai_response)
            self.ai.gpt3.resset_chat_log()


    #AUDIO OUTPUT
    #def. source: 'audio/outputTTS.mp3')
    async def TTS(self, txt, source, lang:str=None, tld:str=None):
        if lang == None:
            lang = 'en'
        if tld == None:
            tld='com'

        #generate file
        if(txt != " " and txt != "" and txt != " ."):
            ttsFile = gtts(txt, lang = lang, tld = tld)
        else:
            ttsFile = gtts("Can you repeat?", lang = lang, tld = tld) #if no text to generate speech from
        ttsFile.save(source)

        await self.PlayAudioFile(source)

    async def PlayAudioFile(self, source):
        if self.vc.is_playing():
            self.vc.stop()
        self.vc.play(discord.FFmpegPCMAudio(source), after=lambda e: print('Player error: %s' % e) if e else None) #play mp3

        #cooldown when playing
        while self.vc.is_playing(): #Checks if voice is playing
            await asyncio.sleep(1) #While it's playing it sleeps for 1 second


    #Play sound from array
    async def Greet(self, member):
        voiceLineId = random.randint(0, (len(HELLOS)-1)) #random voiceline from greetings list

        if self.vc.is_playing() == False:
            await self.TTS((HELLOS[voiceLineId] + " " + str(member.display_name)), 'audio/greetingTTS.mp3')


    async def GiveInstructions(self):
        while self.vc.is_playing(): #Checks if voice is playing
            await asyncio.sleep(1) #While it's playing it sleeps for 1 second

        if(self.vc.is_playing() == False):
            await self.TTS(INSTRUCTIONS, 'audio/instructionsTTS.mp3')


    async def StartConversation(self, member):
        self.conversation = True

        if(self.conversation is True):
            await self.Greet(member)#bot greets user
            print("Greeted " + str(member))
        else:
            if self.vc.is_playing():
                self.vc.stop()
            return

        if(self.conversation is True):
            await self.GiveInstructions()#bot gives instructions
            print("Gave instructions")
        else:
            if self.vc.is_playing():
                self.vc.stop()
            return

        #do{
            #bot starts recording user voice input
            #bot ttses response
        #}until user leaves channel

        while self.conversation == True:
            if self.vc.is_playing() == False:                  

                #start recording
                if(self.conversation is True):
                    self.vi.StartRecording(self.vc, 5)
                else:
                    break  

                #wait for user input
                if(self.conversation is True):
                    await asyncio.sleep(6)
                else:
                    break  

                #generate response
                if(self.conversation is True):
                    ai_response = self.ai.GetAIResponse()
                    print("Generated response")

                    #get channel to post response
                    guild = discord.utils.get(client.guilds, id=self.log_guild)
                    text_channel = discord.utils.get(guild.text_channels, id=self.log_textchannel)

                    if(text_channel is not None):
                        if self.latest_conversation_message is None:
                            self.latest_conversation_message = await text_channel.send('Chat Log with ' + member.mention + ":\n\n" + str(self.ai.gpt3.chat_log[len(self.ai.gpt3.start_chat_log):]))#post new conversation
                        else:
                            await self.latest_conversation_message.edit(content=str('Chat Log with ' + member.mention + ":\n\n" + str(self.ai.gpt3.chat_log[len(self.ai.gpt3.start_chat_log):]))) #edit message with current conversation
                        print("Typed response")

                    textToRead = ai_response
                else:
                    break   

                #TTS the response
                if(self.conversation is True):
                    await self.TTS(textToRead, 'audio/outputTTS.mp3', 'en', 'com')
                    print("Told response")
                else:
                    if self.vc.is_playing():
                        self.vc.stop()
                    break  

            if(self.conversation is False):
                break

    async def StopConversation(self):
        if(self.conversation is True):

            self.vi.StopRecording(self.vc) #stop recording
            if self.vc.is_playing(): #stop ttsing
                self.vc.stop()

            self.latest_conversation_message = None #reset conversation message
            self.ai.gpt3.resset_chat_log()

            self.conversation = False #stop conversation
            print("User left voice channel, reseting cycle")


#bot config
if __name__ == '__main__':
    discord_token = os.getenv('DISCORD_TOKEN')
    auto_join_guild = int(os.getenv('DISCORD_AUTO_JOIN_GUILD'))
    auto_join_vc = int(os.getenv('DISCORD_AUTO_JOIN_VC'))
    log_guild = int(os.getenv('DISCORD_LOG_GUILD'))
    log_textchannel = int(os.getenv('DISCORD_LOG_TEXTCHANNEL'))

    #initialize class
    client = AISupBOT(auto_join_guild, auto_join_vc, log_guild, log_textchannel)

    #slash commands
    slash = SlashCommand(client, sync_commands=True)
    slash_guilds = [auto_join_guild]

    #help slash command
    @slash.slash(name="help", description="Help with AISupBOT", guild_ids=slash_guilds)
    async def slash_help(ctx : SlashContext):
        await ctx.send(HELP_MESSAGE)
        print("Displayed help from slash command")

    #info command
    @slash.slash(name="info", description="Info about AISupBOT", guild_ids=slash_guilds)
    async def slash_help(ctx : SlashContext):
        await ctx.send(INFO_MESSAGE)
        print("Displayed info from slash command")
        
    #yoai [query]
    query_options = [
        {
            "name" : "query",
            "description" : "Text passed to AISupBOT",
            "required" : True,
            "type" : 3
        }
    ]
    @slash.slash(name="yoai", description="Talk to AISupBOT", guild_ids=slash_guilds, options=query_options)
    async def slash_query(ctx : SlashContext, query = ""):
        if(query != "" and query != None):
            ai_response = client.ai.GetAIResponse(query.lower())
            await ctx.send(ctx.author.mention + ": " + query + "\n" + client.user.mention + ": " + ai_response)

            client.ai.gpt3.resset_chat_log()

            print("Passed query from slash command")


    #start
    client.run(discord_token)