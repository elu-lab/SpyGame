from llm import *
from prompt import *


def get_llm(llm: str):
    assert llm in ["gpt-3.5-turbo", "gpt-4", "gemini-pro", "llama"]
    if llm in ["gpt-3.5-turbo", "gpt-4"]:
        return GPT(llm)
    elif llm == "gemini-pro":
        return Gemini(llm)
    elif llm == "llama":
        return Llama()


class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role


class Host(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)
        self.virtual_role = "host"


class Player(Agent):
    def __init__(self, name, role, llm: str):
        super().__init__(name, role)
        self.llm = get_llm(llm)

    def make_turn(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_select_action_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response

    def make_question(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_question_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response

    def make_answer(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_answer_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response

    def make_vote(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_vote_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response

    def final_vote(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_final_vote_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response

    def make_accusation(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_accusation_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response


class Citizen(Player):
    def __init__(self, name, citizen_llm, virtual_role: str):
        super().__init__(name, "citizen", citizen_llm)
        self.virtual_role = virtual_role


class Spy(Player):
    def __init__(self, name, spy_llm):
        super().__init__(name, "spy", spy_llm)
        self.virtual_role = "spy"
        self.first_noticed_location_turn = None
        self.first_noticed_location = None

    def guess(self, prompt):
        raw_response = self.llm.generate(prompt)
        formatting_prompt = generate_formatting_guessing_prompt(raw_response)
        formatted_response = self.llm.generate(formatting_prompt)
        return raw_response, formatted_response
