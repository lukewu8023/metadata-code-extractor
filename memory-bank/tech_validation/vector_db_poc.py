#!/usr/bin/env python3
# Vector Database PoC for Metadata Code Extractor
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required packages
required_packages = ["chromadb", "openai"]
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("Error: Missing required packages:")
    for package in missing_packages:
        print(f"  - {package}")
    print("Install with: pip install " + " ".join(missing_packages))
    sys.exit(1)

# Now that we've checked, import the packages
import chromadb
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMADB_PERSIST_DIRECTORY = os.getenv("CHROMADB_PERSIST_DIRECTORY", "./data/chromadb")
COLLECTION_NAME = "code_snippets_test"

class VectorDBPOC:
    def __init__(self):
        self.connection_success = False
        self.embeddings_success = False
        self.storage_success = False
        self.search_success = False
        
        # Create persistence directory if it doesn't exist
        os.makedirs(CHROMADB_PERSIST_DIRECTORY, exist_ok=True)
        
        # Initialize ChromaDB (persistent)
        try:
            self.client = chromadb.PersistentClient(path=CHROMADB_PERSIST_DIRECTORY)
            print(f"✅ Connected to ChromaDB (persistence: {CHROMADB_PERSIST_DIRECTORY})")
            self.connection_success = True
        except Exception as e:
            print(f"❌ ChromaDB connection error: {e}")
            raise
        
        # Create or get collection
        try:
            # Try to get existing collection or create a new one
            try:
                self.collection = self.client.get_collection(name=COLLECTION_NAME)
                print(f"✅ Using existing collection: {COLLECTION_NAME}")
            except Exception:  # Collection doesn't exist
                self.collection = self.client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"description": "Code snippets for metadata extraction"}
                )
                print(f"✅ Created new collection: {COLLECTION_NAME}")
        except Exception as e:
            print(f"❌ Collection creation error: {e}")
            raise
        
        # Initialize embedding provider (OpenAI in this example)
        if not OPENAI_API_KEY:
            print("❌ Error: OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY not set")
            
        try:
            self.embedding_client = OpenAI(api_key=OPENAI_API_KEY)
            print("✅ Initialized OpenAI client for embeddings")
        except Exception as e:
            print(f"❌ OpenAI client initialization error: {e}")
            raise
        
    def generate_embedding(self, text):
        """Generate embedding for text using OpenAI"""
        try:
            response = self.embedding_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            self.embeddings_success = True
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding generation error: {e}")
            raise
        
    def add_snippets(self, snippets):
        """Add code snippets to vector DB"""
        try:
            ids = [f"snippet_{i}" for i in range(len(snippets))]
            
            # Generate embeddings
            print(f"Generating embeddings for {len(snippets)} snippets...")
            embeddings = [self.generate_embedding(snippet["code"]) for snippet in snippets]
            
            # Extract metadata
            metadatas = [{"language": snippet["language"], 
                        "description": snippet["description"]} 
                        for snippet in snippets]
            
            # Extract document text
            documents = [snippet["code"] for snippet in snippets]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.storage_success = True
            print(f"✅ {len(snippets)} snippets added to vector DB")
            return True
        except Exception as e:
            print(f"❌ Data storage error: {e}")
            return False
        
    def search(self, query, n_results=2):
        """Search for similar snippets"""
        try:
            # Generate query embedding
            print(f"Generating embedding for query: '{query}'")
            query_embedding = self.generate_embedding(query)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            self.search_success = True
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return None
            
    def cleanup(self):
        """Clean up test collection"""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            print(f"✅ Test collection '{COLLECTION_NAME}' deleted")
            return True
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            return False

# Sample data
code_snippets = [
    {
        "code": """
class User:
    \"\"\"Represents a user in the system.\"\"\"
    
    def __init__(self, user_id: str, name: str, email: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.is_active = True
        """,
        "language": "python",
        "description": "User class definition"
    },
    {
        "code": """
class Product:
    \"\"\"Represents a product in the inventory.\"\"\"
    
    def __init__(self, product_id: str, name: str, price: float, category: str = "general"):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.in_stock = True
        """,
        "language": "python",
        "description": "Product class definition"
    },
    {
        "code": """
def process_user_data(user_data: dict) -> User:
    \"\"\"Transform raw user data dictionary into a User object.\"\"\"
    user_id = user_data.get('id')
    name = user_data.get('full_name')
    email = user_data.get('email_address')
    
    if not user_id or not name:
        raise ValueError("User data must contain id and full_name")
        
    return User(user_id=user_id, name=name, email=email)
        """,
        "language": "python",
        "description": "User data transformation function"
    }
]

def run_poc():
    poc = None
    try:
        print("Initializing Vector DB PoC...")
        poc = VectorDBPOC()
        
        # Add snippets
        if not poc.add_snippets(code_snippets):
            return False
        
        # Perform search
        query = "function to convert user data dictionary into user object"
        print(f"\nPerforming similarity search with query: '{query}'")
        results = poc.search(query)
        
        if not results:
            print("❌ Search returned no results")
            return False
            
        print("\n✅ Search Results:")
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0], 
            results["metadatas"][0],
            results["distances"][0]
        )):
            print(f"\nResult {i+1}:")
            print(f"Language: {metadata['language']}")
            print(f"Description: {metadata['description']}")
            print(f"Similarity score: {1 - distance:.4f}")  # Convert distance to similarity
            print(f"Code snippet: {doc[:100]}...")
        
        # Optional cleanup
        poc.cleanup()
        
        # Check overall success
        success = (poc.connection_success and 
                  poc.embeddings_success and 
                  poc.storage_success and 
                  poc.search_success)
        
        print("\n" + "=" * 50)
        print("ChromaDB Connection: " + ("✅ PASS" if poc.connection_success else "❌ FAIL"))
        print("Embedding Generation: " + ("✅ PASS" if poc.embeddings_success else "❌ FAIL"))
        print("Vector Storage: " + ("✅ PASS" if poc.storage_success else "❌ FAIL"))
        print("Similarity Search: " + ("✅ PASS" if poc.search_success else "❌ FAIL"))
        print("=" * 50)
        print(f"\nVector DB PoC: " + ("✅ SUCCESS" if success else "❌ FAILURE"))
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_poc()
    sys.exit(0 if success else 1) 