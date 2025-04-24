from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText
import google.generativeai as genai
from prompt import create_persona

# Setup Gemini API
genai.configure(api_key="GOOGLE_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")

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

    # Create a Gemini conversation context
    persona_prompt = create_persona(user_name)
    chat = model.start_chat(history=[
        {"role": "user", "parts": [persona_prompt]}
    ])

    audio_processor.do_speech_recognition = False
    response = chat.send_message(f"The user's name is {user_name}. Greet them warmly and ask how they're doing.")
    yield session.call("rie.dialogue.say", text=response.text)
    yield sleep(0.3)
    audio_processor.do_speech_recognition = True

    # Main conversation loop
    while True:
        while not audio_processor.new_words:
            audio_processor.loop()
            yield sleep(0.1)

        user_input = audio_processor.give_me_words()
        sentence = user_input[-1][0].strip() if user_input and user_input[-1] else ""
        print(f"{user_name} said:", sentence)

        # Check for exit
        if any(word in sentence.lower() for word in ["bye", "goodbye", "see you", "later"]):
            audio_processor.do_speech_recognition = False
            yield session.call("rie.dialogue.say", text=f"Goodbye, {user_name}! It was lovely talking to you.")
            yield session.call("rom.sensor.hearing.close")
            break
        
        # Build GPT prompt
        response = chat.send_message(sentence)
        reply = response.text 
        
        # Speak response (pause listening)
        audio_processor.do_speech_recognition = False
        yield session.call("rie.dialogue.say", text=reply)
        yield sleep(0.5)
        audio_processor.do_speech_recognition = True



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
