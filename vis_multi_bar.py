import config
def plot_multi_bar(results_list, params_list):
    import numpy as np
    import matplotlib.pyplot as plt

    colors_list = ['r', '#624ea7', 'g', 'yellow', 'k', 'maroon']

    N = 9

    plot_vals = []
    for results in results_list:
        plot_vals.append((results["precision"]["PER"], results["recall"]["PER"], results["accuracy"]["PER"],
                         results["precision"]["ORG"], results["recall"]["ORG"], results["accuracy"]["ORG"],
                         results["precision"]["LOC"], results["recall"]["LOC"], results["accuracy"]["LOC"]))


    ind = np.arange(N)  # the x locations for the groups
    width = 0.15       # the width of the bars

    fig, ax = plt.subplots()

    rects = []
    ctr = 0
    for val in plot_vals:
        ax.bar(ind+width*ctr, val, width, color=colors_list[ctr])
        rects.append(ax.bar(ind+width*ctr, val, width, color=colors_list[ctr]))
        ctr += 1

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Value')
    ax.set_title(config.run_multi_param_dict["module"])
    ax.set_xticks(ind + ctr*width / 2)
    ax.set_xticklabels(('PER-Precision', 'PER-Recall', 'PER-accuracy',
                        'ORG-Precision', 'ORG-Recall', 'ORG-accuracy',
                        'LOC-Precision', 'LOC-Recall', 'LOC-accuracy'))
    ax.set_yticks(np.arange(0, 1.1, 0.1))

    ax.legend(tuple(rects[i][0] for i in range(len(rects))), tuple(params_list))


    plt.show()