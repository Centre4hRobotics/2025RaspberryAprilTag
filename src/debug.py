""" Deal with debugging stuff (unused currently) """

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

error_data = []
tag_count = []

#if robot_pose is not None and best_tag is not None and best_tag.global_pose is not None:
#            error = robot_pose.y
#            error_data.append((runtime, error))
#            if len(tags) == 1:
#                tag_count.append((runtime, (best_tag.id - 25) + .5))
#                # 25 -> 1/2
#                # 26 -> 3/2
#            else:
#                tag_count.append((runtime, len(tags)))
#        else:
#            error_data.append((runtime, numpy.nan))
#            tag_count.append((runtime, 0))

x1, y1 = zip(*error_data)
x2, y2 = zip(*tag_count)

fig, ax1 = plt.subplots()

ax1.plot(x1, y1)
ax1.set_xlabel('Time')
ax1.set_ylabel('Position (m)')

ax2 = ax1.twinx()

ax2.plot(x2, y2, color='orange')
ax2.set_ylabel('Best Tag')
ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

fig.savefig("error.png")
