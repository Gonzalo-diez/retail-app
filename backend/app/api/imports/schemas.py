from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict, Literal

DatasetType = Literal["products", "sales", "inventory"]

class ImportRunOut(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    store_id: Optional[int]
    source_type: str
    dataset_type: str
    file_path: str
    original_filename: str
    status: str
    rows_total: int
    rows_success: int
    rows_failed: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_summary: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ImportErrorOut(BaseModel):
    id: int
    import_run_id: int
    tenant_id: int
    row_number: int
    column_name: str
    error_code: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ColumnMappingCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    dataset_type: DatasetType
    mapping: Dict[str, str] = Field(min_length=1)

class ColumnMappingOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    dataset_type: DatasetType
    mapping: Dict[str, str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProcessOut(BaseModel):
    import_run_id: int
    enqueued: bool