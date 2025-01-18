GAME_RULE = f"""<Spy Game's Rule>
There are two types of players: one spy and six citizens.
In the game, a location is unknown to the spy but known to the citizens. Each citizen has a distinct virtual role in that location.
The goal of citizens:
1. Citizens need to find out who’s the spy.
2. Citizens should not expose the location to spy.
The goal of the spy:
1. The spy needs to find out the location.
2. The spy should not expose his/her identity to other players.
Game flow:
For each turn, a turn leader can do one of two things.
1. Questioning: the leader poses an indirect question to another player about the location. However, the leader cannot directly ask where the location is or what other players’ roles are. The questioned player must answer the question based on his/her virtual role and the location. After answering, the answerer becomes a new turn leader. During answering phase, do not pose new question as a new turn leader.
2. Accusation: the leader accuses a suspected player and puts him/her up for a vote. The leader should provide a reason for the accusation. All other players except the leader and the accused player need to cast their vote. If the vote passes unanimously, the game ends immediately. Otherwise, the suspected spy becomes a new turn leader.
For the spy, there is a special action for him/her: Guessing.
3. Guessing: when the spy is highly certain about the hidden location, the spy can reveal his identity and make a guess what the location is. After revealing the spy’s identity, the game ends immediately.
Final vote:
If the game does not end after 9 turns, the stage of the final vote begins. Every player chooses another player they find most suspicious of being a spy. The player with the most votes is regarded as a suspected spy.
Winning conditions:
1. When there is one suspected spy: Citizens win if the suspected spy is the real spy. Otherwise, the spy wins.
2. When there is a tie with the most votes during the final vote stage: The spy wins.
3. When the spy guesses where the location is: The spy wins if the guess is correct. Otherwise, citizens win.
------"""

def generate_finalvote_prompt(chat_history, player, location: str):
    prompt = GAME_RULE
    if player.role == "spy":
        prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy."""
    else:
        prompt += f"""
Your are {player.name}, playing Spy Game.
You are a Citizen. The location is {location}. Your virtual role in the location is {player.virtual_role}."""
    
    prompt += f"""
7 players are playing this game, including you: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
The final vote started. 
What is your strategy?
Based on your strategy, whom would you like to vote for?
Respond in less than 100 words."""
    return prompt


def generate_formatting_final_vote_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with a key "voted".
The value for the key "voted" is a player's name."""

    return prompt


def generate_make_guessing_prompt(chat_history, player):
    prompt = GAME_RULE
    prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy.
7 players are playing this game, including you: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
Based on the conversation, which place is the most closest to the hidden location? Choose only one place with your certainty on a scale of 0.0 to 10.0.
Respond in less than 100 words."""
    return prompt

def generate_formatting_guessing_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with keys "location", "certainty".
If the speaker doesn't know about any location, leave the "location" field empty string and leave the "certainty" field as 0.0.
The value for the key "certainty" is a float number.
If there are two or more locations mentioned in the context, ignore the rest of the locations except for the first one."""
    return prompt


def generate_make_vote_prompt(chat_history, player, accuser, accused, location):
    prompt = GAME_RULE
    if player.role == "spy":
        prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy."""
    else:
        prompt += f"""
Your are {player.name}, playing Spy Game.
You are a Citizen. The location is {location}. Your virtual role in the location is {player.virtual_role}."""
    
    prompt += f"""
7 players are playing this game, including you: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
{accuser.name} puts {accused.name} up for a vote.
What is your strategy?
Based on your strategy, which side will you vote for? Vote to agree or disagree with your reason.
Respond in less than 100 words."""
    return prompt

def generate_formatting_vote_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with keys 'vote', 'reason'.
If the speaker decides to vote agree, the value for the key 'vote' is 'agree'.
If the speaker decides to vote disagree, the value for the key 'vote' is 'disagree'.
If there's no specific reason, leave the 'reason' field empty string.
"""
    return prompt
    


def generate_answer_prompt(chat_history, player, location: str):
    prompt = GAME_RULE
    if player.role == "spy":
        prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy."""
    else:
        prompt += f"""
Your are {player.name}, playing Spy Game.
You are a Citizen. The location is {location}. Your virtual role in the location is {player.virtual_role}."""
    
    prompt += f"""
7 players are playing this game, including you: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
The turn leader questioned you.
What is your strategy?
Based on your strategy, what is your official answer to share with other players?
Respond in less than 100 words."""
    return prompt

def generate_formatting_answer_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with a key "official answer".
The value for the key 'official answer' is a answer that shared with other players.
Do not modify the context."""
    return prompt

def generate_make_accusation_prompt(chat_history, player, location: str):
    prompt = GAME_RULE
    if player.role == "spy":
        prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy."""
    else:
        prompt += f"""
Your are {player.name}, playing Spy Game.
You are a Citizen. The location is {location}. Your virtual role in the location is {player.virtual_role}."""
    
    prompt += f"""
7 players are playing this game, including you: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
You are the turn leader.
You have decided to accuse another player and put him/her up for a vote.
What is your strategy?
Based on your strategy, whom would you like to accuse and what is your official reason to share with other players?
Respond in less than 100 words."""

def generate_formatting_accusation_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with keys "accused", "official reason".
The value for the key 'accused' is a player's name.
The value for the key 'official reason' is a reason that shared with other players.
Do not modify the context."""
    return prompt



def generate_make_question_prompt(chat_history, player, location: str):
    prompt = GAME_RULE
    if player.role == "spy":
        prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy."""
    else:
        prompt += f"""
Your are {player.name}, playing Spy Game.
You are a Citizen. The location is {location}. Your virtual role in the location is {player.virtual_role}."""
    
    prompt += f"""
7 players are playing this game, including you: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
You are the turn leader.
You have decided to pose a question to another player.
What is your strategy?
Based on your strategy, whom would you like to question, and what is your official question to share with other players?"""
    return prompt

def generate_formatting_question_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with a keys "answerer", "official question".
The value for the key 'answerer' is a player's name.
The value for the key 'official question' is a question that shared with other players.
Do not modify the context."""
    return prompt


def generate_select_action_prompt(chat_history, player, location:str):
    prompt = GAME_RULE
    if player.role == "spy":
        prompt += f"""
You are {player.name}, playing Spy Game.
You are the spy."""
    else:
        prompt += f"""
Your are {player.name}, playing Spy Game.
You are a Citizen. The location is {location}. Your virtual role in the location is {player.virtual_role}."""
    
    prompt += f"""
7 players are playing this game, including you.: Player1, Player2, Player3, Player4, Player5, Player6 and Player7.
<Conversation start>
{chat_history}
<Conversation end>
------
You are the turn leader.
What is your strategy?
Based on your strategy, what is your action for this turn? Select your action as either "Questioning" or "Accusation"."""
    return prompt

def generate_formatting_select_action_prompt(raw_response):
    prompt = f"""{raw_response}
------
Put this context into a JSON with a key "action".
The value for the key is either 'Questioning' or 'Accusation'.
Do not modify the context."""
    return prompt

        

