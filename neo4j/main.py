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
                                    'range_to': 15,
                                    'cache': True,
                                    'cache_probability': 0.25
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
                                    'range_to': 15,
                                    'cache': True,
                                    'cache_probability': 0.2
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
                                            'cache': True,
                                            'cache_probability': 0.3
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


def neo4jInitializer(connection: Neo4jConnection, generator: Neo4jGenerator):
    records = generator.random(Schema)
    for record in records:
        for user in record.get('User', []):
            for cv in user.get('CV', []):
                [cv_id] = connection.query(f"""
                    CREATE
                    (us:User{{
                        login: \"{user.get('login')}\",
                        password: \"{user.get('password')}\"
                    }})
                    -[:HAS]->
                    (cv:CV{{
                        title: \"{cv.get('title')}\"
                    }})
                    RETURN ID(cv)
                """)
                for hobby in cv.get('Hobby', []):
                    connection.query(f"""
                        MATCH
                        (cv:CV)
                        WHERE ID(cv) = {cv_id.value()}
                        CREATE
                        (cv)
                        -[:HAS]->
                        (hb:Hobby{{
                            title: \"{hobby.get('title')}\"
                        }})
                    """)
                for company in cv.get('Company', []):
                    [company_id] = connection.query(f"""
                        MATCH
                        (cv:CV)
                        WHERE ID(cv) = {cv_id.value()}
                        CREATE
                        (cv)
                        -[:HAS]->
                        (cp:Company{{
                            title: \"{company.get('title')}\"
                        }})
                        RETURN ID(cp)
                    """)
                    for city in company.get('City', []):
                        connection.query(f"""
                            MATCH
                            (cp:Company)
                            WHERE ID(cp) = {company_id.value()}
                            CREATE
                            (cp)
                            -[:IN]->
                            (ct:City{{
                                title: \"{city.get('title')}\"
                            }})
                        """)


def neo4jRemover(connection: Neo4jConnection):
    connection.query("""
        MATCH (n) 
        DETACH DELETE n
    """)


def neo4jQuerySimulator(connection: Neo4jConnection):
    # Query #1: забрати рюзюме
    search_user_cv = connection.query("""
        MATCH 
        (us:User)
        -[:HAS]->
        (cv:CV)
        WHERE us.login =~ "^A.*" AND
              cv.title =~ "^A.*"
        RETURN cv
    """)
    app.logger.info(f"CV of User 'A*' in CV with title 'A*': {search_user_cv}")

    # Query #2: забрати всі хоббі які існують в резюме
    search_user_hobbies = connection.query("""
        MATCH 
        (us:User)
        -[:HAS]->
        (cv:CV)
        -[:HAS]->
        (hb:Hobby)
        WHERE us.login =~ "^A.*" AND
              cv.title =~ "^A.*"
        RETURN hb
    """)
    app.logger.info(f"Hobbies of User 'A*' in CV with title 'A*': {search_user_hobbies}")

    # Query #3: забрати всі міста, що зустрічаються в резюме
    search_user_cities = connection.query("""
        MATCH
        (us:User)
        -[:HAS]->
        (cv:CV)
        -[:HAS]->
        (cp:Company)
        -[:IN]->
        (ct:City)
        RETURN ct
    """)
    app.logger.info(f"Cities of User 'A*' in CV with title 'A*': {search_user_cities}")

    # Query #4: забрати хоббі всіх здобувачів, що мешкають в заданому місті
    search_all_hobbies = connection.query("""
        MATCH 
        (us:User)
        -[:HAS]->
        (cv:CV)
        -[:HAS]->
        (hb:Hobby),
        (cp:Company)
            -[:IN]->
            (ct:City)
        WHERE ct.title =~ "^AB.*"
        RETURN hb, ct
    """)
    app.logger.info(f"Hobbies of all Users, who live in City with title 'A*': {search_all_hobbies}")

    # Query #5: забрати всіх здобувачів, що працювали в одному закладі (заклад ми не вказуємо)
    search_all_teammates = connection.query("""
        OPTIONAL MATCH
        (us1:User)-[:HAS]->(cv1:CV)-[:HAS]->(cp:Company)<-[:HAS]-(cv2:CV)<-[:HAS]-(us2:User)
        RETURN us1, us2
    """)
    app.logger.info(f"Teammates, who work in same company': {search_all_teammates}")


def main():
    try:
        connection = Neo4jConnection(uri="neo4j://neo4j:7687",
                                     user="neo4j",
                                     pwd="supersecretpassword")
        generator = Neo4jGenerator()
        neo4jInitializer(connection, generator)
        neo4jQuerySimulator(connection)
        neo4jRemover(connection)
        connection.close()
    except Exception as e:
        return f"Error. {e}"
    return "Success"


@app.route("/")
def index():
    return f"Status: {main()}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
