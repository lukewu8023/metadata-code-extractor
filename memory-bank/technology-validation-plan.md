# Metadata Code Extractor - Technology Validation Plan

## 1. Technology Selection Criteria & Recommendations

### LLM Provider Selection
| Provider | Recommended Models | Selection Criteria | Advantages | Limitations |
|----------|-------------------|-------------------|------------|-------------|
| **OpenRouter** ⭐ | Multiple models via unified API | - Access to multiple providers<br>- Cost optimization<br>- Model flexibility<br>- Unified interface | - Multiple model options<br>- Competitive pricing<br>- Single API integration<br>- Fallback capabilities | - Additional abstraction layer<br>- Dependency on third party<br>- Variable model availability |
| OpenAI   | GPT-4 or GPT-4o   | - Strong code understanding<br>- Robust JSON output<br>- Good technical reasoning | - Strong technical capabilities<br>- Reliable structured output<br>- Widely used with Python | - Higher cost<br>- Rate limits<br>- API changes |
| Anthropic | Claude 3 Opus or Sonnet | - Excellent context handling<br>- Strong reasoning<br>- Code understanding | - Large context window<br>- Good structured output<br>- May handle nuance better | - Less widely used<br>- Higher latency (Opus)<br>- Fewer integrations |

**SELECTED:** OpenRouter with access to multiple models (GPT-4, Claude-3, etc.) for flexibility and cost optimization.

### Graph Database Selection
| Database | Selection Criteria | Advantages | Limitations |
|----------|-------------------|------------|-------------|
| **Neo4j v4.4.44** ⭐ | - Mature graph DB<br>- Rich query language (Cypher)<br>- Strong Python support<br>- Stable LTS version | - Well-established<br>- Extensive documentation<br>- Community support<br>- Visualization tools<br>- Production-ready | - Resource intensive<br>- Licensing costs for enterprise<br>- Setup complexity |
| Memgraph | - Memory-optimized graph DB<br>- Compatible with Cypher<br>- Developer-friendly | - Better performance<br>- Developer-friendly<br>- Docker support<br>- Free developer edition | - Newer project<br>- Smaller community<br>- Fewer integrations |
| SQLite + NetworkX | - Lightweight<br>- No external dependencies<br>- Simplicity | - No setup required<br>- Self-contained<br>- Easier dev/test | - Limited scalability<br>- No graph-native queries<br>- Performance with scale |

**SELECTED:** Neo4j v4.4.44 (LTS) for its maturity, extensive tooling, and production-ready capabilities.

### Vector Database Selection
| Database | Selection Criteria | Advantages | Limitations |
|----------|-------------------|------------|-------------|
| ChromaDB | - Python-native<br>- Embedded mode<br>- Document-oriented | - Simple setup<br>- Python-first API<br>- Active development<br>- Built-in metadata | - Newer project<br>- Scale limitations<br>- Fewer advanced features |
| FAISS (Meta) | - Performance<br>- Scalability<br>- Maturity | - Highly optimized<br>- Low memory usage<br>- Fast search<br>- Industry standard | - Lower-level API<br>- Minimal metadata support<br>- Requires wrappers |
| **Weaviate v1.24.20** ⭐ | - Hybrid search<br>- Cloud-native<br>- GraphQL API<br>- Production-ready<br>- Stable version | - Combines vector & keyword<br>- Built-in schema<br>- Production-ready<br>- Advanced filtering<br>- Multi-tenancy support | - More complex setup<br>- Heavier resource usage<br>- Steeper learning curve |

**SELECTED:** Weaviate v1.24.20 for its production-ready capabilities, hybrid search features, and advanced metadata handling.

## 2. Proof of Concept (PoC) Requirements

### LLM Provider PoC
Create a simple script that:
1. Connects to the chosen LLM API
2. Sends a basic code analysis prompt
3. Retrieves and parses a structured response

**Success Criteria:**
- Successful authentication
- Prompt sent and response received without errors
- Response correctly formatted as JSON/structured data
- Basic extraction of a simple Python class definition works

**Example PoC Code Structure:**
```python
# llm_poc.py
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")  # or ANTHROPIC_API_KEY
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"  # adjust for chosen provider
MODEL = "gpt-4"  # or chosen model

# Simple Python code to analyze
sample_code = """
class User:
    \"\"\"Represents a user in the system.\"\"\"
    
    def __init__(self, user_id: str, name: str, email: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.is_active = True
    
    def deactivate(self):
        \"\"\"Deactivate this user account.\"\"\"
        self.is_active = False
        return self.is_active
"""

# Basic extraction prompt
prompt = f"""
You are a code analyzer. Extract metadata from this Python code:

{sample_code}

Return a JSON object with:
1. Class name
2. Class description
3. Fields with types and descriptions
4. Methods with descriptions

Format as valid JSON only.
"""

# API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.1,
    "response_format": {"type": "json_object"}
}

# Make request
try:
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    
    # Parse response
    result = response.json()
    extracted_data = json.loads(result["choices"][0]["message"]["content"])
    
    print("API Connection Successful!")
    print(f"Model used: {MODEL}")
    print("Extracted Metadata:")
    print(json.dumps(extracted_data, indent=2))
    
    # Validate basic structure
    assert "class_name" in extracted_data, "Missing class name"
    assert "fields" in extracted_data, "Missing fields"
    
    print("\nValidation successful - required fields present")
    
except Exception as e:
    print(f"Error: {e}")
```

