#!/usr/bin/env python3
# Graph Database PoC for Metadata Code Extractor - Neo4j v4.4.44
import os
from dotenv import load_dotenv
import sys

try:
    from neo4j import GraphDatabase
    import neo4j
    print(f"Using Neo4j Python driver version: {neo4j.__version__}")
except ImportError:
    print("Error: neo4j package not installed.")
    print("Install with: pip install neo4j==4.4.44")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class GraphDBPOC:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.connection_success = False
        self.schema_success = False
        self.data_success = False
        self.query_success = False
        
    def close(self):
        if hasattr(self, 'driver'):
            self.driver.close()
        
    def verify_connection(self):
        with self.driver.session() as session:
            result = session.run("RETURN 'Connection Successful!' AS message")
            record = result.single()
            message = record["message"]
            self.connection_success = True
            return message
            
    def create_schema(self):
        # Create constraints for our node types
        with self.driver.session() as session:
            try:
                # Create constraints for unique IDs
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:DataEntity) REQUIRE e.name IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Field) REQUIRE (f.name, f.entity_name) IS NODE KEY")
                
                self.schema_success = True
                print("✅ Schema created successfully")
            except Exception as e:
                print(f"❌ Schema creation error: {e}")
                return False
        return True
            
    def create_sample_data(self):
        try:
            with self.driver.session() as session:
                # Create a DataEntity node
                session.run("""
                    MERGE (e:DataEntity {name: 'User', type: 'class', description: 'Represents a user in the system'})
                """)
                
                # Create Field nodes
                fields = [
                    {"name": "user_id", "type": "str", "description": "Unique identifier for the user"},
                    {"name": "name", "type": "str", "description": "User's full name"},
                    {"name": "email", "type": "str", "description": "User's email address"},
                    {"name": "is_active", "type": "bool", "description": "Whether the user account is active"}
                ]
                
                for field in fields:
                    session.run("""
                        MATCH (e:DataEntity {name: 'User'})
                        MERGE (f:Field {name: $name, entity_name: 'User', type: $type, description: $description})
                        MERGE (e)-[:HAS_FIELD]->(f)
                    """, field)
                    
                self.data_success = True
                print("✅ Sample data created successfully")
                return True
        except Exception as e:
            print(f"❌ Data creation error: {e}")
            return False
            
    def query_entity_with_fields(self, entity_name):
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (e:DataEntity {name: $entity_name})-[:HAS_FIELD]->(f:Field)
                    RETURN e.name AS entity, e.description AS description,
                           collect({name: f.name, type: f.type, description: f.description}) AS fields
                """, {"entity_name": entity_name})
                
                record = result.single()
                if record:
                    self.query_success = True
                    return {
                        "entity": record["entity"],
                        "description": record["description"],
                        "fields": record["fields"]
                    }
                return None
        except Exception as e:
            print(f"❌ Query error: {e}")
            return None

    def cleanup(self):
        """Clean up test data"""
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (e:DataEntity {name: 'User'})
                    OPTIONAL MATCH (e)-[:HAS_FIELD]->(f:Field)
                    DETACH DELETE e, f
                """)
                print("✅ Test data cleaned up successfully")
                return True
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            return False

def run_poc():
    poc = None
    try:
        print(f"Connecting to Neo4j at {URI}...")
        poc = GraphDBPOC(URI, USER, PASSWORD)
        
        # Test connection
        message = poc.verify_connection()
        print(f"✅ {message}")
        
        # Create schema
        if not poc.create_schema():
            return False
        
        # Create sample data
        if not poc.create_sample_data():
            return False
        
        # Query data
        result = poc.query_entity_with_fields("User")
        if not result:
            print("❌ Query returned no results")
            return False
            
        print("\n✅ Query Result:")
        print(f"Entity: {result['entity']}")
        print(f"Description: {result['description']}")
        print("Fields:")
        for field in result['fields']:
            print(f"  - {field['name']} ({field['type']}): {field['description']}")
        
        # Optional: Clean up test data
        poc.cleanup()
        
        # Check overall success
        success = (poc.connection_success and 
                  poc.schema_success and 
                  poc.data_success and 
                  poc.query_success)
        
        print("\n" + "=" * 50)
        print("Neo4j Connection Test: " + ("✅ PASS" if poc.connection_success else "❌ FAIL"))
        print("Schema Creation Test: " + ("✅ PASS" if poc.schema_success else "❌ FAIL"))
        print("Data Creation Test: " + ("✅ PASS" if poc.data_success else "❌ FAIL"))
        print("Data Query Test: " + ("✅ PASS" if poc.query_success else "❌ FAIL"))
        print("=" * 50)
        print(f"\nGraph DB PoC: " + ("✅ SUCCESS" if success else "❌ FAILURE"))
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if poc:
            poc.close()

if __name__ == "__main__":
    success = run_poc()
    sys.exit(0 if success else 1) 