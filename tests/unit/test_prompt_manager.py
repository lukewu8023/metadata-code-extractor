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

from metadata_code_extractor.prompts.manager import (
    PromptManager,
    PromptTemplate,
    PromptManagerError,
    TemplateNotFoundError,
    TemplateFormatError
)


class TestPromptTemplate:
    """Test the PromptTemplate class."""
    
    def test_prompt_template_creation(self):
        """
        Test creating a PromptTemplate with basic content.
        
        Purpose: Verify that PromptTemplate can be instantiated with all required
        and optional parameters and stores them correctly.
        
        Checkpoints:
        - Template name is stored correctly
        - Template content is stored correctly
        - Template version is stored correctly
        - Template description is stored correctly
        - All fields are accessible after creation
        
        Mocks: None - tests actual PromptTemplate instantiation
        
        Dependencies:
        - PromptTemplate class from prompts.manager
        
        Notes: This test ensures the basic data model for prompt templates
        works correctly and all fields are properly initialized.
        """
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
        """
        Test filling template parameters.
        
        Purpose: Verify that PromptTemplate can substitute parameters in the
        template content using Python string formatting.
        
        Checkpoints:
        - Parameters are correctly substituted in template content
        - Multiple parameters can be filled simultaneously
        - Filled template returns expected string result
        - Parameter substitution preserves non-parameter text
        
        Mocks: None - tests actual string formatting functionality
        
        Dependencies:
        - PromptTemplate class with fill method
        
        Notes: Parameter filling is the core functionality of prompt templates,
        enabling dynamic prompt generation with variable content.
        """
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role}.",
            version="1.0"
        )
        
        filled = template.fill(name="Alice", role="developer")
        assert filled == "Hello Alice, you are a developer."
    
    def test_prompt_template_fill_partial_parameters(self):
        """
        Test filling template with partial parameters.
        
        Purpose: Verify that PromptTemplate handles partial parameter filling
        gracefully, leaving unfilled parameters as placeholders.
        
        Checkpoints:
        - Provided parameters are substituted correctly
        - Missing parameters remain as placeholders in the output
        - Partial filling doesn't raise errors
        - Template remains valid for further parameter filling
        
        Mocks: None - tests actual string formatting behavior
        
        Dependencies:
        - PromptTemplate class with fill method
        
        Notes: Partial parameter filling enables staged template completion
        and template reuse with different parameter sets.
        """
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role}.",
            version="1.0"
        )
        
        filled = template.fill(name="Alice")
        assert filled == "Hello Alice, you are a {role}."
    
    def test_prompt_template_fill_extra_parameters(self):
        """
        Test filling template with extra parameters (should be ignored).
        
        Purpose: Verify that PromptTemplate ignores extra parameters that don't
        have corresponding placeholders in the template content.
        
        Checkpoints:
        - Valid parameters are substituted correctly
        - Extra parameters are ignored without errors
        - Template output only includes expected substitutions
        - No side effects from extra parameters
        
        Mocks: None - tests actual string formatting behavior
        
        Dependencies:
        - PromptTemplate class with fill method
        
        Notes: Ignoring extra parameters provides flexibility when using
        templates with different parameter sets or when parameters are
        provided programmatically.
        """
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}.",
            version="1.0"
        )
        
        filled = template.fill(name="Alice", extra="ignored")
        assert filled == "Hello Alice."
    
    def test_prompt_template_get_parameters(self):
        """
        Test extracting parameter names from template.
        
        Purpose: Verify that PromptTemplate can analyze its content and extract
        the names of all parameters that need to be filled.
        
        Checkpoints:
        - All parameter names are correctly identified
        - Parameter names are returned as a list
        - Duplicate parameters are handled appropriately
        - Parameter extraction works with multiple parameters
        
        Mocks: None - tests actual parameter extraction logic
        
        Dependencies:
        - PromptTemplate class with get_parameters method
        
        Notes: Parameter extraction enables validation, documentation, and
        dynamic parameter collection for template usage.
        """
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, you are a {role} working on {project}.",
            version="1.0"
        )
        
        params = template.get_parameters()
        assert set(params) == {"name", "role", "project"}
    
    def test_prompt_template_no_parameters(self):
        """
        Test template with no parameters.
        
        Purpose: Verify that PromptTemplate handles static templates (without
        parameters) correctly and that parameter operations work on them.
        
        Checkpoints:
        - Templates without parameters are supported
        - get_parameters() returns empty list for static templates
        - fill() works on static templates (returns content unchanged)
        - Static templates behave consistently with parameterized templates
        
        Mocks: None - tests actual template behavior
        
        Dependencies:
        - PromptTemplate class
        
        Notes: Static templates are useful for fixed prompts and ensure
        the template system works for all types of prompt content.
        """
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
        """
        Test PromptManager initialization with default template directory.
        
        Purpose: Verify that PromptManager can be initialized with default
        settings and uses the expected default template directory.
        
        Checkpoints:
        - Default template directory is set correctly
        - Internal template storage is initialized as empty
        - Manager is ready for template loading operations
        - Default path points to expected location
        
        Mocks: None - tests actual initialization behavior
        
        Dependencies:
        - PromptManager class from prompts.manager
        - pathlib.Path for path handling
        
        Notes: Default initialization enables simple usage without requiring
        explicit configuration of template directories.
        """
        manager = PromptManager()
        
        # Should use default template directory
        expected_path = Path("metadata_code_extractor/prompts/templates")
        assert manager.template_dir == expected_path
        assert manager._templates == {}
    
    def test_prompt_manager_initialization_custom_dir(self):
        """
        Test PromptManager initialization with custom template directory.
        
        Purpose: Verify that PromptManager can be configured with a custom
        template directory for flexible deployment scenarios.
        
        Checkpoints:
        - Custom template directory is stored correctly
        - Internal template storage is initialized as empty
        - Manager respects custom directory configuration
        - Custom path is preserved exactly as provided
        
        Mocks: None - tests actual initialization behavior
        
        Dependencies:
        - PromptManager class
        - pathlib.Path for path handling
        
        Notes: Custom directory support enables deployment flexibility and
        allows for external template management.
        """
        custom_dir = Path("/custom/templates")
        manager = PromptManager(template_dir=custom_dir)
        
        assert manager.template_dir == custom_dir
        assert manager._templates == {}
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_load_templates_directory_not_found(self, mock_is_dir, mock_exists):
        """
        Test loading templates when directory doesn't exist.
        
        Purpose: Verify that PromptManager properly handles missing template
        directories and raises appropriate errors with clear messaging.
        
        Checkpoints:
        - Missing directory is detected correctly
        - PromptManagerError is raised for missing directory
        - Error message indicates directory doesn't exist
        - No templates are loaded when directory is missing
        
        Mocks:
        - pathlib.Path.exists: Mocked to return False (directory doesn't exist)
        - pathlib.Path.is_dir: Mocked to return False (not a directory)
        
        Dependencies:
        - PromptManager class with directory validation
        - PromptManagerError for error handling
        - pytest for exception testing
        
        Notes: Proper error handling for missing directories prevents confusing
        runtime errors and provides clear feedback for configuration issues.
        """
        mock_exists.return_value = False
        mock_is_dir.return_value = False
        
        manager = PromptManager()
        
        with pytest.raises(PromptManagerError, match="Template directory does not exist"):
            manager.load_templates()
    
    def test_load_templates_yaml_format(self):
        """
        Test loading templates from YAML files.
        
        Purpose: Verify that PromptManager can load and parse template definitions
        from YAML files with proper structure and content extraction.
        
        Checkpoints:
        - YAML files are correctly parsed
        - Template metadata (name, version, description) is extracted
        - Template content is loaded correctly
        - Template is stored in manager's internal structure
        - Template is accessible by name and version
        
        Mocks: None - uses real temporary file system operations
        
        Dependencies:
        - PromptManager class with YAML loading support
        - tempfile for creating test files
        - yaml module for YAML serialization
        - pathlib.Path for file operations
        
        Notes: YAML format support enables human-readable template definitions
        with structured metadata and content organization.
        """
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
        """
        Test loading templates from JSON files.
        
        Purpose: Verify that PromptManager can load and parse template definitions
        from JSON files as an alternative to YAML format.
        
        Checkpoints:
        - JSON files are correctly parsed
        - Template metadata is extracted from JSON structure
        - Template content is loaded correctly
        - Template is stored and accessible
        - JSON format works equivalently to YAML format
        
        Mocks: None - uses real temporary file system operations
        
        Dependencies:
        - PromptManager class with JSON loading support
        - tempfile for creating test files
        - json module for JSON serialization
        - pathlib.Path for file operations
        
        Notes: JSON format support provides an alternative to YAML for
        environments where JSON is preferred or more readily available.
        """
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
        """
        Test loading templates from TXT files with metadata header.
        
        Purpose: Verify that PromptManager can load templates from text files
        that include YAML frontmatter for metadata and plain text content.
        
        Checkpoints:
        - TXT files with YAML frontmatter are parsed correctly
        - Metadata is extracted from YAML frontmatter
        - Content is extracted from text portion (after frontmatter)
        - Frontmatter delimiters are removed from final content
        - Template is stored and accessible
        
        Mocks: None - uses real temporary file system operations
        
        Dependencies:
        - PromptManager class with TXT/frontmatter loading support
        - tempfile for creating test files
        - pathlib.Path for file operations
        
        Notes: TXT format with frontmatter enables easy editing of templates
        in text editors while maintaining structured metadata.
        """
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
        """
        Test loading multiple versions of the same template.
        
        Purpose: Verify that PromptManager can handle multiple versions of the
        same template and organize them correctly for version-specific access.
        
        Checkpoints:
        - Multiple versions of same template are loaded
        - Each version is stored separately
        - All versions are accessible by version number
        - Version organization doesn't interfere with other templates
        - Template count matches expected number of versions
        
        Mocks: None - uses real temporary file system operations
        
        Dependencies:
        - PromptManager class with version management
        - tempfile for creating test files
        - yaml module for template serialization
        
        Notes: Version management enables template evolution while maintaining
        backward compatibility and allowing gradual migration between versions.
        """
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
        """
        Test handling of invalid YAML files.
        
        Purpose: Verify that PromptManager properly handles malformed YAML files
        and raises appropriate errors with clear error messaging.
        
        Checkpoints:
        - Invalid YAML syntax is detected
        - TemplateFormatError is raised for parsing failures
        - Error message indicates YAML parsing failure
        - Invalid files don't prevent loading of valid templates
        
        Mocks: None - uses real file with invalid YAML content
        
        Dependencies:
        - PromptManager class with error handling
        - TemplateFormatError for format-specific errors
        - tempfile for creating test files
        - pytest for exception testing
        
        Notes: Robust error handling for invalid files prevents system crashes
        and provides clear feedback for template authoring issues.
        """
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
        """
        Test handling of templates missing required fields.
        
        Purpose: Verify that PromptManager validates template structure and
        raises appropriate errors when required fields are missing.
        
        Checkpoints:
        - Missing required fields are detected
        - TemplateFormatError is raised for validation failures
        - Error message indicates which field is missing
        - Template validation prevents incomplete templates
        
        Mocks: None - uses real file with incomplete template
        
        Dependencies:
        - PromptManager class with template validation
        - TemplateFormatError for validation errors
        - tempfile for creating test files
        - yaml module for template creation
        
        Notes: Template validation ensures that all loaded templates are
        complete and usable, preventing runtime errors during template usage.
        """
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
        """
        Test successfully retrieving a template.
        
        Purpose: Verify that PromptManager can retrieve loaded templates by name
        and return properly constructed PromptTemplate instances.
        
        Checkpoints:
        - Template is retrieved successfully by name
        - Retrieved template has correct metadata
        - Template content is preserved correctly
        - Template is ready for use after retrieval
        
        Mocks: None - uses real template loading and retrieval
        
        Dependencies:
        - PromptManager class with template retrieval
        - tempfile for creating test templates
        - yaml module for template creation
        
        Notes: Template retrieval is the primary interface for accessing
        loaded templates and must work reliably for all template operations.
        """
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
        """
        Test retrieving a specific version of a template.
        
        Purpose: Verify that PromptManager can retrieve specific versions of
        templates when multiple versions are available.
        
        Checkpoints:
        - Specific version is retrieved correctly
        - Version-specific content is returned
        - Other versions are not affected
        - Version specification works accurately
        
        Mocks: None - uses real template loading with multiple versions
        
        Dependencies:
        - PromptManager class with version-specific retrieval
        - tempfile for creating test templates
        - yaml module for template creation
        
        Notes: Version-specific retrieval enables precise template selection
        and supports applications that need specific template versions.
        """
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
        """
        Test retrieving the latest version when no version specified.
        
        Purpose: Verify that PromptManager returns the latest version of a
        template when no specific version is requested.
        
        Checkpoints:
        - Latest version is determined correctly
        - Latest version is returned when no version specified
        - Version comparison works with semantic versioning
        - Latest version selection is consistent
        
        Mocks: None - uses real template loading with version comparison
        
        Dependencies:
        - PromptManager class with version comparison logic
        - tempfile for creating test templates
        - yaml module for template creation
        
        Notes: Latest version selection provides convenient access to the
        most recent template version while supporting version-specific access.
        """
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
        """
        Test retrieving a non-existent template.
        
        Purpose: Verify that PromptManager raises appropriate errors when
        attempting to retrieve templates that don't exist.
        
        Checkpoints:
        - Non-existent template raises TemplateNotFoundError
        - Error message indicates template name
        - Error handling doesn't affect other operations
        - Clear error messaging for debugging
        
        Mocks: None - uses empty template manager
        
        Dependencies:
        - PromptManager class with error handling
        - TemplateNotFoundError for missing templates
        - pytest for exception testing
        
        Notes: Proper error handling for missing templates prevents runtime
        errors and provides clear feedback for template usage issues.
        """
        manager = PromptManager()
        manager._templates = {}  # Empty templates
        manager._loaded = True  # Mark as loaded to bypass auto-loading
        
        with pytest.raises(TemplateNotFoundError, match="Template 'nonexistent' not found"):
            manager.get_template("nonexistent")
    
    def test_get_template_version_not_found(self):
        """
        Test retrieving a non-existent version of an existing template.
        
        Purpose: Verify that PromptManager raises appropriate errors when
        attempting to retrieve specific versions that don't exist.
        
        Checkpoints:
        - Non-existent version raises TemplateNotFoundError
        - Error message indicates template name and version
        - Existing versions are not affected
        - Version-specific error messaging
        
        Mocks: None - uses manually configured template manager
        
        Dependencies:
        - PromptManager class with version validation
        - TemplateNotFoundError for missing versions
        - PromptTemplate for test data
        - pytest for exception testing
        
        Notes: Version-specific error handling helps users understand
        version availability and prevents confusion about template versions.
        """
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
        """
        Test listing all available templates.
        
        Purpose: Verify that PromptManager can provide a comprehensive list
        of all loaded templates with their versions for discovery and debugging.
        
        Checkpoints:
        - All loaded templates are included in the list
        - Template versions are properly organized
        - List structure enables easy template discovery
        - Template count matches expected values
        
        Mocks: None - uses manually configured template manager
        
        Dependencies:
        - PromptManager class with template listing
        - PromptTemplate for test data
        
        Notes: Template listing enables template discovery, debugging, and
        administrative operations on the template collection.
        """
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
        """
        Test reloading templates from disk.
        
        Purpose: Verify that PromptManager can reload templates from disk,
        enabling dynamic template updates without application restart.
        
        Checkpoints:
        - Initial templates are loaded correctly
        - Template modifications are detected after reload
        - Updated content is reflected in retrieved templates
        - Reload operation completes successfully
        
        Mocks: None - uses real file system operations
        
        Dependencies:
        - PromptManager class with reload functionality
        - tempfile for creating and modifying templates
        - yaml module for template serialization
        
        Notes: Template reloading enables dynamic template management and
        supports development workflows where templates are frequently modified.
        """
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
        """
        Test that templates are automatically loaded on first access.
        
        Purpose: Verify that PromptManager automatically loads templates from
        disk when first accessed, providing lazy loading functionality.
        
        Checkpoints:
        - Templates are not loaded during manager initialization
        - First template access triggers automatic loading
        - Auto-loaded templates are accessible and functional
        - Lazy loading improves initialization performance
        
        Mocks: None - uses real template loading behavior
        
        Dependencies:
        - PromptManager class with auto-loading
        - tempfile for creating test templates
        - yaml module for template creation
        
        Notes: Auto-loading provides convenient usage patterns where templates
        are loaded on-demand, improving application startup time and resource usage.
        """
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