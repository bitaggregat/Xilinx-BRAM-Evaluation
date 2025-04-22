import matplotlib.pyplot as plt
import numpy as np

# data from https://allisonhorst.github.io/palmerpenguins/
from pathlib import Path
import numpy as np
import numpy.typing as npt



def generate_diagram(
    path: Path, labels: list[str], 
    weight_counts: dict[str, npt.NDArray[np.int32]],
    bar_count: int,
    width: float = 0.45,
) -> None:

    fig, ax = plt.subplots()
    bottom = np.zeros(bar_count)

    for boolean, weight_count in weight_counts.items():
        p = ax.bar(labels, weight_count, width, label=boolean, bottom=bottom)
        bottom += weight_count
    ax.legend(bbox_to_anchor=(-0.17,.92,0,0.2), loc="upper left")
    ax.set_ylabel("Configuration time (Milliseconds)")
    ax.set_xlabel("FPGA Bitstreams", rotation=180)
    ax.tick_params(axis='x', labelrotation=90)
    ax.tick_params(axis='y', labelrotation=90)


    ax.set_xlim(-0.6, bar_count - 1 + 0.6)
    fig.set_size_inches(3.6, 9, forward=True)
    fig.savefig(path.with_suffix(".svg"), format="svg")
    




if __name__ == "__main__":
    devices = (
        "large\n(xczu9eg)",
        "medium\n(xczu2cg)"
    )

    weight_counts = {
    "Full Bitstream (compressed)": np.array([3997.61867, 953.68176]),
    "Bramless Partial Bitstream (compressed)": np.array([188.06703, 188.1364]),
    "Modified Partial Bistream (headless)": np.array([173.23239, 171.65447])
    }

    path = Path("stacked_bar_plot_bitstream_time")

    generate_diagram(
        path, devices, weight_counts, bar_count=2
    )