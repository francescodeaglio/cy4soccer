import cmasher as cmr
import streamlit as st
from mplsoccer import Pitch, VerticalPitch
from numpy import ceil
from numpy.linalg import LinAlgError

from streamlit_pages.neo4j_utils.App_grids import App_grids
from streamlit_pages.neo4j_utils.utils import (cypherify_grids, getGamesList,
                                               getTeams)


def get_map_data(pattern, team, match, app):
    """
    Function to perform queries on Neo4j db
    :param pattern: pattern to be matched (ex ABACA)
    :param team: team
    :param match: match_id
    :param app: App instance (connection to Neo4j db)
    :return:
    """
    query = cypherify_grids(pattern, team, match)
    v = app.find_pattern(query)

    number_of_rel = len(pattern) - 1

    glob = []
    for i in range(number_of_rel + 1):
        glob.append({"x": {"start": [], "end": []}, "y": {"start": [], "end": []}})

    for row in v:
        for i in range(number_of_rel):
            glob[i]["x"]["start"].append(row["p" + str(i) + "." + "location"][0])
            glob[i]["y"]["start"].append(row["p" + str(i) + "." + "location"][1])
            glob[i]["x"]["end"].append(row["p" + str(i) + "." + "end_location"][0])
            glob[i]["y"]["end"].append(row["p" + str(i) + "." + "end_location"][1])

    for i in range(number_of_rel):
        for row in v:
            glob[number_of_rel]["x"]["start"].append(
                row["p" + str(i) + "." + "location"][0]
            )
            glob[number_of_rel]["y"]["start"].append(
                row["p" + str(i) + "." + "location"][1]
            )
            glob[number_of_rel]["x"]["end"].append(
                row["p" + str(i) + "." + "end_location"][0]
            )
            glob[number_of_rel]["y"]["end"].append(
                row["p" + str(i) + "." + "end_location"][1]
            )

    return glob


def create_heatmap(
    glob, pattern, pitch, titles=None, bw0=0.3, bw1=0.2, show_start=True, show_end=True
):
    """
    FUnction to create a grid of heatmaps
    :param glob: data
    :param pattern: pattern matched (ex ABACA)
    :param pitch: Pitch object
    :param titles: array of titles (one for each pitch plotted)
    :param bw0: kernel bandwidth for starting location (rbf)
    :param bw1: kernel bandwidth for ending location
    :param show_start: boolean to show/hide start location density
    :param show_end: boolean to show/hide end location density
    :return:
    """
    number_of_rel = len(pattern) - 1

    fig, axs = pitch.grid(
        nrows=int(ceil((number_of_rel + 1) / 4)),
        ncols=4,
        space=0.1,
        figheight=5,
        title_height=0,
        endnote_height=0,  # no title/ endnote
        grid_width=0.9,
        grid_height=0.98,
        bottom=0.01,
        left=0.05,
    )

    if not titles:
        names = [
            pattern + " : " + "location" + " of p" + str(i)
            for i in range(number_of_rel)
        ] + [pattern + " Overall"]
    else:
        names = titles

    for idx, ax in enumerate(axs.flat):
        name = f"{names[idx]}"
        if show_start:
            kdeplot = pitch.kdeplot(
                glob[idx]["x"]["start"],
                glob[idx]["y"]["start"],
                ax=ax,
                shade=True,
                levels=7,
                bw_method=bw0,
                cmap=cmr.arctic,
            )
        if show_end:
            kdeplot2 = pitch.kdeplot(
                glob[idx]["x"]["end"],
                glob[idx]["y"]["end"],
                ax=ax,
                shade=True,
                levels=7,
                bw_method=bw1,
                cmap=cmr.fall,
            )

        ax.set_title(name, fontsize=13)
        if idx == number_of_rel:
            break

    st.pyplot(fig)


