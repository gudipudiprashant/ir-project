
def visualize_params_per_method(results_list, params_list):
    import numpy as np
    import matplotlib.pyplot as plt

    colors_list = ['r', '#624ea7', 'g', 'yellow', 'k', 'maroon']

    N = 9

    plot_vals = []
    for results in results_list:
        plot_vals.append((results["precision"]["PER"], results["recall"]["PER"], results["f_measure"]["PER"],
                         results["precision"]["ORG"], results["recall"]["ORG"], results["f_measure"]["ORG"],
                         results["precision"]["LOC"], results["recall"]["LOC"], results["f_measure"]["LOC"]))


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
    ax.set_title('Score Name')
    ax.set_xticks(ind + ctr*width / 2)
    ax.set_xticklabels(('PER-Precision', 'PER-Recall', 'PER-f_measure',
                        'ORG-Precision', 'ORG-Recall', 'ORG-f_measure',
                        'LOC-Precision', 'LOC-Recall', 'LOC-f_measure'))

    ax.legend(tuple(rects[i][0] for i in range(len(rects))), tuple(params_list))


    plt.show()