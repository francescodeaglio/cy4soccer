import streamlit as st
import json

from rumble_preprocessing import preprocess_lineups, preprocess_passes
from utils import isNet, distinct_letters, first_new_letter

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
        st.error(string+" is an invalid passage network!")
        return None


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
    print(query)
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

        fp = open("data/players_static/players_belgium.txt", "r")
        players = [ p.strip() for p in fp]

    elif st.session_state["team"] == "Denmark":

        fp = open("data/players_static/players_denmark.txt", "r")
        players = [ p.strip() for p in fp]

    else:
        fp = open("data/players_static/players_belgium.txt", "r")
        players_belgium = [p.strip() for p in fp]
        fp = open("data/players_static/players_denmark.txt", "r")
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

def search_pass_net(i, n, vect, app, silent):
    if i == 1:
        vect[i - 1] = "A"
        search_pass_net(2, n, vect, app, silent)
    elif i == 2:
        vect[i - 1] = "B"
        search_pass_net(3, n, vect, app, silent)
    elif i == n + 1:
        pattern = "".join(vect)
        query = cypherify(pattern)

        app.find_pattern(query, pattern, silent)

        return
    else:
        for l in distinct_letters(vect, i - 2):
            vect[i - 1] = l
            search_pass_net(i + 1, n, vect, app, silent)
        vect[i - 1] = first_new_letter(vect, i - 1)
        search_pass_net(i + 1, n, vect, app, silent)

def find_all_patterns():
    with st.form("Max length"):
        c1, c2 = st.columns(2)
        val = c1.text_input("Pattern length (min=3)", value=3)
        val = int(val)
        silent = c2.checkbox("Show only count")
        sub = st.form_submit_button("Search")

    if sub and val >= 3:
        uri = st.secrets["uri"]

        user = "neo4j"
        password = st.secrets["password"]
        app = App(uri, user, password)
        search_pass_net(1, val, [0] * val, app, silent)


if __name__ == '__main__':


    teams = ["Belgium", "Denmark"]
    st.title(" vs ".join(teams))

    with st.expander("Query"):
        if "step" not in st.session_state:
            st.session_state["step"] = 0
            st.session_state["bounding"] = []

        if st.session_state["step"] == 0:
            first_form()

        if st.session_state["step"] == 1:
            second_form()

        if st.session_state["step"] == 2:
            query()

    with st.expander("Search all possible passing nets"):
        find_all_patterns()
                
                
        






