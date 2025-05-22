from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

def test_connection():
    load_dotenv()
    
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run('RETURN 1 as test')
            success = result.single()['test'] == 1
            print('Neo4j Connection Successful:', success)
        driver.close()
    except Exception as e:
        print('Neo4j Connection Failed:', str(e))

if __name__ == '__main__':
    test_connection() 