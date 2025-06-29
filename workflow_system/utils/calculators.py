"""
Enhanced shared calculation utilities with comprehensive financial calculations
File: workflow_system/utils/calculators.py (UPDATED)
"""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
import math


def calculate_data_quality_score(data: Dict[str, Any], core_fields: list = None) -> int:
    """Enhanced data quality score calculation with weighted scoring"""
    if not data:
        return 0
    
    total_fields = len(data)
    if total_fields == 0:
        return 0
    
    # Count completed fields (non-null, non-empty, not "Not specified")
    completed_fields = len([
        v for v in data.values() 
        if v is not None and 
        str(v).strip().lower() not in ["", "not specified", "none", "null"]
    ])
    
    if core_fields:
        # Core fields have higher weight (70%), optional fields have lower weight (30%)
        core_completed = sum(
            1 for field in core_fields 
            if data.get(field) is not None and 
            str(data.get(field, "")).strip().lower() not in ["", "not specified", "none", "null"]
        )
        
        core_fields_count = len(core_fields)
        if core_fields_count == 0:
            return round((completed_fields / total_fields) * 100)
        
        # Calculate weighted score
        core_score = (core_completed / core_fields_count) * 70
        
        # Optional fields score (all fields minus core fields)
        optional_fields_count = max(1, total_fields - core_fields_count)
        optional_completed = completed_fields - core_completed
        optional_score = (optional_completed / optional_fields_count) * 30
        
        total_score = core_score + optional_score
        return round(min(100, max(0, total_score)))
    else:
        # Simple percentage if no core fields specified
        return round((completed_fields / total_fields) * 100)


def calculate_completion_percentage(data: Dict[str, Any], required_fields: List[str] = None) -> float:
    """Enhanced completion percentage calculation"""
    if not data:
        return 0.0
    
    fields_to_check = required_fields if required_fields else list(data.keys())
    
    if not fields_to_check:
        return 0.0
    
    completed_count = 0
    for field in fields_to_check:
        value = data.get(field)
        if value is not None and str(value).strip().lower() not in ["", "not specified", "none", "null"]:
            completed_count += 1
    
    percentage = (completed_count / len(fields_to_check)) * 100
    return round(percentage, 1)


def calculate_term_years_from_dates(start_date: date, end_date: date) -> Decimal:
    """Calculate term years from two dates with high precision"""
    if end_date <= start_date:
        raise ValueError("End date must be after start date")
    
    days_difference = (end_date - start_date).days
    years = Decimal(days_difference) / Decimal('365.25')  # Account for leap years
    
    return years.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_term_years_from_years_months(years: int, months: int = 0) -> Decimal:
    """Calculate term years from years and months input"""
    if years < 0 or months < 0 or months > 11:
        raise ValueError("Invalid years or months input")
    
    total_years = Decimal(years) + (Decimal(months) / 12)
    return total_years.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_term_years_from_ages(current_age: int, target_age: int) -> Decimal:
    """Calculate term years from current age to target age"""
    if target_age <= current_age:
        raise ValueError("Target age must be greater than current age")
    
    return Decimal(target_age - current_age)


