"""
Implementation for Phase 1: Core Input Validation and Initial Values
"""

import datetime
import logging
from typing import Dict, Any

from workflow_system.utils.normalizers import (
    normalize_date, normalize_currency, normalize_product_type,
    normalize_provider_name, normalize_years, normalize_age
)
from .calculations import assess_data_readiness

logger = logging.getLogger(__name__)


def financial_input_validation_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 1: Core Input Validation and Initial Values
    Validates and processes core financial product inputs
    """
    logger.info(f"Executing financial input validation workflow with params: {params}")
    
    # Extract parameters
    valuation_date = params.get("valuation_date")
    current_fund_value = params.get("current_fund_value")
    annual_contribution = params.get("annual_contribution")
    product_type = params.get("product_type")
    provider_name = params.get("provider_name")
    income_withdrawal = params.get("income_withdrawal", "None")
    term_years = params.get("term_years", "Not specified")
    client_age = params.get("client_age", "Not specified")
    
    # Process and normalize the data using utils
    processed_data = {
        "valuation_date": normalize_date(valuation_date),
        "current_fund_value": normalize_currency(current_fund_value),
        "annual_contribution": normalize_currency(annual_contribution),
        "product_type": normalize_product_type(product_type),
        "provider_name": normalize_provider_name(provider_name),
        "income_withdrawal": normalize_currency(income_withdrawal) if income_withdrawal.lower() != "none" else "£0",
        "term_years": normalize_years(term_years),
        "client_age": normalize_age(client_age)
    }
    
    # Assess data readiness using phase-specific calculations
    validation_results = assess_data_readiness(processed_data)
    
    # Generate completion message
    if validation_results["core_fields_complete"]:
        completion_message = f"""
✅ **Phase 1: Core Input Validation - COMPLETED**

🎉 **All required information has been successfully collected and validated!**

**📋 Summary of Your Financial Product Information:**
• **Valuation Date:** {processed_data['valuation_date']}
• **Product Type:** {processed_data['product_type']}
• **Provider:** {processed_data['provider_name']}
• **Current Fund Value:** {processed_data['current_fund_value']}
• **Annual Contribution:** {processed_data['annual_contribution']}
• **Income Withdrawal:** {processed_data['income_withdrawal']}
• **Investment Term:** {processed_data['term_years']}
• **Client Age:** {processed_data['client_age']}

**✨ Data Quality Score:** {validation_results['completion_score']}/100

**🚀 Ready to proceed to Phase 2: Client Demographics and Income Analysis**

Your core financial product information is now complete and ready for comprehensive analysis.
        """.strip()
    else:
        missing_fields = validation_results["missing_core_fields"]
        completion_message = f"""
⚠️ **Phase 1: Core Input Validation - INCOMPLETE**

Missing required fields: {', '.join(missing_fields)}

Please provide the missing information to complete Phase 1.
        """.strip()
    
    result = {
        "status": "completed" if validation_results["core_fields_complete"] else "incomplete",
        "phase": "Phase 1: Core Input Validation and Initial Values",
        "completion_message": completion_message,
        "processed_data": processed_data,
        "validation_results": validation_results,
        "completed_at": datetime.datetime.utcnow().isoformat(),
        "workflow_type": "financial_input_validation",
        "metadata": {
            "fields_completed": len([v for v in processed_data.values() if v and v != "Not specified"]),
            "total_fields": len(processed_data),
            "completion_percentage": round((len([v for v in processed_data.values() if v and v != "Not specified"]) / len(processed_data)) * 100, 1),
            "ready_for_next_phase": validation_results["core_fields_complete"]
        }
    }
    
    logger.info(f"Financial input validation completed. Status: {result['status']}")
    return result