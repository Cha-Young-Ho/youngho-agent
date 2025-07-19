"""
Custom exceptions for MCP server.
"""


class MCPError(Exception):
    """Base exception for MCP server errors."""
    pass


class OpenSearchError(MCPError):
    """Exception raised for OpenSearch related errors."""
    pass


class ValidationError(MCPError):
    """Exception raised for validation errors."""
    pass


class ConfigurationError(MCPError):
    """Exception raised for configuration errors."""
    pass


class DocumentProcessingError(MCPError):
    """Exception raised for document processing errors."""
    pass


class SearchError(MCPError):
    """Exception raised for search related errors."""
    pass


class AuthenticationError(MCPError):
    """Exception raised for authentication errors."""
    pass


class FileProcessingError(MCPError):
    """Exception raised for file processing errors."""
    pass 