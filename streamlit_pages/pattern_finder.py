import streamlit as st
from streamlit_pages.neo4j_utils.neo4j_app import App
from streamlit_pages.neo4j_utils.utils import isNet, getGamesList, getTeams


def cypherify(string, team=None, match_id=None, extra_filter=None):
    """
    Utils function to automatically write cypher queries
    :param string: pattern to be matched (ex ABACA)
    :param team: team
    :param match_id: match_id
    :param extra_filter: extra text filter
    :return: the cypher query
    """
    letters = list(string)
    if not isNet(letters):
        st.error(string+" is an invalid passage network!")
        return None

    if team:
        query = "MATCH (A:"+team+")"
        for i in range(len(string) - 1):
            query += "-[p" + str(i) + ":PASS]->(" + letters[i + 1] + ":"+team+")"
    else:
        query = "MATCH (A)"
        for i in range(len(string) - 1):
            query += "-[p" + str(i) + ":PASS]->(" + letters[i + 1] + ")"

    query += "\nWHERE "

    #correct order
    first = True
    for i in range(len(string) - 2):
        if first:
            query += "p" + str(i) + ".order + 1 = p" + str(i + 1) + ".order"
            first = False
        else:
            query += " and p" + str(i) + ".order + 1 = p" + str(i + 1) + ".order"

    #same possession
    first = True
    for i in range(len(string) - 2):
        if first:
            query += " and p" + str(i) + ".possession = p" + str(i + 1) + ".possession"
            first = False
        else:
            query += " and p" + str(i) + ".possession = p" + str(i + 1) + ".possession"

    #same match
    first = True
    for i in range(len(string) - 2):
        if first:
            query += " and p" + str(i) + ".match_id = p" + str(i + 1) + ".match_id"
            first = False
        else:
            query += " and p" + str(i) + ".match_id = p" + str(i + 1) + ".match_id"
    #bound match

    query += " and p0.match_id = "+str(match_id)
    #different players
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


def pattern_finder():
    """
    Streamlit wrapper
    """

    st.title("Pattern finder")

    if "step" not in st.session_state:
        st.session_state["step"] = 0
        st.session_state["bounding"] = []

    if st.session_state["step"] == 0:
        first_form()

    if st.session_state["step"] == 1:
        second_form()

    if st.session_state["step"] == 2:
        query()

def first_form():
    """
    First page of the streamlit form
    """

    with st.form("Pattern"):
        c = st.columns(2)
        st.session_state["pattern"] = c[0].text_input("Search for a pattern: ")

        st.session_state["team"] = c[1].selectbox("Specify Team: ", getTeams()).upper()
        games = getGamesList()
        game = c[0].selectbox("Specify the match: ", games.keys())
        st.session_state["match"] = games[game]
        advanced = c[1].checkbox("Specify player(s) name")
        st.session_state["only query"] = c[1].checkbox("Show only the query (but not execute it)")
        submit = st.form_submit_button("Next step")
    if advanced and submit:
        if len(st.session_state["pattern"]) < 2:
            st.error("Please insert a valid pattern")
        else:
            st.session_state["step"] = 1
            st.experimental_rerun()
    if submit:
        if len(st.session_state["pattern"]) < 2:
            st.error("Please insert a valid pattern")
        else:
            st.session_state["step"] = 2
            st.experimental_rerun()

def second_form():
    """
    Second page of the streamlit form. Used for advanced filters
    """

    with st.form("Advanced"):

        st.write("Searching for pattern "+ st.session_state["pattern"]+" in match " + str(st.session_state["match"]))
        letters = sorted(list(set(st.session_state["pattern"])))
        c = st.columns(2)
        bounding = {}
        for letter in letters:
            bounding[letter] = c[(letters.index(letter)) % 2].text_input("Insert player name for " + letter)

        print(bounding)
        st.session_state["bounding"] = bounding
        query = st.form_submit_button("Query the data!")
    if query:
        st.session_state["step"] = 2
        st.experimental_rerun()

def query():
    """
    Last page of the form, where results are shown
    """
    uri = st.secrets["uri"]

    user = "streamlit"
    password = st.secrets["password"]
    app = App(uri, user, password)

    extra_filter = " ".join( [" and " + letter + '.name = "' + st.session_state["bounding"][letter] + '"' for letter in st.session_state["bounding"] if st.session_state["bounding"][letter] is not ""])
    print(extra_filter)
    query = cypherify(st.session_state["pattern"], st.session_state["team"], st.session_state["match"], extra_filter)


    if query:
        if st.session_state["only query"]:
            st.code(query)
        else:
            app.find_pattern(query, st.session_state["pattern"])
    if st.button("New query"):
       del st.session_state["step"]
       st.experimental_rerun()


