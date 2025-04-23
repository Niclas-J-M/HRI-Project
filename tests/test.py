from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText
audio_processor = SpeechToText() # create an instance of the class

# changing these values might not be necessary
audio_processor.silence_time = 0.5 # parameter set to indicate when to stop recording
audio_processor.silence_threshold2 = 100 # any sound recorded below this value is considered silence 
audio_processor.logging = False # set to true if you want to see all the output


@inlineCallbacks
def STT_dialogue(session):
    # Set up language and sensitivity
    yield session.call("rom.sensor.hearing.sensitivity", 1650)
    yield session.call("rie.dialogue.config.language", lang="en")

    # Prompt user
    yield session.call("rie.dialogue.say", text="Please say something")

    # Start STT stream
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream")
    yield session.call("rom.sensor.hearing.stream")

    # Dialogue loop
    while True:
        # wait for a full utterance
        while not audio_processor.new_words:
            yield sleep(0.1)
            audio_processor.loop()
            yield sleep(0.1)
            

        # grab and then clear so next time is fresh
        raw = audio_processor.give_me_words()
        words = [w[0] if isinstance(w, tuple) else str(w) for w in raw]
        sentence = " ".join(words).strip()
        print("User said:", sentence)

        # … after you build your `words` list …
        words_lower = [w.lower() for w in words]
        if "bye" in words_lower:
            yield session.call("rie.dialogue.say", text="Goodbye!")
            break
        else:
            yield session.call("rie.dialogue.say", text="Please say something else")

    # Clean up
    yield session.call("rom.sensor.hearing.close")



@inlineCallbacks
def main(session, details):


    yield STT_dialogue(session)
    
    session.leave()

wamp = Component(
        transports=[
    {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["msgpack"],
            "max_retries": 0,
    }
    ],
    realm="rie.6808d97a29c04006ecc04b7f",
)
wamp.on_join(main)
if __name__ == "__main__": 
    run([wamp])
