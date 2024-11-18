"""Data endpoint for querying the database"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.models import QueryRequest, QueryResponse
from ..dbs import get_read_only_session
from ..services.data_service import DataService, get_api_key

data_router = APIRouter(tags=["Data"], prefix="/data")


@data_router.post("/query", response_model=QueryResponse)
async def get_data(
    request: QueryRequest,
    api_key: str = Depends(get_api_key),
    session: Session = Depends(get_read_only_session),
):
    return await DataService.get_data(request, api_key, session)
