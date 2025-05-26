"""
Tests for the PromptManager class.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml
import json

from metadata_code_extractor.core.prompts.manager import (
    PromptManager,
    PromptTemplate,
    PromptManagerError,
    TemplateNotFoundError,
    TemplateFormatError
)


class TestPromptTemplate:
    """Test the PromptTemplate class."""
    
    def test_prompt_template_creation(self):
        """Test creating a PromptTemplate with basic content."""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role}.",
            version="1.0",
            description="A test template"
        )
        
        assert template.name == "test_template"
        assert template.content == "Hello {name}, you are a {role}."
        assert template.version == "1.0"
        assert template.description == "A test template"
    
    def test_prompt_template_fill_parameters(self):
        """Test filling template parameters."""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role}.",
            version="1.0"
        )
        
        filled = template.fill(name="Alice", role="developer")
        assert filled == "Hello Alice, you are a developer."
    
    def test_prompt_template_fill_partial_parameters(self):
        """Test filling template with partial parameters."""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role}.",
            version="1.0"
        )
        
        filled = template.fill(name="Alice")
        assert filled == "Hello Alice, you are a {role}."
    
    def test_prompt_template_fill_extra_parameters(self):
        """Test filling template with extra parameters (should be ignored)."""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}.",
            version="1.0"
        )
        
        filled = template.fill(name="Alice", extra="ignored")
        assert filled == "Hello Alice."
    
    def test_prompt_template_get_parameters(self):
        """Test extracting parameter names from template."""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role} working on {project}.",
            version="1.0"
        )
        
        params = template.get_parameters()
        assert set(params) == {"name", "role", "project"}
    
    def test_prompt_template_no_parameters(self):
        """Test template with no parameters."""
        template = PromptTemplate(
            name="test_template",
            content="This is a static template.",
            version="1.0"
        )
        
        params = template.get_parameters()
        assert params == []
        
        filled = template.fill()
        assert filled == "This is a static template."


class TestPromptManager:
    """Test the PromptManager class."""
    
    def test_prompt_manager_initialization_default(self):
        """Test PromptManager initialization with default template directory."""
        manager = PromptManager()
        
        # Should use default template directory
        expected_path = Path("metadata_code_extractor/prompts/templates")
        assert manager.template_dir == expected_path
        assert manager._templates == {}
    
    def test_prompt_manager_initialization_custom_dir(self):
        """Test PromptManager initialization with custom template directory."""
        custom_dir = Path("/custom/templates")
        manager = PromptManager(template_dir=custom_dir)
        
        assert manager.template_dir == custom_dir
        assert manager._templates == {}
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_load_templates_directory_not_found(self, mock_is_dir, mock_exists):
        """Test loading templates when directory doesn't exist."""
        mock_exists.return_value = False
        mock_is_dir.return_value = False
        
        manager = PromptManager()
        
        with pytest.raises(PromptManagerError, match="Template directory does not exist"):
            manager.load_templates()
    
    def test_load_templates_yaml_format(self):
        """Test loading templates from YAML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create a YAML template file
            yaml_content = {
                "name": "entity_extraction",
                "version": "1.0",
                "description": "Extract entities from code",
                "content": "You are a code analyzer. Extract entities from:\n{code_chunk}"
            }
            
            yaml_file = template_dir / "entity_extraction.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            assert "entity_extraction" in manager._templates
            template = manager._templates["entity_extraction"]["1.0"]
            assert template.name == "entity_extraction"
            assert template.version == "1.0"
            assert template.description == "Extract entities from code"
            assert "Extract entities from:" in template.content
    
    def test_load_templates_json_format(self):
        """Test loading templates from JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create a JSON template file
            json_content = {
                "name": "field_extraction",
                "version": "2.0",
                "description": "Extract fields from entities",
                "content": "Analyze the following entity and extract fields:\n{entity_code}"
            }
            
            json_file = template_dir / "field_extraction.json"
            with open(json_file, 'w') as f:
                json.dump(json_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            assert "field_extraction" in manager._templates
            template = manager._templates["field_extraction"]["2.0"]
            assert template.name == "field_extraction"
            assert template.version == "2.0"
            assert "extract fields:" in template.content
    
    def test_load_templates_txt_format(self):
        """Test loading templates from TXT files with metadata header."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create a TXT template file with YAML frontmatter
            txt_content = """---
name: validation_extraction
version: 1.5
description: Extract validation rules
---
You are analyzing validation rules.

CODE:
{code_chunk}

Extract all validation rules for {entity_name}.
"""
            
            txt_file = template_dir / "validation_extraction.txt"
            with open(txt_file, 'w') as f:
                f.write(txt_content)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            assert "validation_extraction" in manager._templates
            template = manager._templates["validation_extraction"]["1.5"]
            assert template.name == "validation_extraction"
            assert template.version == "1.5"
            assert "You are analyzing validation rules." in template.content
            assert "---" not in template.content  # Frontmatter should be removed
    
    def test_load_templates_multiple_versions(self):
        """Test loading multiple versions of the same template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create multiple versions
            for version in ["1.0", "1.1", "2.0"]:
                yaml_content = {
                    "name": "entity_extraction",
                    "version": version,
                    "description": f"Extract entities v{version}",
                    "content": f"Version {version}: Extract entities from {{code_chunk}}"
                }
                
                yaml_file = template_dir / f"entity_extraction_v{version.replace('.', '_')}.yaml"
                with open(yaml_file, 'w') as f:
                    yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            assert "entity_extraction" in manager._templates
            assert len(manager._templates["entity_extraction"]) == 3
            assert "1.0" in manager._templates["entity_extraction"]
            assert "1.1" in manager._templates["entity_extraction"]
            assert "2.0" in manager._templates["entity_extraction"]
    
    def test_load_templates_invalid_yaml(self):
        """Test handling of invalid YAML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create invalid YAML file
            yaml_file = template_dir / "invalid.yaml"
            with open(yaml_file, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            manager = PromptManager(template_dir=template_dir)
            
            with pytest.raises(TemplateFormatError, match="Failed to parse YAML"):
                manager.load_templates()
    
    def test_load_templates_missing_required_fields(self):
        """Test handling of templates missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create template missing 'content' field
            yaml_content = {
                "name": "incomplete_template",
                "version": "1.0",
                "description": "Missing content field"
                # Missing 'content' field
            }
            
            yaml_file = template_dir / "incomplete.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            
            with pytest.raises(TemplateFormatError, match="Missing required field"):
                manager.load_templates()
    
    def test_get_template_success(self):
        """Test successfully retrieving a template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create template
            yaml_content = {
                "name": "test_template",
                "version": "1.0",
                "description": "Test template",
                "content": "Hello {name}"
            }
            
            yaml_file = template_dir / "test_template.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            template = manager.get_template("test_template")
            assert template.name == "test_template"
            assert template.version == "1.0"
            assert template.content == "Hello {name}"
    
    def test_get_template_specific_version(self):
        """Test retrieving a specific version of a template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create multiple versions
            for version in ["1.0", "2.0"]:
                yaml_content = {
                    "name": "test_template",
                    "version": version,
                    "description": f"Test template v{version}",
                    "content": f"Version {version}: Hello {{name}}"
                }
                
                yaml_file = template_dir / f"test_template_v{version.replace('.', '_')}.yaml"
                with open(yaml_file, 'w') as f:
                    yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            template = manager.get_template("test_template", version="1.0")
            assert template.version == "1.0"
            assert "Version 1.0:" in template.content
    
    def test_get_template_latest_version(self):
        """Test retrieving the latest version when no version specified."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create multiple versions (not in order)
            for version in ["1.0", "2.1", "1.5"]:
                yaml_content = {
                    "name": "test_template",
                    "version": version,
                    "description": f"Test template v{version}",
                    "content": f"Version {version}: Hello {{name}}"
                }
                
                yaml_file = template_dir / f"test_template_v{version.replace('.', '_')}.yaml"
                with open(yaml_file, 'w') as f:
                    yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            template = manager.get_template("test_template")
            assert template.version == "2.1"  # Should be the latest version
    
    def test_get_template_not_found(self):
        """Test retrieving a non-existent template."""
        manager = PromptManager()
        manager._templates = {}  # Empty templates
        manager._loaded = True  # Mark as loaded to bypass auto-loading
        
        with pytest.raises(TemplateNotFoundError, match="Template 'nonexistent' not found"):
            manager.get_template("nonexistent")
    
    def test_get_template_version_not_found(self):
        """Test retrieving a non-existent version of an existing template."""
        manager = PromptManager()
        manager._templates = {
            "test_template": {
                "1.0": PromptTemplate("test_template", "content", "1.0")
            }
        }
        manager._loaded = True  # Mark as loaded to bypass auto-loading
        
        with pytest.raises(TemplateNotFoundError, match="Version '2.0' of template 'test_template' not found"):
            manager.get_template("test_template", version="2.0")
    
    def test_list_templates(self):
        """Test listing all available templates."""
        manager = PromptManager()
        manager._templates = {
            "template1": {
                "1.0": PromptTemplate("template1", "content1", "1.0"),
                "2.0": PromptTemplate("template1", "content1", "2.0")
            },
            "template2": {
                "1.0": PromptTemplate("template2", "content2", "1.0")
            }
        }
        manager._loaded = True  # Mark as loaded to bypass auto-loading
        
        templates = manager.list_templates()
        
        assert len(templates) == 2
        assert "template1" in templates
        assert "template2" in templates
        assert len(templates["template1"]) == 2
        assert len(templates["template2"]) == 1
    
    def test_reload_templates(self):
        """Test reloading templates from disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create initial template
            yaml_content = {
                "name": "test_template",
                "version": "1.0",
                "description": "Initial template",
                "content": "Initial content"
            }
            
            yaml_file = template_dir / "test_template.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            manager.load_templates()
            
            # Verify initial load
            template = manager.get_template("test_template")
            assert template.content == "Initial content"
            
            # Modify template file
            yaml_content["content"] = "Updated content"
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            # Reload templates
            manager.reload_templates()
            
            # Verify updated content
            template = manager.get_template("test_template")
            assert template.content == "Updated content"
    
    def test_auto_load_on_first_access(self):
        """Test that templates are automatically loaded on first access."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            
            # Create template
            yaml_content = {
                "name": "auto_load_template",
                "version": "1.0",
                "description": "Auto load test",
                "content": "Auto loaded content"
            }
            
            yaml_file = template_dir / "auto_load_template.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            manager = PromptManager(template_dir=template_dir)
            # Don't call load_templates() explicitly
            
            # First access should trigger auto-load
            template = manager.get_template("auto_load_template")
            assert template.content == "Auto loaded content" 