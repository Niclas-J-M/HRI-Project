import os
import google.generativeai as genai
from prompt import create_persona

# Configure API key
genai.configure(api_key="GOOGLE_API_KEY")

# Start conversation
print("Bot: Hi there! What's your name?")
user_name = input("You: ")

# Initialize the model
model = genai.GenerativeModel("gemini-2.0-flash")  
persona_prompt = create_persona(user_name)
chat = model.start_chat(history=[
    {"role": "user", "parts": [persona_prompt]}
])

# Use the name in the response
response = chat.send_message(f"The user's name is {user_name}. Greet them warmly and ask how they're doing.")
print(f"Bot: {response.text}")

# Chat loop
while True:
    user_input = input("You: ")
    if any(word in user_input.lower() for word in ["bye", "goodbye", "see you", "later"]):
        print(f"Goodbye, {user_name}! It was lovely talking to you.")
        break
    
    response = chat.send_message(user_input)
    print(f"Bot: {response.text}")
