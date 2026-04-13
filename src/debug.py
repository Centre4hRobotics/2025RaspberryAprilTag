""" Wrap matplotlib stuff """

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

data1: list[tuple] = []
data2: list[tuple] = []

x_name: str = ""
y1_name: str = ""
y2_name: str | None = None

figure = None
ax1 = None
ax2 = None

def create_plot(x_axis_name: str, y1_axis_name: str = "Y1", y2_axis_name: str | None = None):
    """ Initialize the plot """
    global x_name, y1_name, y2_name, figure, ax1, ax2

    x_name = x_axis_name
    y1_name = y1_axis_name
    y2_name = y2_axis_name

    figure, ax1 = plt.subplots()

    if y2_name is not None:
        ax2 = ax1.twinx()

def save_plot(file: str) -> None:
    """ Save plot to file """
    x1, y1 = zip(*data1)
    x2, y2 = zip(*data2)

    if ax1 and figure:
        ax1.plot(x1, y1)
        ax1.set_xlabel(x_name)
        ax1.set_ylabel(y1_name)

        if y2_name and ax2:
            ax2.plot(x2, y2, color='orange')
            ax2.set_ylabel(y2_name)
            ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        figure.savefig(file)

def add_data(x, data, plot_num: int = 1) -> None:
    """ Add data to plots. plot_num determines which dataset to add to; data1 or data2 """
    if plot_num == 1:
        data1.append((x, data))
    elif plot_num == 2:
        data2.append((x, data))
