"""
Database Models for Phase 1: Core Input Validation
File: workflow_system/phases/phase1_financial_input/database_models.py
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from workflow_system.models.database import DatabaseField, DatabaseRecord


@dataclass
class FinancialInputValidationRecord:
    """Complete database record for Phase 1 financial input validation"""
    
    # Primary identification
    id: Optional[int] = None
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Core financial data (always required)
    valuation_date: Optional[date] = None
    provider_name: Optional[str] = None
    product_name: Optional[str] = None
    product_type: Optional[str] = None  # Enum value as string
    fund_value: Optional[Decimal] = None
    surrender_value: Optional[Decimal] = None
    
    # Investment term configuration
    investment_term_type: Optional[str] = None  # Enum: until, years, age
    end_date: Optional[date] = None  # Used when term_type = 'until'
    user_input_years: Optional[int] = None  # Used when term_type = 'years'
    user_input_months: Optional[int] = None  # Additional months
    current_age: Optional[int] = None  # Used when term_type = 'age'
    target_age: Optional[int] = None  # Used when term_type = 'age'
    
    # Calculated fields (computed from other values)
    term_years: Optional[Decimal] = None  # Calculated based on term type
    initial_investment_value: Optional[Decimal] = None  # Fund or surrender value
    analysis_mode: Optional[str] = None  # Enum: switching, remodeling
    
    # Tax configuration
    include_taxation: Optional[bool] = None
    tax_band: Optional[str] = None  # Enum: basic_rate_20, higher_rate_40, additional_rate_45
    client_tax_rate: Optional[Decimal] = None  # Tax band as decimal
    
    # Analysis metadata
    performing_switch_analysis: Optional[bool] = None
    data_quality_score: Optional[int] = None
    completion_percentage: Optional[Decimal] = None
    validation_status: Optional[str] = None  # pending, validated, failed
    
    # Error tracking
    missing_fields: Optional[str] = None  # JSON array of missing field names
    validation_errors: Optional[str] = None  # JSON array of validation errors
    
    def to_database_record(self, formatted_values: Dict[str, str]) -> DatabaseRecord:
        """Convert to DatabaseRecord for insertion - FIXED VERSION"""
        
        fields = {}
        
        # Core identification fields
        if self.id is not None:
            fields['id'] = DatabaseField('id', self.id, 'INTEGER', False, True)
            
        fields['session_id'] = DatabaseField('session_id', self.session_id, 'VARCHAR(100)')
        fields['created_at'] = DatabaseField('created_at', self.created_at or datetime.utcnow(), 'TIMESTAMP')
        fields['updated_at'] = DatabaseField('updated_at', self.updated_at or datetime.utcnow(), 'TIMESTAMP')
        
        # Core financial data
        fields['valuation_date'] = DatabaseField('valuation_date', self.valuation_date, 'DATE')
        fields['provider_name'] = DatabaseField('provider_name', self.provider_name, 'VARCHAR(255)')
        fields['product_name'] = DatabaseField('product_name', self.product_name, 'VARCHAR(255)')
        fields['product_type'] = DatabaseField('product_type', self.product_type, 'VARCHAR(50)')
        fields['fund_value'] = DatabaseField('fund_value', self.fund_value, 'DECIMAL(15,2)')
        fields['surrender_value'] = DatabaseField('surrender_value', self.surrender_value, 'DECIMAL(15,2)')
        
        # Investment term configuration
        fields['investment_term_type'] = DatabaseField('investment_term_type', self.investment_term_type, 'VARCHAR(20)')
        fields['end_date'] = DatabaseField('end_date', self.end_date, 'DATE')
        fields['user_input_years'] = DatabaseField('user_input_years', self.user_input_years, 'INTEGER')
        fields['user_input_months'] = DatabaseField('user_input_months', self.user_input_months, 'INTEGER')
        fields['current_age'] = DatabaseField('current_age', self.current_age, 'INTEGER')
        fields['target_age'] = DatabaseField('target_age', self.target_age, 'INTEGER')
        
        # FIXED: Calculated fields - ensure they're properly set
        fields['term_years'] = DatabaseField('term_years', self.term_years, 'DECIMAL(10,4)')
        fields['initial_investment_value'] = DatabaseField('initial_investment_value', self.initial_investment_value, 'DECIMAL(15,2)')
        fields['analysis_mode'] = DatabaseField('analysis_mode', self.analysis_mode, 'VARCHAR(20)')
        
        # Tax configuration
        fields['include_taxation'] = DatabaseField('include_taxation', self.include_taxation, 'BOOLEAN')
        fields['tax_band'] = DatabaseField('tax_band', self.tax_band, 'VARCHAR(30)')
        fields['client_tax_rate'] = DatabaseField('client_tax_rate', self.client_tax_rate, 'DECIMAL(5,4)')
        
        # Analysis metadata - ENSURE these are populated
        fields['performing_switch_analysis'] = DatabaseField('performing_switch_analysis', self.performing_switch_analysis, 'BOOLEAN')
        fields['data_quality_score'] = DatabaseField('data_quality_score', self.data_quality_score, 'INTEGER')
        fields['completion_percentage'] = DatabaseField('completion_percentage', self.completion_percentage, 'DECIMAL(5,2)')
        fields['validation_status'] = DatabaseField('validation_status', self.validation_status, 'VARCHAR(20)')
        
        # Error tracking
        fields['missing_fields'] = DatabaseField('missing_fields', self.missing_fields, 'TEXT')
        fields['validation_errors'] = DatabaseField('validation_errors', self.validation_errors, 'TEXT')
        
        return DatabaseRecord(
            table_name="financial_input_validation",
            fields=fields,
            formatted_values=formatted_values,
            metadata={
                "phase": "phase1_financial_input",
                "record_type": "FinancialInputValidationRecord",
                "schema_version": "1.0",
                "total_fields": len(fields),
                "non_null_fields": len([f for f in fields.values() if f.value is not None])
            }
        )
    
    @classmethod
    def from_params(cls, params: Dict[str, Any], session_id: Optional[str] = None) -> 'FinancialInputValidationRecord':
        """Create record from parameter dictionary"""
        return cls(
            session_id=session_id,
            valuation_date=params.get('valuation_date'),
            provider_name=params.get('provider_name'),
            product_name=params.get('product_name'),
            product_type=params.get('product_type'),
            fund_value=params.get('fund_value'),
            surrender_value=params.get('surrender_value'),
            investment_term_type=params.get('investment_term_type'),
            end_date=params.get('end_date'),
            user_input_years=params.get('user_input_years'),
            user_input_months=params.get('user_input_months'),
            current_age=params.get('current_age'),
            target_age=params.get('target_age'),
            include_taxation=params.get('include_taxation'),
            tax_band=params.get('tax_band'),
            performing_switch_analysis=params.get('performing_switch_analysis')
        )


# Database schema definition for reference
DATABASE_SCHEMA = {
    "financial_input_validation": {
        "columns": {
            "id": "INTEGER PRIMARY KEY AUTO_INCREMENT",
            "session_id": "VARCHAR(100) NOT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            
            # Core financial data
            "valuation_date": "DATE",
            "provider_name": "VARCHAR(255)",
            "product_name": "VARCHAR(255)",
            "product_type": "VARCHAR(50)",
            "fund_value": "DECIMAL(15,2)",
            "surrender_value": "DECIMAL(15,2)",
            
            # Investment term configuration
            "investment_term_type": "VARCHAR(20)",
            "end_date": "DATE",
            "user_input_years": "INTEGER",
            "user_input_months": "INTEGER",
            "current_age": "INTEGER",
            "target_age": "INTEGER",
            
            # Calculated fields
            "term_years": "DECIMAL(10,4)",
            "initial_investment_value": "DECIMAL(15,2)",
            "analysis_mode": "VARCHAR(20)",
            
            # Tax configuration
            "include_taxation": "BOOLEAN",
            "tax_band": "VARCHAR(30)",
            "client_tax_rate": "DECIMAL(5,4)",
            
            # Analysis metadata
            "performing_switch_analysis": "BOOLEAN",
            "data_quality_score": "INTEGER",
            "completion_percentage": "DECIMAL(5,2)",
            "validation_status": "VARCHAR(20)",
            
            # Error tracking
            "missing_fields": "TEXT",
            "validation_errors": "TEXT"
        },
        "indexes": [
            "INDEX idx_session_id (session_id)",
            "INDEX idx_valuation_date (valuation_date)",
            "INDEX idx_product_type (product_type)",
            "INDEX idx_validation_status (validation_status)"
        ],
        "constraints": [
            "CHECK (fund_value > 0)",
            "CHECK (surrender_value > 0)",
            "CHECK (current_age >= 16 AND current_age <= 100)",
            "CHECK (target_age > current_age)",
            "CHECK (data_quality_score >= 0 AND data_quality_score <= 100)"
        ]
    }
}