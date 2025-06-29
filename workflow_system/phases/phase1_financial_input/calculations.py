"""
Enhanced calculations specific to Phase 1: Financial Input Validation
File: workflow_system/phases/phase1_financial_input/calculations.py (UPDATED)
"""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime

from workflow_system.utils.calculators import (
    calculate_data_quality_score,
    calculate_completion_percentage,
    calculate_term_years_from_dates,
    calculate_term_years_from_years_months,
    calculate_term_years_from_ages,
    calculate_surrender_penalty,
    calculate_comprehensive_projection
)
from .constants import (
    CORE_REQUIRED_FIELDS, 
    PENSION_PRODUCTS, 
    ISA_PRODUCTS,
    INVESTMENT_PRODUCTS,
    TAX_EXEMPT_PRODUCTS,
    SystemLimits,
    DEFAULT_GROWTH_RATES,
    TAX_RATES
)


def calculate_phase1_completion_score(processed_data: Dict[str, Any]) -> int:
    """Enhanced completion score calculation specific to Phase 1 requirements"""
    
    # Define core fields with higher weight for Phase 1
    phase1_core_fields = [
        'valuation_date', 
        'current_fund_value', 
        'annual_contribution', 
        'product_type', 
        'provider_name',
        'investment_term_type'
    ]
    
    # Use the enhanced calculator with Phase 1 specific core fields
    return calculate_data_quality_score(processed_data, phase1_core_fields)


