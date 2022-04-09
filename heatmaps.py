from neo4j import GraphDatabase
import streamlit as st
from numpy.linalg import LinAlgError

from utils import getTeams, getGamesList
from mplsoccer import VerticalPitch
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


def create_map(glob, pattern, location, pitch, titles=None, bw0=0.3, bw1=0.2, show_start = True, show_end = True):
    number_of_rel = len(pattern) - 1

    fig, axs = pitch.grid(nrows=int(ceil((number_of_rel + 1) / 4)), ncols=4, space=0.1, figheight=5,
                          title_height=0, endnote_height=0,  # no title/ endnote
                          grid_width=0.9, grid_height=0.98, bottom=0.01, left=0.05)

    if not titles:
        names = [pattern + " : " + location + " of p" + str(i) for i in range(number_of_rel)] + [pattern + " Overall"]
    else:
        names = titles
    for idx, ax in enumerate(axs['pitch'].flat):

        name = f'{names[idx]}'
        if show_start:
            kdeplot = pitch.kdeplot(glob[idx]["x"]["start"], glob[idx]["y"]["start"], ax=ax, shade=True, levels=7,
                                bw_method=bw0)
        if show_end:
            kdeplot2 = pitch.kdeplot(glob[idx]["x"]["end"], glob[idx]["y"]["end"], ax=ax, shade=True, levels=7,
                                bw_method=bw1)

        ax.set_title(name, fontsize=13)
        if idx == number_of_rel:
            break


    st.pyplot(fig)


def heatmap():
    uri = st.secrets["uri"]

    user = "streamlit"
    password = st.secrets["password"]
    app = App(uri, user, password)
    st.title("Heatmaps")

    st.write("""
    
    Another interesting visualization is to understand how passage patterns evolve in space. To do this we have available, in each passage, the location from which it starts and the one in which it arrives.

In this page it is possible to visualize this information for all the passage patterns of length four. It is produced a table of 24 graphs in which each row is a different passage pattern and each column is the position of departure and arrival of the passages (p0, p1, p2, where passage pattern is X-[p0]->Y-[p1]->W-[p2]->Z where XYWZ depend on pattern that is being matched). An overall column in the pattern and an overall column in the passage are also added.

You can specify below the match, the team and the bandwidth of the kernels (rule of thumb: the lower the value, the less influence the points have on each other, the more the chart is composed of disconnected clusters)
    
    """)

    c1, c2 = st.columns(2)

    with c1:
        team = st.selectbox("Specify Team: ", getTeams()).upper()
        bw1 = st.slider("Select start position bandwidth ", 0.001, 4.0, 0.3)
        show_start = st.checkbox("Show start position density on the chart", True)

    with c2:
        games = getGamesList()
        game = st.selectbox("Specify the match: ", games.keys())
        match = games[game]
        bw2 = st.slider("Select end position bandwidth ", 0.001, 4.0, 0.2)
        show_end = st.checkbox("Show end position density on the chart", True)

    if st.button("Create the plot"):

        st.warning("The graphic is created from scratch every time and streamlit takes a while to render. The operation can take tens of seconds.")
        st.success("If both are plotted, Blue = starting position Orange = finish position")

        globs = []
        pitch = VerticalPitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#122c3d', figsize = (3,2))
        for pattern in ["ABAC", "ABAB", "ABCD", "ABCA", "ABCB"]:
            try :
                a = get_map_data(pattern, team, match, app=app, pitch=pitch)
                create_map(a, pattern, "location", pitch=pitch, bw0=bw1, bw1=bw2, show_start= show_start, show_end=show_end)
                globs.append(a)
            except LinAlgError:
                st.error("Linear algebra error in seaborn library. I think it's due to the fact that there are too few points to calculate the density.")

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
                   ["Overall location of p0", "Overall location of p1", "Overall location of p2", "Overall location"], bw0 = bw1, bw1 = bw2)

        st.balloons()


