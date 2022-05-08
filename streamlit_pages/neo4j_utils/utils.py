import streamlit as st


def cypherify_grids(string, team=None, match=None):
    """
    Function to automatically write cypher queries for the 3 grid sections
    :param string: pattern to be matched (ex ABAC)
    :param team: team
    :param match: match_id
    :return: cypher query string
    """
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


def isNet(array):
    """
    Wrapper to the recursive function pass_net_check
    :param array: list of char (ex list("ABACA"))
    :return:
    """
    vect = [0]*len(array)
    return pass_net_check(1, len(array),vect, array)


def pass_net_check(i, n, vect, check):
    """
    Function to check whether a given array describes a valid passing motif.
    Not optimal, it firstly creates all the possibile passing motifs and then checks if the one given in among them
    :param i:
    :param n:
    :param vect:
    :param check:
    :return:
    """
    if i == 1:
        vect[i - 1] = "A"
        return pass_net_check(2, n, vect, check)
    elif i == 2:
        vect[i - 1] = "B"
        return pass_net_check(3, n, vect, check)
    elif i == n + 1:
        if vect == check:
            return True
        else:
            return False
    else:
        for l in distinct_letters(vect, i - 2):

            vect[i - 1] = l
            a = pass_net_check(i + 1, n, vect, check)
            if a:
                return a
        vect[i - 1] = first_new_letter(vect, i - 1)
        a = pass_net_check(i + 1, n, vect, check)
        if a:
            return a


def first_new_letter(vect,end):
    """
    SImple function that returns the first unused letter
    :param vect: letters already used
    :param end: index upperbound in the array (it may contain dirty values from previous iterations)
    :return: the first new letter
    """
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "L", "M"]
    max_letter = max(vect[:end])
    return letters[letters.index(max_letter)+1]

def distinct_letters(vect, end):
    """
    Returns a list of distinct letters used in an array
    :param vect: letters with duplicates
    :param end: index upperbound in the array (it may contain dirty values from previous iterations)
    :return: list of distinct letters
    """
    el = set(vect[:end])
    el.discard(vect[end])
    return list(el)

def read(path):
    '''
    Read content of a file
    '''
    with open(path, 'r') as f:
        return f.read()


def getTeams():
    """
    Returns all the teams that have played Euro2020
    :return: a list of teams
    """
    return [
        'Belgium',
    'Finland',
    'Austria',
     'Croatia',
     'Czech_Republic',
     'Denmark',
     'England',
     'France',
     'Germany',
     'Hungary',
     'Italy',
     'Netherlands',
     'MACEDONIA_REPUBLIC_OF',
     'Poland',
     'Portugal',
     'Russia',
     'Scotland',
     'Slovakia',
     'Spain',
     'Sweden',
     'Switzerland',
     'Turkey',
     'Ukraine',
     'Wales']
def getGamesList():
    """
    Returns the list of euro2020 games
    :return: list of euro2020 games
    """
    return {
 'Denmark-Belgium': 3788757,
 'Finland-Russia': 3788753,
 'Switzerland-Turkey': 3788765,
 'Belgium-Italy': 3795107,
 'England-Denmark': 3795221,
 'Italy-England': 3795506,
 'England-Germany': 3794688,
 'Sweden-Ukraine': 3794692,
 'Croatia-Spain': 3794686,
 'Belgium-Portugal': 3794687,
 'Italy-Austria': 3794685,
 'Germany-Hungary': 3788774,
 'Croatia-Scotland': 3788771,
 'Czech Republic-England': 3788772,
 'Finland-Belgium': 3788768,
 'Ukraine-Austria': 3788767,
 'Hungary-France': 3788763,
 'England-Scotland': 3788759,
 'Ukraine-North Macedonia': 3788758,
 'England-Croatia': 3788745,
 'Netherlands-Ukraine': 3788746,
 'France-Switzerland': 3794691,
 'Netherlands-Czech Republic': 3794690,
 'Wales-Denmark': 3794689,
 'Russia-Denmark': 3788769,
 'Sweden-Slovakia': 3788761,
 'Portugal-Germany': 3788764,
 'Italy-Wales': 3788766,
 'Italy-Switzerland': 3788754,
 'Turkey-Wales': 3788755,
 'Portugal-France': 3788773,
 'Spain-Poland': 3788762,
 'Croatia-Czech Republic': 3788760,
 'Austria-North Macedonia': 3788747,
 'Turkey-Italy': 3788741,
 'Italy-Spain': 3795220,
 'North Macedonia-Netherlands': 3788770,
 'Switzerland-Spain': 3795108,
 'Ukraine-England': 3795187,
 'Czech Republic-Denmark': 3795109,
 'Netherlands-Austria': 3788756,
 'Poland-Slovakia': 3788749,
 'Spain-Sweden': 3788750,
 'Scotland-Czech Republic': 3788748,
 'France-Germany': 3788751,
 'Hungary-Portugal': 3788752,
 'Denmark-Finland': 3788742,
 'Slovakia-Spain': 3788775,
 'Sweden-Poland': 3788776,
 'Belgium-Russia': 3788743,
 'Wales-Switzerland': 3788744}


def cypherify(string, team = None, extra_filter = None):
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
        st.error(string+" is an invalid passing motif!")
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