### Graph Database PoC
Create a script that:
1. Connects to the chosen Graph DB
2. Creates a simple schema with essential node types
3. Inserts sample data
4. Performs a basic query

**Success Criteria:**
- Successful connection
- Schema creation without errors
- Successful data insertion
- Query returns expected results
- Basic relationship traversal works

**Example PoC Code Structure:**
```python
# graph_db_poc.py
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase  # adjust for chosen DB

# Load environment variables
load_dotenv()

# Configuration
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class GraphDBPOC:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def verify_connection(self):
        with self.driver.session() as session:
            result = session.run("RETURN 'Connection Successful!' AS message")
            record = result.single()
            return record["message"]
            
    def create_schema(self):
        # Create constraints for our node types
        with self.driver.session() as session:
            # Create constraints for unique IDs
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:DataEntity) REQUIRE e.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Field) REQUIRE (f.name, f.entity_name) IS NODE KEY")
            
            print("Schema created successfully")
            
    def create_sample_data(self):
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
                
            print("Sample data created successfully")
            
    def query_entity_with_fields(self, entity_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:DataEntity {name: $entity_name})-[:HAS_FIELD]->(f:Field)
                RETURN e.name AS entity, e.description AS description,
                       collect({name: f.name, type: f.type, description: f.description}) AS fields
            """, {"entity_name": entity_name})
            
            record = result.single()
            if record:
                return {
                    "entity": record["entity"],
                    "description": record["description"],
                    "fields": record["fields"]
                }
            return None

# Run PoC
try:
    poc = GraphDBPOC(URI, USER, PASSWORD)
    
    # Test connection
    message = poc.verify_connection()
    print(message)
    
    # Create schema
    poc.create_schema()
    
    # Create sample data
    poc.create_sample_data()
    
    # Query data
    result = poc.query_entity_with_fields("User")
    print("\nQuery Result:")
    print(f"Entity: {result['entity']}")
    print(f"Description: {result['description']}")
    print("Fields:")
    for field in result['fields']:
        print(f"  - {field['name']} ({field['type']}): {field['description']}")
        
    poc.close()
    print("\nGraph DB PoC completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
```

### Vector Database PoC
Create a script that:
1. Connects to the chosen Vector DB
2. Generates embeddings for code snippets
3. Stores embeddings with metadata
4. Performs a similarity search

**Success Criteria:**
- Successful connection
- Embedding generation works
- Data storage without errors
- Similarity search returns relevant results
- Metadata retrieval works

**Example PoC Code Structure:**
```python
# vector_db_poc.py
import os
from dotenv import load_dotenv
import chromadb  # adjust for chosen DB
import numpy as np
from openai import OpenAI  # for embedding generation, adjust as needed

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class VectorDBPOC:
    def __init__(self):
        # Initialize ChromaDB (persistent)
        self.client = chromadb.Client()
        
        # Create or get collection
        self.collection = self.client.create_collection(
            name="code_snippets",
            metadata={"description": "Code snippets for metadata extraction"}
        )
        
        # Initialize embedding provider (OpenAI in this example)
        self.embedding_client = OpenAI(api_key=OPENAI_API_KEY)
        
    def generate_embedding(self, text):
        """Generate embedding for text using OpenAI"""
        response = self.embedding_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
        
    def add_snippets(self, snippets):
        """Add code snippets to vector DB"""
        ids = [f"snippet_{i}" for i in range(len(snippets))]
        
        # Generate embeddings
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
        
        print(f"{len(snippets)} snippets added to vector DB")
        
    def search(self, query, n_results=2):
        """Search for similar snippets"""
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results

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

# Run PoC
try:
    # Initialize
    poc = VectorDBPOC()
    
    # Add snippets
    poc.add_snippets(code_snippets)
    
    # Perform search
    query = "function to convert user data dictionary into user object"
    results = poc.search(query)
    
    print("\nSearch Results:")
    for i, (doc, metadata, _) in enumerate(zip(
        results["documents"][0], 
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"\nResult {i+1}:")
        print(f"Language: {metadata['language']}")
        print(f"Description: {metadata['description']}")
        print(f"Code snippet: {doc[:100]}...")
    
    print("\nVector DB PoC completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
```

