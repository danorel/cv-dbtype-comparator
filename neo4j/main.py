from core.server import app
from core.db.generator import Neo4jGenerator
from core.db.connector import Neo4jConnection


Schema = {
    'name': 'Root',
    'properties': [
        {
            'name': 'User',
            'min_items': 1000,
            'max_items': 1000,
            'properties': [
                {
                    'name': 'login',
                    'instance': 'str',
                    'range_from': 8,
                    'range_to': 8
                },
                {
                    'name': 'password',
                    'instance': 'str',
                    'range_from': 8,
                    'range_to': 16
                },
                {
                    'name': 'CV',
                    'min_items': 1,
                    'max_items': 5,
                    'properties': [
                        {
                            'name': 'title',
                            'instance': 'str',
                            'range_from': 5,
                            'range_to': 15
                        },
                        {
                            'name': 'Hobby',
                            'min_items': 1,
                            'max_items': 5,
                            'properties': [
                                {
                                    'name': 'title',
                                    'instance': 'str',
                                    'range_from': 3,
                                    'range_to': 15
                                }
                            ]
                        },
                        {
                            'name': 'Company',
                            'min_items': 1,
                            'max_items': 3,
                            'properties': [
                                {
                                    'name': 'title',
                                    'instance': 'str',
                                    'range_from': 3,
                                    'range_to': 15
                                },
                                {
                                    'name': 'City',
                                    'min_items': 1,
                                    'max_items': 2,
                                    'properties': [
                                        {
                                            'name': 'title',
                                            'instance': 'str',
                                            'range_from': 5,
                                            'range_to': 15,
                                            'cache': True
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}


def Neo4jInitializer(connection: Neo4jConnection, generator: Neo4jGenerator):
    root = generator.random(Schema)

    users = root.get('User', [])
    for user in users:
        cvs = user.get('CV', [])
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
            hobbies = cv.get('Hobby', [])
            for hobby in hobbies:
                connection.query(f"""
                    CREATE
                    (p:CV{{
                        title: \"{cv.get('title')}\"
                    }})
                    -[:HAS]->
                    (t:Hobby{{
                        title: \"{hobby.get('title')}\"
                    }})
                """)
            companies = cv.get('Company', [])
            for company in companies:
                connection.query(f"""
                    CREATE
                    (p:CV{{
                        title: \"{cv.get('title')}\"
                    }})
                    -[:HAS]->
                    (t:Company{{
                        title: \"{company.get('title')}\"
                    }})
                """)
                cities = company.get('City', [])
                for city in cities:
                    connection.query(f"""
                        CREATE
                        (p:Company{{
                            title: \"{company.get('title')}\"
                        }})
                        -[:IN]->
                        (t:City{{
                            title: \"{city.get('title')}\"
                        }})
                    """)


def Neo4jRemover(connection: Neo4jConnection):
    connection.query("""MATCH (n) DETACH DELETE n""")


def main():
    try:
        connection = Neo4jConnection(uri="neo4j://neo4j:7687",
                                     user="neo4j",
                                     pwd="supersecretpassword")
        generator = Neo4jGenerator()
        # Neo4jInitializer(connection, generator)
        # Neo4jRemover(connection)
        connection.close()
    except Exception as e:
        return f"Error. {e}"
    return "Success"


@app.route("/")
def index():
    return f"Status: {main()}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
