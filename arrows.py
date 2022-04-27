import streamlit as st
from utils import getTeams, getGamesList, cypherify_grids
from mplsoccer import Pitch
from numpy import ceil
from App_grids import App_grids


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
            glob[number_of_rel]["x"]["start"].append(row["p" + str(i) + "." + "location"][0])
            glob[number_of_rel]["y"]["start"].append(row["p" + str(i) + "." + "location"][1])
            glob[number_of_rel]["x"]["end"].append(row["p" + str(i) + "." + "end_location"][0])
            glob[number_of_rel]["y"]["end"].append(row["p" + str(i) + "." + "end_location"][1])

    return glob


def create_map(glob, pattern, pitch, titles=None):
    """
    Function to create and display a grid of pitches
    :param glob: data
    :param pattern: pattern to be matched
    :param pitch: Pitch object
    :param titles: array of titles for each pitch
    :return: nothing
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

        name = f'{names[idx]}'
        pitch.arrows(glob[idx]["x"]["start"], glob[idx]["y"]["start"],
                     glob[idx]["x"]["end"], glob[idx]["y"]["end"], width=2,
                     headwidth=10, headlength=10, color='#ad993c', ax=ax)

        ax.set_title(name, fontsize=13)
        if idx == number_of_rel:
            break

    st.pyplot(fig)


def arrows():
    """
    Streamlit wrapper for this page
    """
    uri = st.secrets["uri"]

    user = "streamlit"
    password = st.secrets["password"]
    app = App_grids(uri, user, password)
    st.title("Arrows")

    st.write("""
    
    On this page you can see exactly the same information as in the "Heatmaps" section, but represented differently. 
    
    Each pass in fact does not contribute to create a gaussian density but is simply represented as an arrow that connects the starting and ending point.
    """)
    with st.form("Inputs"):
        c1, c2 = st.columns(2)

        with c1:
            team = st.selectbox("Specify Team: ", getTeams()).upper()

        with c2:
            games = getGamesList()
            game = st.selectbox("Specify the match: ", games.keys())
            match = games[game]

        if st.form_submit_button("Create the plot"):

            st.warning(
                "The graphic is created from scratch every time and streamlit takes a while to render. The operation can take tens of seconds.")

            globs = []
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
            for pattern in ["ABAC", "ABAB", "ABCD", "ABCA", "ABCB"]:
                a = get_map_data(pattern, team, match, app=app)

                create_map(a, pattern, pitch=pitch)
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
                       ["Overall location of p0", "Overall location of p1", "Overall location of p2", "Overall location"], )

            st.balloons()
