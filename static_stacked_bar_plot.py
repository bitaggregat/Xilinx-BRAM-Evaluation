import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
import matplotlib.patches as mpatches

df = pd.DataFrame(columns=['Context', 'Device', 'One Stable Bits', 'Zero Stable Bits'],
                  data=[['One biased stripes', "Small", 4825.25, 3702.85],
                        ['Zero biased stripes', "Small", 4002.81, 4666.40],
                        ['Entire BRAM', "Small", 9084.15, 8668.48],
df.set_index(['Context', 'Device'], inplace=True)
df0 = df.reorder_levels(['Device', 'Context']).sort_index()

colors = plt.cm.Paired.colors

df0 = df0.unstack(level=-1) # unstack the 'Context' column
fig, ax = plt.subplots()
hatches = ['.', '///', 'o']
(df0['One Stable Bits']+df0['Zero Stable Bits']).plot(kind='bar', color=[colors[1], colors[1]], rot=0, ax=ax, hatch=hatches)
(df0['Zero Stable Bits']).plot(kind='bar', color=[colors[3], colors[3]], rot=0, ax=ax, hatch=hatches)

legend_handles = [
    mpatches.Patch(color=colors[1], label="One Stable Bits"),
    mpatches.Patch(color=colors[3], label="Zero Stable Bits")
]
plt.legend(handles=legend_handles)

ax.patches[0].set_hatch("///")
ax.patches[1].set_hatch("///")
ax.patches[2].set_hatch("///")
ax.patches[3].set_hatch(".")
ax.patches[4].set_hatch(".")
ax.patches[5].set_hatch(".")
ax.patches[6].set_hatch("o")
ax.patches[7].set_hatch("o")
ax.patches[8].set_hatch("o")
ax.patches[9].set_hatch("///")
ax.patches[10].set_hatch("///")
ax.patches[11].set_hatch("///")
ax.patches[12].set_hatch(".")
ax.patches[13].set_hatch(".")
ax.patches[14].set_hatch(".")
ax.patches[15].set_hatch("o")
ax.patches[16].set_hatch("o")
ax.patches[17].set_hatch("o")






plt.savefig(
                Path("results", "peter").with_suffix(".png"),
                format="png",
                dpi=900,
            )
