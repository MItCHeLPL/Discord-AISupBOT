#using modified version of Sheepposu's discord.py fork: https://github.com/Sheepposu/discord.py

import discord

Sink = discord.Sink

class VoiceInput:
    def __init__(self):
        self.is_recording = False

    def StartRecording(self, vc, time=10):
        filters = {}
        filters.update({'time': time})
        print("Voice input filters: " + str(filters))

        vc.start_recording(Sink(encoding='wav', filters=filters, output_path=''), self.on_stopped)
        self.is_recording = True
        print("Started recording")

    def StopRecording(self, vc):
        if(self.is_recording):
            vc.stop_recording()

    async def on_stopped(self, sink, *args):
        self.is_recording = False
        print("Stopped recording and saved")
        