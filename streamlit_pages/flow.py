#no longer used, now moved in pattern_positions

import streamlit as st
from streamlit_pages.neo4j_utils.utils import getTeams, getGamesList, cypherify_grids
from mplsoccer import Pitch
from streamlit_pages.neo4j_utils.App_grids import App_grids
from numpy import ceil


def get_map_data(pattern, team, match, app):
    """
        function to perform queries on Neo4j db
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
            glob[number_of_rel]["x"]["start"].append(row["p" + str(i) + "." + "location"][0])
            glob[number_of_rel]["y"]["start"].append(row["p" + str(i) + "." + "location"][1])
            glob[number_of_rel]["x"]["end"].append(row["p" + str(i) + "." + "end_location"][0])
            glob[number_of_rel]["y"]["end"].append(row["p" + str(i) + "." + "end_location"][1])

    return glob


def create_map(glob, pattern, pitch, titles=None, bins=(6, 4)):
    """
    Function to plot a grid of flowmap
    :param glob: data
    :param pattern: pattern to be matched
    :param pitch: Pitch object
    :param titles: chart titles
    :param bins: number of (vertical_bins, horiziontal_bins) to split the pitch in
    """
    number_of_rel = len(pattern) - 1

    fig, axs = pitch.grid(nrows=int(ceil((number_of_rel + 1) / 4)), ncols=4, space=0.1, figheight=5,
                          title_height=0, endnote_height=0,  # no title/ endnote
                          grid_width=0.9, grid_height=0.98, bottom=0.01, left=0.05)

    if not titles:
        names = [pattern + " : " + "location" + " of p" + str(i) for i in range(number_of_rel)] + [pattern + " Overall"]
    else:
        names = titles
    for idx, ax in enumerate(axs['pitch'].flat):

        bs_heatmap = pitch.bin_statistic(glob[idx]["x"]["start"], glob[idx]["y"]["start"], statistic='count', bins=bins)
        hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Blues')
        name = f'{names[idx]}'
        fm = pitch.flow(glob[idx]["x"]["start"], glob[idx]["y"]["start"],
                        glob[idx]["x"]["end"], glob[idx]["y"]["end"], color='black',
                        arrow_length=10, bins=bins, ax=ax, arrow_type='same')

        ax.set_title(name, fontsize=18)
        if idx == number_of_rel:
            break

    st.pyplot(fig)


def flow():
    """
    Streamlit wrapper
    """
    uri = st.secrets["uri"]

    user = st.secrets["user"]
    password = st.secrets["password"]
    app = App_grids(uri, user, password)
    st.title("Flow")

    st.write("""
    
    On this page you can see exactly the same information as in the "Heatmaps" section, but represented differently. 
    
    In this graph the field is divided into bins and the passes coming from that area are grouped to define the color of the cell (simply defined by the number of passes started from that cell) and the direction of the arrow (which points in the average direction of the passes started from that cell)""")

    with st.form("inputs"):
        c1, c2 = st.columns(2)

        with c1:
            team = st.selectbox("Specify Team: ", getTeams()).upper()
            vbin = st.slider("Vertical bins", 1, 20, 6)

        with c2:
            games = getGamesList()
            game = st.selectbox("Specify the match: ", games.keys())
            match = games[game]
            hbin = st.slider("Horizontal bins", 1, 20, 4)

        if st.form_submit_button("Create the plot"):

            st.warning(
                "The graphic is created from scratch every time and streamlit takes a while to render. The operation can take tens of seconds.")

            globs = []
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
            for pattern in ["ABAC", "ABAB", "ABCD", "ABCA", "ABCB"]:
                a = get_map_data(pattern, team, match, app=app)

                create_map(a, pattern, pitch=pitch, bins=(vbin, hbin))
                globs.append(a)

            vertical_glob = []
            for i in range(4):
                vertical_glob.append({"x": {"start": [], "end": []}, "y": {"start": [], "end": []}})

            for glob in globs:
                for pattern in range(len(glob)):
                    vertical_glob[pattern]["x"]["start"] += glob[pattern]["x"]["start"]
                    vertical_glob[pattern]["x"]["end"] += glob[pattern]["x"]["end"]
                    vertical_glob[pattern]["y"]["start"] += glob[pattern]["y"]["start"]
                    vertical_glob[pattern]["y"]["end"] += glob[pattern]["y"]["end"]

            create_map(vertical_glob, "AAAA", pitch,
                       ["Overall of p0", "Overall of p1", "Overall of p2", "Overall "], )

            st.balloons()