def create_flowmap(glob, pattern, pitch, titles=None, bins=(6, 4)):
    """
    Function to plot a grid of flowmap
    :param glob: data
    :param pattern: pattern to be matched
    :param pitch: Pitch object
    :param titles: chart titles
    :param bins: number of (vertical_bins, horiziontal_bins) to split the pitch in
    """
    number_of_rel = len(pattern) - 1

    fig, axs = pitch.grid(
        nrows=int(ceil((number_of_rel + 1) / 4)),
        ncols=4,
        space=0.1,
        figheight=5,
        title_height=0,
        endnote_height=0,  # no title/ endnote
        grid_width=0.9,
        grid_height=0.98,
        bottom=0.01,
        left=0.05,
    )

    if not titles:
        names = [
            pattern + " : " + "location" + " of p" + str(i)
            for i in range(number_of_rel)
        ] + [pattern + " Overall"]
    else:
        names = titles
    for idx, ax in enumerate(axs.flat):
        bs_heatmap = pitch.bin_statistic(
            glob[idx]["x"]["start"],
            glob[idx]["y"]["start"],
            statistic="count",
            bins=bins,
        )
        hm = pitch.heatmap(bs_heatmap, ax=ax, cmap="Blues")
        name = f"{names[idx]}"
        fm = pitch.flow(
            glob[idx]["x"]["start"],
            glob[idx]["y"]["start"],
            glob[idx]["x"]["end"],
            glob[idx]["y"]["end"],
            color="black",
            arrow_length=10,
            bins=bins,
            ax=ax,
            arrow_type="same",
        )

        ax.set_title(name, fontsize=18)
        if idx == number_of_rel:
            break

    st.pyplot(fig)


def create_arrowmap(glob, pattern, pitch, titles=None):
    """
    Function to create and display a grid of pitches
    :param glob: data
    :param pattern: pattern to be matched
    :param pitch: Pitch object
    :param titles: array of titles for each pitch
    :return: nothing
    """
    number_of_rel = len(pattern) - 1

    fig, axs = pitch.grid(
        nrows=int(ceil((number_of_rel + 1) / 4)),
        ncols=4,
        space=0.1,
        figheight=5,
        title_height=0,
        endnote_height=0,  # no title/ endnote
        grid_width=0.9,
        grid_height=0.98,
        bottom=0.01,
        left=0.05,
    )

    if not titles:
        names = [
            pattern + " : " + "location" + " of p" + str(i)
            for i in range(number_of_rel)
        ] + [pattern + " Overall"]
    else:
        names = titles
    for idx, ax in enumerate(axs.flat):
        name = f"{names[idx]}"
        pitch.arrows(
            glob[idx]["x"]["start"],
            glob[idx]["y"]["start"],
            glob[idx]["x"]["end"],
            glob[idx]["y"]["end"],
            width=2,
            headwidth=10,
            headlength=10,
            color="#ad993c",
            ax=ax,
        )

        ax.set_title(name, fontsize=13)
        if idx == number_of_rel:
            break

    st.pyplot(fig)


