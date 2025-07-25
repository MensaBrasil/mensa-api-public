"""Data models for the API"""

from typing import Any

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import Session

from people_api.endpoints.errors import (
    DatabaseConnectionError,
    InsufficientPrivilegeError,
    QueryExecutionError,
    QuerySyntaxError,
)


class QueryRequest(BaseModel):
    """Request model for the query input"""

    query: str

    @classmethod
    async def execute(cls, query: str, session: Session):
        """Execute the SQL query and return the results"""
        try:
            result = session.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]

        except ProgrammingError as pe:
            if "must be" in str(pe):
                raise InsufficientPrivilegeError(
                    f"Insufficient privilege to execute the query: {str(pe)}"
                ) from pe

            raise QuerySyntaxError(f"Syntax error in SQL query: {str(pe)}") from pe

        except DBAPIError as dbe:
            raise DatabaseConnectionError(f"Database connection error: {str(dbe)}") from dbe

        except SQLAlchemyError as se:
            raise QueryExecutionError(f"General database error: {str(se)}") from se


class QueryResponse(BaseModel):
    """Response model for the query results"""

    results: list[dict[str, Any]]  # Structure for the query results
    status: str
