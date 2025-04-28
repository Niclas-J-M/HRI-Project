from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

class AlphaMini:
    def __init__(self, session, audio_processor, language="en"):
        self.session = session
        self.language = language
        self.audio_processor = audio_processor
        
    @inlineCallbacks  
    def setup(self):
        """Set up the speech recognition of the alpha mini"""

        yield self.session.call("rie.dialogue.config.language", lang="en")
        yield self.session.call("rom.sensor.hearing.sensitivity", 1650)
        self.audio_processor.setup(self.session)
         
    @inlineCallbacks
    def speak(self, message, action=None):
        """ Speech function with optional movement"""
        if action:
            self.session.call("rom.optional.behavior.play", name=action)
            
        # disable audio processor before speech to prevent it from hearing itself
        yield self.audio_processor.disable()
        yield self.session.call("rie.dialogue.say", text=message)
        yield sleep(0.5)
        self.audio_processor.enable()
    
    @inlineCallbacks
    def ask_for_name(self):
        self.session.call("rom.optional.behavior.play", name="BlocklyBow")
        self.speak("Hello, this is Blockly. What is your name?")
        response = yield self.audio_processor.await_response()
        print(response)
        return response
     
    @inlineCallbacks   
    def stop_listening(self):
        self.audio_processor.disable()
        yield self.session.call("rom.sensor.hearing.close")
        self.session.leave()

    @inlineCallbacks
    # not used as gemini function calling api didn't work
    def raise_volume(self):
        """Raises the volume level of the robot by 10"""
        current_volume = yield self.session.call("rom.actuator.audio.volume")
        yield self.session.call("rom.actuator.audio.volume", current_volume)

    @inlineCallbacks
    # not used as gemini function calling api didn't work
    def reduce_volume(self):
        """Reduces the volume level of the robot by 10"""
        yield self.session.call("rom.actuator.audio.volume", 10)