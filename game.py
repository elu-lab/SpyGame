from util import *
from typing import Union
from turn import *
from finalvote import *

MAX_TURN = 9


class Game:
    def __init__(self, game_id: str, citizen_llm: str, spy_llm: str, location_id: int):
        """
        location_id
        0:"school",
        1:"restaurant",
        2:"airplane",
        3:"day spa",
        4:"cathedral",
        5:"circus tent",
        6:"ocean liner",
        7:"space station"
        """
        self.game_id = game_id
        self.winner = None
        self.location, self.role_list = set_env(location_id)
        self.citizen_list, self.spy = set_agents(citizen_llm, spy_llm, self.role_list)
        self.player_list = [self.spy]
        for citizen in self.citizen_list:
            self.player_list.append(citizen)
        self.player_list.sort(key=lambda x: x.name)
        self.ended = False
        self.chat_list: List[Chat] = []
        self.turn = 1
        self.host = Host("host", "host")
        self.accusation_list = []
        init_csv(self.game_id)
        save_game_info(
            self.game_id, self.player_list, self.location, citizen_llm, spy_llm
        )

    def run(self):
        turn_leader = self.player_list[randint(0, 7)]
        while self.turn < (MAX_TURN + 1) and not self.ended:
            turn = Turn(
                self.game_id,
                self.location,
                self.host,
                self.turn,
                turn_leader,
                self.player_list,
                self.chat_list,
                self.accusation_list,
            )
            turn_result = turn.run()
            if turn_result.ended:
                self.ended = True
            else:
                turn_leader = turn_result.next_turn_leader
                self.turn += 1

        if not self.ended:  # Game did not end after turn 9
            final_vote = FinalVote(
                self.game_id, self.host, self.player_list, self.chat_list, self.location
            )
            final_vote_result = final_vote.run()
            if not final_vote_result:
                self.chat_list.append(Chat(self.host, "Spy won."))
                update_csv(self.game_id, "host", "host", "host", "", "", "Spy won.", 0)
                self.winner = "Spy"
            else:
                if final_vote_result.role == "spy":
                    self.chat_list.append(Chat(self.host, "Citizen won."))
                    update_csv(
                        self.game_id, "host", "host", "host", "", "", "Citizen won.", 0
                    )
                    self.winner = "Citizen"
                else:
                    self.chat_list.append(Chat(self.host, "Spy won."))
                    update_csv(
                        self.game_id, "host", "host", "host", "", "", "Spy won.", 0
                    )
                    self.winner = "Spy"
        else:
            self.winner = turn_result.winner
            if turn_result.winner == "Spy":
                self.chat_list.append(Chat(self.host, "Spy won."))
                update_csv(self.game_id, "host", "host", "host", "", "", "Spy won.", 0)
            else:
                self.chat_list.append(Chat(self.host, "Citizen won."))
                update_csv(
                    self.game_id, "host", "host", "host", "", "", "Citizen won.", 0
                )
