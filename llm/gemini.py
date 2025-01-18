from time import sleep
import google.generativeai as genai
class Gemini:
    def __init__(self, model):
        self.model = genai.GenerativeModel(model)
    
    def generate(self, prompt: str)-> str:
        sleep(20)
        err_count = 0
        chat = self.model.start_chat(history=[])
        while True:
            try:
                response = chat.send_message(prompt)
                break
            except Exception as e:
                sleep(61)
                if err_count>2:
                    raise RuntimeError("Gemini server response not working. err_count>2")
                err_count += 1

        return response.candidates[0].content.parts[0].text
