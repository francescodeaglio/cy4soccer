import streamlit as st
import pymongo

import plotly.express as px

from streamlit_pages.neo4j_utils.utils import getTeams, getGamesList


def get_sunburst(data_in):
    """
    Function that creates a sunburst diagram (plotly) from data
    :param data_in: data queried from mongodb
    :return: the plotly chart
    """
    patterns = []
    prefixes = []
    values = []
    colors = []
    for res in data_in:
        patterns.append(res)
        prefixes.append(res[:-1])
        values.append(data_in[res])
        colors.append(res[0:4] if len(res) >= 4 else 12)

    prefixes[0] = ""
    data = dict(
        patterns=patterns,
        prefixes=prefixes,
        values=values
    )

    fig = px.sunburst(data,
                      names="patterns",
                      parents="prefixes",
                      values="values",
                      color=prefixes
                      )
    return fig

def get_data(team, match):
    """
    FUnction to perform the query on mongoDb. Auth credentials are hidden.
    :param team: team
    :param match: match_id (-1 to get all the games from a team (GROUP BY team COUNT..)
    :return: the queried data from mongo
    """
    client = pymongo.MongoClient(st.secrets["mongostring"])
    db = client.soccer_analytics
    col = db["sunburst_cache"]
    res = col.find_one({"team": team, "match_id": match})
    if res is not None:
        return res["data"]
    st.error("Please make sure that the selected team played the selected game.")
    return None


def sunburst_mongo():
    """
    Streamlit wrapper
    """

    st.title("Sunburst diagrams")


    st.write("""
    The idea of this diagram is to see how the various passing motifs evolve. For example, an AB network can continue by becoming ABA, ABC or by changing possession (lost ball, shot, end of game...).

In order to represent this, we have used the sunburst diagram. To speed up the GUI we have pre-calculated the values for all teams and all games. Data is "cached" on MongoDb.
   
The graphs are interactive. For example, if you click on ABA, it shows you the graph with ABA as the starting pattern (thus removing its "brothers" ABC and AB-lost).
    """)

    with st.form("Input info"):
        c1, c2 = st.columns(2)

        with c1:
            team = st.selectbox("Specify Team: ", getTeams()).upper()

        with c2:
            games =  getGamesList()
            game = st.selectbox("Specify the match: ", ["All games played by the selected team"] + list(games.keys()))
            if game == "All games played by the selected team":
                match = -1
            else:
                match = games[game]

        if st.form_submit_button("Create the plot"):
            res = get_data(team, match)
            if res:
                fig = get_sunburst(res)

                st.plotly_chart(fig, use_container_width=True)

    with st.expander("Credits"):
            st.text("""Developed by Francesco Deaglio and Filippo Costa""")
