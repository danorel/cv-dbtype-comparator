from bson.objectid import ObjectId

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
    collection = connection.collection("UserCV")
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
        result = collection.insert_many(users)
        app.logger.info(f"Result: {result.acknowledged}")
    pass


def mongodbRemover(connection: MongoDBConnection):
    collection = connection.collection("UserCV")
    collection.drop()
    pass


def mongodbQuerySimulator(connection: MongoDBConnection):
    collection = connection.collection("UserCV")

    # # Query #1: забрати рюзюме
    user_cvs = collection \
        .aggregate([
        {
            "$match": {
                "_id": ObjectId("638b5f2b39c1a807a822e272")
            }
        },
        {
            "$project": {
                "_id": False,
                "cv": "$cvs.title"
            }
        },
        *[{"$unwind": "$cv"} for _ in range(1)],
        {
            "$group": {"_id": "$cv"}
        },
        {
            "$project": {
                "_id": False,
                "cv": "$_id"
            }
        }
    ])
    app.logger.info(f"CVs of User with ID '638b5f2b39c1a807a822e272': {list(user_cvs)}")

    # # Query #2: забрати всі хоббі які існують в резюме
    user_hobbies = collection \
        .aggregate([
        {
            "$match": {
                "_id": ObjectId("638b5f2b39c1a807a822e272")
            }
        },
        {
            "$project": {
                "_id": False,
                "hobby": "$cvs.hobbies.title"
            }
        },
        *[{"$unwind": "$hobby"} for _ in range(2)],
        {
            "$group": {"_id": "$hobby"}
        },
        {
            "$project": {
                "_id": False,
                "hobby": "$_id"
            }
        }
    ])
    app.logger.info(f"Hobbies of User with ID '638b5f2b39c1a807a822e272' in all CVs: {list(user_hobbies)}")

    # Query #3: забрати всі міста, що зустрічаються в резюме
    user_cities = collection \
        .aggregate([
        {
            "$match": {
                "_id": ObjectId("638b5f2b39c1a807a822e272")
            }
        },
        {
            "$project": {
                "_id": False,
                "city": "$cvs.companies.cities.title"
            }
        },
        *[{"$unwind": "$city"} for _ in range(3)],
        {
            "$group": {"_id": "$city"}
        },
        {
            "$project": {
                "_id": False,
                "city": "$_id"
            }
        }
    ])
    app.logger.info(f"Cities of User with ID '638b5f2b39c1a807a822e272' in all CVs: {list(user_cities)}")

    # # Query #4: забрати хоббі всіх здобувачів, що мешкають в заданому місті
    # user_hobbies_by_city = connection.query("""
    #         MATCH (us:User)-[:HAS]->(cv:CV)-[:HAS]->(hb:Hobby)
    #         MATCH (us:User)-[:HAS]->(cv:CV)-[:HAS]->(cp:Company)-[:IN]->(ct:City)
    #         WHERE ct.title =~ "^ABC.*"
    #         RETURN hb, ct
    #     """)
    # app.logger.info(f"Hobbies of all Users, who live in City with title 'A*': {user_hobbies_by_city}")
    #
    # # Query #5: забрати всіх здобувачів, що працювали в одному закладі (заклад ми не вказуємо)
    # users_by_company = connection.query("""
    #         MATCH (us1:User)-[:HAS]->(cv1:CV)-[:HAS]->(cp1:Company)
    #         MATCH (us2:User)-[:HAS]->(cv2:CV)-[:HAS]->(cp2:Company)
    #         WHERE cp1.title = cp2.title AND
    #               ID(us1) <> ID(us2)
    #         RETURN us1, collect(us2)
    #     """)
    # app.logger.info(f"Teammates, who work in same company': {users_by_company}")
    pass


def main():
    try:
        connection = MongoDBConnection(host="mongodb://mongo:supersecretpassword@mongo:27017",
                                       db="test")
        generator = MongoDBGenerator()
        # mongodbInitializer(connection, generator)
        mongodbQuerySimulator(connection)
        # mongodbRemover(connection)
        connection.close()
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return f"Error. {e}"
    return "Success"


@app.route("/")
def index():
    return f"Status: {main()}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
