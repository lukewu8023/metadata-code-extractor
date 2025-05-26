#!/usr/bin/env python3
# Configuration Loading PoC for Metadata Code Extractor
import os
import sys
from dotenv import load_dotenv

# Check for required packages
try:
    from pydantic import BaseModel, Field
except ImportError:
    print("Error: pydantic package not installed.")
    print("Install with: pip install pydantic")
    sys.exit(1)

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    provider: str = Field(
        default=os.getenv("LLM_PROVIDER", "openrouter"), 
        description="LLM provider to use"
    )
    openrouter_api_key: str = Field(
        default=os.getenv("OPENROUTER_API_KEY", ""), 
        description="OpenRouter API key"
    )
    openrouter_model: str = Field(
        default=os.getenv("OPENROUTER_MODEL", "openai/gpt-4"), 
        description="OpenRouter model to use"
    )
    openrouter_site_url: str = Field(
        default=os.getenv("OPENROUTER_SITE_URL", "https://github.com/metadata-code-extractor"), 
        description="OpenRouter site URL for referrer"
    )
    openrouter_app_name: str = Field(
        default=os.getenv("OPENROUTER_APP_NAME", "metadata-code-extractor"), 
        description="OpenRouter app name"
    )

class DatabaseConfig(BaseModel):
    graph_provider: str = Field(
        default=os.getenv("GRAPH_DB_PROVIDER", "neo4j"), 
        description="Graph database provider"
    )
    vector_provider: str = Field(
        default=os.getenv("VECTOR_DB_PROVIDER", "weaviate"), 
        description="Vector database provider"
    )
    neo4j_uri: str = Field(
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"), 
        description="Neo4j connection URI"
    )
    neo4j_user: str = Field(
        default=os.getenv("NEO4J_USER", "neo4j"), 
        description="Neo4j username"
    )
    neo4j_password: str = Field(
        default=os.getenv("NEO4J_PASSWORD", "password"), 
        description="Neo4j password"
    )
    weaviate_url: str = Field(
        default=os.getenv("WEAVIATE_URL", "http://localhost:8080"), 
        description="Weaviate connection URL"
    )
    weaviate_api_key: str = Field(
        default=os.getenv("WEAVIATE_API_KEY", ""), 
        description="Weaviate API key (optional for local instances)"
    )

class ScanningConfig(BaseModel):
    chunk_size: int = Field(
        default=int(os.getenv("DEFAULT_CHUNK_SIZE", "40")), 
        description="Default code chunk size"
    )
    chunk_overlap: int = Field(
        default=int(os.getenv("DEFAULT_CHUNK_OVERLAP", "10")), 
        description="Default chunk overlap"
    )
    max_tokens: int = Field(
        default=int(os.getenv("MAX_TOKENS", "16000")), 
        description="Maximum tokens for LLM context"
    )
    temperature: float = Field(
        default=float(os.getenv("TEMPERATURE", "0.1")), 
        description="LLM temperature setting"
    )

class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    scanning: ScanningConfig = Field(default_factory=ScanningConfig)
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"), description="Logging level")
    log_file: str = Field(default=os.getenv("LOG_FILE", "metadata_code_extractor.log"), description="Log file path")

def run_poc():
    success = True
    validation_results = {
        "config_loading": False,
        "llm_provider_validation": False,
        "database_provider_validation": False
    }
    
    try:
        print("Loading configuration...")
        config = AppConfig()
        validation_results["config_loading"] = True
        
        print("\n✅ Configuration loaded successfully:")
        print(f"LLM Provider: {config.llm.provider}")
        print(f"Graph DB: {config.database.graph_provider}")
        print(f"Vector DB: {config.database.vector_provider}")
        print(f"Chunk Size: {config.scanning.chunk_size}")
        print(f"Log Level: {config.log_level}")
        
        # Validate provider-specific configurations
        print("\nValidating LLM provider configuration...")
        if config.llm.provider == "openrouter":
            if not config.llm.openrouter_api_key:
                print("❌ Warning: OpenRouter API key is empty")
                success = False
            else:
                print("✅ OpenRouter API key is set")
                
            if not config.llm.openrouter_model:
                print("❌ Warning: OpenRouter model is empty")
                success = False
            else:
                print(f"✅ OpenRouter model is set: {config.llm.openrouter_model}")
                
            if not config.llm.openrouter_site_url:
                print("❌ Warning: OpenRouter site URL is empty")
                success = False
            else:
                print(f"✅ OpenRouter site URL is set: {config.llm.openrouter_site_url}")
                
            validation_results["llm_provider_validation"] = bool(
                config.llm.openrouter_api_key and 
                config.llm.openrouter_model and 
                config.llm.openrouter_site_url
            )
        
        print("\nValidating database provider configuration...")
        if config.database.graph_provider == "neo4j":
            if not config.database.neo4j_uri:
                print("❌ Warning: Neo4j URI is empty")
                success = False
            else:
                print(f"✅ Neo4j URI is set: {config.database.neo4j_uri}")
                
            if not config.database.neo4j_user:
                print("❌ Warning: Neo4j username is empty")
                success = False
            else:
                print(f"✅ Neo4j username is set: {config.database.neo4j_user}")
                
            if not config.database.neo4j_password:
                print("❌ Warning: Neo4j password is empty")
                success = False
            else:
                print("✅ Neo4j password is set")
                
            validation_results["database_provider_validation"] = bool(
                config.database.neo4j_uri and 
                config.database.neo4j_user and 
                config.database.neo4j_password
            )
            
        if config.database.vector_provider == "weaviate":
            if not config.database.weaviate_url:
                print("❌ Warning: Weaviate URL is empty")
                success = False
            else:
                print(f"✅ Weaviate URL is set: {config.database.weaviate_url}")
                
            # API key is optional for local instances
            if config.database.weaviate_api_key:
                print("✅ Weaviate API key is set (for cloud instances)")
            else:
                print("ℹ️ Weaviate API key not set (assuming local instance)")

        # Test serialization
        print("\nTesting config serialization...")
        config_dict = config.model_dump()
        print("✅ Config successfully serialized to dictionary")
        
        # Recreate from dict
        print("Testing config deserialization...")
        config2 = AppConfig.model_validate(config_dict)
        print("✅ Config successfully deserialized from dictionary")
        
        # Print summary
        print("\n" + "=" * 50)
        print("Config Loading: " + ("✅ PASS" if validation_results["config_loading"] else "❌ FAIL"))
        print(f"LLM Provider ({config.llm.provider}) Validation: " + 
              ("✅ PASS" if validation_results["llm_provider_validation"] else "❌ FAIL"))
        print(f"Database Provider ({config.database.graph_provider}) Validation: " + 
              ("✅ PASS" if validation_results["database_provider_validation"] else "❌ FAIL"))
        print("=" * 50)
        
        if success:
            print("\n✅ Configuration PoC: SUCCESS")
        else:
            print("\n⚠️ Configuration PoC: PARTIAL SUCCESS (some warnings)")
            
        return success
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    success = run_poc()
    # Exit with status 0 even with warnings, since this is just validation
    sys.exit(0) 