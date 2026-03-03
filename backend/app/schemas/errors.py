from pydantic import BaseModel
from typing import Any, Optional

class ErrorPayload(BaseModel):
    code: str
    message: str
    detail: Optional[Any] = None
    field: Optional[str] = None

class ErrorResponse(BaseModel):
    error: ErrorPayload