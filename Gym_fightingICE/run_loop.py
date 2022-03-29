import imp


import os


def run_one_game(opponent_ai, predict_ai, depth, game_num):
    os.system("./loop.sh {} {} {} {}".format(opponent_ai, 
                                            predict_ai, 
                                            depth,
                                            game_num))

if __name__ == '__main__':

    # opponent can be selected
    opponent_ais = []

    # predict ai action function can choice
    predict_ais = []

    depths = []

    game_nums = []

    for opponent_ai in opponent_ais:
        for predict_ai in predict_ais:
            for depth in depths:
                for game_num in game_nums:
                     run_one_game(opponent_ai, predict_ai, depth, game_num)
