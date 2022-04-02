import streamlit as st
import base64

def intro():
    st.title("Cy4soccer")
    st.write("""
    Neo4j è un graph database in cui i dati sono rappresentati come grafi. Un grafo è formato da due elementi principali: i nodi e le relazioni che li congiungono. 
    Ogni nodo e ogni relazione hanno una Label (ad esempio la nazione d'appartenenza) e delle properties (ad esempio il nome del giocatore)
    In questa veloce intro verrà mostrato come sono rappresentati i dati e come scrivere query in Cypher.
    Cypher è un linguaggio di query dichiarativo (specifichi cosa vuoi che sia fatto, non come) in cui si matchano pattern 
    
    Ad esempio:
    """)

    st.code("""
    MATCH (a:ITALY)-[:HAS_PLAYED]->(g:GAME)<-[:HAS_PLAYED]-(b:ENGLAND)
WHERE a.name = "Gianluigi Donnarumma" and b.name = "Bukayo Saka"
RETURN g
    """)
    st.write("Ritorna tutte le gare di Euro2020 in cui Donnarumma ha giocato contro Saka. Nelle prossime sezioni vedremo come arrivare a scrivere questa query.")
    st.image("media/donnarumma_saka.jpeg")

    st.header("Data Model")
    st.subheader("Nodes")
    st.write("""
    Come scritto in precedenza, i componenti principali sono i nodi e le relationships. Vediamo ora i nodi.
    Ci sono tre categorie di nodi: Partite, Giocatori e Speciali
    """)

    with st.expander("Matches"):
        st.write("""
        Tutti i match sono etichettati con la label GAME (MATCH è una parola che fa parte della sintassi di cypher). 
        Ad esempio la query sottostante ritorna tutti i match di Euro2020
        """)
        st.code("""
MATCH (a:GAME)
RETURN a        
        """)
        st.write("""
        Per controprova possiamo contare quanti match ci sono nel database e controllare che siano effettivamente 51.
        """)
        st.code("""
MATCH (a:GAME)
RETURN count(a)        
                """, language="Cypher")
        st.write("""
        
        """)
        st.write("""
        Ogni nodo GAME ha delle properties, che possiamo vedere ad esempio per la finale.
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
        st.write("I dati mostrati sono esattamente gli stessi del file matches.json di Statsbomb")

        st.write("""
        Nella clausola where è possibile specificare dei filtri su questi attributi. Ad esempio, per vedere tutte le gare giocate alle 21 si può usare la seguente query
        """)
        st.code("""
MATCH (a:GAME)
WHERE a.kick_off = "21:00:00.000"
RETURN count(a) 
""")
        st.write("E si scopre che 24 delle 51 gare son state giocate alle 21.")
        st.write("""
        Inoltre è possibile ritornare solo delle proprietà, ad esempio per ottenere i risultati delle gare giocate alle 21
        """)
        st.code("""
        MATCH (a:GAME)
WHERE a.kick_off = "21:00:00.000"
RETURN a.home_score, a.away_score
        """)

    with st.expander("Players"):
        st.write("""
        Ogni player ha due labels PLAYERS e il nome della squadra d'appartenza in maiuscolo (ex ITALY, SWITZERLAND..).
        Nel nodo sono memorizzate solo le informazioni generali, mentre per vedere le info di un giocatore in una determinata partita viene usata la relazione HAS_PLAYED
        Vediamo ad esempio quelle di Ciro Immobile
        """)

        st.code("""
MATCH (c:ITALY)
WHERE c.name = "Ciro Immobile"
RETURN c
        """)
        st.write("Che ritorna")
        st.json("""{
"country": "Italy",
"player_id": 7788,
"name": "Ciro Immobile",
"jersey_number": 17
  }""")
        st.warning("I nomi son stati 'inglesizzati'.....")

    with st.expander("Special nodes"):
        st.write("""
        Ci sono due extra nodi, START ed END che vengono usati per modellare rispettivamente l'inizio e la fine delle azioni.
        Ad esempio un tiro è modellato come un arco che parte dal giocatore che l'ha effettuato e finisce nel nodo END, mentre una palla recuperata è rappresentata da un arco che parte da
        START e raggiunge il giocatore che l'ha recuperata.
        
        Ecco una veloce query per vedere questi due archi all'opera
        """)

        st.code("""
    MATCH (a:SWITZERLAND)-[s:SHOT]->(e:END)
WHERE s.outcome = "Goal" 
RETURN a,s,e
        """)
        st.write("""
        E ritorna i goal segnati da giocatori svizzeri, includendo i calci di rigore
        """)
        st.image("media/endnode.png")
        st.write("Mentre per escludere i calci di rigore bisogna ricordarsi che StatsBomb codifica i rigori con period=5 "
                 "e quindi è necessario aggiungere una clausola nel where")

        st.code("""
        MATCH (a:SWITZERLAND)-[s:SHOT]->(e:END)
WHERE s.outcome = "Goal" and s.period <> "5"
RETURN a,s,e
        """)
    st.subheader("Relationships")
    st.write("L'altro tassello fondamentale sono le relationships, che collegano i nodi tra di loro.")

    with st.expander("HAS_PLAYED, relationship between players and games"):
        st.write("""Nei nodi, i giocatori hanno come properties solo delle informazioni
        generali, per le informazioni specifiche di una partita bisogna far riferimento a questa categoria di relationships.
        Ad esempio, per vedere tutte le gare che ha giocato Harry Kane basta eseguire la seguente query
        """)

        st.code("""
MATCH (a)-[r:HAS_PLAYED]->(g:GAME)
WHERE a.name = "Harry Kane"
RETURN g,a,r
        """)

        st.image("media/harrykane.png")
        st.write("""
        Ogni arco ha delle properties specifiche per il giocatore PLAYER, prese dal file lineups/MATCH.json 
        dove PLAYER e MATCH sono i due nodi d'interesse (nell'esempio sopra a è PLAYER, g è MATCH).
        
        Ad esempio le properties tra Harry Kane e la Finale son le seguenti.
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
        E' inoltre possibile vedere tutti i giocatori e le relazioni HAS_PLAYED clickando sul seguente link
        """)
        link = '[Show svg file (new window)](https://fili.tk/ca/graph.svg)'
        st.markdown(link, unsafe_allow_html=True)

    with st.expander("PASS, relationship between players"):

        st.write("""
        I passaggi sono il motivo per cui questo modello è stato costruito. Ogni passaggio effettuato è una
        relationship che connette chi passa a chi ha ricevuto.
        Nel database ci sono 49041 passaggi quindi è importante sapere come son rappresentati.
        Innanzi tutto vediamo quante volte Jorginho ha passato la palla a Verratti (ma non viceversa) in questo Europeo.
        Per farlo eseguiamo la seguente query""")

        st.code("""
