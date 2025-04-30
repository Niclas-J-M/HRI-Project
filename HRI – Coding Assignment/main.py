from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from language_model import LanguageModel
from audio_processor import AudioProcessor
from alpha_mini import AlphaMini
    
@inlineCallbacks
def main(session, details):
    language_model = LanguageModel(api_key="GOOGLE API KEY")
    audio_processor = AudioProcessor(
        silence_time=0.5,
        silence_threshold=100,
        logging=False
    )
    robot = AlphaMini(session, audio_processor)
    robot.setup()
    
    # ask the user for their name and let the language model extract the name from their response
    raw_name = yield robot.ask_for_name()
    user_name = language_model.process_name(raw_name)
    language_model.setup(user_name)
    
    # greet the user with their name
    message, action = language_model.process_response(f"The user's name is {user_name}. Greet them warmly and ask how they're doing.")
    robot.speak(message, action)
    
    # conversation loop
    while True:
        sentence = yield audio_processor.await_response()
        
        # Check for exit
        if any(word in sentence.lower() for word in ["bye", "goodbye", "see you", "later"]):
            yield robot.speak(f"Goodbye, {user_name}! It was lovely talking to you.", "BlocklyWaveRightArm")
            robot.stop_listening()
            break
        
        message, action = language_model.process_response(sentence)
        robot.speak(message, action)

    session.leave()

# WAMP connection setup
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="REALM KEY"
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