## 3. Build Process & Dependencies Verification

### Required Dependencies
Create a `pyproject.toml` file with these dependencies:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "metadata-code-extractor"
version = "0.1.0"
description = "LLM-based code metadata extraction tool with agent-driven orchestration"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
dependencies = [
    # Core utilities
    "click>=8.1.3",           # CLI framework
    "pydantic>=2.4.0",        # Data validation and settings management
    "python-dotenv>=1.0.0",   # Environment variable management
    "PyYAML>=6.0",            # Configuration file support
    
    # LLM integration - OpenRouter
    "openai>=1.6.0",          # OpenAI client (compatible with OpenRouter API)
    
    # Graph database - Neo4j v4.4.44
    "neo4j==4.4.44",          # Neo4j driver (specific LTS version)
    
    # Vector database - Weaviate v1.24.20
    "weaviate-client==3.24.2", # Weaviate client (compatible with v1.24.20)
    
    # HTTP and async support
    "aiohttp>=3.8.5",         # Async HTTP client
    "tenacity>=8.2.3",        # Retry logic
    
    # Utils
    "rich>=13.5.2",           # Rich text and progress display
    "tqdm>=4.66.1",           # Progress bars
    "tiktoken>=0.5.1",        # OpenAI tokenizer (for token counting)
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "mypy>=1.5.1",
    "ruff>=0.0.285",
]

[project.scripts]
metadata-code-extractor = "metadata_code_extractor.cli:main"
```

### Validation Steps
1. Create a clean Python virtual environment
2. Install the dependencies from pyproject.toml
3. Execute each PoC script to validate base functionality
4. Document any issues or conflicts

**Script for Dependencies Validation:**
```bash
#!/bin/bash
# validate_dependencies.sh

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Validate installations
echo "Validating installations..."
python -c "import openai; print(f'OpenAI: {openai.__version__}')"
python -c "import anthropic; print(f'Anthropic: {anthropic.__version__}')"
python -c "import neo4j; print(f'Neo4j: {neo4j.__version__}')"
python -c "import chromadb; print(f'ChromaDB: {chromadb.__version__}')"
python -c "import networkx; print(f'NetworkX: {networkx.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"

# Run PoC scripts if they exist
echo "Running PoC scripts..."
if [ -f "llm_poc.py" ]; then
    echo "Testing LLM PoC..."
    python llm_poc.py
fi

if [ -f "graph_db_poc.py" ]; then
    echo "Testing Graph DB PoC..."
    python graph_db_poc.py
fi

if [ -f "vector_db_poc.py" ]; then
    echo "Testing Vector DB PoC..."
    python vector_db_poc.py
fi

echo "Validation complete!"
```

## 4. Configuration Validation

### .env.example File
Create a `.env.example` file with all required configuration variables:

```
# LLM Provider Configuration - OpenRouter
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4  # Options: openai/gpt-4, anthropic/claude-3-sonnet, etc.
OPENROUTER_SITE_URL=https://github.com/metadata-code-extractor
OPENROUTER_APP_NAME=metadata-code-extractor

# Database Configuration
GRAPH_DB_PROVIDER=neo4j
VECTOR_DB_PROVIDER=weaviate

# Neo4j v4.4.44 Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Weaviate v1.24.20 Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=  # Optional - leave empty for local instances

# Scanning Configuration
DEFAULT_CHUNK_SIZE=40
DEFAULT_CHUNK_OVERLAP=10
MAX_TOKENS=16000
TEMPERATURE=0.1

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=metadata_code_extractor.log
```

### Configuration Loading PoC

```python
# config_poc.py
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    provider: str = Field(
        default_env="LLM_PROVIDER", 
        description="LLM provider to use"
    )
    openai_api_key: str = Field(
        default_env="OPENAI_API_KEY", 
        description="OpenAI API key"
    )
    anthropic_api_key: str = Field(
        default_env="ANTHROPIC_API_KEY", 
        description="Anthropic API key"
    )
    openai_model: str = Field(
        default_env="OPENAI_MODEL", 
        description="OpenAI model to use"
    )
    anthropic_model: str = Field(
        default_env="ANTHROPIC_MODEL", 
        description="Anthropic model to use"
    )