def calculate_compound_growth(principal: Decimal, annual_rate: Decimal, years: Decimal) -> Decimal:
    """Calculate compound growth with high precision"""
    if principal <= 0:
        raise ValueError("Principal must be positive")
    if years <= 0:
        raise ValueError("Years must be positive")
    
    # Handle zero or negative growth rates
    if annual_rate <= Decimal('-1'):
        raise ValueError("Annual rate cannot be less than -100%")
    
    # Convert to float for mathematical operations, then back to Decimal
    principal_float = float(principal)
    rate_float = float(annual_rate)
    years_float = float(years)
    
    future_value = principal_float * ((1 + rate_float) ** years_float)
    
    return Decimal(str(future_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_annuity_future_value(annual_payment: Decimal, annual_rate: Decimal, years: Decimal) -> Decimal:
    """Calculate future value of annuity (regular payments)"""
    if annual_payment <= 0:
        raise ValueError("Annual payment must be positive")
    if years <= 0:
        raise ValueError("Years must be positive")
    
    # Handle zero rate case
    if annual_rate == 0:
        return annual_payment * years
    
    # Convert to float for calculation
    payment_float = float(annual_payment)
    rate_float = float(annual_rate)
    years_float = float(years)
    
    # Future value of annuity formula: PMT * [((1 + r)^n - 1) / r]
    future_value = payment_float * (((1 + rate_float) ** years_float - 1) / rate_float)
    
    return Decimal(str(future_value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_total_future_value(initial_value: Decimal, annual_contribution: Decimal, 
                                annual_rate: Decimal, years: Decimal) -> Dict[str, Decimal]:
    """Calculate total future value including initial investment and regular contributions"""
    
    # Future value of initial investment
    initial_fv = calculate_compound_growth(initial_value, annual_rate, years)
    
    # Future value of contributions (annuity)
    contributions_fv = calculate_annuity_future_value(annual_contribution, annual_rate, years)
    
    # Total future value
    total_fv = initial_fv + contributions_fv
    
    # Total contributions made
    total_contributions = annual_contribution * years
    
    # Total growth
    total_growth = total_fv - initial_value - total_contributions
    
    return {
        'initial_future_value': initial_fv,
        'contributions_future_value': contributions_fv,
        'total_future_value': total_fv,
        'total_contributions': total_contributions,
        'total_growth': total_growth,
        'effective_annual_return': total_growth / (initial_value + total_contributions) if (initial_value + total_contributions) > 0 else Decimal('0')
    }


def calculate_tax_impact(gross_amount: Decimal, tax_rate: Decimal) -> Dict[str, Decimal]:
    """Calculate tax impact on withdrawals or gains"""
    if gross_amount < 0:
        raise ValueError("Gross amount cannot be negative")
    if tax_rate < 0 or tax_rate > 1:
        raise ValueError("Tax rate must be between 0 and 1")
    
    tax_amount = gross_amount * tax_rate
    net_amount = gross_amount - tax_amount
    
    return {
        'gross_amount': gross_amount,
        'tax_amount': tax_amount,
        'net_amount': net_amount,
        'tax_rate': tax_rate,
        'effective_tax_rate': tax_amount / gross_amount if gross_amount > 0 else Decimal('0')
    }


def calculate_inflation_adjustment(nominal_amount: Decimal, inflation_rate: Decimal, years: Decimal) -> Dict[str, Decimal]:
    """Calculate inflation-adjusted (real) values"""
    if years <= 0:
        raise ValueError("Years must be positive")
    
    # Real purchasing power in today's money
    real_value = nominal_amount / ((1 + float(inflation_rate)) ** float(years))
    
    # Inflation impact
    inflation_impact = nominal_amount - Decimal(str(real_value)).quantize(Decimal('0.01'))
    
    return {
        'nominal_value': nominal_amount,
        'real_value': Decimal(str(real_value)).quantize(Decimal('0.01')),
        'inflation_impact': inflation_impact,
        'purchasing_power_loss': (inflation_impact / nominal_amount) * 100 if nominal_amount > 0 else Decimal('0')
    }


def calculate_retirement_income(fund_value: Decimal, withdrawal_rate: Decimal, 
                              tax_rate: Decimal = Decimal('0')) -> Dict[str, Decimal]:
    """Calculate sustainable retirement income from fund"""
    if fund_value <= 0:
        raise ValueError("Fund value must be positive")
    if withdrawal_rate <= 0 or withdrawal_rate > 1:
        raise ValueError("Withdrawal rate must be between 0 and 1")
    
    # Annual gross income
    annual_gross = fund_value * withdrawal_rate
    
    # Tax impact
    tax_impact = calculate_tax_impact(annual_gross, tax_rate)
    
    # Monthly amounts
    monthly_gross = annual_gross / 12
    monthly_net = tax_impact['net_amount'] / 12
    
    return {
        'fund_value': fund_value,
        'withdrawal_rate': withdrawal_rate,
        'annual_gross_income': annual_gross,
        'annual_net_income': tax_impact['net_amount'],
        'monthly_gross_income': monthly_gross,
        'monthly_net_income': monthly_net,
        'annual_tax': tax_impact['tax_amount'],
        'fund_depletion_years': Decimal('1') / withdrawal_rate if withdrawal_rate > 0 else Decimal('0')
    }


def calculate_cost_analysis(fund_value: Decimal, annual_charge: Decimal, years: Decimal) -> Dict[str, Decimal]:
    """Calculate impact of charges on investment growth"""
    if fund_value <= 0:
        raise ValueError("Fund value must be positive")
    if annual_charge < 0:
        raise ValueError("Annual charge cannot be negative")
    if years <= 0:
        raise ValueError("Years must be positive")
    
    # Total charges over period
    total_charges = annual_charge * years
    
    # Charge as percentage of fund
    charge_percentage = (annual_charge / fund_value) * 100
    
    # Cumulative impact (simplified - assumes charges don't compound)
    cumulative_impact = total_charges
    
    # Fund value after charges
    net_fund_value = fund_value - cumulative_impact
    
    return {
        'annual_charge': annual_charge,
        'charge_percentage': charge_percentage,
        'total_charges': total_charges,
        'cumulative_impact': cumulative_impact,
        'net_fund_value': max(Decimal('0'), net_fund_value),
        'impact_on_returns': (cumulative_impact / fund_value) * 100 if fund_value > 0 else Decimal('0')
    }


def calculate_surrender_penalty(fund_value: Decimal, surrender_value: Decimal) -> Dict[str, Decimal]:
    """Calculate surrender penalty and impact"""
    if fund_value <= 0 or surrender_value < 0:
        raise ValueError("Invalid fund or surrender values")
    
    penalty_amount = fund_value - surrender_value
    penalty_percentage = (penalty_amount / fund_value) * 100 if fund_value > 0 else Decimal('0')
    
    return {
        'fund_value': fund_value,
        'surrender_value': surrender_value,
        'penalty_amount': penalty_amount,
        'penalty_percentage': penalty_percentage,
        'surrender_ratio': surrender_value / fund_value if fund_value > 0 else Decimal('0')
    }


def calculate_switching_analysis(current_fund: Decimal, current_charges: Decimal,
                               new_fund_rate: Decimal, new_charges: Decimal,
                               switch_costs: Decimal, years: Decimal) -> Dict[str, Decimal]:
    """Comprehensive switching analysis"""
    
    # Current product projection
    current_net_rate = new_fund_rate - (current_charges / current_fund) if current_fund > 0 else Decimal('0')
    current_future_value = calculate_compound_growth(current_fund, current_net_rate, years)
    
    # New product projection (after switch costs)
    new_initial_value = current_fund - switch_costs
    new_net_rate = new_fund_rate - (new_charges / new_initial_value) if new_initial_value > 0 else Decimal('0')
    new_future_value = calculate_compound_growth(new_initial_value, new_net_rate, years)
    
    # Comparison
    switching_benefit = new_future_value - current_future_value
    breakeven_years = switch_costs / (new_charges - current_charges) if (new_charges - current_charges) != 0 else Decimal('999')
    
    return {
        'current_future_value': current_future_value,
        'new_future_value': new_future_value,
        'switching_benefit': switching_benefit,
        'switch_costs': switch_costs,
        'breakeven_years': min(breakeven_years, Decimal('999')),
        'net_benefit_percentage': (switching_benefit / current_future_value) * 100 if current_future_value > 0 else Decimal('0'),
        'recommendation': 'SWITCH' if switching_benefit > 0 and breakeven_years < years else 'STAY'
    }


def calculate_risk_metrics(expected_return: Decimal, volatility: Decimal, years: Decimal) -> Dict[str, Decimal]:
    """Calculate risk metrics for investment analysis"""
    if volatility < 0:
        raise ValueError("Volatility cannot be negative")
    if years <= 0:
        raise ValueError("Years must be positive")
    
    # Annualized volatility over period
    period_volatility = volatility * Decimal(str(math.sqrt(float(years))))
    
    # Confidence intervals (simplified normal distribution)
    confidence_95_upper = expected_return + (period_volatility * Decimal('1.96'))
    confidence_95_lower = expected_return - (period_volatility * Decimal('1.96'))
    
    # Sharpe ratio (assuming risk-free rate of 2%)
    risk_free_rate = Decimal('0.02')
    sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility > 0 else Decimal('0')
    
    return {
        'expected_return': expected_return,
        'volatility': volatility,
        'period_volatility': period_volatility,
        'confidence_95_upper': confidence_95_upper,
        'confidence_95_lower': confidence_95_lower,
        'sharpe_ratio': sharpe_ratio,
        'risk_level': 'LOW' if volatility < Decimal('0.1') else 'MEDIUM' if volatility < Decimal('0.2') else 'HIGH'
    }


def calculate_comprehensive_projection(initial_value: Decimal, annual_contribution: Decimal,
                                     annual_rate: Decimal, annual_charges: Decimal,
                                     tax_rate: Decimal, inflation_rate: Decimal,
                                     years: Decimal) -> Dict[str, Any]:
    """Comprehensive financial projection with all factors"""
    
    # Basic growth calculation
    net_annual_rate = annual_rate - (annual_charges / initial_value) if initial_value > 0 else annual_rate
    growth_projection = calculate_total_future_value(initial_value, annual_contribution, net_annual_rate, years)
    
    # Tax impact on final value
    tax_impact = calculate_tax_impact(growth_projection['total_growth'], tax_rate)
    
    # Inflation adjustment
    nominal_value = growth_projection['total_future_value']
    inflation_adjustment = calculate_inflation_adjustment(nominal_value, inflation_rate, years)
    
    # Cost analysis
    total_charges = annual_charges * years
    cost_impact = calculate_cost_analysis(initial_value, annual_charges, years)
    
    # Retirement income potential (4% rule)
    withdrawal_rate = Decimal('0.04')
    income_projection = calculate_retirement_income(nominal_value, withdrawal_rate, tax_rate)
    
    return {
        'projection_summary': {
            'initial_value': initial_value,
            'total_contributions': growth_projection['total_contributions'],
            'nominal_future_value': nominal_value,
            'real_future_value': inflation_adjustment['real_value'],
            'total_growth': growth_projection['total_growth'],
            'net_growth_after_tax': tax_impact['net_amount']
        },
        'cost_analysis': {
            'total_charges': total_charges,
            'charge_impact_percentage': cost_impact['impact_on_returns']
        },
        'income_potential': {
            'annual_income': income_projection['annual_net_income'],
            'monthly_income': income_projection['monthly_net_income']
        },
        'inflation_impact': {
            'purchasing_power_loss': inflation_adjustment['purchasing_power_loss'],
            'real_value': inflation_adjustment['real_value']
        }
    }