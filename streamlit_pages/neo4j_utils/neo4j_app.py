from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import streamlit as st


class App:
    """
    Neo4j connection. Used in pattern matching section and to populate the db.
    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_player(self, player, team):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_player, player, team
            )
            for row in result:
                print(
                    "Created player: {p1}".format(
                        p1=row["_".join(player["name"].split())]
                    )
                )

    @staticmethod
    def _create_and_return_player(tx, player, team):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        string = ""
        first = True
        for key in player:
            if key == "name":
                continue
            if first:
                first = False
                string += key + ' : "' + str(player[key]) + '"'
            else:
                string += ", " + key + ' : "' + str(player[key]) + '"'

        string += ', name : "' + player["name"] + '"'

        labs = "_".join(player["name"].split())
        query = "CREATE (x:" + team + " { " + string + " }) RETURN x"
        result = tx.run(query)

        try:
            return [{labs: row["x"]["name"]} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    def find_pattern(self, query_string, pattern, silent=False):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_pattern, query_string
            )

            if len(result) == 0:
                st.error("No match for pattern " + pattern)
            else:
                st.success(
                    "Pattern " + pattern + " matched " + str(len(result)) + " times!"
                )
            if not silent:
                for row in result:
                    string = "{" + "}->{".join(list(pattern)) + "}"
                    diz = {}
                    for letter in pattern:
                        diz[letter] = row[letter + ".name"]
                    string = string.format(**diz)
                    st.write("Possession " + str(row["p0.possession"]) + ":\t" + string)

    @staticmethod
    def _find_and_return_pattern(tx, query_string):
        result = tx.run(query_string + ", p0.possession")
        return [row for row in result]

    def create_passage(self, passage):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(self._create_and_return_passage, passage)
            for row in result:
                print(
                    "Created passage: {p1} to {p2}".format(
                        p1=passage["from"], p2=passage["to"]
                    )
                )

    @staticmethod
    def _create_and_return_passage(tx, passage):
        properties = ""
        first = True
        for key in passage:
            if first:
                first = False

                properties += key + ' : "' + str(passage[key]) + '"'
            else:
                properties += ", " + key + ' : "' + str(passage[key]) + '"'

        joined = "_".join(passage["height"].split())
        query = (
            'MATCH (a), (b) \
            WHERE a.name = "'
            + passage["from"]
            + '" AND b.name = "'
            + passage["to"]
            + '" CREATE (a)-[r:'
            + joined
            + " {"
            + properties
            + "}]->(b) \
            RETURN type(r)"
        )

        # print(query)

        result = tx.run(query)
        try:
            return [{"row": row} for row in result]

        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise
