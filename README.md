# Cy4soccer

Cy4soccer is a project developed in parallel with the Soccer Analytics course (ETHZ FS22) which aims to analyse the Euro2020 using a graph database.

The name recalls the fundamental components of this project: _Cy_ for Cypher, the language used for queries, _4_ for Neo4j, the database used to store the data, and _soccer_, as the data analysed is related to football.

The whole project serves the streamlit dashboard which can be found at this link: https://share.streamlit.io/francescodeaglio/cy4soccer/streamlit_home.py

The initial aim of the project was to efficiently match passing motifs (e.g. an ABAC pattern means that I, A, pass the ball to another player, B, who passes it back to me and I pass it to a third player, C).
Right from the start, Cypher seemed a good ally for solving this problem, as it is a pattern matching language 'by example'.
### Preprocessing
The data is originally in JSON format and has been translated into nodes and relationships 
using RumbleDB (for JSON handling and querying), python, cypher and Neo4j. 
You can find the data model description in the dashboard home and all the preprocessing 
in the related notebook (notebooks/Rumble preprocessing)

### Tools
There are various tools written to exploit the created database, they can be used directly on the dashboard (with the possibility to choose which query to display).

### Software/database/programming language used
*Python*: the language that encompasses all operations is python. In particular Streamlit is used for the web app.

*RumbleDb/Jsoniq*: queries written in jsoniq and executed through RumbleDB were used for preprocessing, to convert data from Json format to Graph-like format. The queries are executed by sending an http request to the rumble server, everything has been wrapped to be integrated in python.

*Cypher/Neo4j*: the output of the preprocessing phase has been uploaded to an instance of a Neo4j database. Two versions of the database are currently active: a private one, used for dashboard queries and deployed on our server, and a public one, created on Neo4jAura, in order to provide a ready-to-use database for those who want to use it. All dashboard queries are written in Cypher. Some are executed, others have been precomputed and cached because they take too long to execute each time.

*MongoDB*: is used as a "cache" for visualisations that require long queries (e.g. sunburst diagram that requires the amount of passes made per passing motif to be between 2 and 6 in length).