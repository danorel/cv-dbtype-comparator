from core.server import app
from core.db.generator import MongoDBGenerator
from core.db.connector import MongoDBConnection


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


def mongodbInitializer(connection: MongoDBConnection, generator: MongoDBGenerator):
    (
        user,
        cv,
        hobby,
        company,
        city
    ) = (
        connection.collection("User"),
        connection.collection("CV"),
        connection.collection("Hobby"),
        connection.collection("Company"),
        connection.collection("City")
    )
    records = generator.random(Schema)
    for record in records:
        users = []
        for user in record.get('User', []):
            cvs = []
            for cv in user.get('CV', []):
                hobbies, companies = [], []
                for hobby in cv.get('Hobby', []):
                    hobbies.append({
                        "title": hobby.get('title')
                    })
                for company in cv.get('Company', []):
                    cities = []
                    for city in company.get('City', []):
                        cities.append({
                            "title": city.get('title')
                        })
                    companies.append({
                        "title": company.get('title'),
                        "cities": cities
                    })
                cvs.append({
                    "title": cv.get('title'),
                    "hobbies": hobbies,
                    "companies": companies
                })
            users.append({
                "login": user.get('login'),
                "password": user.get('password'),
                "cvs": cvs
            })
        cv.insert_many(users)
    pass


def mongodbRemover(connection: MongoDBConnection):
    (
        user,
        cv,
        hobby,
        company,
        city
    ) = (
        connection.collection("User"),
        connection.collection("CV"),
        connection.collection("Hobby"),
        connection.collection("Company"),
        connection.collection("City")
    )
    user.drop()
    cv.drop()
    hobby.drop()
    company.drop()
    city.drop()
    pass


def mongodbQuerySimulator(connection: MongoDBConnection):
    # # Query #1: забрати рюзюме
    # search_user_cv = connection.collection("""
    #     MATCH
    #     (us:User)
    #     -[:HAS]->
    #     (cv:CV)
    #     WHERE us.login =~ "^A.*" AND
    #           cv.title =~ "^A.*"
    #     RETURN cv
    # """)
    # app.logger.info(f"CV of User 'A*' in CV with title 'A*': {search_user_cv}")
    #
    # # Query #2: забрати всі хоббі які існують в резюме
    # search_user_hobbies = connection.collection("""
    #     MATCH
    #     (us:User)
    #     -[:HAS]->
    #     (cv:CV)
    #     -[:HAS]->
    #     (hb:Hobby)
    #     WHERE us.login =~ "^A.*" AND
    #           cv.title =~ "^A.*"
    #     RETURN hb
    # """)
    # app.logger.info(f"Hobbies of User 'A*' in CV with title 'A*': {search_user_hobbies}")
    #
    # # Query #3: забрати всі міста, що зустрічаються в резюме
    # search_user_cities = connection.collection("""
    #     MATCH
    #     (us:User)
    #     -[:HAS]->
    #     (cv:CV)
    #     -[:HAS]->
    #     (cp:Company)
    #     -[:IN]->
    #     (ct:City)
    #     RETURN ct
    # """)
    # app.logger.info(f"Cities of User 'A*' in CV with title 'A*': {search_user_cities}")
    #
    # # Query #4: забрати хоббі всіх здобувачів, що мешкають в заданому місті
    # search_all_hobbies = connection.collection("""
    #     MATCH
    #     (us:User)
    #     -[:HAS]->
    #     (cv:CV)
    #     -[:HAS]->
    #     (hb:Hobby),
    #     (cp:Company)
    #         -[:IN]->
    #         (ct:City)
    #     WHERE ct.title =~ "^AB.*"
    #     RETURN hb, ct
    # """)
    # app.logger.info(f"Hobbies of all Users, who live in City with title 'A*': {search_all_hobbies}")
    #
    # # Query #5: забрати всіх здобувачів, що працювали в одному закладі (заклад ми не вказуємо)
    # search_all_teammates = connection.collection("""
    #     OPTIONAL MATCH
    #     (us1:User)-[:HAS]->(cv1:CV)-[:HAS]->(cp:Company)<-[:HAS]-(cv2:CV)<-[:HAS]-(us2:User)
    #     RETURN us1, us2
    # """)
    # app.logger.info(f"Teammates, who work in same company': {search_all_teammates}")
    pass


def main():
    try:
        connection = MongoDBConnection(host="mongodb://mongo:supersecretpassword@mongo:27017",
                                       db="mongo")
        generator = MongoDBGenerator()
        mongodbInitializer(connection, generator)
        mongodbQuerySimulator(connection)
        mongodbRemover(connection)
        connection.close()
    except Exception as e:
        return f"Error. {e}"
    return "Success"


@app.route("/")
def index():
    return f"Status: {main()}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
