from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText

# Initialize the speech-to-text processor
audio_processor = SpeechToText()
audio_processor.silence_time = 0.5
audio_processor.silence_threshold2 = 100
audio_processor.logging = False


@inlineCallbacks
def ask_for_name(session):
    """Ask the user for their name and capture it using STT."""
    audio_processor.do_speech_recognition = False
    yield session.call("rie.dialogue.say", text="Hello, this is RobotName. What is your name?")
    yield sleep(0.3)
    audio_processor.do_speech_recognition = True

    # Wait for user's spoken name
    while not audio_processor.new_words:
        audio_processor.loop()
        yield sleep(0.1)

    raw = audio_processor.give_me_words()
    name = raw[-1][0].strip() if raw else "there"

    print("Captured name:", name)

    audio_processor.do_speech_recognition = False
    yield session.call("rie.dialogue.say", text=f"Nice to meet you, {name}!")
    yield sleep(0.3)
    audio_processor.do_speech_recognition = True

    return name


@inlineCallbacks
def STT_dialogue(session):
    """Conduct a speech-based dialogue with the user, using their name."""
    
    yield session.call("rom.sensor.hearing.sensitivity", 1650)
    yield session.call("rie.dialogue.config.language", lang="en")

    # Subscribe to the hearing stream
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream")
    yield session.call("rom.sensor.hearing.stream")

    # Ask for name and store it
    user_name = yield ask_for_name(session)

    # Main conversation loop
    while True:
        while not audio_processor.new_words:
            audio_processor.loop()
            yield sleep(0.1)

        raw = audio_processor.give_me_words()
        sentence = raw[-1][0].strip() if raw else ""

        print(f"{user_name} said:", sentence)

        if "bye" in sentence.lower().split():
            yield session.call("rie.dialogue.say", text=f"Goodbye, {user_name}!")
            break
        else:
            yield session.call("rie.dialogue.say", text=f"What else would you like to say, {user_name}?")

    # Clean up the stream
    yield session.call("rom.sensor.hearing.close")


@inlineCallbacks
def main(session, details):
    yield STT_dialogue(session)
    session.leave()


# WAMP connection setup
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.6808d97a29c04006ecc04b7f"
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
