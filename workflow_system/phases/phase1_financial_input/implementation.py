"""
Enhanced Implementation for Phase 1: Core Input Validation and Initial Values
File: workflow_system/phases/phase1_financial_input/implementation.py (UPDATED)
"""

import datetime
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal

from workflow_system.utils.converters import Phase1DataConverter
from workflow_system.phases.phase1_financial_input.field_calculators import (
    Phase1FieldCalculator, BusinessRuleValidator
)
from workflow_system.phases.phase1_financial_input.database_models import (
    FinancialInputValidationRecord
)
from workflow_system.phases.phase1_financial_input.constants import (
    CORE_REQUIRED_FIELDS, VALIDATION_MESSAGES, SystemLimits
)

logger = logging.getLogger(__name__)


class Phase1WorkflowProcessor:
    """Enhanced processor for Phase 1 workflow with database integration"""
    
    def __init__(self):
        self.data_converter = Phase1DataConverter()
        self.field_calculator = Phase1FieldCalculator()
        self.validation_errors = []
        self.processing_warnings = []
        
    def clear_errors_and_warnings(self):
        """Clear all errors and warnings"""
        self.validation_errors.clear()
        self.processing_warnings.clear()
        self.field_calculator.clear_errors()
    
    def validate_core_requirements(self, params: Dict[str, Any]) -> List[str]:
        """Validate core required fields"""
        errors = []
        
        for field in CORE_REQUIRED_FIELDS:
            value = params.get(field)
            if not value or str(value).strip().lower() in ['', 'none', 'not specified', 'null']:
                field_message = VALIDATION_MESSAGES.get(f"{field}_required", f"{field} is required")
                errors.append(field_message)
        
        return errors
    
    def validate_data_types_and_ranges(self, params: Dict[str, Any]) -> List[str]:
        """Validate data types and value ranges"""
        errors = []
        
        try:
            # Validate dates
            valuation_date = params.get('valuation_date')
            if valuation_date:
                try:
                    self.data_converter.type_converter.to_database_date(valuation_date)
                except ValueError as e:
                    errors.append(VALIDATION_MESSAGES.get('valuation_date_format', str(e)))
            
            end_date = params.get('end_date')
            if end_date:
                try:
                    self.data_converter.type_converter.to_database_date(end_date)
                except ValueError as e:
                    errors.append(f"End date format error: {str(e)}")
            
            # Validate currency amounts
            for field in ['fund_value', 'surrender_value']:
                value_str = params.get(field)
                if value_str:
                    try:
                        decimal_value = self.data_converter.type_converter.to_database_decimal(value_str)
                        if decimal_value:
                            if decimal_value <= 0:
                                errors.append(VALIDATION_MESSAGES.get(f"{field}_positive"))
                            elif decimal_value > SystemLimits.MAX_FUND_VALUE:
                                errors.append(VALIDATION_MESSAGES.get(f"{field}_maximum"))
                            elif decimal_value < SystemLimits.MIN_FUND_VALUE:
                                errors.append(VALIDATION_MESSAGES.get(f"{field}_minimum"))
                    except ValueError as e:
                        errors.append(f"Invalid amount for {field}: {str(e)}")
            
            # Validate ages
            for field in ['current_age', 'target_age']:
                age_str = params.get(field)
                if age_str:
                    try:
                        age_value = self.data_converter.type_converter.to_database_integer(age_str)
                        if age_value:
                            if age_value < SystemLimits.MIN_AGE:
                                errors.append(VALIDATION_MESSAGES.get('age_minimum'))
                            elif age_value > SystemLimits.MAX_AGE:
                                errors.append(VALIDATION_MESSAGES.get('age_maximum'))
                    except ValueError as e:
                        errors.append(f"Invalid age for {field}: {str(e)}")
            
            # Validate year inputs
            years_str = params.get('user_input_years')
            if years_str:
                try:
                    years_value = self.data_converter.type_converter.to_database_integer(years_str)
                    if years_value and years_value > SystemLimits.MAX_TERM_YEARS:
                        errors.append(VALIDATION_MESSAGES.get('term_years_maximum'))
                except ValueError as e:
                    errors.append(f"Invalid years input: {str(e)}")
            
            months_str = params.get('user_input_months')
            if months_str:
                try:
                    months_value = self.data_converter.type_converter.to_database_integer(months_str)
                    if months_value and (months_value < 0 or months_value > 11):
                        errors.append("Months must be between 0 and 11")
                except ValueError as e:
                    errors.append(f"Invalid months input: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error during data validation: {e}")
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def process_and_convert_data(self, params: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, str]]:
        """
        Process and convert all field data
        Returns: (database_values, formatted_display_values)
        """
        try:
            # Get user input fields only (exclude computed fields)
            from workflow_system.phases.phase1_financial_input.parameters import FinancialInputValidationParams
            user_input_fields = FinancialInputValidationParams.get_user_input_fields()
            
            # Filter to only user input fields
            user_params = {k: v for k, v in params.items() if k in user_input_fields}
            
            # Convert user input fields
            database_values = self.data_converter.get_database_values(user_params)
            display_values = self.data_converter.get_display_values(user_params)
            
            # Calculate computed fields
            calculated_fields = self.field_calculator.calculate_all_fields(
                database_values, CORE_REQUIRED_FIELDS
            )
            
            # Add calculated fields to database values
            database_values.update(calculated_fields)
            
            # Format calculated fields for display
            calculated_display = self.data_converter.get_display_values(calculated_fields)
            display_values.update(calculated_display)
            
            # Add calculation errors to validation errors
            calc_errors = self.field_calculator.get_errors()
            if calc_errors:
                self.validation_errors.extend(calc_errors)
            
            return database_values, display_values
            
        except Exception as e:
            logger.error(f"Error during data processing: {e}")
            self.validation_errors.append(f"Data processing error: {str(e)}")
            return {}, {}
    
    def run_business_rule_validation(self, database_values: Dict[str, Any]) -> List[str]:
        """Run business rule validations"""
        try:
            return BusinessRuleValidator.validate_all_business_rules(database_values)
        except Exception as e:
            logger.error(f"Error during business rule validation: {e}")
            return [f"Business rule validation error: {str(e)}"]
    
    def create_database_record(self, database_values: Dict[str, Any], 
                             display_values: Dict[str, str], 
                             session_id: Optional[str] = None) -> FinancialInputValidationRecord:
        """Create database record from processed values"""
        try:
            # Create record from database values
            record = FinancialInputValidationRecord.from_params(database_values, session_id)
            
            # Set additional metadata fields
            record.created_at = datetime.datetime.utcnow()
            record.updated_at = datetime.datetime.utcnow()
            
            # Convert to full database record with formatting
            db_record = record.to_database_record(display_values)
            
            return db_record
            
        except Exception as e:
            logger.error(f"Error creating database record: {e}")
            raise ValueError(f"Database record creation failed: {str(e)}")
    
    def generate_completion_message(self, database_values: Dict[str, Any], 
                                  display_values: Dict[str, str]) -> str:
        """Generate user-friendly completion message"""
        try:
            validation_status = database_values.get('validation_status', 'unknown')
            data_quality_score = database_values.get('data_quality_score', 0)
            missing_fields = database_values.get('missing_fields', [])
            
            if validation_status == 'validated':
                return self._generate_success_message(database_values, display_values, data_quality_score)
            elif validation_status == 'pending':
                return self._generate_pending_message(missing_fields, display_values)
            else:
                return self._generate_error_message(missing_fields, self.validation_errors)
                
        except Exception as e:
            logger.error(f"Error generating completion message: {e}")
            return f"❌ Error generating completion message: {str(e)}"
    
    def _generate_success_message(self, database_values: Dict[str, Any], 
                                display_values: Dict[str, str], 
                                score: int) -> str:
        """Generate success completion message"""
        product_type = display_values.get('product_type', 'financial product')
        provider = display_values.get('provider_name', 'Unknown provider')
        fund_value = display_values.get('fund_value', 'Not specified')
        analysis_mode = display_values.get('analysis_mode', 'analysis')
        
        return f"""
✅ **Phase 1: Core Input Validation - COMPLETED**

🎉 **All required information has been successfully collected and validated!**

**📋 Summary of Your {product_type.title()} Information:**
• **Provider:** {provider}
• **Product:** {display_values.get('product_name', 'Not specified')}
• **Current Fund Value:** {fund_value}
• **Valuation Date:** {display_values.get('valuation_date', 'Not specified')}
• **Analysis Type:** {analysis_mode.title()}
• **Investment Term:** {display_values.get('term_years', 'Not specified')} years

**✨ Data Quality Score:** {score}/100

**🚀 Ready for next phase of analysis**

Your core financial product information is complete and validated.
        """.strip()
    
    def _generate_pending_message(self, missing_fields: List[str], 
                                display_values: Dict[str, str]) -> str:
        """Generate message for pending validation"""
        if not missing_fields:
            missing_fields = ["Some required fields"]
            
        # Convert field names to user-friendly format
        friendly_names = {
            'valuation_date': 'Valuation Date',
            'provider_name': 'Provider Name',
            'product_name': 'Product Name',
            'product_type': 'Product Type',
            'fund_value': 'Current Fund Value',
            'surrender_value': 'Surrender/Transfer Value',
            'investment_term_type': 'Investment Term Type',
            'current_age': 'Client Age',
            'target_age': 'Target Age',
            'end_date': 'End Date',
            'user_input_years': 'Number of Years',
            'include_taxation': 'Include Tax Analysis',
            'tax_band': 'Tax Band'
        }
        
        missing_friendly = [friendly_names.get(field, field.replace('_', ' ').title()) 
                          for field in missing_fields]
        
        return f"""
⚠️ **Phase 1: Core Input Validation - INCOMPLETE**

📝 **Missing Required Information:**
{chr(10).join(f'• {field}' for field in missing_friendly)}

**Current Progress:**
• **Provider:** {display_values.get('provider_name', 'Not specified')}
• **Product Type:** {display_values.get('product_type', 'Not specified')}
• **Fund Value:** {display_values.get('fund_value', 'Not specified')}

Please provide the missing information to complete Phase 1 validation.
        """.strip()
    
    def _generate_error_message(self, missing_fields: List[str], 
                              validation_errors: List[str]) -> str:
        """Generate error message for failed validation"""
        error_summary = []
        
        if missing_fields:
            error_summary.append(f"Missing fields: {', '.join(missing_fields[:3])}")
            if len(missing_fields) > 3:
                error_summary.append(f"and {len(missing_fields) - 3} more")
        
        if validation_errors:
            error_summary.extend(validation_errors[:2])  # Show first 2 errors
            
        return f"""
❌ **Phase 1: Core Input Validation - VALIDATION FAILED**

**Issues Found:**
{chr(10).join(f'• {error}' for error in error_summary)}

Please correct these issues and try again.
        """.strip()


