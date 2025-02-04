"""Service for handling data requests from the data endpoints."""

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from people_api.endpoints.errors import (
    DatabaseConnectionError,
    QueryExecutionError,
    QuerySyntaxError,
    ReadOnlyTransactionError,
)

from ..database.models import QueryRequest, QueryResponse
from ..settings import get_settings

SETTINGS = get_settings()

API_KEY_NAME = "data_endpoint_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = SETTINGS.data_route_api_key


def get_api_key(api_key: str = Security(api_key_header)):
    if API_KEY is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API Key is not set")

    if api_key != API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    return API_KEY


class DataService:
    @staticmethod
    async def get_data(request: QueryRequest, api_key: str, session: Session):
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