def assess_data_readiness(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced data readiness assessment with comprehensive analysis"""
    
    # Core fields that are absolutely required
    core_fields = CORE_REQUIRED_FIELDS.copy()
    
    # Check core field completion
    core_complete = all(
        processed_data.get(field) and 
        str(processed_data.get(field, "")).strip().lower() not in ["", "not specified", "none", "null"]
        for field in core_fields
    )
    
    # Calculate completion score
    completion_score = calculate_phase1_completion_score(processed_data)
    
    # Identify missing core fields
    missing_core_fields = [
        field for field in core_fields 
        if not processed_data.get(field) or
        str(processed_data.get(field, "")).strip().lower() in ["", "not specified", "none", "null"]
    ]
    
    # Product-specific field validation
    product_type = processed_data.get('product_type')
    product_specific_missing = []
    
    if product_type:
        if product_type in PENSION_PRODUCTS:
            pension_fields = ['current_age', 'include_taxation', 'tax_band']
            product_specific_missing.extend([
                field for field in pension_fields
                if not processed_data.get(field) or
                str(processed_data.get(field, "")).strip().lower() in ["", "not specified", "none", "null"]
            ])
        
        elif product_type in INVESTMENT_PRODUCTS:
            investment_fields = ['include_taxation', 'tax_band']
            product_specific_missing.extend([
                field for field in investment_fields
                if not processed_data.get(field) or
                str(processed_data.get(field, "")).strip().lower() in ["", "not specified", "none", "null"]
            ])
    
    # Term-specific field validation
    term_type = processed_data.get('investment_term_type')
    term_specific_missing = []
    
    if term_type:
        if term_type == 'until':
            if not processed_data.get('end_date'):
                term_specific_missing.append('end_date')
        elif term_type == 'years':
            if not processed_data.get('user_input_years'):
                term_specific_missing.append('user_input_years')
        elif term_type == 'age':
            age_fields = ['current_age', 'target_age']
            term_specific_missing.extend([
                field for field in age_fields
                if not processed_data.get(field) or
                str(processed_data.get(field, "")).strip().lower() in ["", "not specified", "none", "null"]
            ])
    
    # Overall readiness assessment
    all_missing = list(set(missing_core_fields + product_specific_missing + term_specific_missing))
    is_ready = len(all_missing) == 0
    
    # Calculate readiness percentage
    total_required_fields = len(core_fields) + len(product_specific_missing) + len(term_specific_missing)
    missing_count = len(all_missing)
    readiness_percentage = max(0, ((total_required_fields - missing_count) / max(1, total_required_fields)) * 100)
    
    return {
        "core_fields_complete": core_complete,
        "completion_score": completion_score,
        "ready_for_next_phase": is_ready,
        "readiness_percentage": round(readiness_percentage, 1),
        "missing_core_fields": missing_core_fields,
        "missing_product_specific": product_specific_missing,
        "missing_term_specific": term_specific_missing,
        "all_missing_fields": all_missing,
        "total_missing_count": len(all_missing),
        "analysis_summary": _generate_readiness_summary(is_ready, completion_score, all_missing)
    }


def calculate_investment_projection(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate basic investment projection based on processed Phase 1 data"""
    
    try:
        # Extract required values
        initial_value = processed_data.get('initial_investment_value') or processed_data.get('fund_value')
        term_years = processed_data.get('term_years')
        product_type = processed_data.get('product_type')
        
        if not all([initial_value, term_years, product_type]):
            return {
                "projection_available": False,
                "error": "Insufficient data for projection calculation"
            }
        
        # Convert to Decimal for precision
        if isinstance(initial_value, str):
            initial_value = Decimal(initial_value.replace('£', '').replace(',', ''))
        elif isinstance(initial_value, (int, float)):
            initial_value = Decimal(str(initial_value))
        
        if isinstance(term_years, (int, float, str)):
            term_years = Decimal(str(term_years))
        
        # Determine appropriate growth rate based on product type
        if product_type in PENSION_PRODUCTS:
            growth_rate = DEFAULT_GROWTH_RATES['moderate']  # 5% for pensions
        elif product_type in ISA_PRODUCTS:
            growth_rate = DEFAULT_GROWTH_RATES['moderate']  # 5% for ISAs
        elif product_type in INVESTMENT_PRODUCTS:
            growth_rate = DEFAULT_GROWTH_RATES['growth']    # 8% for investments
        else:
            growth_rate = DEFAULT_GROWTH_RATES['conservative']  # 2% for others
        
        # Calculate basic projection (no contributions assumed for simplicity)
        annual_contribution = Decimal('0')  # Phase 1 doesn't collect contributions
        
        # Use comprehensive projection calculator
        projection = calculate_comprehensive_projection(
            initial_value=initial_value,
            annual_contribution=annual_contribution,
            annual_rate=growth_rate,
            annual_charges=Decimal('0'),  # No charges assumed
            tax_rate=Decimal('0'),        # Tax will be handled in later phases
            inflation_rate=Decimal('0.025'),  # 2.5% inflation assumption
            years=term_years
        )
        
        return {
            "projection_available": True,
            "initial_value": initial_value,
            "projected_value": projection['projection_summary']['nominal_future_value'],
            "real_value": projection['projection_summary']['real_future_value'],
            "total_growth": projection['projection_summary']['total_growth'],
            "growth_rate_used": growth_rate,
            "term_years": term_years,
            "annual_income_potential": projection['income_potential']['annual_income'],
            "monthly_income_potential": projection['income_potential']['monthly_income']
        }
        
    except Exception as e:
        return {
            "projection_available": False,
            "error": f"Projection calculation failed: {str(e)}"
        }


def calculate_surrender_penalty_analysis(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze surrender penalty based on fund value vs surrender value"""
    
    try:
        fund_value = processed_data.get('fund_value')
        surrender_value = processed_data.get('surrender_value')
        
        if not fund_value or not surrender_value:
            return {
                "analysis_available": False,
                "reason": "Fund value and surrender value required"
            }
        
        # Convert to Decimal
        if isinstance(fund_value, str):
            fund_value = Decimal(fund_value.replace('£', '').replace(',', ''))
        if isinstance(surrender_value, str):
            surrender_value = Decimal(surrender_value.replace('£', '').replace(',', ''))
        
        # Calculate penalty analysis
        penalty_analysis = calculate_surrender_penalty(fund_value, surrender_value)
        
        # Add interpretation
        penalty_percentage = penalty_analysis['penalty_percentage']
        
        if penalty_percentage <= 0:
            penalty_level = "No penalty"
            recommendation = "No exit penalty - good liquidity"
        elif penalty_percentage <= 2:
            penalty_level = "Low penalty"
            recommendation = "Minimal exit costs"
        elif penalty_percentage <= 5:
            penalty_level = "Moderate penalty"
            recommendation = "Consider timing of any transfers"
        elif penalty_percentage <= 10:
            penalty_level = "High penalty"
            recommendation = "Significant exit costs - review alternatives"
        else:
            penalty_level = "Very high penalty"
            recommendation = "Substantial exit penalty - seek advice before proceeding"
        
        return {
            "analysis_available": True,
            "fund_value": fund_value,
            "surrender_value": surrender_value,
            "penalty_amount": penalty_analysis['penalty_amount'],
            "penalty_percentage": penalty_percentage,
            "penalty_level": penalty_level,
            "recommendation": recommendation,
            "surrender_ratio": penalty_analysis['surrender_ratio']
        }
        
    except Exception as e:
        return {
            "analysis_available": False,
            "error": f"Surrender penalty analysis failed: {str(e)}"
        }


def calculate_age_based_recommendations(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate age-based recommendations for pension and investment products"""
    
    try:
        current_age = processed_data.get('current_age')
        target_age = processed_data.get('target_age')
        product_type = processed_data.get('product_type')
        
        if not current_age or not product_type:
            return {
                "recommendations_available": False,
                "reason": "Age and product type required"
            }
        
        # Convert age to integer
        if isinstance(current_age, str):
            current_age = int(current_age.replace(' years old', '').strip())
        
        recommendations = []
        warnings = []
        
        # Age-specific recommendations
        if current_age < 30:
            recommendations.append("Consider higher-risk growth investments for long-term wealth building")
            recommendations.append("Take advantage of compound growth over extended timeframe")
            
        elif current_age < 40:
            recommendations.append("Balance growth and stability in investment approach")
            recommendations.append("Consider increasing contributions as income grows")
            
        elif current_age < 50:
            recommendations.append("Begin shifting towards more balanced investment strategy")
            recommendations.append("Review retirement planning regularly")
            
        elif current_age < 60:
            recommendations.append("Consider more conservative investment approach")
            recommendations.append("Plan for potential early retirement options")
            
        else:
            recommendations.append("Focus on capital preservation and income generation")
            recommendations.append("Consider annuity options for guaranteed income")
        
        # Product-specific recommendations
        if product_type in PENSION_PRODUCTS:
            if current_age < SystemLimits.MIN_PENSION_ACCESS_AGE:
                years_to_access = SystemLimits.MIN_PENSION_ACCESS_AGE - current_age
                recommendations.append(f"Pension benefits accessible in {years_to_access} years (age 55)")
            
            if target_age and target_age < SystemLimits.MIN_PENSION_ACCESS_AGE:
                warnings.append(f"Target age {target_age} is below minimum pension access age of {SystemLimits.MIN_PENSION_ACCESS_AGE}")
            
            if current_age >= SystemLimits.STATE_PENSION_AGE:
                recommendations.append("Eligible for state pension - consider coordination with private pension")
        
        # Investment term recommendations
        if target_age:
            term_years = target_age - current_age
            if term_years < 5:
                warnings.append("Short investment term - consider more liquid investments")
                recommendations.append("Focus on capital preservation over growth")
            elif term_years > 40:
                warnings.append("Very long investment term - review regularly")
                recommendations.append("Take advantage of long-term compound growth")
        
        return {
            "recommendations_available": True,
            "current_age": current_age,
            "target_age": target_age,
            "product_type": product_type,
            "recommendations": recommendations,
            "warnings": warnings,
            "years_to_target": target_age - current_age if target_age else None,
            "years_to_pension_access": max(0, SystemLimits.MIN_PENSION_ACCESS_AGE - current_age) if current_age < SystemLimits.MIN_PENSION_ACCESS_AGE else 0,
            "years_to_state_pension": max(0, SystemLimits.STATE_PENSION_AGE - current_age) if current_age < SystemLimits.STATE_PENSION_AGE else 0
        }
        
    except Exception as e:
        return {
            "recommendations_available": False,
            "error": f"Age-based recommendations failed: {str(e)}"
        }


def calculate_tax_efficiency_analysis(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze tax efficiency based on product type and client tax situation"""
    
    try:
        product_type = processed_data.get('product_type')
        include_taxation = processed_data.get('include_taxation')
        tax_band = processed_data.get('tax_band')
        fund_value = processed_data.get('fund_value')
        
        if not product_type:
            return {
                "analysis_available": False,
                "reason": "Product type required"
            }
        
        analysis = {
            "analysis_available": True,
            "product_type": product_type,
            "is_tax_exempt": product_type in TAX_EXEMPT_PRODUCTS,
            "recommendations": [],
            "tax_benefits": [],
            "considerations": []
        }
        
        # Tax-exempt products (ISAs)
        if product_type in TAX_EXEMPT_PRODUCTS:
            analysis["tax_benefits"].append("Tax-free growth on investments")
            analysis["tax_benefits"].append("Tax-free withdrawals at any time")
            analysis["recommendations"].append("Maximize annual ISA allowance")
            analysis["considerations"].append("No tax relief on contributions")
        
        # Pension products
        elif product_type in PENSION_PRODUCTS:
            analysis["tax_benefits"].append("Tax relief on contributions")
            analysis["tax_benefits"].append("Tax-free growth within pension")
            analysis["tax_benefits"].append("25% tax-free lump sum on retirement")
            
            if tax_band and include_taxation:
                tax_rate = TAX_RATES.get(tax_band, Decimal('0.2'))
                relief_rate = tax_rate * 100
                analysis["tax_benefits"].append(f"Tax relief at {relief_rate:.0f}% on contributions")
                
                # Calculate potential annual tax relief
                if fund_value:
                    if isinstance(fund_value, str):
                        fund_val = Decimal(fund_value.replace('£', '').replace(',', ''))
                    else:
                        fund_val = Decimal(str(fund_value))
                    
                    # Assume 10% annual contribution for illustration
                    annual_contribution = fund_val * Decimal('0.1')
                    annual_relief = annual_contribution * tax_rate
                    analysis["estimated_annual_tax_relief"] = annual_relief
            
            analysis["considerations"].append("Income tax on withdrawals above 25% lump sum")
            analysis["considerations"].append("Minimum access age of 55 (rising to 57 in 2028)")
        
        # Investment products
        elif product_type in INVESTMENT_PRODUCTS:
            analysis["considerations"].append("Liable for income tax on distributions")
            analysis["considerations"].append("Capital gains tax may apply on disposals")
            analysis["recommendations"].append("Consider ISA wrapper for tax efficiency")
            
            if tax_band:
                tax_rate = TAX_RATES.get(tax_band, Decimal('0.2'))
                analysis["considerations"].append(f"Tax on gains at {tax_rate * 100:.0f}% rate")
        
        # General recommendations based on tax band
        if tax_band == 'additional_rate_45':
            analysis["recommendations"].append("Maximize pension contributions for 45% tax relief")
            analysis["recommendations"].append("Consider salary sacrifice arrangements")
        elif tax_band == 'higher_rate_40':
            analysis["recommendations"].append("Pension contributions provide valuable 40% tax relief")
            analysis["recommendations"].append("ISAs provide tax-free alternative")
        else:  # Basic rate
            analysis["recommendations"].append("ISAs may be more flexible than pensions")
            analysis["recommendations"].append("20% pension tax relief still valuable")
        
        return analysis
        
    except Exception as e:
        return {
            "analysis_available": False,
            "error": f"Tax efficiency analysis failed: {str(e)}"
        }


def generate_comprehensive_analysis(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive analysis combining all Phase 1 calculations"""
    
    comprehensive_analysis = {
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "data_readiness": assess_data_readiness(processed_data),
        "investment_projection": calculate_investment_projection(processed_data),
        "surrender_penalty_analysis": calculate_surrender_penalty_analysis(processed_data),
        "age_based_recommendations": calculate_age_based_recommendations(processed_data),
        "tax_efficiency_analysis": calculate_tax_efficiency_analysis(processed_data)
    }
    
    # Generate overall summary
    readiness = comprehensive_analysis["data_readiness"]
    
    summary = {
        "overall_score": readiness["completion_score"],
        "ready_for_next_phase": readiness["ready_for_next_phase"],
        "total_recommendations": 0,
        "total_warnings": 0,
        "key_insights": []
    }
    
    # Count recommendations and warnings
    for analysis_type, analysis_data in comprehensive_analysis.items():
        if isinstance(analysis_data, dict):
            if "recommendations" in analysis_data:
                summary["total_recommendations"] += len(analysis_data["recommendations"])
            if "warnings" in analysis_data:
                summary["total_warnings"] += len(analysis_data["warnings"])
    
    # Generate key insights
    product_type = processed_data.get('product_type')
    if product_type:
        if product_type in TAX_EXEMPT_PRODUCTS:
            summary["key_insights"].append("Tax-efficient ISA wrapper provides flexibility")
        elif product_type in PENSION_PRODUCTS:
            summary["key_insights"].append("Pension provides tax relief but less flexibility")
        
        if readiness["ready_for_next_phase"]:
            summary["key_insights"].append("All required data collected - ready for detailed analysis")
        else:
            missing_count = readiness["total_missing_count"]
            summary["key_insights"].append(f"{missing_count} additional fields needed for complete analysis")
    
    comprehensive_analysis["summary"] = summary
    
    return comprehensive_analysis


def _generate_readiness_summary(is_ready: bool, completion_score: int, missing_fields: List[str]) -> str:
    """Generate human-readable readiness summary"""
    
    if is_ready:
        if completion_score >= 95:
            return "✅ Excellent - All required data collected with high quality"
        elif completion_score >= 85:
            return "✅ Very Good - Ready to proceed with minor optional data missing"
        else:
            return "✅ Good - Ready to proceed though some optional information could enhance analysis"
    else:
        missing_count = len(missing_fields)
        if missing_count == 1:
            return f"⚠️ Nearly Complete - 1 required field missing: {missing_fields[0]}"
        elif missing_count <= 3:
            return f"⚠️ Partially Complete - {missing_count} required fields missing"
        else:
            return f"📝 In Progress - {missing_count} required fields still needed"