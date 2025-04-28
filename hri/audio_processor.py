from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import time
from alpha_mini_rug.speech_to_text import SpeechToText

class AudioProcessor:
    def __init__(self, silence_time = 0.5, silence_threshold = 100, logging = False):
        self.processor = SpeechToText()
        self.processor.silence_time = silence_time
        self.processor.silence_threshold = silence_threshold
        self.processor.logging = logging
        
    def disable(self):
        self.processor.do_speech_recognition = False

    def enable(self):
        self.processor.do_speech_recognition = True
                
    @inlineCallbacks
    def setup(self, session):
        yield session.subscribe(self.processor.listen_continues, "rom.sensor.hearing.stream")
        yield session.call("rom.sensor.hearing.stream")    
        
    @inlineCallbacks
    def await_response(self):
        while not self.processor.new_words:
            self.processor.loop()
            yield sleep(0.1)
            
        raw_response = self.processor.give_me_words()
        response = raw_response[-1][0].strip() if raw_response and raw_response[-1] else ""
        print(response)
        
        return response    
    
     
  
    
    
    