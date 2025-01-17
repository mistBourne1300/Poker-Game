from table import table
from players import expector
import numpy as np
import time
import datetime
import os
import argparse
from tqdm.auto import tqdm

# non command-line-editable constants
exponent_range = (1,4)

# command-line-editable constants
num_gen = 10
pop_per_gen = 25
starting_money = 25
players_per_game = 2

exp1_loc = "exponent1_data.npy"
exp2_loc = "exponent2_data.npy"

def nada(x):
    pass


def main(args):

    num_gen = int(args.num_gen)
    pop_per_gen = int(args.pop_per_gen)
    starting_money = int(args.starting_money)
    players_per_game = int(args.players_per_game)
    say = print if args.v else nada

    if not args.overwrite:
        if os.path.exists(exp1_loc):
            try:
                exp1dat = np.load(exp1_loc)
                pop_per_gen = exp1dat.shape[1]
            except:
                os.remove(exp1_loc)
                exp1dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))
        else:
            exp1dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))
        
        if os.path.exists(exp2_loc):
            try:
                exp2dat = np.load(exp2_loc)
                assert (1,pop_per_gen) == exp2dat.shape[1]
                assert len(exp2dat) == len(exp1dat)
            except:
                os.remove(exp2_loc)
                exp2dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))
                if os.path.exists(exp1_loc):
                    os.remove(exp1_loc)
                exp1dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))

        else:
            exp2dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))
    else:
        exp1dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))
        exp2dat = np.random.uniform(exponent_range[0],exponent_range[1],size=(1,pop_per_gen))
        if os.path.exists(exp1_loc):
            os.remove(exp1_loc)
        if os.path.exists(exp2_loc):
            os.remove(exp2_loc)
    
    

    for gen in tqdm(range(num_gen)):
        ordering = np.arange(pop_per_gen)
        np.random.shuffle(ordering)
        ordering = list(ordering)

        winning_exp1s = []
        winning_exp2s = []
        
        num_games = pop_per_gen//players_per_game

        for game in tqdm(range(num_games)):
            idxs = [ordering.pop() for i in range(players_per_game)]
            if len(ordering) < players_per_game:
                idxs = idxs + ordering
            exp1s = exp1dat[-1,idxs]
            exp2s = exp2dat[-1,idxs]
            t = table(player_constructors=[expector.constructor]*len(exp1s), player_names=[f"x{i}" for i in range(len(exp1s))], starting_money=starting_money, say=say, verbose=False)
            
            for i,player in enumerate(t.players):
                player.EXPONENT1 = exp1s[i]
                player.EXPONENT2 = exp2s[i]
            
            t.play_game()
            winner = t.players[0]
            winning_exp1s.append(winner.EXPONENT1)
            winning_exp2s.append(winner.EXPONENT2)

        # get stats for winning exp1
        winning_exp1_mean = np.mean(winning_exp1s)
        if len(winning_exp1s) > 1:
            winning_exp1_std = np.mean(winning_exp1s)
        else:
            winning_exp1_std = 1

        # get stats for winning exp2
        winning_exp2_mean = np.mean(winning_exp2s)
        if len(winning_exp2s) > 1:
            winning_exp2_std = np.mean(winning_exp2s)
        else:
            winning_exp2_std = 1
        
        # number of new exponents to create
        num_to_create = pop_per_gen - len(winning_exp1s)

        # create new exponents
        new_exp1s = np.clip(np.random.normal(loc=winning_exp1_mean, scale=winning_exp1_std, size=num_to_create), a_min=1, a_max=np.inf)
        new_exp2s = np.clip(np.random.normal(loc=winning_exp2_mean, scale=winning_exp2_std, size=num_to_create), a_min=1, a_max=np.inf)

        # concatenate new exponents to winning exponents
        new_gen_exp1 = np.concatenate((np.array(winning_exp1s), new_exp1s))
        new_gen_exp2 = np.concatenate((np.array(winning_exp2s), new_exp2s))

        # make new exponent generation a 2-d matrix
        new_gen_exp1 = np.expand_dims(new_gen_exp1, axis=0)
        new_gen_exp2 = np.expand_dims(new_gen_exp2, axis=0)

        # concatenate new winning generation onto exponent data
        exp1dat = np.concatenate((exp1dat, new_gen_exp1))
        exp2dat = np.concatenate((exp2dat, new_gen_exp2))
        np.save(exp1_loc,exp1dat)
        np.save(exp2_loc,exp2dat)
    import plot_exp_data
    plot_exp_data.main(exp1_loc=exp1_loc, exp2_loc=exp2_loc)


        



if __name__ == "__main__":
    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument("--num-gen",default=str(num_gen),help="number of generations to run. this will tack on to previously collected data, unless --overwrite is flagged.")
    parser.add_argument("--pop-per-gen",default=str(pop_per_gen),help="the population per generation. will be overwritten when loading from file, unless the --overwrite flag is set.")
    parser.add_argument("--starting-money",default=str(starting_money), help="the starting money per player per game.")
    parser.add_argument("--players-per-game",default=str(players_per_game), help="the number of players per game.")
    parser.add_argument("-v",action="store_true",help="whether to print out each game.")
    parser.add_argument("--overwrite",action="store_true",default=False,help="whether to overwrite exponent data. must be true if a change in population size is desired.")

    args = parser.parse_args()
    main(args)


    print("computation time:")
    print(datetime.timedelta(seconds = time.time() - start))



