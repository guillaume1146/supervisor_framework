"""
Parameters for Data Processing workflow
"""

from pydantic import BaseModel, Field
from typing import Optional


class ProcessDataParams(BaseModel):
    """Parameters for data processing workflow"""
    data_source: Optional[str] = Field(
        default=None,
        description="Extract data source (sales, user_metrics, analytics, sales_data, etc.)",
        examples=["sales_data", "user_metrics", "analytics", "financial_data"]
    )
    analysis_type: Optional[str] = Field(
        default=None,
        description="Extract analysis type (trend, performance, comparison, forecast, etc.)",
        examples=["trend", "performance", "comparison", "forecast"]
    )