from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText
from google import genai
from google.genai import types
from prompt import create_persona
import time
# Setup Gemini API
client = genai.Client(api_key="")

# Initialize the speech-to-text processor
audio_processor = SpeechToText()
audio_processor.silence_time = 0.5
audio_processor.silence_threshold2 = 200
audio_processor.logging = False


@inlineCallbacks
def ask_for_name(session):
    """Ask the user for their name and capture it using STT."""
    audio_processor.do_speech_recognition = False
    session.call("rom.optional.behavior.play", name="BlocklyBow")
    yield session.call("rie.dialogue.say", text="Hello, this is Blockly. What is your name?")
    audio_processor.do_speech_recognition = True

    start_time = time.time()
    # Wait for user's spoken name
    while not audio_processor.new_words:
        audio_processor.loop()
        yield sleep(0.1)

        if time.time() - start_time > 7:
            print("Timeout: No user input detected for 7 seconds.")
            audio_processor.do_speech_recognition = False
            yield session.call("rie.dialogue.say", text="Are you still there?")
            yield sleep(0.5)
            audio_processor.do_speech_recognition = True
            start_time = time.time()  # Reset timer if you want to keep waiting


    raw = audio_processor.give_me_words()
    raw_name = raw[-1][0].strip() if raw else "there"
    name = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=f"Find the name in the following text and only return the name: {raw_name}"
    )
    name = name.text

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
    chat = client.chats.create(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=[persona_prompt],
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                )
            ]
        )
    )

    audio_processor.do_speech_recognition = False
    response = chat.send_message(f"The user's name is {user_name}. Greet them warmly and ask how they're doing.")
    greetings = response.text.split('~ ')
    reply_text = greetings[0]
    action = greetings[1].rstrip()
    print(action)
    session.call("rom.optional.behavior.play", name=action)
    yield session.call("rie.dialogue.say", text=reply_text)
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
            session.call("rom.optional.behavior.play", name="BlocklyWaverRightArm")
            yield session.call("rie.dialogue.say", text=f"Goodbye, {user_name}! It was lovely talking to you.")
            yield session.call("rom.optional.behavior.play", name="BlocklySitDown")
            yield session.call("rom.sensor.hearing.close")
            break
        
        # Build GPT prompt
        response = chat.send_message(sentence)
        response_clean = response.text.split('~ ') 
        reply_text = response_clean[0]
        action = response_clean[1].rstrip()
        print(f"Robot said: {reply_text}")
        print(action)

        # Speak response (pause listening)
        audio_processor.do_speech_recognition = False
        session.call("rom.optional.behavior.play", name=action)
        yield session.call("rie.dialogue.say", text=reply_text)
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
    realm="rie."
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
