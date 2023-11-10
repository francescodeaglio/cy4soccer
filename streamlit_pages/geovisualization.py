import json
import os

import numpy as np
import pandas as pd
import pydeck as pdk
import pymongo
import streamlit as st
from neo4j import GraphDatabase
from pydeck.types import String
from skimage.transform import ProjectiveTransform

from streamlit_pages.neo4j_utils.utils import getGamesList, getTeams


def statsbomb2geo(x, y, stadium="Nya Parken"):
    """
    function to map statsbomb rectangular pitch to real pitch
    :param x: x coordinate (in Statsbomb notation)
    :param y: y coordinate (in Statsbomb notation)
    :param stadium: name of the stadium
    :return: geocoordinates in the given stadium
    """
    path = os.path.join(os.curdir, "data", "stadium_geo.json")
    fp = open(path, "r")
    data = json.load(fp)[stadium]
    fp.close()
    top_left = data["top_left"]
    bottom_right = data["bottom_right"]
    top_right = data["top_right"]
    bottom_left = data["bottom_left"]

    t = ProjectiveTransform()
    src = np.asarray([[0, 80], [0, 0], [120, 0], [120, 80]])

    dst = np.asarray([bottom_left, top_left, top_right, bottom_right])

    if not t.estimate(src, dst):
        raise Exception("estimate failed")

    data = np.asarray([[x, y]])
    data_local = t(data)
    return data_local[0][0], data_local[0][1]


def get_center(stadium):
    """
    function to get the center of a given pitch
    :param stadium: stadium name
    :return: coordinates of the center
    """
    path = os.path.join(os.curdir, "data", "stadium_geo.json")
    fp = open(path, "r")
    data = json.load(fp)[stadium]
    fp.close()
    points = [
        data["top_left"],
        data["bottom_right"],
        data["top_right"],
        data["bottom_left"],
    ]
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    centroid = (sum(x) / len(points), sum(y) / len(points))
    return centroid


