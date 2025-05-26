"""
Prompt Management System for LLM Integration.

This module provides functionality for loading, managing, and using prompt templates
from various file formats (YAML, JSON, TXT with frontmatter).
"""
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from packaging import version


class PromptManagerError(Exception):
    """Base exception for prompt manager errors."""
    pass


class TemplateNotFoundError(PromptManagerError):
    """Raised when a requested template is not found."""
    pass


class TemplateFormatError(PromptManagerError):
    """Raised when a template file has invalid format or missing required fields."""
    pass


class PromptTemplate:
    """
    Represents a prompt template with parameter substitution capabilities.
    """
    
    def __init__(
        self,
        name: str,
        content: str,
        version: str = "1.0",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a prompt template.
        
        Args:
            name: Template name/identifier
            content: Template content with parameter placeholders
            version: Template version (semantic versioning)
            description: Optional description of the template
            metadata: Optional additional metadata
        """
        self.name = name
        self.content = content
        self.version = version
        self.description = description
        self.metadata = metadata or {}
    
    def fill(self, **kwargs) -> str:
        """
        Fill template parameters with provided values.
        
        Args:
            **kwargs: Parameter values to substitute
            
        Returns:
            Template content with parameters filled
        """
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            # Handle partial parameter substitution by using format_map with a defaultdict
            from collections import defaultdict
            
            # Create a defaultdict that returns the original placeholder for missing keys
            format_dict = defaultdict(lambda: "{" + str(e).strip("'") + "}")
            format_dict.update(kwargs)
            
            # Use string.Formatter for more control over the formatting process
            import string
            formatter = string.Formatter()
            
            # Parse the format string and substitute only available parameters
            result = ""
            for literal_text, field_name, format_spec, conversion in formatter.parse(self.content):
                result += literal_text
                if field_name is not None:
                    if field_name in kwargs:
                        # Format the field with the provided value
                        obj = kwargs[field_name]
                        if conversion:
                            obj = formatter.convert_field(obj, conversion)
                        result += formatter.format_field(obj, format_spec)
                    else:
                        # Keep the original placeholder for missing parameters
                        result += "{" + field_name + "}"
            
            return result
    
    def get_parameters(self) -> List[str]:
        """
        Extract parameter names from template content.
        
        Returns:
            List of parameter names found in the template
        """
        # Find all {parameter} patterns in the content
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, self.content)
        return list(set(matches))  # Remove duplicates
    
    def __repr__(self) -> str:
        return f"PromptTemplate(name='{self.name}', version='{self.version}')"


class PromptManager:
    """
    Manages loading and retrieval of prompt templates from files.
    
    Supports multiple file formats:
    - YAML files (.yaml, .yml)
    - JSON files (.json)
    - Text files with YAML frontmatter (.txt)
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the prompt manager.
        
        Args:
            template_dir: Directory containing template files.
                         Defaults to 'metadata_code_extractor/prompts/templates'
        """
        if template_dir is None:
            template_dir = Path("metadata_code_extractor/prompts/templates")
        else:
            template_dir = Path(template_dir)
        
        self.template_dir = template_dir
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self._loaded = False
    
    def load_templates(self) -> None:
        """
        Load all templates from the template directory.
        
        Raises:
            PromptManagerError: If template directory doesn't exist
            TemplateFormatError: If template files have invalid format
        """
        if not self.template_dir.exists() or not self.template_dir.is_dir():
            raise PromptManagerError(f"Template directory does not exist: {self.template_dir}")
        
        self._templates.clear()
        
        # Supported file extensions
        supported_extensions = {'.yaml', '.yml', '.json', '.txt'}
        
        for file_path in self.template_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    template = self._load_template_file(file_path)
                    if template:
                        self._add_template(template)
                except Exception as e:
                    raise TemplateFormatError(f"Error loading template from {file_path}: {e}")
        
        self._loaded = True
    
    def _load_template_file(self, file_path: Path) -> Optional[PromptTemplate]:
        """
        Load a single template file.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            PromptTemplate instance or None if file should be skipped
            
        Raises:
            TemplateFormatError: If file format is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise TemplateFormatError(f"Failed to read file {file_path}: {e}")
        
        if file_path.suffix.lower() in {'.yaml', '.yml'}:
            return self._load_yaml_template(content, file_path)
        elif file_path.suffix.lower() == '.json':
            return self._load_json_template(content, file_path)
        elif file_path.suffix.lower() == '.txt':
            return self._load_txt_template(content, file_path)
        
        return None
    
    def _load_yaml_template(self, content: str, file_path: Path) -> PromptTemplate:
        """Load template from YAML content."""
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise TemplateFormatError(f"Failed to parse YAML in {file_path}: {e}")
        
        return self._create_template_from_data(data, file_path)
    
    def _load_json_template(self, content: str, file_path: Path) -> PromptTemplate:
        """Load template from JSON content."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise TemplateFormatError(f"Failed to parse JSON in {file_path}: {e}")
        
        return self._create_template_from_data(data, file_path)
    
    def _load_txt_template(self, content: str, file_path: Path) -> PromptTemplate:
        """Load template from text file with YAML frontmatter."""
        # Check for YAML frontmatter
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                # Has frontmatter
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    template_content = parts[2].strip()
                except yaml.YAMLError as e:
                    raise TemplateFormatError(f"Failed to parse YAML frontmatter in {file_path}: {e}")
                
                # Merge frontmatter with content
                data = frontmatter.copy()
                data['content'] = template_content
                
                return self._create_template_from_data(data, file_path)
        
        # No frontmatter, treat as plain text template
        # Try to infer name from filename
        name = file_path.stem
        data = {
            'name': name,
            'version': '1.0',
            'content': content.strip()
        }
        
        return self._create_template_from_data(data, file_path)
    
    def _create_template_from_data(self, data: Dict[str, Any], file_path: Path) -> PromptTemplate:
        """Create PromptTemplate from parsed data."""
        # Validate required fields
        required_fields = ['name', 'content']
        for field in required_fields:
            if field not in data:
                raise TemplateFormatError(f"Missing required field '{field}' in {file_path}")
        
        # Extract fields with defaults
        name = data['name']
        content = data['content']
        version_str = data.get('version', '1.0')
        description = data.get('description')
        
        # Extract any additional metadata
        metadata = {k: v for k, v in data.items() 
                   if k not in {'name', 'content', 'version', 'description'}}
        
        return PromptTemplate(
            name=name,
            content=content,
            version=str(version_str),
            description=description,
            metadata=metadata
        )
    
    def _add_template(self, template: PromptTemplate) -> None:
        """Add a template to the internal storage."""
        if template.name not in self._templates:
            self._templates[template.name] = {}
        
        self._templates[template.name][template.version] = template
    
    def get_template(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """
        Retrieve a template by name and optionally version.
        
        Args:
            name: Template name
            version: Specific version to retrieve. If None, returns latest version.
            
        Returns:
            PromptTemplate instance
            
        Raises:
            TemplateNotFoundError: If template or version not found
        """
        # Auto-load templates on first access if not already loaded and no templates present
        if not self._loaded and not self._templates:
            self.load_templates()
        
        if name not in self._templates:
            raise TemplateNotFoundError(f"Template '{name}' not found")
        
        template_versions = self._templates[name]
        
        if version is None:
            # Return latest version
            latest_version = self._get_latest_version(list(template_versions.keys()))
            return template_versions[latest_version]
        else:
            if version not in template_versions:
                raise TemplateNotFoundError(
                    f"Version '{version}' of template '{name}' not found. "
                    f"Available versions: {list(template_versions.keys())}"
                )
            return template_versions[version]
    
    def _get_latest_version(self, versions: List[str]) -> str:
        """
        Get the latest version from a list of version strings.
        
        Uses semantic versioning comparison.
        """
        if not versions:
            raise ValueError("No versions provided")
        
        if len(versions) == 1:
            return versions[0]
        
        # Sort versions using packaging.version for proper semantic versioning
        try:
            sorted_versions = sorted(versions, key=lambda v: version.parse(v), reverse=True)
            return sorted_versions[0]
        except Exception:
            # Fallback to string sorting if version parsing fails
            return sorted(versions, reverse=True)[0]
    
    def list_templates(self) -> Dict[str, List[str]]:
        """
        List all available templates and their versions.
        
        Returns:
            Dictionary mapping template names to lists of available versions
        """
        # Auto-load templates on first access if not already loaded and no templates present
        if not self._loaded and not self._templates:
            self.load_templates()
        
        return {name: list(versions.keys()) for name, versions in self._templates.items()}
    
    def reload_templates(self) -> None:
        """
        Reload all templates from disk.
        
        This clears the current template cache and reloads from files.
        """
        self._loaded = False
        self.load_templates()
    
    def __len__(self) -> int:
        """Return the number of unique template names."""
        return len(self._templates)
    
    def __contains__(self, name: str) -> bool:
        """Check if a template name exists."""
        # Auto-load templates on first access if not already loaded and no templates present
        if not self._loaded and not self._templates:
            self.load_templates()
        
        return name in self._templates 