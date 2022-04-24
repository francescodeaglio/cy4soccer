# Cy4soccer

Cy4soccer is a project developed in parallel with the Soccer Analytics course (ETHZ FS22) which aims to analyse the Euro2020 using a graph database.

The name recalls the fundamental components of this project: _Cy_ for Cypher, the language used for queries, _4_ for Neo4j, the database used to store the data, and _soccer_, as the data analysed is related to football.

The whole project serves the streamlit dashboard which can be found at this link: https://share.streamlit.io/francescodeaglio/cy4soccer/streamlit_home.py

### Preprocessing
The data is originally in JSON format and has been translated into nodes and relationships 
using RumbleDB (for JSON handling and querying), python, cypher and Neo4j. 
You can find the datamodel description in the dashboard home and all the preprocessing 
in the related notebook (notebooks/Rumble preprocessing)

### Queries
There are various tools written to exploit the created database, they can be used directly on the dashboard (with the possibility to choose which query to display).