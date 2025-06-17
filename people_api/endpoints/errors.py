"""Custom exceptions for the endpoints module."""


class QueryExecutionError(Exception):
    """Base class for query execution errors."""


class QuerySyntaxError(QueryExecutionError):
    """Raised when there is a syntax error in the SQL query."""


class DatabaseConnectionError(QueryExecutionError):
    """Raised when the connection to the database fails."""


class ReadOnlyTransactionError(QueryExecutionError):
    """Raised when an attempt is made to write in a read-only transaction."""