def pattern_positions():
    """
    Streamlit wrapper
    """
    uri = st.secrets["uri"]
    user = st.secrets["user"]
    password = st.secrets["password"]
    app = App_grids(uri, user, password)

    st.title("Pattern positions")

    st.markdown(
        """

    Another interesting visualization is to understand how passing motifs evolve in space. To do this we have available, in each passage, the location from which it starts and the one in which it arrives.

In this page it is possible to visualize this information for all the passing motifs of length four. It is produced a table of 24 graphs in which each row is a different passing motif and each column is the position of departure and arrival of the passes (p0, p1, p2, where passing motif is """
    )
    st.code("X-[p0]->Y-[p1]->W-[p2]->Z")

    st.markdown(
        """ where _XYWZ_ depend on pattern that is being matched). An overall column in the pattern and an overall column in the pass are also added.



There are 3 possibile visualization of the data described above, for each of them you can specify the match, the team and some additional parameters (for example the kernel bandwidth for the heatmaps).

**Heatmaps** :
You can specify below the match, the team and the bandwidth of the kernels (rule of thumb: the lower the value, the less influence the points have on each other, the more the chart is composed of disconnected clusters)

**Flow**:
In this graph the field is divided into bins and the passes coming from that area are grouped to define the color of the cell (simply defined by the number of passes started from that cell) and the direction of the arrow (which points in the average direction of the passes started from that cell). You can specify the number of horizontal and vertical bins.

**Arrows**:
Each pass is simply represented as an arrow that connects the starting and ending point. No extra parameters are required here.
   

    
    
    """
    )
    with st.form("Inputs"):
        type = st.selectbox("Select the visualization", ["Heatmap", "Flow", "Arrows"])
        c1, c2 = st.columns(2)
        with c1:
            team = st.selectbox("Specify Team: ", getTeams()).upper()

        with c2:
            games = getGamesList()
            game = st.selectbox("Specify the match: ", games.keys())
            match = games[game]

        with st.expander("Extra parameters for heatmaps"):
            c1, c2 = st.columns(2)
            with c1:
                bw1 = st.slider("Select start position bandwidth ", 0.001, 4.0, 0.3)
                show_start = st.checkbox(
                    "Show start position density on the chart", True
                )
            with c2:
                bw2 = st.slider("Select end position bandwidth ", 0.001, 4.0, 0.2)
                show_end = st.checkbox("Show end position density on the chart", True)

        with st.expander("Extra parameters for flow"):
            c1, c2 = st.columns(2)
            with c1:
                vbin = st.slider("Vertical bins", 1, 20, 6)
            with c2:
                hbin = st.slider("Horizontal bins", 1, 20, 4)

        if st.form_submit_button("Create the plot"):
            st.warning(
                "The graphic is created from scratch every time and streamlit takes a while to render. The operation can take tens of seconds."
            )

            if type == "Heatmap":
                st.success("Blue = starting position Orange = finish position")

            globs = []

            pitch = VerticalPitch(
                line_color="#cfcfcf", line_zorder=2, pitch_color="#122c3d"
            )  # , figsize=(3, 2))

            for pattern in ["ABAC", "ABAB", "ABCD", "ABCA", "ABCB"]:
                try:
                    a = get_map_data(pattern, team, match, app=app)
                    if type == "Heatmap":
                        create_heatmap(
                            a,
                            pattern,
                            pitch=pitch,
                            bw0=bw1,
                            bw1=bw2,
                            show_start=show_start,
                            show_end=show_end,
                        )
                    elif type == "Flow":
                        create_flowmap(a, pattern, pitch=pitch, bins=(vbin, hbin))
                    elif type == "Arrows":
                        create_arrowmap(a, pattern, pitch=pitch)

                    globs.append(a)
                except LinAlgError:
                    st.error(
                        "Linear algebra error in seaborn library. I think it's due to the fact that there are too few points to calculate the density."
                    )

            vertical_glob = []
            for i in range(4):
                vertical_glob.append(
                    {"x": {"start": [], "end": []}, "y": {"start": [], "end": []}}
                )

            for glob in globs:
                for pattern in range(len(glob)):
                    vertical_glob[pattern]["x"]["start"] += glob[pattern]["x"]["start"]
                    vertical_glob[pattern]["x"]["end"] += glob[pattern]["x"]["end"]
                    vertical_glob[pattern]["y"]["start"] += glob[pattern]["y"]["start"]
                    vertical_glob[pattern]["y"]["end"] += glob[pattern]["y"]["end"]
            if type == "Heatmap":
                create_heatmap(
                    vertical_glob,
                    "AAAA",
                    pitch,
                    [
                        "Overall location of p0",
                        "Overall location of p1",
                        "Overall location of p2",
                        "Overall location",
                    ],
                    bw0=bw1,
                    bw1=bw2,
                    show_start=show_start,
                    show_end=show_end,
                )
            elif type == "Flow":
                create_flowmap(
                    vertical_glob,
                    "AAAA",
                    pitch,
                    ["Overall of p0", "Overall of p1", "Overall of p2", "Overall "],
                )
            elif type == "Arrows":
                create_arrowmap(
                    vertical_glob,
                    "AAAA",
                    pitch,
                    [
                        "Overall location of p0",
                        "Overall location of p1",
                        "Overall location of p2",
                        "Overall location",
                    ],
                )

            st.balloons()
