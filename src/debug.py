""" Deal with debugging stuff (unused currently) """

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

class Plot:
    """ Save data to a graph """

    def __init__(self, x_name: str, y1_name: str = "Y1", y2_name: str = "Y2"):

        self.data1: list[tuple] = []
        self.data2: list[tuple] = []

        self.x_name = x_name
        self.y1_name = y1_name
        self.y2_name = y2_name

        self.fig, self.ax1 = plt.subplots()

        if self.y2_name:
            self.ax2 = self.ax1.twinx()

    def save_plot(self, file: str) -> None:
        """ Save the plot with collected data to a file """
        x1, y1 = zip(*self.data1)
        x2, y2 = zip(*self.data2)

        self.ax1.plot(x1, y1)
        self.ax1.set_xlabel(self.x_name)
        self.ax1.set_ylabel(self.y1_name)

        if self.y2_name:
            self.ax2.plot(x2, y2, color='orange')
            self.ax2.set_ylabel(self.y2_name)
            self.ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        self.fig.savefig(file)

    def add_data(self, x, data, plot_num: int = 1) -> None:
        """ Add data to plots. plot_num determines which dataset to add to; data1 or data2 """
        if plot_num == 1:
            self.data1.append((x, data))
        elif plot_num == 2:
            self.data2.append((x, data))
