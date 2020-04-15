import numpy as np
import matplotlib.pyplot as plt

def plot(data, outpath):
    data = np.array(data)
    fig, ax = plt.subplots()
    ax.plot(data[:,1], data[:,0], label='linear')
    # ax.set_xlabel('x label')
    # ax.set_ylabel('y label')
    # ax.set_title("Simple Plot")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")
    fig.tight_layout()
    fig.savefig(outpath, transparent=True)