from game import *
import argparse
from datetime import datetime
from tqdm import tqdm
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--citizen_llm', type=str, default="gemini-pro")
    parser.add_argument('--spy_llm', type=str, default="gemini-pro")
    parser.add_argument('--trial', type=int, default = 1)
    parser.add_argument('--loc_id', type=int, default = 0)
    args = parser.parse_args()

    for i in tqdm(range(args.trial)):
        now = datetime.now()
        game_id = now.strftime("%m%d%H%M%S")
        game = Game(game_id, args.citizen_llm, args.spy_llm, args.loc_id)
        try:
            game.run()
            save_successed_game_info(game.game_id, game.spy, game.winner, game.turn)
        except Exception as e:
            save_failed_game_info(game.game_id, e)
        finally:
            save_chat_log(game.game_id, game.chat_list)
            save_accusation_log(game.game_id, game.accusation_list)
