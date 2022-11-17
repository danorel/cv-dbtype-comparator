from core.server import app
from core.db import Neo4jConnection, Neo4jGenerator


generator = Neo4jGenerator(N=1000)


UserSchema = {
    'name': 'User',
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
            'name': 'cv',
            'instance': 'list',
            'count_from': 0,
            'count_to': 3,
            'range_from': 8,
            'range_to': 8
        }
    ]
}


def main():
    try:
        conn = Neo4jConnection(uri="neo4j://neo4j:7687",
                               user="neo4j",
                               pwd="supersecretpassword")
        user_data = generator.random_data(properties=UserSchema.get('properties'))
        for user_instance in user_data:
            user_cvs = user_instance.get('cv')
            for user_cv in user_cvs:
                conn.query(f"""
                    CREATE
                    (p:User{{
                        login: \"{user_instance.get('login')}\",
                        password: \"{user_instance.get('password')}\"
                    }})
                    -[:HAS]->
                    (t:CV{{
                        title: \"{user_cv}\"
                    }})
                """)
        # conn.query("""MATCH (n) DETACH DELETE n""")
        conn.close()
    except Exception as e:
        return f"Error. {e}"
    return "Success"


@app.route("/")
def index():
    return f"Status: {main()}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
