from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class RecommendationStatus(str, Enum):
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"


@dataclass
class RecommendationResult:
    """Result of credit recommendation analysis"""
    status: RecommendationStatus
    score: float
    reasoning: str
    warnings: List[str]
    swot_analysis: Dict[str, List[str]]


class RecommendationEngine:
    """Rule-based credit recommendation engine"""
    
    # Threshold constants
    DEBT_TO_EQUITY_THRESHOLD = 2.5
    DEBT_TO_EQUITY_BORDERLINE = 2.0
    
    INTEREST_COVERAGE_THRESHOLD = 2.0
    INTEREST_COVERAGE_BORDERLINE = 1.5
    
    PROFIT_MARGIN_THRESHOLD = 5.0  # minimum 5% profit margin
    PROFIT_MARGIN_BORDERLINE = 2.0
    
    TURNOVER_MINIMUM = 1000000  # Minimum 10L turnover
    
    def __init__(self):
        self.thresholds = {
            'debt_to_equity': self.DEBT_TO_EQUITY_THRESHOLD,
            'debt_to_equity_borderline': self.DEBT_TO_EQUITY_BORDERLINE,
            'interest_coverage': self.INTEREST_COVERAGE_THRESHOLD,
            'interest_coverage_borderline': self.INTEREST_COVERAGE_BORDERLINE,
            'profit_margin': self.PROFIT_MARGIN_THRESHOLD,
            'profit_margin_borderline': self.PROFIT_MARGIN_BORDERLINE,
        }
    
    def analyze(
        self,
        entity_data: Dict[str, Any],
        annual_report_data: Dict[str, Any],
        borrowing_profile_data: Optional[Dict[str, Any]] = None
    ) -> RecommendationResult:
        """
        Analyze entity and financial data to generate recommendation
        """
        warnings = []
        score = 100.0
        reasoning_parts = []
        
        # Extract key metrics
        debt_to_equity = annual_report_data.get('debt_to_equity')
        interest_coverage = annual_report_data.get('interest_coverage')
        profit_margin = annual_report_data.get('profit_margin')
        revenue = annual_report_data.get('revenue')
        ebitda = annual_report_data.get('ebitda')
        net_profit = annual_report_data.get('net_profit')
        turnover = entity_data.get('turnover', 0)
        
        # Analyze Debt to Equity ratio
        if debt_to_equity is not None:
            if debt_to_equity >= self.DEBT_TO_EQUITY_THRESHOLD:
                score -= 40
                reasoning_parts.append(
                    f"High debt-to-equity ratio ({debt_to_equity:.2f}) exceeds threshold ({self.DEBT_TO_EQUITY_THRESHOLD})"
                )
                warnings.append(f"High leverage: D/E ratio of {debt_to_equity:.2f}")
            elif debt_to_equity >= self.DEBT_TO_EQUITY_BORDERLINE:
                score -= 20
                reasoning_parts.append(
                    f"Borderline debt-to-equity ratio ({debt_to_equity:.2f})"
                )
                warnings.append(f"Moderate leverage: D/E ratio of {debt_to_equity:.2f}")
            else:
                reasoning_parts.append(
                    f"Healthy debt-to-equity ratio ({debt_to_equity:.2f})"
                )
        
        # Analyze Interest Coverage ratio
        if interest_coverage is not None:
            if interest_coverage < self.INTEREST_COVERAGE_THRESHOLD:
                score -= 30
                reasoning_parts.append(
                    f"Low interest coverage ratio ({interest_coverage:.2f}) below threshold ({self.INTEREST_COVERAGE_THRESHOLD})"
                )
                warnings.append(f"Weak interest coverage: {interest_coverage:.2f}x")
            elif interest_coverage < self.INTEREST_COVERAGE_BORDERLINE:
                score -= 15
                reasoning_parts.append(
                    f"Borderline interest coverage ratio ({interest_coverage:.2f})"
                )
                warnings.append(f"Moderate interest coverage: {interest_coverage:.2f}x")
            else:
                reasoning_parts.append(
                    f"Good interest coverage ratio ({interest_coverage:.2f}x)"
                )
        
        # Analyze Profit Margin
        if profit_margin is not None:
            if profit_margin < self.PROFIT_MARGIN_BORDERLINE:
                score -= 25
                reasoning_parts.append(
                    f"Low profit margin ({profit_margin:.2f}%)"
                )
                warnings.append(f"Low profitability: {profit_margin:.2f}% margin")
            elif profit_margin < self.PROFIT_MARGIN_THRESHOLD:
                score -= 10
                reasoning_parts.append(
                    f"Below target profit margin ({profit_margin:.2f}%)"
                )
            else:
                reasoning_parts.append(
                    f"Good profit margin ({profit_margin:.2f}%)"
                )
        
        # Check minimum turnover
        if turnover < self.TURNOVER_MINIMUM:
            score -= 20
            reasoning_parts.append(f"Turnover below minimum threshold")
            warnings.append(f"Low turnover: ₹{turnover:,.0f}")
        
        # Check for negative values
        if net_profit is not None and net_profit < 0:
            score -= 20
            reasoning_parts.append("Entity has net loss")
            warnings.append("Net loss in recent period")
        
        if ebitda is not None and ebitda < 0:
            score -= 15
            reasoning_parts.append("Negative EBITDA")
            warnings.append("Negative operating earnings")
        
        # Calculate final status
        score = max(0, min(100, score))
        
        if score >= 70:
            status = RecommendationStatus.APPROVED
            reasoning = f"APPROVED: Score {score:.0f}/100. " + ". ".join(reasoning_parts)
        elif score >= 50:
            status = RecommendationStatus.FLAGGED
            reasoning = f"FLAGGED: Score {score:.0f}/100. " + ". ".join(reasoning_parts)
        else:
            status = RecommendationStatus.REJECTED
            reasoning = f"REJECTED: Score {score:.0f}/100. " + ". ".join(reasoning_parts)
        
        # Generate SWOT analysis
        swot = self._generate_swot(
            entity_data=entity_data,
            annual_report_data=annual_report_data,
            borrowing_profile_data=borrowing_profile_data,
            score=score
        )
        
        return RecommendationResult(
            status=status,
            score=score,
            reasoning=reasoning,
            warnings=warnings,
            swot_analysis=swot
        )
    
    def _generate_swot(
        self,
        entity_data: Dict[str, Any],
        annual_report_data: Dict[str, Any],
        borrowing_profile_data: Optional[Dict[str, Any]],
        score: float
    ) -> Dict[str, List[str]]:
        """Generate SWOT analysis"""
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        # Strengths
        debt_to_equity = annual_report_data.get('debt_to_equity')
        if debt_to_equity and debt_to_equity < self.DEBT_TO_EQUITY_BORDERLINE:
            swot['strengths'].append("Low debt-to-equity ratio indicates strong capital structure")
        
        interest_coverage = annual_report_data.get('interest_coverage')
        if interest_coverage and interest_coverage > self.INTEREST_COVERAGE_THRESHOLD:
            swot['strengths'].append("Strong interest coverage ratio")
        
        profit_margin = annual_report_data.get('profit_margin')
        if profit_margin and profit_margin > self.PROFIT_MARGIN_THRESHOLD:
            swot['strengths'].append("Healthy profit margins")
        
        if annual_report_data.get('cashflow_from_operations', 0) > 0:
            swot['strengths'].append("Positive operating cash flow")
        
        # Weaknesses
        if debt_to_equity and debt_to_equity >= self.DEBT_TO_EQUITY_BORDERLINE:
            swot['weaknesses'].append("High leverage risk")
        
        if interest_coverage and interest_coverage < self.INTEREST_COVERAGE_BORDERLINE:
            swot['weaknesses'].append("Limited debt servicing capacity")
        
        if annual_report_data.get('net_profit', 0) < 0:
            swot['weaknesses'].append("Net loss in recent period")
        
        if annual_report_data.get('revenue', 0) < entity_data.get('turnover', 0):
            swot['weaknesses'].append("Declining revenue trend")
        
        # Opportunities
        sector = entity_data.get('sector', '').lower()
        if 'technology' in sector or 'it' in sector or 'software' in sector:
            swot['opportunities'].append("Technology sector growth potential")
        
        if borrowing_profile_data and borrowing_profile_data.get('loan_amount'):
            swot['opportunities'].append("Growth financing opportunity")
        
        swot['opportunities'].append("Market expansion potential")
        
        # Threats
        if debt_to_equity and debt_to_equity > self.DEBT_TO_EQUITY_THRESHOLD:
            swot['threats'].append("High debt burden limits financial flexibility")
        
        if profit_margin and profit_margin < self.PROFIT_MARGIN_BORDERLINE:
            swot['threats'].append("Margin pressure from competition")
        
        swot['threats'].append("Economic downturn risk")
        
        return swot
    
    def get_default_recommendation(self) -> RecommendationResult:
        """Return default recommendation when insufficient data"""
        return RecommendationResult(
            status=RecommendationStatus.FLAGGED,
            score=50,
            reasoning="INSUFFICIENT DATA: Unable to analyze due to missing financial data. Manual review required.",
            warnings=["Missing financial data for analysis"],
            swot={
                'strengths': [],
                'weaknesses': ["Insufficient data for analysis"],
                'opportunities': [],
                'threats': ["Unable to assess risk profile"]
            }
        )


# Singleton instance
recommendation_engine = RecommendationEngine()
