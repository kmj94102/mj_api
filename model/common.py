from fastapi import HTTPException
from pydantic import BaseModel


def raise_http_exception(detail: str = "Error", status_code: int = 400):
    raise HTTPException(status_code=status_code, detail=detail)


class IntIdParam(BaseModel):
    id: int
