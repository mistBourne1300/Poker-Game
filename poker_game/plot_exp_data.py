import matplotlib.pyplot as plt
import numpy as np

def main(exp1_loc,exp2_loc):
    exp1dat = np.load(exp1_loc)
    exp2dat = np.load(exp2_loc)
    plt.style.use('dark_background')
    fig,axes = plt.subplots(nrows=2,ncols=1)
    axes[0].plot(exp1dat,c='r')
    axes[0].set_title("exponent 1")

    axes[1].plot(exp2dat,c='goldenrod')
    axes[1].set_title("exponent 2")

    fig.suptitle("genetically trained expector exponents")
    fig.tight_layout()
    fig.savefig("genetic_expectors.jpg")

if __name__ == "__main__":
    from genetic_expector_training import exp1_loc, exp2_loc
    main(exp1_loc=exp1_loc, exp2_loc=exp2_loc)