class App:
    """
    Neo4j function
    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def query(self, query_string):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_pattern, query_string
            )
            return result

    def get_starters(self, team, match_id):
        """
        Function to get the starting XI of a given team on a given match
        :param team: the team
        :param match_id: match_id
        :return: list of starters names
        """
        query = (
            """MATCH (A:"""
            + team
            + """)-[h:HAS_PLAYED]->(N {match_id:"""
            + str(match_id)
            + """}) WHERE h.starting = true
                        RETURN A.name"""
        )
        return self.query(query)

    def get_stadium(self, match_id):
        """
        Function to get the stadium in which a game was played
        :param match_id: the identifier of the game
        :return: the name of the stadium
        """
        query = (
            "MATCH (n:GAME) WHERE n.match_id = " + str(match_id) + " RETURN n.stadium"
        )
        return self.query(query)[0]["n.stadium"]

    def get_average_positions(self, team, match_id, player):
        """
        Function to compute the average position of a given player in a specific match
        :param team: the team of the player
        :param match_id: the match_id
        :param player: player's name
        :return: a tuple with (avg_x, avg_y)
        """
        query = (
            """MATCH r = (A:"""
            + team
            + """)-[p:PASS]->(B:"""
            + team
            + """) WHERE p.match_id = """
            + str(match_id)
            + ' AND A.name = "'
            + player
            + '" RETURN AVG(p.location[0]) as avg_x, AVG(p.location[1]) as avg_y'
        )
        r = self.query(query)
        return (r[0]["avg_x"], r[0]["avg_y"])

    def compute_number_of_pass(self, team, match_id, player1, player2):
        """
        Function to compute the number of passes between a given couple of players
        :param team: the team of the players
        :param match_id: tha match
        :param player1: first player (symmetric)
        :param player2: second player (symmetric)
        :return: number of passages
        """
        query = (
            """MATCH r = (A:"""
            + team
            + """)-[p:PASS]-(B:"""
            + team
            + """) WHERE p.match_id = """
            + str(match_id)
            + ' and A.name = "'
            + player1
            + '" and B.name = "'
            + player2
            + '" RETURN count(r) as cnt'
        )
        r = self.query(query)
        return r[0]["cnt"]

    @staticmethod
    def _find_and_return_pattern(tx, query_string):
        result = tx.run(query_string)
        return [row for row in result]


def create_pitchdf(stadium):
    """
    Function to create a pitch with real world coordinates
    :param stadium: stadium name
    :return: the dataframe with the lines to create the pitch
    """
    path = os.path.join(os.curdir, "data", "stadium_geo.json")
    fp = open(path, "r")
    data = json.load(fp)[stadium]
    fp.close()
    top_left = data["top_left"]
    bottom_right = data["bottom_right"]
    top_right = data["top_right"]
    bottom_left = data["bottom_left"]

    diz = {
        "lng_s": [top_left[1], bottom_left[1], bottom_right[1], top_right[1]],
        "lat_s": [top_left[0], bottom_left[0], bottom_right[0], top_right[0]],
        "lng_to": [bottom_left[1], bottom_right[1], top_right[1], top_left[1]],
        "lat_to": [bottom_left[0], bottom_right[0], top_right[0], top_left[0]],
    }

    lines = [
        ((0, 18), (18, 18)),
        ((18, 18), (18, 62)),
        ((18, 62), (0, 62)),
        ((0, 30), (6, 30)),
        ((6, 30), (6, 50)),
        ((6, 50), (0, 50)),
        ((60, 0), (60, 80)),
    ]
    # symmetric points
    lines2 = []
    for start, end in lines:
        lines2.append(((120 - start[0], start[1]), (120 - end[0], end[1])))

    lines = lines + lines2

    for start, end in lines:
        start = statsbomb2geo(start[0], start[1], stadium)
        end = statsbomb2geo(end[0], end[1], stadium)
        diz["lng_s"].append(start[1])
        diz["lat_s"].append(start[0])
        diz["lng_to"].append(end[1])
        diz["lat_to"].append(end[0])

    pitch = pd.DataFrame(diz)
    return pitch


def compute_matrix(team, match_id, players, app, placeholder=st):
    """
    Function to compute the matrix of pass(ie matrix[i][j] = number of passbetween player i and j)
    :param team:
    :param match_id:
    :param players:
    :param app: object of class App
    :param placeholder: streamlit element on which show the progress bar
    :return: the computed matrix
    """
    cnt = 0
    pb = placeholder.progress(0)
    matrix = [[0] * len(players) for i in range(len(players))]
    for player1 in players:
        i = players.index(player1)
        player1 = player1["A.name"]

        for player2 in players:
            j = players.index(player2)
            player2 = player2["A.name"]
            if player1 != player2 and i > j:
                matrix[i][j] = app.compute_number_of_pass(
                    team, match_id, player1, player2
                )
            cnt += 1
            pb.progress(cnt / 121)
    return matrix


def compute_positions(team, match_id, players, stadium, app, placeholder=st):
    """
    Function to compute the average positions of every player in a given team
    :param team:
    :param match_id:
    :param players: list of players
    :param stadium: stadium name (to retrieve the coordinates)
    :param app:
    :param placeholder: streamlit element on which show the progress bar
    :return:
    """
    pb = placeholder.progress(0)
    positions = []
    for player in players:
        i = players.index(player)
        player = player["A.name"]
        x, y = app.get_average_positions(team, match_id, player)
        positions.append(statsbomb2geo(x, y, stadium=stadium))
        pb.progress((i + 1) / 11)

    return positions


def get_data_from_mongo(team, match):
    """
    FUnction to perform the query on mongoDb. Auth credentials are hidden.
    :param team: team
    :param match: match_id
    :return: the queried data from mongo
    """
    client = pymongo.MongoClient(st.secrets["mongostring"])
    db = client.soccer_analytics
    col = db["geovisualization_cache_matrix"]
    ret = col.find_one({"team": team, "match_id": match})

    if ret is not None:
        return ret["data"]
    else:
        return None


def cache_on_mongo(team, match, df):
    """
    Function to store the computed data on mongo and speedup following queries
    :param team:
    :param match:
    :param df: data to be stored (df, dfp, stadium)
    :return:
    """
    client = pymongo.MongoClient(st.secrets["mongostring"])
    db = client.soccer_analytics
    col = db["geovisualization_cache_matrix"]
    col.insert_one({"team": team, "match_id": match, "data": df})


def show_matrix(matrix, players):
    """
    Util function to display the passmatrix
    :param matrix:
    :param players:
    :return:
    """
    X = np.array(matrix)
    X = X + X.T - np.diag(np.diag(X))
    st.dataframe(
        pd.DataFrame(
            X,
            columns=[player[0] for player in players],
            index=[player[0] for player in players],
        )
    )


def show_positions(positions, players):
    st.dataframe(
        pd.DataFrame(
            positions,
            index=[starter[0] for starter in players],
            columns=["avg(lat)", "avg(lng)"],
        )
    )


def create_df(matrix, players, positions):
    """
    Function to create the dataframe used for the visualization.
    It takes the matrix of passand replaces the player indexes with their average position on the real pitch
    :param matrix:
    :param players:
    :param positions:
    :return:
    """
    diz = {
        "lng_h": [],
        "lat_h": [],
        "lng_w": [],
        "lat_w": [],
        "count": [],
        "p1": [],
        "p2": [],
    }

    for player1 in players:
        i = players.index(player1)
        player1 = player1["A.name"]

        for player2 in players:
            j = players.index(player2)
            player2 = player2["A.name"]

            if i > j:
                diz["lng_h"].append(positions[i][1])
                diz["lat_h"].append(positions[i][0])

                diz["lng_w"].append(positions[j][1])
                diz["lat_w"].append(positions[j][0])

                diz["p1"].append(player1)
                diz["p2"].append(player2)
                diz["count"].append(matrix[i][j])

    df = pd.DataFrame(diz)
    df["color"] = df["count"] / max(df["count"])

    return df


def get_layers(df, dfp, stadium):
    """
    Function to get pydeck layers
    :param df:
    :param dfp:
    :param stadium:
    :return:
    """
    RED_RGB = [240, 100, 0, 100]
    # javascript snippet to color the arrows based on color column described above
    GET_COLOR_JS = [
        "color * 255",
        "100",
        "255 * (1-color)",
        "255 * 0.4",
    ]
    # deckgl line layer to encode passages
    line_layer = pdk.Layer(
        "LineLayer",
        data=df,
        get_width=3,
        get_source_position=["lng_h", "lat_h"],
        get_target_position=["lng_w", "lat_w"],
        get_tilt=1,
        get_color=GET_COLOR_JS,
        pickable=True,
        auto_highlight=True,
    )
    # scatterplotlayer to show average position of players
    scatterplot = pdk.Layer(
        "ScatterplotLayer",
        dfp,
        pickable=False,
        opacity=10,
        stroked=False,
        filled=True,
        get_position=["lng", "lat"],
        get_fill_color=RED_RGB,
        get_radius=1,
    )
    # name of players
    text = pdk.Layer(
        "TextLayer",
        dfp,
        pickable=False,
        get_position=["lng", "lat"],
        get_text="name",
        get_size=18,
        get_color=[0, 0, 0],
        get_angle=0,
        # Note that string constants in pydeck are explicitly passed as strings
        # This distinguishes them from columns in a data set
        get_text_anchor=String("middle"),
        get_alignment_baseline=String("top"),
    )
    pitch = create_pitchdf(stadium)
    pitchl = pdk.Layer(
        "LineLayer",
        data=pitch,
        get_width=3,
        get_source_position=["lng_s", "lat_s"],
        get_target_position=["lng_to", "lat_to"],
        get_tilt=1,
        get_color=[0, 0, 0, 50],
        pickable=False,
        auto_highlight=True,
    )

    dft = pd.DataFrame(
        {"lng": [get_center(stadium)[1]], "lat": [get_center(stadium)[0]]}
    )
    center_r = pdk.Layer(
        "ScatterplotLayer",
        dft,
        get_position=["lng", "lat"],
        get_radius=5,
        pickable=False,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=2,
        get_fill_color=[255, 255, 255, 0],
        get_line_color=[0, 0, 0, 70],
        get_line_width=0.25,
    )

    return [line_layer, scatterplot, text, center_r, pitchl]


def geovisualization():
    """
    Streamlit wrapper
    """
    st.title("Geovisualization")

    st.write(
        """In this screen you can see an interactive version of the passing network.
    
The passes are mapped geographically to the stadium where the match was played (not that it was needed but it was a good excuse to learn how to use pydeck :) ).

The map is interactive and has tooltips when passing over the arches. 
     
The colourscale starts from blue (few passes between that pair of players) and goes up to red (many passes). At the moment only passes between starters are taken into account."""
    )
    uri = st.secrets["uri"]

    user = st.secrets["user"]
    password = st.secrets["password"]
    app = App(uri, user, password)
    with st.form("Input"):
        c1, c2 = st.columns(2)

        with c1:
            TEAM = st.selectbox("Specify Team: ", getTeams()).upper()

        with c2:
            games = getGamesList()
            game = st.selectbox("Specify the match: ", games.keys())
            MATCH_ID = games[game]

        if st.form_submit_button("Create the plot"):
            # checking if we have the data precomputed on mongo

            cached = get_data_from_mongo(team=TEAM, match=MATCH_ID)

            if cached is None:
                # Getting players
                starters = app.get_starters(TEAM, MATCH_ID)
                # Getting stadium
                stadium = app.get_stadium(MATCH_ID)
                # matrix of passages. Since it's symmetric, only the lower part is computed
                st.write("Evaluating the number of passbetween every couple of players")
                placeholder = st.empty()
                matrix = compute_matrix(TEAM, MATCH_ID, starters, app, placeholder)

                with placeholder.expander("Show the matrix"):
                    show_matrix(matrix, starters)

                # getting average positions of players in the real pitch
                st.write("Getting average positions of players in the real pitch")
                placeholder2 = st.empty()
                positions = compute_positions(
                    TEAM, MATCH_ID, starters, stadium, app, placeholder2
                )

                with placeholder2.expander("Show the computed data"):
                    show_positions(positions, starters)

                # creating the dataframe containing all the info for pydeck
                df = create_df(matrix, starters, positions)

                # df for players positions
                dfp = pd.DataFrame(
                    {
                        "lng": [position[1] for position in positions],
                        "lat": [position[0] for position in positions],
                        "name": [name[0].split()[-1] for name in starters],
                    }
                )

                cache_on_mongo(
                    team=TEAM,
                    match=MATCH_ID,
                    df={"df": df.to_json(), "dfp": dfp.to_json(), "stadium": stadium},
                )

            else:
                # parse the cached data
                df = pd.read_json(cached["df"])
                with st.expander("Show the matrix"):
                    st.dataframe(df)
                dfp = pd.read_json(cached["dfp"])
                with st.expander("Show the computed data"):
                    st.dataframe(dfp)
                stadium = cached["stadium"]

            layers = get_layers(df, dfp, stadium)
            center = get_center(stadium)
            view_state = pdk.ViewState(
                latitude=center[0],
                longitude=center[1],
                bearing=0,
                pitch=0,
                zoom=17.8,
            )

            TOOLTIP_TEXT = {"html": "{count} pass between {p1} and {p2}"}
            r = pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=TOOLTIP_TEXT,
                map_provider="carto",
                map_style="light",
            )
            if stadium == "Saint-Petersburg Stadium":
                st.warning(
                    "The St. Petersburg stadium is covered so it is impossible to take exact positions of the playing field."
                )

            st.pydeck_chart(r)
