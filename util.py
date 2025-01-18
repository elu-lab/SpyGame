import json
from agent import *
from typing import List, Union
from numpy.random import randint
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

ERR_TOLERANCE = 4


@dataclass
class Chat:
    speaker: Agent
    utterance: str


@dataclass
class Question:
    questioner: Player
    answerer: Player
    question: str


@dataclass
class Accusation:
    accuser: Player
    suspect: Player
    overt_reason: str


@dataclass
class Guess:
    guessed: bool
    location: str


@dataclass
class Answer:
    questioner: Player
    answerer: Player
    question: str
    answer: str


@dataclass
class Vote:
    voter: Player
    vote: bool
    underlying_reason: str


@dataclass
class Announcement:
    announcer: Host
    utterance: str


@dataclass
class TurnResult:
    ended: bool
    end_type: Union["Accusation", "Guess", None]
    winner: Union["Spy", "Citizen", None]
    next_turn_leader: Union[None, Player]


class VoteResult:
    def __init__(self, vote_list: List[Vote]):
        for vote in vote_list:
            if not vote.vote:
                self.unanimity = False
                return
        self.unanimity = True


def build_chat_history(chat_list: List[Chat]):
    chat_history = ""
    for chat in chat_list:
        chat_history += f"""

{chat.speaker.name}: {chat.utterance}"""
    return chat_history


def cut_formatted_response(formatted_response: str):
    start = formatted_response.find("{")
    end = formatted_response.rfind("}")
    if start > -1 and end > -1:
        return formatted_response[start : end + 1]
    else:
        return formatted_response


def save_game_info(
    game_id: str, player_list, location: str, citizen_llm: str, spy_llm: str
):
    import os

    txt_dir = "log/" + game_id + "/"
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    txt_dir = txt_dir + "game_info.txt"
    f = open(txt_dir, "a")
    f.write(
        f"""
==========
GAME INFO
=========="""
    )
    f.write(f"\ncitizen llm: {citizen_llm}\nspy_llm: {spy_llm}")
    f.write(f"\nlocation: {location}\n==========")
    for player in player_list:
        f.write(
            f"\nName: {player.name}, role: {player.role}, virtual role: {player.virtual_role}"
        )
    f.write("\n")
    f.write("=" * 10)
    f.close()


def save_failed_game_info(game_id: str, err: str):
    import os

    txt_dir = "log/" + game_id + "/"
    end_condition = "Fail"
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    txt_dir = txt_dir + "game_info.txt"
    f = open(txt_dir, "a")
    f.write(
        f"""
==========
GAME END CONDITION
==========
{end_condition}
==========
Failed Error
==========
{err}
==========
"""
    )
    f.close()


def save_successed_game_info(game_id: str, spy, winner: str, end_turn: int):
    end_condition = "Success"
    import os

    txt_dir = "log/" + game_id + "/"
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    txt_dir = txt_dir + "game_info.txt"
    f = open(txt_dir, "a")
    f.write(
        f"""
==========
GAME END CONDITION
==========
{end_condition}
END TURN: {end_turn}
WINNER: {winner}
SPY FIRST NOTICED LOCATION TURN: {spy.first_noticed_location_turn}
SPY FIRST NOTICED LOCATION (GUESSING): {spy.first_noticed_location}
==========
"""
    )


def save_chat_log(game_id, chat_list: List[Chat]):
    import os

    txt_dir = "log/" + game_id + "/"
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    txt_dir = txt_dir + "conversation.txt"
    f = open(txt_dir, "a")
    for chat in chat_list:
        f.write(
            f"\n{chat.speaker.name}({chat.speaker.role})({chat.speaker.virtual_role}): {chat.utterance}\n"
        )
    f.close()


def save_accusation_log(game_id, accusation_list):
    import os

    txt_dir = "log/" + game_id + "/"
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    txt_dir = txt_dir + "game_info.txt"
    f = open(txt_dir, "a")
    f.write(
        f"""
==========
Accusation Log
=========="""
    )
    for log in accusation_list:
        accuser = log[0]
        accused = log[1]
        f.write(
            f"""\nAccuser: {accuser.name}({accuser.role}), Accused: {accused.name}({accused.role})"""
        )
    f.write(
        f"""
=========="""
    )
    f.close()


def init_csv(game_id: str):
    import os

    csv_dir = "log/" + game_id + "/"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    csv_dir = csv_dir + "log.csv"
    pd.DataFrame(
        {
            "speaker": [],
            "role": [],
            "virtual_role": [],
            "raw_response": [],
            "formatted_response": [],
            "utterance": [],
            "trial": [],
        }
    ).to_csv(csv_dir, index=False)
    return


def update_csv(
    game_id: str,
    speaker: str,
    role: str,
    virtual_role,
    raw_response: str,
    formatted_response: str,
    utterance: str,
    trial: int,
):
    csv_dir = "log/" + game_id + "/log.csv"
    new_data = {
        "speaker": [speaker],
        "role": [role],
        "virtual_role": [virtual_role],
        "raw_response": [raw_response],
        "formatted_response": [formatted_response],
        "utterance": [utterance],
        "trial": [trial],
    }
    df = pd.DataFrame(new_data)
    df.to_csv(csv_dir, mode="a", index=False, header=False)
    return


def set_env(location_id: int):
    f = open("cards.json")
    cards = json.load(f)
    f.close()
    location: str = cards["location"][location_id]
    roles: List[str] = cards["role"][location_id]
    return location, roles


def set_agents(citizen_llm: str, spy_llm: str, virtual_role_list: List[str]):
    mafia_id = randint(1, 8)
    citizen_list = []
    spy = None

    for i in range(1, 8):
        if i == mafia_id:
            spy = Spy("Player" + str(i), spy_llm)
        else:
            citizen_list.append(
                Citizen("Player" + str(i), citizen_llm, virtual_role_list[i - 1])
            )
    return citizen_list, spy


def get_agent_by_name(name: str, player_list: List[Player]):
    for player in player_list:
        if player.name == name:
            return player
    return None
