"""Data endpoint for querying the database"""

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from ..database.models import QueryRequest, QueryResponse
from ..dbs import get_read_only_session
from ..settings import DataRouteSettings
from .errors import (
    DatabaseConnectionError,
    QueryExecutionError,
    QuerySyntaxError,
    ReadOnlyTransactionError,
)

data_router = APIRouter(tags=["Data"], prefix="/data")

API_KEY_NAME = "data_endpoint_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = DataRouteSettings.data_api_key


def get_api_key(api_key: str = Security(api_key_header)):
    """
    Retrieve the API key from the request header.

    This function is used to extract the API key from the request's header
    using FastAPI's `Security` dependency. The `api_key_header` defines the
    name of the header where the API key should be provided.

    Args:
        api_key (str): The API key extracted from the request header.
                       Defaults to using the `api_key_header`.

    Returns:
        str: The extracted API key.

    Raises:
        HTTPException: If the API key is invalid or missing, depending on
                       how further validation is implemented.
    """

    if API_KEY is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API Key is not set")

    if api_key != API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    return API_KEY


@data_router.post("/query", response_model=QueryResponse)
async def get_data(
    request: QueryRequest,
    api_key: str = Depends(get_api_key),
    session: Session = Depends(get_read_only_session),
):
    """Execute a SQL query and return the results"""
    try:
        result = await QueryRequest.execute(request.query, session)
        return QueryResponse(results=result, status="success")

    except QuerySyntaxError as qse:
        raise HTTPException(status_code=400, detail=str(qse)) from qse

    except ReadOnlyTransactionError as rote:
        raise HTTPException(status_code=403, detail=str(rote)) from rote

    except DatabaseConnectionError as dce:
        raise HTTPException(status_code=503, detail=str(dce)) from dce

    except QueryExecutionError as qee:
        raise HTTPException(status_code=500, detail=str(qee)) from qee

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        ) from e
