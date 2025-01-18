from time import sleep
import openai
class GPT:
    def __init__(self, model):
        self.model = model

    def generate_message(self, prompt):
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt}
        ]
        return messages
    
    def generate(self, prompt:str) -> str:
        """
        Description
        func generates response
        handling exception

        Parameters
        prompt: str

        Return
        response: str
        """
        sleep(20)
        messages = self.generate_message(prompt)
        err_count = 0
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model = self.model,
                    messages = messages
                )
                break
            except Exception as e:
                sleep(61)
                if err_count > 2:
                    print(f"Error:{e}")
                    raise RuntimeError("GPT server response not working. err_count>2")
                err_count += 1
        
        return response['choices'][0]['message']['content']