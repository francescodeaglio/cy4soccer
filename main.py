import streamlit as st
import json

from rumble_preprocessing import preprocess_lineups, preprocess_passes
from utils import isNet


from neo4j_app import App

def load_new_team(game, nation):
    preprocess_lineups(str(game), nation)
    preprocess_passes(str(game),nation)

    uri = st.secrets["uri"]

    user = "neo4j"
    password = st.secrets["password"]

    app = App(uri, user, password)

    add_all_players(app, nation)
    add_all_passages(app, nation)


def add_all_players(app, team):
    with open("lineup_"+team+".json", encoding="utf-8") as r:
        a = json.load(r)
    for x in a:
        app.create_player(x, team)


def add_all_passages(app, team):
    with open("passes_"+team+".json", encoding="utf-8") as r:
        a = json.load(r)
    for x in a:
        app.create_passage(x)


def cypherify(string, team = None, extra_filter = None):
    letters = list(string)
    if not isNet(letters):
        print("Invalid passage network")
        return None
    else:
        print("Valid pattern")
    if team:
        query = "MATCH (A:"+team+")"
    else:
        query = "MATCH (A)"
    for i in range(len(string) - 1):
        query += "-[p" + str(i) + "]->(" + letters[i + 1] + ")"
    query += "\nWHERE "
    first = True
    for i in range(len(string) - 2):
        if first:
            query += "toInteger(p" + str(i) + ".order) + 1 = toInteger(p" + str(i + 1) + ".order)"
            first = False
        else:
            query += " and toInteger(p" + str(i) + ".order) + 1 = toInteger(p" + str(i + 1) + ".order)"
    query += " and p0.possession = p" + str(len(string) - 2) + ".possession"
    unorderedPairGenerator = ((x, y) for x in set(letters) for y in set(letters) if y > x)
    query += " and " + " and ".join([x + ".name <>" + " " +y + ".name" for x, y in list(unorderedPairGenerator)])
    if extra_filter:
        query+= extra_filter
    query += "\nRETURN A.name"
    s = set(letters)
    s.discard("A")

    for i in s:
        query += ", " + i + ".name"

    return query


if __name__ == '__main__':

    uri = st.secrets["uri"]

    user = "neo4j"
    password = st.secrets["password"]
    app = App(uri, user, password)

    teams = ["Belgium", "Denmark"]
    st.title(" vs ".join(teams))

    with st.form("Pattern"):
        c = st.columns(2)
        pattern = c[0].text_input("Search for a pattern: ")

        team = c[1].selectbox("Specify Team: ", ["Both", *teams])
        if team == "Both":
            team = None

        st.caption("Bound nodes")
        c = st.columns(2)
        bounding = {}

        letters = ["A", "B", "C", "D", "E", "F"]
        for letter in ["A", "B", "C", "D", "E", "F"]:
            bounding[letter] = c[(letters.index(letter))%2].text_input("Insert player name for "+letter)

        a = st.form_submit_button("Start query")

    if a:
        extra_filter = " ".join([" and "+letter+'.name = "'+ bounding[letter] +'"' for letter in bounding if bounding[letter] is not ""])
        query = cypherify(pattern, team, extra_filter)



        if query:
            app.find_pattern(query, pattern)


    app.close()

