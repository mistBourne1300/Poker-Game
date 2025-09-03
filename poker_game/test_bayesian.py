from table import table
from players import bayesian, player, expector
import inspect
import numpy
import itertools
import json

STARTING_MONEY = 10
NUM_GAMES = 100

def generate_table_w_players(player_class:player):
    # sig = inspect.signature(player_class.constructor)
    # TF_variables = [False]*len(sig.parameters.keys())
    # int_variables = [False]*len(sig.parameters.keys()) # TODO: implement int bayesian learning
    # float_variables = [False]*len(sig.parameters.keys()) # TODO: implement float bayesian learning
    # for i,param in enumerate(sig.parameters.values()):
    #     print(param.name)
    #     print(type(param.default))
    #     if type(param.default) == bool:
    #         TF_variables[i] = True
    #     elif type(param.default) == int:
    #         int_variables[i] = True
    #     elif type(param.default) == float:
    #         float_variables[i] = True
    
    # # the below code assumes we only need to define a different bot for each bool, and no bots for int or float
    # num_bool_args = sum(TF_variables)
    # num_players_to_create = 2**num_bool_args

    players = []
    num_players = len(list(itertools.product([True,False],repeat=3)))
    t = table([bayesian.constructor]*num_players, [str(i) for i in range(num_players)],starting_money=10, say=print)
    auths = t.auths

    for i,(bayes_avg, ignore_ties, lamb_multi) in enumerate(itertools.product([True,False],repeat=3)):
        new_player = bayesian.constructor(f"bayes{i}",auths[i],bayes_avg=bayes_avg, ignore_ties=ignore_ties, lamb_multi=lamb_multi)
        new_player.add_money(auths[i],STARTING_MONEY)
        players.append(new_player)
    
    t.players = players
    return t




def main():
    standings = {}

    for game in range(NUM_GAMES):

        t = generate_table_w_players(bayesian)
        t.start_game()

        winner = t.players[0]
        winner_name = winner.name
        if winner_name not in standings:
            standings[winner_name] = (1,winner.bayes_avg,winner.ignore_ties,winner.lamb_multi)
        else:
            num_wins, bayes_avg, ignore_ties, lamb_multi = standings[winner_name]
            num_wins += 1
            standings[winner_name] = (num_wins, bayes_avg, ignore_ties, lamb_multi)
    
    
        with open("results.json",'w') as file:
            json.dump(standings,file,indent=1)
    




    
if __name__ == "__main__":
    # print("bayes1"[5:])
    main()