MATCH (a:ITALY)-[p]->(b:ITALY)
WHERE a.name = "Jorge Luiz Frello Filho" and b.name = "Marco Verratti"
RETURN COUNT(p)
        """)
        st.write("""
        Scopriamo che son stati effettuati 75 passaggi. 
        Ora siamo interessati a vedere quanti di questi passaggi sono avvenuti nella finale, possiamo farlo
        sfruttando il campo 
        """)
        st.code("match_id")
        st.write("""
        della relationship. Il codice quindi diventa
        """)

        st.code("""
MATCH (a:ITALY)-[p]->(b:ITALY)
WHERE a.name = "Jorge Luiz Frello Filho" and b.name = "Marco Verratti"
and p.match_id = 3795506
RETURN COUNT(p)
                """)

        st.write("""
        E scopriamo che solo 20 dei 75 passaggi son stati effettuati nella finale. A questo punto possiamo essere interessati
        a sapere quanti di questi passaggi sono avvenuti in uno specifico possesso.
        Per fare ciò, si può utilizzare il campo
        """)
        st.code("possession")
        st.write("""
        della relationship. Il codice quindi diventa
        """)
        st.code("""
MATCH (a:ITALY)-[p]->(b:ITALY)
WHERE a.name = "Jorge Luiz Frello Filho" and b.name = "Marco Verratti"
and p.match_id = 3795506 and p.possession = 53
RETURN COUNT(p)     
        """)
        st.write("""
        Solo due volte Jorginho ha passato la palla a Verratti nel 53esimo possesso della finale.
        Ogni possesso ha ulteriori importanti proprietà, ad esempio
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
        st.write("""Ad esempio, order serve per identificare passaggi successivi, mentre possession_length serve per stabilire
        se è l'ultimo passaggio del possesso (if order==possession_length)"""
                 )

    with st.expander("Special relationships between players and START/END nodes"):

        st.write("""
        Ci sono diverse relationship per modellare l'inizio e la fine di un'azione. Ad esempio, 
        se siamo interessati a scoprire chi ha fatto l'ultimo passaggio prima dei gol della finale possiamo scrivere la seguente
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
        In cui non viene mostrato il goal di Bonucci in quanto ha recuperato palla dopo che è sbattuta sul palo.
        Tornano molto comodi gli attributi possession_length per controllare che il tiro sia partito dal giocatore corretto
        (ad esempio, nel codice prima, se Luke Shaw avesse ricevuto un altro passaggio da Kevin Trippier nella stessa azione, 
        questo verrebbe mostrato togliendo p1.order = p1.possession_length anche se non è il passaggio di interesse.
        Un'altra proprietà interessante è che l'attributo order parte da uno ogni azione, quindi se vogliamo vincolare
        un passaggio ad essere il primo dell'azione basta controllare
        """)
        st.code("p1.order = 1")

    st.subheader("User Defined Functions")
    st.write("Inoltre son state definite delle funzioni specifiche per il corso, per facilitare la ricerca di pattern")
    with st.expander("User defined functions for pattern matching"):
        st.write("""
        L'intento iniziale di questa dashboard era quello di trovare pattern nei passaggi in un modo efficiente.
        
        Questo è molto facile con Cypher ma bisogna controllare una serie di parametri, ovvero che giocatori con lettere
        diverse siano diversi e che i passaggi siano consecutivi all'interno dello stesso match e dello stesso possesso.
        
        Per semplificare la sintassi abbiamo creato due UDF: sa.differentPlayers and sa.consecutivePossession
        (dove sa sta per Soccer Analytics)
        
        """)
        st.markdown("""##### sa.differentPlayers""")
        st.write("""Serve per controllare che i giocatori siano effettivamente diversi. 
        Se ad esempio sono interessato a cercare il pattern ABABCA devo assicurarmi che 
        A, B e C sian diversi (mentre che le tre A che appaiono siano dello stesso giocatore è gestito in automatico da Cypher)
        Per farlo basta invocare la seguente funzione che ritorna true solo se i passaggi sono all'interno dello stesso possesso
        """)
        st.code("sa.differentPlayers([A,B,C])"
                 )
        st.warning("Attenzione a non mettere sa.differentPlayers([A,B,A,B,C,A]) che ritornerà sempre falso")
        st.markdown("""##### sa.consecutivePossession""")
        st.write("""
        Serve a controllare che la rete di passaggi avvenga nello stesso possesso e sia consecutiva. In questo caso il controllo
        è sugli archi, non sui nodi. Quindi nel pattern di prima, chiamando gli archi A-p1->B-p2->A-p3->B-p4->C-p5->A
        il controllo è il seguente
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
        
        The tool to create the aforementioned queries is in the section pattern finder on the left menù.
        
        Before running the queries, you can modify them by adding filters in the where clause (for example if you want to find
        all patterns ABAC ended in goals you have to add an extra relationship -[s:SHOT]->(:END) and check that the shot
        is in the same possession, game and the outcome is "Goal"
        """)




