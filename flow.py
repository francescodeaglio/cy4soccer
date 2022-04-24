from neo4j import GraphDatabase
import streamlit as st

from utils import getTeams, getGamesList
from mplsoccer import VerticalPitch, Pitch
import matplotlib.pyplot as plt


def cypherify(string, team=None, match=None):
    letters = list(string)

    if team:
        query = "MATCH p=(A:" + team + ")"
        for i in range(len(string) - 1):
            query += "-[p" + str(i) + ":PASS]->(" + letters[i + 1] + ":" + team + ")"
    else:
        query = "MATCH (A)"
        for i in range(len(string) - 1):
            query += "-[p" + str(i) + ":PASS]->(" + letters[i + 1] + ")"

    query += "\nWHERE "

    # correct order
    first = True
    for i in range(len(string) - 2):
        if first:
            query += "p" + str(i) + ".order + 1 = p" + str(i + 1) + ".order"
            first = False
        else:
            query += " and p" + str(i) + ".order + 1 = p" + str(i + 1) + ".order"

    # same possession
    first = True
    for i in range(len(string) - 2):
        if first:
            query += " and p" + str(i) + ".possession = p" + str(i + 1) + ".possession"
            first = False
        else:
            query += " and p" + str(i) + ".possession = p" + str(i + 1) + ".possession"

    # same match
    first = True
    for i in range(len(string) - 2):
        if first:
            query += " and p" + str(i) + ".match_id = p" + str(i + 1) + ".match_id"
            first = False
        else:
            query += " and p" + str(i) + ".match_id = p" + str(i + 1) + ".match_id"

    if match and string != "AB":
        query += " and p0.match_id = " + str(match)
    elif match:
        query += " p0.match_id = " + str(match) + " and "

    # different players
    unorderedPairGenerator = ((x, y) for x in set(letters) for y in set(letters) if y > x)
    if string != "AB":
        query += " and " + " and ".join([x + ".name <>" + " " + y + ".name" for x, y in list(unorderedPairGenerator)])
    else:
        query += " and ".join([x + ".name <>" + " " + y + ".name" for x, y in list(unorderedPairGenerator)])

    query += "\nRETURN " + ", ".join(["p" + str(i) + "." + "location " for i in range(len(string) - 1)])
    query += ", " + ", ".join(["p" + str(i) + "." + "end_location" for i in range(len(string) - 1)])

    return query


class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def find_pattern(self, query_string):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_pattern, query_string)
            return result

    @staticmethod
    def _find_and_return_pattern(tx, query_string):
        result = tx.run(query_string)
        return [row for row in result]


from numpy import ceil


def get_map_data(pattern, team, match, app, pitch):
    query = cypherify(pattern, team, match)
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


def create_map(glob, pattern, location, pitch, titles=None, bins=(6, 4)):
    number_of_rel = len(pattern) - 1

    fig, axs = pitch.grid(nrows=int(ceil((number_of_rel + 1) / 4)), ncols=4, space=0.1, figheight=5,
                          title_height=0, endnote_height=0,  # no title/ endnote
                          grid_width=0.9, grid_height=0.98, bottom=0.01, left=0.05)

    if not titles:
        names = [pattern + " : " + location + " of p" + str(i) for i in range(number_of_rel)] + [pattern + " Overall"]
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
    uri = st.secrets["uri"]

    user = "streamlit"
    password = st.secrets["password"]
    app = App(uri, user, password)
    st.title("Flow")

    st.write("""
    
    On this page you can see exactly the same information as in the "Heatmaps" section, but represented differently. 
    
    In this graph the field is divided into bins and the passages coming from that area are grouped to define the color of the cell (simply defined by the number of passages started from that cell) and the direction of the arrow (which points in the average direction of the passages started from that cell)""")

    c1, c2 = st.columns(2)

    with c1:
        team = st.selectbox("Specify Team: ", getTeams()).upper()
        vbin = st.slider("Vertical bins", 1, 20, 6)

    with c2:
        games = getGamesList()
        game = st.selectbox("Specify the match: ", games.keys())
        match = games[game]
        hbin = st.slider("Horizontal bins", 1, 20, 4)

    if st.button("Create the plot"):

        st.warning(
            "The graphic is created from scratch every time and streamlit takes a while to render. The operation can take tens of seconds.")


        globs = []
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
        for pattern in ["ABAC", "ABAB", "ABCD", "ABCA", "ABCB"]:
            a = get_map_data(pattern, team, match, app=app, pitch=pitch)

            create_map(a, pattern, "location", pitch=pitch, bins=(vbin, hbin))
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

        create_map(vertical_glob, "AAAA", "location", pitch,
                   ["Overall of p0", "Overall of p1", "Overall of p2", "Overall "], )

        st.balloons()
