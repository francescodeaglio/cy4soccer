
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymongo
import streamlit as st
from matplotlib.projections import get_projection_class
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mplsoccer import Pitch
from neo4j import GraphDatabase

from streamlit_pages.neo4j_utils.utils import getGamesList, getTeams


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def find_pattern(self, query_string):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_pattern, query_string
            )
            return result  ##########<----- here you have to change with the data you inserted into the query.
            # for example if we have RETURN A.match_id, P, count(c) as cnt you can access to the returned values using
            # row["A.match_id"], row["P"] and row["cnt"] respectively

    @staticmethod
    def _find_and_return_pattern(tx, query_string):
        result = tx.run(query_string)
        return [row for row in result]


def players_with_coordinates(
    team,
    match_id,
    app,
):
    team_dict = {}
    player_number_mapping = {}

    query = (
        """MATCH (A:"""
        + team
        + """)-[h:HAS_PLAYED]->(N {match_id:"""
        + str(match_id)
        + """}) WHERE h.starting = true
    RETURN A.name, A.jersey_number"""
    )
    starters = app.find_pattern(query)

    average_position_query = 'MATCH r = (A:{team})-[p:PASS]->(B:{team}) WHERE p.match_id = {match_id} AND A.name = "{player}" RETURN AVG(p.location[0]) as avg_x, AVG(p.location[1]) as avg_y'
    for starter in starters:
        jersey_number = starter["A.jersey_number"]
        starter = starter["A.name"]

        query = average_position_query.format(
            team=team, match_id=match_id, player=starter
        )
        r = app.find_pattern(query)
        team_dict[starter] = [r[0]["avg_x"], r[0]["avg_y"]]
        player_number_mapping[starter] = jersey_number

    return team_dict, player_number_mapping


def Passer(player, match_id, app):
    string = 'MATCH (a)-[p:PASS]->(b) WHERE a.name = "{player}" and p.match_id = {game} RETURN p.angle, p.length'
    string = string.format(player=player, game=match_id)

    passages = app.find_pattern(string)

    angles = [passage["p.angle"] for passage in passages]
    lengths = [passage["p.length"] for passage in passages]

    d = {"pass.angle": angles, "pass.length": lengths}

    df1 = pd.DataFrame(d)
    bins = np.linspace(-np.pi, np.pi, 20)
    df1["binned"] = pd.cut(angles, bins, include_lowest=True, right=True)
    df1["Bin_Mids"] = df1["binned"].apply(lambda x: x.mid)
    df1 = df1[:-1]

    A = df1.groupby("Bin_Mids", as_index=False, dropna=False).mean()
    B = df1.groupby("Bin_Mids", as_index=False, dropna=False).count()
    A["count"] = B["pass.length"]
    A = A.dropna(axis=0)
    # A["Incomplete"] = 1-A["Complete"]

    return A


def plot_inset(width, axis_main, data, x, y, number):
    ax_sub = inset_axes(
        axis_main,
        width=width * 6,
        height=width * 6,
        loc=10,
        bbox_to_anchor=(x, y),
        bbox_transform=axis_main.transData,
        borderpad=0.0,
        axes_class=get_projection_class("polar"),
    )

    ax_sub.set_zorder(2)
    theta = data["Bin_Mids"]
    radii = data["pass.length"]
    color_metric = data["count"]
    bars = ax_sub.bar(theta, radii, width=0.3, bottom=0.0, zorder=2)

    ax_sub.patch.set_alpha(0)
    ax_sub.set_xticklabels([])
    ax_sub.set_yticks([])
    ax_sub.yaxis.grid(False)
    ax_sub.xaxis.grid(False)
    ax_sub.spines["polar"].set_visible(False)

    for r, bar, color in zip(theta, bars, color_metric):
        bar.set_facecolor(plt.cm.YlOrBr(color * 20))
        bar.set_alpha(1)

    ax_sub.text(
        0,
        0,
        str(number),
        size=50,
        ha="center",
        va="center",
        weight="bold",
        color="#a5fc03",
        path_effects=[
            path_effects.Stroke(linewidth=10, foreground="black"),
            path_effects.Normal(),
        ],
        zorder=3,
    )


