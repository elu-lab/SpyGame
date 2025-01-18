from time import sleep
from groq import Groq


class Llama:
    def __init__(self):
        self.model = Groq(
            api_key="YOUR API KEY",
        )

    def generate(self, prompt: str) -> str:
        sleep(20)
        err_count = 0
        while True:
            try:
                response = self.model.chat.completions.create(
                    messages=[
                        {"role": "system", "content": ""},
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    model="llama2-70b-4096",
                )
                break
            except Exception as e:
                sleep(61)
                if err_count > 2:
                    print(f"Error:{e}")
                    raise RuntimeError("Llama server response not working. err_count>2")
                err_count += 1

        return response.choices[0].message.content