class DatabaseConfig(BaseModel):
    graph_provider: str = Field(
        default_env="GRAPH_DB_PROVIDER", 
        description="Graph database provider"
    )
    vector_provider: str = Field(
        default_env="VECTOR_DB_PROVIDER", 
        description="Vector database provider"
    )
    neo4j_uri: str = Field(
        default_env="NEO4J_URI", 
        description="Neo4j connection URI"
    )
    neo4j_user: str = Field(
        default_env="NEO4J_USER", 
        description="Neo4j username"
    )
    neo4j_password: str = Field(
        default_env="NEO4J_PASSWORD", 
        description="Neo4j password"
    )
    chromadb_persist_directory: str = Field(
        default_env="CHROMADB_PERSIST_DIRECTORY", 
        description="ChromaDB persistence directory"
    )

class ScanningConfig(BaseModel):
    chunk_size: int = Field(
        default_env="DEFAULT_CHUNK_SIZE", 
        description="Default code chunk size"
    )
    chunk_overlap: int = Field(
        default_env="DEFAULT_CHUNK_OVERLAP", 
        description="Default chunk overlap"
    )
    max_tokens: int = Field(
        default_env="MAX_TOKENS", 
        description="Maximum tokens for LLM context"
    )
    temperature: float = Field(
        default_env="TEMPERATURE", 
        description="LLM temperature setting"
    )

class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    scanning: ScanningConfig = Field(default_factory=ScanningConfig)
    log_level: str = Field(default_env="LOG_LEVEL", description="Logging level")
    log_file: str = Field(default_env="LOG_FILE", description="Log file path")

# Load and validate configuration
try:
    config = AppConfig()
    
    print("Configuration loaded successfully:")
    print(f"LLM Provider: {config.llm.provider}")
    print(f"Graph DB: {config.database.graph_provider}")
    print(f"Vector DB: {config.database.vector_provider}")
    print(f"Chunk Size: {config.scanning.chunk_size}")
    print(f"Log Level: {config.log_level}")
    
    # Validate provider-specific configurations
    if config.llm.provider == "openai":
        assert config.llm.openai_api_key, "OpenAI API key is required"
        assert config.llm.openai_model, "OpenAI model is required"
        
    if config.database.graph_provider == "neo4j":
        assert config.database.neo4j_uri, "Neo4j URI is required"
        assert config.database.neo4j_user, "Neo4j username is required"
        assert config.database.neo4j_password, "Neo4j password is required"
        
    print("\nConfiguration validation successful!")
    
except Exception as e:
    print(f"Configuration error: {e}")
```

## 5. Technology Validation Checklist

Create a validation checklist to ensure all components are properly validated before proceeding to implementation:

```
✓ TECHNOLOGY VALIDATION CHECKLIST

1. LLM Provider
   - [ ] Provider selected: ______________
   - [ ] API connectivity established
   - [ ] Authentication working
   - [ ] Basic prompt/response flowing
   - [ ] JSON structured output working
   - [ ] Rate limits understood
   - [ ] Cost estimates documented

2. Graph Database
   - [ ] Provider selected: ______________
   - [ ] Connection established
   - [ ] Basic CRUD operations working
   - [ ] Schema creation validated
   - [ ] Relationship creation working
   - [ ] Query performance acceptable
   - [ ] Resource requirements documented

3. Vector Database
   - [ ] Provider selected: ______________
   - [ ] Connection established
   - [ ] Embedding generation working
   - [ ] Storage mechanism validated
   - [ ] Similarity search functional
   - [ ] Metadata retrieval working
   - [ ] Performance acceptable

4. Dependencies & Build
   - [ ] All required packages identified
   - [ ] No conflicting dependencies
   - [ ] Project builds in clean environment
   - [ ] Development tools configured
   - [ ] Virtual environment setup documented

5. Configuration
   - [ ] All required config parameters identified
   - [ ] Example configuration created
   - [ ] Config loading mechanism works
   - [ ] Validation of values works
   - [ ] Sensitive values properly handled

→ If all sections complete: Ready for Technology Validation Execution
→ If any section incomplete: Address gaps before proceeding
```

## 6. Next Steps

1. **Make Final Technology Selections:**
   - Review the criteria for each technology category
   - Select specific LLM provider and model
   - Select specific Graph Database
   - Select specific Vector Database
   - Document choices in a summary report

2. **Set Up Development Environment:**
   - Create Python virtual environment
   - Install dependencies from the finalized pyproject.toml
   - Configure IDE with appropriate linting/formatting

3. **Implement PoC Scripts:**
   - Develop the LLM PoC script for the chosen provider
   - Develop the Graph DB PoC script for the chosen database
   - Develop the Vector DB PoC script for the chosen database
   - Create the configuration loading PoC

4. **Validate Technologies:**
   - Run each PoC script and validate functionality
   - Complete the validation checklist
   - Document any issues or limitations discovered
   - Finalize technology choices based on validation results

5. **Prepare for Phase 1:**
   - Update tasks.md to reflect completion of Technology Validation Planning
   - Document the validated technology stack
   - Prepare for Phase 1 implementation based on validation results 