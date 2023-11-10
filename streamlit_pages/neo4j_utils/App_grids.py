from neo4j import GraphDatabase


class App_grids:
    """
    Neo4j App to query the graphdb in the arrows, heatmaps and flow section
    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def find_pattern(self, query_string):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_pattern, query_string
            )
            return result

    @staticmethod
    def _find_and_return_pattern(tx, query_string):
        result = tx.run(query_string)
        return [row for row in result]