def get_team_sonar(
    team_dict,
    TEAM,
    MATCH_ID,
    app,
    player_to_jersey_mapping,
    df,
    width=0.8,
    opposite_team=None,
    passer_df=None,
):
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, axs = pitch.grid(
        figheight=30,
        title_height=0.06,
        endnote_space=0,
        axis=False,
        title_space=0,
        grid_height=0.80,
        endnote_height=0.05,
    )
    fig.set_facecolor("#22312b")

    pitch.lines(
        df["fromx"],
        df["fromy"],
        df["tox"],
        df["toy"],
        lw=df["count"] / 3,
        ax=axs["pitch"],
        color="white",
        zorder=1,
    )

    if passer_df is None:
        passer_df = {}
        for player_name, loc in team_dict.items():
            data = Passer(player_name, MATCH_ID, app)
            plot_inset(
                width,
                axs["pitch"],
                data=data,
                x=loc[0],
                y=loc[1],
                number=player_to_jersey_mapping[player_name],
            )
            passer_df[player_name] = data.to_json()
    else:
        for player_name, loc in team_dict.items():
            data = pd.read_json(passer_df[player_name])
            plot_inset(
                width,
                axs["pitch"],
                data=data,
                x=loc[0],
                y=loc[1],
                number=player_to_jersey_mapping[player_name],
            )
    team_print = TEAM
    if TEAM == "MACEDONIA_REPUBLIC_OF":
        team_print = "North Macedonia".upper()
    elif TEAM == "CZECH_REPUBLIC":
        team_print = "Czech Republic".upper()

    axs["title"].text(
        0.5,
        0.50,
        team_print + " PASSING SONAR",
        color="#c7d5cc",
        va="center",
        ha="center",
        fontsize=100,
    )

    axs["title"].text(
        0.5,
        0.001,
        "vs " + opposite_team,
        color="#c7d5cc",
        va="center",
        ha="center",
        fontsize=45,
    )

    reversed = {
        player_to_jersey_mapping[player_name]: player_name
        for player_name in list(team_dict.keys())
    }

    reversed_order = sorted(list(reversed.keys()))

    axs["endnote"].text(
        1, 1, "Jersey numbers", color="#a5fc03", va="center", ha="right", fontsize=25
    )

    axs["endnote"].text(
        0,
        0.4,
        "Created with Cy4soccer",
        color="#c7d5cc",
        va="center",
        ha="left",
        fontsize=25,
    )

    joined = [reversed[key] + ": " + str(key) for key in reversed_order[:5]]
    joined = ", ".join(joined)
    axs["endnote"].text(
        1, 0.7, joined, color="#c7d5cc", va="center", ha="right", fontsize=25
    )

    joined = [reversed[key] + ": " + str(key) for key in reversed_order[5:]]
    joined = ", ".join(joined)
    axs["endnote"].text(
        1, 0.4, joined, color="#c7d5cc", va="center", ha="right", fontsize=25
    )

    st.pyplot(fig)

    return passer_df


def get_passagenetwork(players, team, match_id, app):
    matrix = [[0] * len(players) for i in range(len(players))]
    for player1 in players:
        i = players.index(player1)

        for player2 in players:
            j = players.index(player2)

            if i > j:
                query = 'MATCH r = (A:{team})-[p:PASS]-(B:{team}) WHERE p.match_id = {match_id} and A.name = "{player1}" and B.name = "{player2}" RETURN count(r) as cnt'
                query = query.format(
                    team=team, match_id=match_id, player1=player1, player2=player2
                )
                r = app.find_pattern(query)
                matrix[i][j] = r[0]["cnt"]

    return matrix


def create_pass_df(players, matrix, team_dict):
    diz = {"count": [], "fromx": [], "fromy": [], "tox": [], "toy": []}
    for player1 in players:
        i = players.index(player1)

        for player2 in players:
            j = players.index(player2)

            if i > j:
                diz["count"].append(matrix[i][j])
                diz["fromx"].append(team_dict[player1][0])
                diz["tox"].append(team_dict[player2][0])

                diz["fromy"].append(team_dict[player1][1])
                diz["toy"].append(team_dict[player2][1])
    return pd.DataFrame(diz)


def get_data_from_mongo(team, match):
    """
    FUnction to perform the query on mongoDb. Auth credentials are hidden.
    :param team: team
    :param match: match_id
    :return: the queried data from mongo
    """
    client = pymongo.MongoClient(st.secrets["mongostring"])
    db = client.soccer_analytics
    col = db["passing_sonar"]
    ret = col.find_one({"team": team, "match_id": match})

    if ret is not None:
        return ret["data"]
    else:
        return None


def cache_on_mongo(team, match, team_dict, player_to_jersey_mapping, df, passer_df):
    client = pymongo.MongoClient(st.secrets["mongostring"])
    db = client.soccer_analytics
    col = db["passing_sonar"]

    col.insert_one(
        {
            "team": team,
            "match_id": match,
            "data": {
                "team_dict": team_dict,
                "player_to_jersey_mapping": player_to_jersey_mapping,
                "df": df.to_json(),
                "passer_df": passer_df,
            },
        }
    )


def passagesonar():
    st.title("Passing Sonar")
    st.write(
        """On this page you can create the passing sonar for the chosen match and team. 
Players are positioned on the pitch according to their average position when they have made passes. In addition, the display of the team pass-net is added to complete the graph."""
    )
    uri = st.secrets["uri"]

    user = st.secrets["user"]
    password = st.secrets["password"]
    app = App(uri, user, password)
    with st.form("Input"):
        c1, c2 = st.columns(2)

        with c1:
            team = st.selectbox("Specify Team: ", getTeams())
            TEAM = team.upper()

        with c2:
            games = getGamesList()
            game = st.selectbox("Specify the match: ", games.keys())
            MATCH_ID = games[game]

        if st.form_submit_button("Create the plot"):
            try:
                opposite_team = game.split("-")
                if TEAM == "MACEDONIA_REPUBLIC_OF":
                    team = "North Macedonia"
                elif TEAM == "CZECH_REPUBLIC":
                    team = "Czech Republic"
                opposite_team.remove(team)
            except:
                pass
            # check if we have already computed the needed data
            cached = get_data_from_mongo(team=TEAM, match=MATCH_ID)
            s = st.empty()

            if cached is None:
                s.write("Getting players coordinates...")
                team_dict, player_to_jersey_mapping = players_with_coordinates(
                    TEAM, MATCH_ID, app
                )

                s.write("Evaluating passing matrix...")
                pass_matrix = get_passagenetwork(
                    list(player_to_jersey_mapping.keys()), TEAM, MATCH_ID, app
                )
                df = create_pass_df(
                    list(player_to_jersey_mapping.keys()), pass_matrix, team_dict
                )

                s.write("Creating the chart...")
                passer_df = get_team_sonar(
                    team_dict,
                    TEAM,
                    MATCH_ID,
                    app,
                    player_to_jersey_mapping,
                    df,
                    opposite_team=opposite_team[0],
                )
                s.write()
                cache_on_mongo(
                    TEAM, MATCH_ID, team_dict, player_to_jersey_mapping, df, passer_df
                )

            else:
                s.write(
                    "The data for this match has already been calculated. The visualisation will be much faster."
                )
                team_dict = cached["team_dict"]
                player_to_jersey_mapping = cached["player_to_jersey_mapping"]
                df = pd.read_json(cached["df"])
                passer_df = cached["passer_df"]
                get_team_sonar(
                    team_dict,
                    TEAM,
                    MATCH_ID,
                    app,
                    player_to_jersey_mapping,
                    df,
                    opposite_team=opposite_team[0],
                    passer_df=passer_df,
                )

    with st.expander("Credits"):
        st.text(
            """The tool is created from the $424 and $416 snippets from the 
soccer analytics course and the mplsoccer tutorial [1].
The queries are modified to use the graph database.

[1] https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_plots/plot_pass_network.html#sphx-glr-gallery-pitch-plots-plot-pass-network-py
"""
        )
