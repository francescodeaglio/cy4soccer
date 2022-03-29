import streamlit as st

def create_nodes(lineups):

    players = {player["player_name"]: {
        "player_id": player["player_id"],
        "player_name": player["player_name"],
        "jersey_number": player["jersey_number"],
        "country" : player["country"]["name"],
        "cards" : player["cards"],
        "positions" : player["positions"],
        "starting":None,
    }
        for team in lineups for player in team["lineup"]}

    for player in players:
        try:
            if players[player]["positions"][0]["start_reason"] == 'Substitution - On (Tactical)':
                players[player]["starting"] = False
        except IndexError:
            players[player]["starting"] = True

    for player in players:
        if players[player]["starting"] is None:
            print(players[player])

    st.json(players)

def create_nodes_after_rumble_preprocessing(lineups):
    pass
