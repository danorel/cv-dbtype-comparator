from core.server import app
from core.db.generator import Neo4jGenerator, Schema
from core.db.connector import Neo4jConnection


def Neo4jInitializer(connection: Neo4jConnection, generator: Neo4jGenerator):
    root = generator.random(Schema)

    users = root.get('User')
    for user in users:
        cvs = user.get('CV')
        for cv in cvs:
            connection.query(f"""
                CREATE
                (p:User{{
                    login: \"{user.get('login')}\",
                    password: \"{user.get('password')}\"
                }})
                -[:HAS]->
                (t:CV{{
                    title: \"{cv.get('title')}\"
                }})
            """)


def main():
    try:
        connection = Neo4jConnection(uri="neo4j://neo4j:7687",
                                     user="neo4j",
                                     pwd="supersecretpassword")
        generator = Neo4jGenerator()
        Neo4jInitializer(connection, generator)
        # connection.query("""MATCH (n) DETACH DELETE n""")
        connection.close()
    except Exception as e:
        return f"Error. {e}"
    return "Success"


@app.route("/")
def index():
    return f"Status: {main()}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
