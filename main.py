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

def first_form():

    with st.form("Pattern"):
        c = st.columns(2)
        st.session_state["pattern"] = c[0].text_input("Search for a pattern: ")

        st.session_state["team"] = c[1].selectbox("Specify Team: ", ["Both", *teams])
        if st.session_state["team"] == "Both":
            st.session_state["team"] = None

        advanced = st.checkbox("Set advanced parameters")
        submit = st.form_submit_button("Next step")
    if advanced and submit:
        st.session_state["step"] = 1
        st.experimental_rerun()
    if submit:
        st.session_state["step"] = 2
        st.experimental_rerun()

def second_form():

    if st.session_state["team"] == "Belgium":

        fp = open("players_belgium.txt", "r")
        players = [ p.strip() for p in fp]

    elif st.session_state["team"] == "Denmark":

        fp = open("players_denmark.txt", "r")
        players = [ p.strip() for p in fp]

    else:
        fp = open("players_belgium.txt", "r")
        players_belgium = [p.strip() for p in fp]
        fp = open("players_denmark.txt", "r")
        players_denmark = [p.strip() for p in fp]


        players =  players_belgium + players_denmark





    with st.form("Advanced"):
        options = ["Unconstrained"] + players

        letters = sorted(list(set(st.session_state["pattern"])))
        c = st.columns(2)
        bounding = {}
        for letter in letters:
            bounding[letter] = c[(letters.index(letter)) % 2].selectbox("Insert player name for " + letter, options)

        print(bounding)
        st.session_state["bounding"] = bounding
        query = st.form_submit_button("Query the data!")
    if query:
        st.session_state["step"] = 2
        st.experimental_rerun()

def query():
    uri = st.secrets["uri"]

    user = "neo4j"
    password = st.secrets["password"]
    app = App(uri, user, password)

    extra_filter = " ".join( [" and " + letter + '.name = "' + st.session_state["bounding"][letter] + '"' for letter in st.session_state["bounding"] if st.session_state["bounding"][letter] is not "Unconstrained"])
    print(extra_filter)
    query = cypherify(st.session_state["pattern"], st.session_state["team"], extra_filter)

    if query:
        app.find_pattern(query, st.session_state["pattern"])
        if st.button("New query"):

            del st.session_state["step"]
            st.experimental_rerun()


if __name__ == '__main__':


    teams = ["Belgium", "Denmark"]
    st.title(" vs ".join(teams))

    if "step" not in st.session_state:
        st.session_state["step"] = 0
        st.session_state["bounding"] = []

    if st.session_state["step"] == 0:
        first_form()

    if st.session_state["step"] == 1:
        second_form()

    if st.session_state["step"] == 2:
        query()






