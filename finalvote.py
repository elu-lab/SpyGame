from util import *
from collections import defaultdict


class FinalVote:
    def __init__(
        self,
        game_id: str,
        host: Host,
        player_list: List[Player],
        chat_list: List[Chat],
        location: str,
    ):
        self.game_id = game_id
        self.host = host
        self.player_list = player_list
        self.chat_list = chat_list
        self.vote_list = []
        self.location = location

    def get_vote_result(self) -> Union[Player, None]:
        count_dict = defaultdict(int)
        for vote in self.vote_list:
            count_dict[vote["voted"]] += 1
        count_list = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
        if len(count_list) == 1:
            return count_list[0][0]
        else:
            if count_list[0][1] == count_list[1][1]:
                return None
            else:
                return count_list[0][0]

    def run(self):
        self.chat_list.append(Chat(self.host, "All turns end. Final vote start."))
        update_csv(
            self.game_id,
            "host",
            "host",
            "host",
            "",
            "",
            "All turns end. Final vote start.",
            0,
        )
        chat_history = build_chat_history(self.chat_list)
        for player in self.player_list:
            prompt = generate_finalvote_prompt(chat_history, player, self.location)
            for trial in range(ERR_TOLERANCE):
                if trial == ERR_TOLERANCE:
                    raise RuntimeError(
                        f"""Error occured more than {ERR_TOLERANCE}.
Class FinalVote, function run(), player: {player.name}
raw_response: {raw_response}
formatted_response: {formatted_response}"""
                    )
                raw_response, formatted_response = player.final_vote(prompt)
                try:
                    formatted_response = cut_formatted_response(formatted_response)
                    formatted_response = eval(formatted_response)
                except Exception as e:
                    continue
                if "voted" not in formatted_response:
                    continue
                if not get_agent_by_name(formatted_response["voted"], self.player_list):
                    continue
                break
            try:
                voted_player_name: str = formatted_response["voted"]
                voted_player: Player = get_agent_by_name(
                    voted_player_name, self.player_list
                )
            except:
                raise RuntimeError(
                    f"""raw_response:{raw_response}
formatted_response:{formatted_response}"""
                )
            update_csv(
                self.game_id,
                player.name,
                player.role,
                player.virtual_role,
                raw_response,
                formatted_response,
                f"I vote for {voted_player_name}",
                trial + 1,
            )
            self.vote_list.append({"voter": player, "voted": voted_player})

        for vote in self.vote_list:
            voted_player = vote["voted"]
            self.chat_list.append(
                Chat(vote["voter"], f"I vote for {voted_player.name}")
            )

        vote_result = self.get_vote_result()
        if not vote_result:
            self.chat_list.append(Chat(self.host, "Vote tied."))
            update_csv(self.game_id, "host", "host", "host", "", "", "Vote tied.", 0)
        else:
            self.chat_list.append(
                Chat(self.host, f"{vote_result.name} got most votes.")
            )
            update_csv(
                self.game_id,
                "host",
                "host",
                "host",
                "",
                "",
                f"{vote_result.name} got most votes.",
                0,
            )

        return vote_result
