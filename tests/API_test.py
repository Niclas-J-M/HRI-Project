import os
from google import genai
from google.genai import types
from prompt import create_persona

# Configure API key
client = genai.Client(api_key="")

# Start conversation
print("Bot: Hi there! What's your name?")
user_name = input("You: ")

# Initialize the model
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

# Use the name in the response
response = chat.send_message(f"The user's name is {user_name}. Greet them warmly and ask how they're doing.")
greetings = response.text 
text = greetings.split('~')[0]
action = greetings.split('~')[1]
print(text)
print(action)

# Chat loop
while True:
    user_input = input("You: ")
    if any(word in user_input.lower() for word in ["bye", "goodbye", "see you", "later"]):
        print(f"Goodbye, {user_name}! It was lovely talking to you.")
        break
    
    response = chat.send_message(user_input)
    reply = response.text
    text = reply.split('~')[0]
    action = reply.split('~')[1]
    print(text)
    print(action)