import streamlit as st

def intro():
    st.title("Cy4soccer")
    st.write("""
    Neo4j is a database in which data is represented as graphs. A graph is made up of two main elements: nodes and the relationships that join them. 
    Each node and each relationship can have one or more labels (for example the nation of a player) and properties (for example the player's name and jersey number).
    
    This is an image of 25 nodes in the database. In total there are more than 600 nodes and about 60 thousand relationships stored.
    """)

    st.image("media/overall.jpeg")

    st.write("""
    In this quick intro will be shown how data are represented and how to write simple queries in Cypher.
    Cypher is a declarative query language (you specify what you want done, not how) specifically designed to match patterns.
    
    For example:
    """)

    st.code("""
    MATCH (a:ITALY)-[:HAS_PLAYED]->(g:GAME)<-[:HAS_PLAYED]-(b:ENGLAND)
WHERE a.name = "Gianluigi Donnarumma" and b.name = "Bukayo Saka"
RETURN g
    """)
    st.write("It returns all the Euro2020 matches in which Donnarumma played against Saka. In the next sections we will see the main ingredients to get to write this query.")
    st.image("media/donnarumma_saka.jpeg")

    st.header("Data Model")
    st.subheader("Nodes")
    st.write("""
    As written earlier, the main components are nodes and relationships. Let's now look at nodes.
    There are three categories of nodes: Matches, Players and Specials.
    """)

    with st.expander("Matches"):
        st.write("""
        All matches are labeled with the label GAME (MATCH is a word that is part of the cypher syntax). 
        
        
        For example, the following query returns all matches of Euro2020
        """)
        st.code("""
MATCH (a:GAME)
RETURN a        
        """)
        st.write("""
        As a countercheck we can count how many matches there are in the database and check that there are actually 51.
        """)
        st.code("""
MATCH (a:GAME)
RETURN count(a)        
                """, language="Cypher")
        st.write("""
        
        """)
        st.write("""
        Each GAME node has several properties, which we can see for example for the final.
        """)
        st.json("""
       {
"match_week": 7,
"teams": [
      "Italy",
      "England"
    ],
"home_score": 1,
"away_score": 1,
"match_id": 3795506,
"referee": "Bjorn Kuipers",
"competition_stage": "Final",
"match_date": "2021-07-11",
"away_team": "England",
"score": "1-1",
"away_team_manager": "Gareth Southgate",
"stadium": "Wembley Stadium (London)",
"kick_off": "21:00:00.000",
"home_team": "Italy",
"home_team_manager": "Roberto Mancini"
  }
""")
        st.write("The data shown are taken from the matches.json file of Statsbomb, taking into account the constraints of neo4j (for example the properties can be atomic types (float, integer, strings...) or lists, but not dictionaries)")

        st.write("""
        In the WHERE clause it is possible to specify filters on these attributes. For example, to see all the matches played at 9 p.m. we can use the following query""")
        st.code("""
MATCH (a:GAME)
WHERE a.kick_off = "21:00:00.000"
RETURN count(a) 
""")
        st.write("And it turns out that 24 of the 51 matches were played at 9pm.")
        st.write("""
        Moreover it is possible to return only some properties, for example to obtain the results of the games played at 21:00
        """)
        st.code("""
        MATCH (a:GAME)
WHERE a.kick_off = "21:00:00.000"
RETURN a.home_score, a.away_score
        """)

    with st.expander("Players"):
        st.write("""
        Each player has two labels: PLAYERS and the team name in uppercase (ex ITALY, SWITZERLAND..).
        Only general information is stored in the node, while to see the info of a player in a specific match the HAS_PLAYED relation is used.
        Let's see for example those of Ciro Immobile
        """)

        st.code("""
MATCH (c:ITALY)
WHERE c.name = "Ciro Immobile"
RETURN c
        """)
        st.write("Which returns")
        st.json("""{
"country": "Italy",
"player_id": 7788,
"name": "Ciro Immobile",
"jersey_number": 17
  }""")
        st.warning("""In the original json file the names contain accented letters and special characters that are not accepted by the database. Therefore all names have been "Englishified". For example, Kylian Mbappé was transformed into Kylian Mbappe""")

    with st.expander("Special nodes"):
        st.write("""
        There are two extra nodes, START and END that are used to model the start and end of actions respectively.
        For example, a shot is modeled as an arc that starts from the player who made it and ends in the END node, while a recovered ball is represented by an arc that starts from
        START and reaches the player who retrieved it.
        
        Here is a quick query to see these two arcs at work
        """)

        st.code("""
    MATCH (a:SWITZERLAND)-[s:SHOT]->(e:END)
WHERE s.outcome = "Goal" 
RETURN a,s,e
        """)
        st.write("""
        And returns the goals scored by Swiss players, including penalty kicks
        """)
        st.image("media/endnode.png")
        st.write("While to exclude the penalty kicks it is necessary to remember that StatsBomb encodes the penalties with period=5 "
                 " and therefore it is necessary to add a clause in the WHERE")

        st.code("""
        MATCH (a:SWITZERLAND)-[s:SHOT]->(e:END)
WHERE s.outcome = "Goal" and s.period <> 5
RETURN a,s,e
        """)
    st.subheader("Relationships")
    st.write("The other key piece are the relationships, which connect the nodes together.")

    with st.expander("HAS_PLAYED, relationship between players and games"):
        st.write("""In the nodes, the players have as properties only general information
        general, for the specific information of a match you have to refer to this category of relationships.
        For example, to see all the matches played by Harry Kane just run the following query
        """)

        st.code("""
MATCH (a)-[r:HAS_PLAYED]->(g:GAME)
WHERE a.name = "Harry Kane"
RETURN g,a,r
        """)

        st.image("media/harrykane.png")
        st.write("""
        Each arc has specific properties for the player PLAYER, taken from the file lineups/MATCH.json 
        where PLAYER and MATCH are the two nodes of interest (in the example above "a" is PLAYER, "g" is MATCH).
        
        For example, the properties between Harry Kane and the Final are the following.
        """)

        st.json("""
        {
"cards": [],
"positions": [
      "Center Forward"
    ],
"starting": true
}"""
        )
        st.write("""
        It is also possible to see all the players and HAS_PLAYED relationships by clicking on the following link
        """)
        link = '[Show svg file (new window)](https://fili.tk/ca/graph.svg)'
        st.markdown(link, unsafe_allow_html=True)

    with st.expander("PASS, relationship between players"):

        st.write("""
        The passes are the reason this model was built. Every passage carried out is a
        relationship that connects the passer to the receiver.
        
        
        In the database there are almost 50k passes so it is important to know how they are represented.
        First of all let's see how many times Jorginho passed the ball to Verratti (but not vice versa) in this European Championship.
        To do this we run the following query""")

        st.code("""
MATCH (a:ITALY)-[p]->(b:ITALY)
WHERE a.name = "Jorge Luiz Frello Filho" and b.name = "Marco Verratti"
RETURN COUNT(p)
        """)
        st.write("""
        We find that 75 passes have been made. 
        Now we are interested in seeing how many of these passes have been made in the final, we can do it
        using the field 
        """)
        st.code("match_id")
        st.write("""
        of the relationship. The code then becomes
        """)

        st.code("""
MATCH (a:ITALY)-[p]->(b:ITALY)
WHERE a.name = "Jorge Luiz Frello Filho" and b.name = "Marco Verratti"
and p.match_id = 3795506
RETURN COUNT(p)
                """)

        st.write("""
        And we find that only 20 of the 75 passes were made in the final. 
        
        At this point we can be interested to know how many of these passes have been made in a specific possession.
        To do this, we can use the field
        """)
        st.code("possession")
        st.write("""
        of the relationship. The code then becomes
        """)
        st.code("""
MATCH (a:ITALY)-[p]->(b:ITALY)
WHERE a.name = "Jorge Luiz Frello Filho" and b.name = "Marco Verratti"
and p.match_id = 3795506 and p.possession = 53
RETURN COUNT(p)     
        """)
        st.write("""
        Only twice did Jorginho pass the ball to Verratti in the 53rd possession of the final.
        Each possession has additional important properties, e.g.
        """)
        st.json(
            """
{
"period": 1,
"possession": 53,
"match_id": 3795506,
"length": 5.67186,
"index": 1145,
"team": "Italy",
"possession_length": 50,
"play_pattern": "Regular Play",
"minute": 31,
"second": 59,
"duration": 0.70303,
"end_location": [
      78.9,
      47.3
    ],
"angle": -1.730148,
"location": [
      79.8,
      52.9
    ],
"position": "Center Defensive Midfield",
"body_part": "Right Foot",
"timestamp": "00:31:59.929",
"order": 32,
"height": "Ground Pass"
  }
            """)
        st.write("""For example, order is used to identify successive steps, while possession_length is used to determine
        if it is the last possession step (if order==possession_length)"""
                 )

    with st.expander("Special relationships between players and START/END nodes"):

        st.write("""
        There are several relationships for modeling the beginning and end of an action. For example, 
        if we are interested in finding out who made the last pass before the goals of the final we can write the following
        query
        """)
        st.code("""
MATCH p=(a)-[p1:PASS]->(b)-[s:SHOT]->(:END)
WHERE  p1.match_id = 3795506 and s.outcome = "Goal" and p1.possession = s.possession
and p1.order = p1.possession_length  
RETURN p
        """)
        st.image("media/goalengland.jpeg")
        st.write("""
        In which Bonucci's goal is not shown because he recovered the ball after it hit the post.


        The possession_length attribute is very useful to check that the shot is coming from the correct player.
        (for example, in the code before, if Luke Shaw had received another pass from Kieran Trippier in the same action, 
        this would be shown by removing p1.order = p1.possession_length even if it is not the pass of interest).
        
        
        Another interesting property is that the order attribute starts at one every action, so if we want to constrain
        a step to be the first of the action just check
        """)
        st.code("p1.order = 1")

    st.subheader("User Defined Functions")
    st.write("In addition, course-specific functions have been defined to facilitate pattern searches.")
    with st.expander("User defined functions for pattern matching"):
        st.write("""
        The initial intent of this dashboard was to find patterns in passes in an efficient way.
        
        This is very easy with Cypher but you need to check a number of parameters, namely that players with different letters
        are different and that the passes are consecutive within the same match and the same possession.
        
        To simplify the syntax we have created two UDFs: sa.differentPlayers and sa.consecutivePossession
        (where sa stands for Soccer Analytics)
        
        """)
        st.warning("""
        These functions do not allow for predicate pushdown by the Cypher optimizer, 
        so they are inefficient for the patterns of interest. 
        However, I leave the explanation and reference to better understand what properties 
        are involved. An automated tool that writes these queries can be used in the side menu.
        """)
        st.markdown("""##### sa.differentPlayers""")
        st.write("""This is to check that the players are actually different. 
        For example, if I'm interested in looking for the ABABCA pattern, I have to make sure that 
        A, B and C are different (while Cypher automatically checks that the three A's are from the same player).
        To do this just invoke the following function that returns true only if the passes are within the same possession """)
        st.code("sa.differentPlayers([A,B,C])"
                 )
        st.warning("Be careful not to put sa.differentPlayers([A,B,A,B,C,A]) which will always return false")
        st.markdown("""##### sa.consecutivePossession""")
        st.write("""
        It is used to check that the network of passes occurs in the same possession and is consecutive. In this case the control
        is on the arcs, not on the nodes. So in the pattern of before, calling the arcs A-p1->B-p2->A-p3->B-p4->C-p5->A
        the control is as follows
        """)
        st.code("""
        sa.consecutivePossession([p1,p2,p3,p4,p5])
        """)
        st.markdown("""##### Example code""")
        st.write("So for example, to match all ABABCA in Euro2020 we need to write te following query")
        st.code("""
MATCH  p = (A)-[p1:PASS]->(B)-[p2:PASS]->(A)-[p3:PASS]->(B)-[p4:PASS->(C)-[p5:PASS]->(A)
WHERE sa.consecutivePossession([p1,p2,p3,p4,p5]) and sa.differentPlayers([A,B,C])
RETURN p
        """)
        st.write("""
        The query takes long because the search space is huge and Cypher cannot push down selections (in order to call the UDF
        it firstly needs to perform a cartesianproduct-like operation, which is very expensive in a graph with this size).
        
        To avoid this unexpected behaviour we have created a tool that, given the pattern to match, returns the ready-to-run 
        Cypher query. We suggest to use UDFs only for short paths, while for longer is not so efficient. 
        
        The tool to create the aforementioned queries is in the section pattern finder on the left menu.
        
        Before running the queries, you can modify them by adding filters in the where clause (for example if you want to find
        all patterns ABAC ended in goals you have to add an extra relationship -[s:SHOT]->(:END) and check that the shot
        is in the same possession, game and the outcome is "Goal"
        """)

    with st.expander("Tools"):

        st.write("""
        Integrating Cypher into a programming language is extremely simple, so interesting tools can be written by accessing the database. Examples are shown in the side menu, if you have more reviews send them to me via email (fdeaglio@ethz.ch) and I'll be happy to mention you as a contributor.
        """)





