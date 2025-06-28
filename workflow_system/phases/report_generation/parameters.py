"""
Parameters for Report Generation workflow
"""

from pydantic import BaseModel, Field
from typing import Optional

class GenerateReportParams(BaseModel):
    """Parameters for report generation workflow"""
    user_name: Optional[str] = Field(
        default=None,
        description="Extract the user's name (look for names like 'Alice', 'John', 'for user X')",
        examples=["Alice", "John", "Sarah"]
    )
    report_type: Optional[str] = Field(
        default=None,
        description="Extract report type (monthly, quarterly, annual, daily, weekly)",
        examples=["monthly", "quarterly", "annual", "daily", "weekly"]
    )