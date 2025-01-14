from table import table
from players import expector
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import os

num_generations = 10
pop_per_generation = 25
moneys_per_player = 50
exponent_range = (1,4)

if __name__ == "__main__":
    retable = table([],[],starting_money=moneys_per_player, say=print)
    
    if os.path.exists("exponent_data.npy"):
        try:
            exponents_over_time = [dat for dat in np.load("exponent_data.npy")]
        except:
            exponents_over_time = []
    else:
        exponents_over_time = []

    if len(exponents_over_time) > 0:
        last_pop_exps = exponents_over_time[-1]
        last_pop_exps_mean = np.mean(last_pop_exps)
        last_pop_exps_std = np.std(last_pop_exps)
        exponents = np.random.normal(loc=last_pop_exps_mean, scale=last_pop_exps_std,size=pop_per_generation)
    else:
        exponents = np.random.uniform(exponent_range[0], exponent_range[1], size=pop_per_generation)
    exponents_over_time.append(exponents)
    population = []
    auths = []
    for exp in exponents:
        new_auth = np.random.randint(1000000)
        new_expector = expector.constructor(f"x{exp:.3f}", auth = new_auth)
        new_expector.EXPONENT = exp
        population.append(new_expector)
        auths.append(new_auth)

    start = time.time()
    for gen in range(num_generations):
        winners = []
        winning_auths = []

        ordering = np.array([i for i in range(len(population))])
        np.random.shuffle(ordering)
        ordering = list(ordering)
        while len(ordering) > 0:
            x1_idx = ordering.pop()
            x2_idx = ordering.pop()

            x1 = population[x1_idx]
            x2 = population[x2_idx]


            x1_auth = auths[x1_idx]
            x2_auth = auths[x2_idx]

            retable.players = [x1,x2]
            retable.auths = [x1_auth,x2_auth]

            if len(ordering) == 1:
                idx = ordering.pop()
                retable.players.append(population[idx])
                retable.auths.append(auths[idx])
            for player in retable.players:
                player.money = moneys_per_player
            retable.play_game()
            winners.append(retable.players.pop())
            winning_auths.append(retable.auths.pop())
        
        population = [w for w in winners]
        auths = [a for a in winning_auths]


        winning_exps = [player.EXPONENT for player in winners]
        winning_exps_mean = np.mean(winning_exps)
        winning_exp_std = np.std(winning_exps)

        num_to_repopulate = pop_per_generation - len(population)

        for exp in np.random.normal(loc=winning_exps_mean, scale=winning_exp_std, size=num_to_repopulate):
            new_auth = np.random.randint(1000000)
            new_expector = expector(f"x{exp:.3f}", new_auth)
            new_expector.EXPONENT = exp
            population.append(new_expector)
            auths.append(new_auth)
        
        exponents_over_time.append(np.array([p.EXPONENT for p in population]))
        np.save("exponent_data", np.array(exponents_over_time))
    exponents_over_time = np.load("exponent_data.npy")
    [plt.plot(exponents_over_time[:,i]) for i in range(exponents_over_time.shape[1])]
    plt.title("exponents over time")
    plt.xlabel("generation")
    plt.ylabel("exponents (unordered)")
    plt.savefig("exponents_over_time.jpg")
    print(time.time() - start)
    print("computation time:")
    print(datetime.timedelta(seconds = time.time() - start))