def financial_input_validation_workflow(params: Dict[str, Any], 
                                      session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhanced Phase 1: Core Input Validation and Initial Values
    Validates, processes, and converts core financial product inputs with database integration
    
    Args:
        params: Dictionary of input parameters
        session_id: Optional session identifier
        
    Returns:
        Dictionary containing workflow results, database record, and formatted data
    """
    logger.info(f"Executing enhanced financial input validation workflow with params: {list(params.keys())}")
    
    processor = Phase1WorkflowProcessor()
    
    try:
        # Clear any previous errors
        processor.clear_errors_and_warnings()
        
        # Step 1: Validate core requirements
        core_errors = processor.validate_core_requirements(params)
        processor.validation_errors.extend(core_errors)
        
        # Step 2: Validate data types and ranges
        type_errors = processor.validate_data_types_and_ranges(params)
        processor.validation_errors.extend(type_errors)
        
        # Step 3: Process and convert all data
        database_values, display_values = processor.process_and_convert_data(params)
        
        # Step 4: Run business rule validation
        business_errors = processor.run_business_rule_validation(database_values)
        processor.validation_errors.extend(business_errors)
        
        # Step 5: Determine completion status
        missing_fields = database_values.get('missing_fields', [])
        is_complete = len(missing_fields) == 0 and len(processor.validation_errors) == 0
        
        # Step 6: Create database record (even if incomplete for progress tracking)
        try:
            database_record = processor.create_database_record(
                database_values, display_values, session_id
            )
        except Exception as e:
            logger.error(f"Failed to create database record: {e}")
            database_record = None
        
        # Step 7: Generate completion message
        completion_message = processor.generate_completion_message(database_values, display_values)
        
        # Step 8: Prepare workflow result
        status = "completed" if is_complete else "incomplete"
        
        result = {
            "status": status,
            "phase": "Phase 1: Core Input Validation and Initial Values",
            "completion_message": completion_message,
            "processed_data": display_values,  # User-friendly formatted data
            "database_values": database_values,  # Raw database values
            "database_record": database_record.get_insert_data() if database_record else None,
            "validation_results": {
                "is_complete": is_complete,
                "missing_fields": missing_fields,
                "validation_errors": processor.validation_errors,
                "data_quality_score": database_values.get('data_quality_score', 0),
                "completion_percentage": float(database_values.get('completion_percentage', 0))
            },
            "completed_at": datetime.datetime.utcnow().isoformat(),
            "workflow_type": "financial_input_validation",
            "metadata": {
                "session_id": session_id,
                "total_user_fields": len(params),
                "processed_fields": len(database_values),
                "display_fields": len(display_values),
                "ready_for_next_phase": is_complete,
                "analysis_mode": database_values.get('analysis_mode'),
                "product_type": database_values.get('product_type')
            }
        }
        
        logger.info(f"Enhanced financial input validation completed. Status: {status}")
        logger.info(f"Data quality score: {database_values.get('data_quality_score', 0)}/100")
        
        return result
        
    except Exception as e:
        logger.error(f"Critical error in enhanced financial input validation: {e}", exc_info=True)
        
        return {
            "status": "failed",
            "phase": "Phase 1: Core Input Validation and Initial Values",
            "completion_message": f"❌ **Critical Error**: {str(e)}",
            "processed_data": {},
            "database_values": {},
            "database_record": None,
            "validation_results": {
                "is_complete": False,
                "missing_fields": [],
                "validation_errors": [str(e)],
                "data_quality_score": 0,
                "completion_percentage": 0.0
            },
            "completed_at": datetime.datetime.utcnow().isoformat(),
            "workflow_type": "financial_input_validation",
            "error": str(e),
            "metadata": {
                "session_id": session_id,
                "error_type": type(e).__name__,
                "ready_for_next_phase": False
            }
        }