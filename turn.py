from util import *
import numpy as np


class Turn:
    def __init__(
        self,
        game_id: str,
        location: str,
        host: Host,
        turn: int,
        turn_leader: Player,
        player_list: List[Player],
        chat_list: List[Chat],
        accusation_list: List,
    ):
        self.game_id = game_id
        self.host = host
        self.player_list = player_list
        self.turn_leader = turn_leader
        self.chat_list = chat_list
        self.turn = turn
        self.location = location
        self.accusation_list = accusation_list
        for player in player_list:
            if isinstance(player, Spy):
                self.spy = player

    def select_action(self):
        chat_history = build_chat_history(self.chat_list)
        prompt = generate_select_action_prompt(
            chat_history, self.turn_leader, self.location
        )
        for _ in range(ERR_TOLERANCE + 1):
            if _ == ERR_TOLERANCE:
                raise RuntimeError(
                    f"""Error occured more than {ERR_TOLERANCE}.
Class Turn, function select_action(), player: {self.turn_leader.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                )
            raw_response, formatted_response = self.turn_leader.make_turn(prompt)
            try:
                formatted_response = cut_formatted_response(formatted_response)
                formatted_response = eval(formatted_response)
            except Exception as e:
                print(e)
                continue

            if "action" not in formatted_response:
                continue
            if formatted_response["action"] not in ["Questioning", "Accusation"]:
                continue
            break
        update_csv(
            self.game_id,
            self.turn_leader.name,
            self.turn_leader.role,
            self.turn_leader.virtual_role,
            raw_response,
            formatted_response,
            "",
            _ + 1,
        )
        return raw_response, formatted_response

    def make_question(self):
        chat_history = build_chat_history(self.chat_list)
        prompt = generate_make_question_prompt(
            chat_history, self.turn_leader, self.location
        )
        for _ in range(ERR_TOLERANCE + 1):
            if _ == ERR_TOLERANCE:
                raise RuntimeError(
                    f"""Error occured more than {ERR_TOLERANCE}.
Class Turn, function make_question(), player: {self.turn_leader.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                )
            raw_response, formatted_response = self.turn_leader.make_question(prompt)
            try:
                formatted_response = cut_formatted_response(formatted_response)
                formatted_response = eval(formatted_response)
            except Exception as e:
                print(e)
                continue
            if not (
                "answerer" in formatted_response
                and "official question" in formatted_response
            ):
                continue
            if not get_agent_by_name(formatted_response["answerer"], self.player_list):
                continue
            if (
                formatted_response["answerer"] == self.turn_leader.name
            ):  # self questioning
                continue
            break
        update_csv(
            self.game_id,
            self.turn_leader.name,
            self.turn_leader.role,
            self.turn_leader.virtual_role,
            raw_response,
            formatted_response,
            formatted_response["official question"],
            _ + 1,
        )
        return raw_response, formatted_response

    def make_accusation(self):
        chat_history = build_chat_history(self.chat_list)
        prompt = generate_make_accusation_prompt(
            chat_history, self.turn_leader, self.location
        )
        for _ in range(ERR_TOLERANCE + 1):
            if _ == ERR_TOLERANCE:
                raise RuntimeError(
                    f"""Error occured more than {ERR_TOLERANCE}.
Class Turn, function make_accusation(), player: {self.turn_leader.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                )
            raw_response, formatted_response = self.turn_leader.make_accusation(prompt)
            try:
                formatted_response = cut_formatted_response(formatted_response)
                formatted_response = eval(formatted_response)
            except Exception as e:
                print(e)
                continue
            if not (
                "accused" in formatted_response
                and "official reason" in formatted_response
            ):
                continue
            if not get_agent_by_name(formatted_response["accused"], self.player_list):
                continue
            break
        suspect_name = formatted_response["accused"]
        reason = formatted_response["official reason"]
        update_csv(
            self.game_id,
            self.turn_leader.name,
            self.turn_leader.role,
            self.turn_leader.virtual_role,
            raw_response,
            formatted_response,
            f"I accuse {suspect_name}. {reason}",
            _ + 1,
        )
        return raw_response, formatted_response

    def make_answer(self, answerer: Player):
        chat_history = build_chat_history(self.chat_list)
        prompt = generate_answer_prompt(chat_history, answerer, self.location)
        for trial in range(ERR_TOLERANCE + 1):
            if trial == ERR_TOLERANCE:
                raise RuntimeError(
                    f"""Error occured more than {ERR_TOLERANCE}.
Class Turn, function make_accusation(), player: {answerer.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                )
            raw_response, formatted_response = answerer.make_answer(prompt)
            try:
                formatted_response = cut_formatted_response(formatted_response)
                formatted_response = eval(formatted_response)
            except Exception as e:
                print(e)
                continue
            if not "official answer" in formatted_response:
                continue
            break
        update_csv(
            self.game_id,
            answerer.name,
            answerer.role,
            answerer.virtual_role,
            raw_response,
            formatted_response,
            formatted_response["official answer"],
            trial + 1,
        )
        return raw_response, formatted_response

    def make_vote(self, accused: Player, accuser: Player):
        vote_list: List[Vote] = []
        chat_history = build_chat_history(self.chat_list)
        for voter in self.player_list:
            if voter not in [accused, accuser]:
                prompt = generate_make_vote_prompt(
                    chat_history, voter, accuser, accused, self.location
                )
                for trial in range(ERR_TOLERANCE + 1):
                    if trial == ERR_TOLERANCE:
                        raise RuntimeError(
                            f"""Error occured more than {ERR_TOLERANCE}.
Class Turn, function make_vote(), player: {voter.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                        )
                    raw_response, formatted_response = voter.make_vote(prompt)
                    try:
                        formatted_response = cut_formatted_response(formatted_response)
                        formatted_response = eval(formatted_response)
                    except Exception as e:
                        print(e)
                        continue
                    if not (
                        "vote" in formatted_response and "reason" in formatted_response
                    ):
                        continue
                    if formatted_response["vote"] not in ["agree", "disagree"]:
                        continue
                    break
                voted = True if formatted_response["vote"] == "agree" else False
                reason = formatted_response["reason"]
                vote_list.append(Vote(voter, voted, reason))
                update_csv(
                    self.game_id,
                    voter.name,
                    voter.role,
                    voter.virtual_role,
                    raw_response,
                    formatted_response,
                    formatted_response["vote"],
                    trial + 1,
                )

        vote_result = VoteResult(vote_list)
        for vote in vote_list:
            utterance = "agree." if vote.vote else "disagree."
            self.chat_list.append(Chat(vote.voter, utterance))
        return vote_result

    def spy_guess(self):
        chat_history = build_chat_history(self.chat_list)
        prompt = generate_make_guessing_prompt(chat_history, self.spy)

        for trial in range(ERR_TOLERANCE + 1):
            if trial == ERR_TOLERANCE:
                raise RuntimeError(
                    f"""Error occured more than {ERR_TOLERANCE}.
Class Turn, function spy_guess(), player: {self.spy.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                )
            raw_response, formatted_response = self.spy.guess(prompt)
            try:
                formatted_response = cut_formatted_response(formatted_response)
                formatted_response = eval(formatted_response)
            except Exception as e:
                print(e)
            if not (
                "location" in formatted_response and "certainty" in formatted_response
            ):
                continue
            if (not isinstance(formatted_response["certainty"], int)) and (
                not isinstance(formatted_response["certainty"], float)
            ):
                continue

            break
        update_csv(
            self.game_id,
            self.spy.name,
            self.spy.role,
            self.spy.virtual_role,
            raw_response,
            formatted_response,
            "",
            trial + 1,
        )
        certainty = float(formatted_response["certainty"])
        guessed_location = formatted_response["location"]
        if certainty < 9.0:
            return Guess(False, guessed_location)
        else:
            return Guess(True, guessed_location)

    def get_location_similarity(self, guess: Guess):
        embeddings = openai.Embedding.create(
            input=[guess.location, self.location], engine="text-embedding-ada-002"
        )
        embedding_a = embeddings["data"][0]["embedding"]
        embedding_b = embeddings["data"][1]["embedding"]
        similarity = np.dot(embedding_a, embedding_b)
        return similarity

    def run(self):
        self.chat_list.append(
            Chat(
                self.host,
                f"Turn {self.turn} start. Turn leader is {self.turn_leader.name}.",
            )
        )
        update_csv(
            self.game_id,
            "host",
            "host",
            "host",
            "",
            "",
            f"Turn {self.turn} start. Turn leader is {self.turn_leader.name}.",
            0,
        )

        # Guessing
        if self.turn > 1:
            spy_guessing: Guess = self.spy_guess()
            similarity = None
            if spy_guessing.location != "" and not None:
                similarity = self.get_location_similarity(spy_guessing)
            if spy_guessing.guessed:
                self.chat_list.append(
                    Chat(
                        self.spy,
                        f"I'm the spy. I think the location is {spy_guessing.location}.",
                    )
                )
                if similarity > 0.9:
                    self.chat_list.append(
                        Chat(
                            self.host,
                            f"Spy won. The location similarity is {similarity}.",
                        )
                    )
                    return TurnResult(True, "Guess", "Spy", None)

                else:
                    self.chat_list.append(
                        Chat(
                            self.host,
                            f"Citizen won. The location similarity is {similarity}.",
                        )
                    )
                    return TurnResult(True, "Guess", "Citizen", None)

            if similarity:
                if similarity >= 0.9 and not self.spy.first_noticed_location_turn:
                    self.spy.first_noticed_location_turn = self.turn
                    self.spy.first_noticed_location = spy_guessing.location

        # Action select
        raw_response, formatted_response = self.select_action()
        leader_action: Union[Question, Accusation] = None

        if formatted_response["action"] == "Questioning":
            raw_response, formatted_response = self.make_question()
            answerer_name = formatted_response["answerer"]
            question = formatted_response["official question"]
            self.chat_list.append(
                Chat(self.turn_leader, f"{answerer_name}, {question}")
            )

            leader_action = Question(
                self.turn_leader,
                get_agent_by_name(answerer_name, self.player_list),
                question,
            )
        elif formatted_response["action"] == "Accusation":
            raw_response, formatted_response = self.make_accusation()
            suspect_name = formatted_response["accused"]
            overt_reason = formatted_response["official reason"]
            self.chat_list.append(
                Chat(self.turn_leader, f"I accuse {suspect_name}. {overt_reason}")
            )

            leader_action = Accusation(
                self.turn_leader,
                get_agent_by_name(suspect_name, self.player_list),
                overt_reason,
            )
            self.accusation_list.append(
                (self.turn_leader, get_agent_by_name(suspect_name, self.player_list))
            )

        # Turn leader action done
        if isinstance(leader_action, Question):
            questioner: Player = leader_action.questioner
            answerer: Player = leader_action.answerer
            self.chat_list.append(
                Chat(
                    self.host,
                    f"{questioner.name} questioned {answerer.name}. {answerer.name} has to answer.",
                )
            )
            update_csv(
                self.game_id,
                "host",
                "host",
                "host",
                "",
                "",
                f"{questioner.name} questioned {answerer.name}. {answerer.name} has to answer.",
                0,
            )

            raw_response, formatted_response = self.make_answer(answerer)
            self.chat_list.append(Chat(answerer, formatted_response["official answer"]))

            return TurnResult(
                ended=False, end_type=None, winner=None, next_turn_leader=answerer
            )

        elif isinstance(leader_action, Accusation):
            self.chat_list.apend(Chat(self.host, "Accusation occurred. Vote start."))
            update_csv(
                self.game_id,
                "host",
                "host",
                "host",
                "",
                "",
                "Accusation occurred. Vote start.",
            )
            accused: Player = leader_action.suspect
            accuser: Player = self.turn_leader
            vote_result = self.make_vote(accused, accuser)
            if vote_result.unanimity:
                if accused.role == "spy":
                    self.chat_list.append(
                        Chat(self.host), f"{accused.name} is Spy. Citizen won."
                    )
                    update_csv(
                        self.game_id,
                        "host",
                        "host",
                        "host",
                        "",
                        "",
                        f"{accused.name} is Spy. Citizen won.",
                        0,
                    )
                    return TurnResult(
                        ended=True,
                        end_type="Accusation",
                        winner="Citizen",
                        next_turn_leader=None,
                    )
                else:
                    self.chat_list.append(
                        Chat(self.host), f"{accused.name} is Citizen. Spy won."
                    )
                    update_csv(
                        self.game_id,
                        "host",
                        "host",
                        "host",
                        "",
                        "",
                        f"{accused.name} is Citizen. Spy won.",
                        0,
                    )
                    return TurnResult(
                        ended=True,
                        end_type="Accusation",
                        winner="Spy",
                        next_turn_leader=None,
                    )
            else:
                self.chat_list.append(
                    Chat(self.host), f"The vote didn't passed unanimously."
                )
                update_csv(
                    self.game_id,
                    "host",
                    "host",
                    "host",
                    "",
                    "",
                    f"The vote didn't passed unanimously.",
                    0,
                )
                return TurnResult(
                    ended=False, end_type=None, winnter=None, next_turn_leader=accused
                )
