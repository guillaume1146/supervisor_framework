"""
Database models for structured data ready for database insertion
File: workflow_system/models/database.py
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from enum import Enum


@dataclass
class DatabaseField:
    """Represents a field ready for database insertion"""
    column_name: str
    value: Any
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    foreign_key: Optional[str] = None
    constraints: Optional[List[str]] = None


@dataclass
class DatabaseRecord:
    """Represents a complete record ready for database insertion"""
    table_name: str
    fields: Dict[str, DatabaseField]
    formatted_values: Dict[str, str]  # Human-readable formatted values
    metadata: Dict[str, Any]
    
    def get_insert_data(self) -> Dict[str, Any]:
        """Get data ready for database INSERT"""
        return {field.column_name: field.value for field in self.fields.values()}
    
    def get_formatted_data(self) -> Dict[str, str]:
        """Get formatted data for display"""
        return self.formatted_values.copy()


# Database Models for Phase 1
@dataclass
class Phase1DatabaseRecord(DatabaseRecord):
    """Phase 1 specific database record with validation"""
    
    def __post_init__(self):
        self.table_name = "financial_input_validation"
        if not self.metadata:
            self.metadata = {}
        self.metadata.update({
            "phase": "phase1_financial_input",
            "schema_version": "1.0"
        })


