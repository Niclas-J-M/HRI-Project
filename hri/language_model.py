from google import genai
from google.genai import types 
from prompt import create_persona

class LanguageModel:
    def __init__(self, api_key, model="gemini-2.0-flash-lite"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        
    def setup(self, user_name):
        persona_prompt = create_persona(user_name)
        self.chat = self.client.chats.create(
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
        
    def process_name(self, raw_name):
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"Find the name in the following text and only return the name: {raw_name}"
        )
        name = response.text

        print("Captured name:", name)
        return name

    def process_response(self, message):
        response = self.chat.send_message(message)
        response_clean = response.text.split('~ ') 
        response_text = response_clean[0]
        response_action = response_clean[1].rstrip()
        return response_text, response_action