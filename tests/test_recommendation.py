import pytest
from app.services.recommendation import RecommendationEngine, RecommendationStatus


class TestRecommendationEngine:
    """Test cases for recommendation engine"""
    
    def setup_method(self):
        """Setup test engine"""
        self.engine = RecommendationEngine()
    
    def test_approve_good_metrics(self):
        """Test approval with good financial metrics"""
        entity_data = {
            'name': 'Test Company',
            'sector': 'Manufacturing',
            'turnover': 10000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 10000000,
            'ebitda': 2000000,
            'net_profit': 1000000,
            'total_debt': 2000000,
            'total_equity': 5000000,
            'debt_to_equity': 0.4,  # Good
            'interest_coverage': 4.0,  # Good
            'profit_margin': 10.0,  # Good
            'cashflow_from_operations': 1500000,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        assert result.status == RecommendationStatus.APPROVED
        assert result.score >= 70
        assert 'Healthy debt-to-equity ratio' in result.reasoning
    
    def test_reject_high_leverage(self):
        """Test rejection due to high debt-to-equity ratio"""
        entity_data = {
            'name': 'Test Company',
            'sector': 'Manufacturing',
            'turnover': 10000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 10000000,
            'ebitda': 2000000,
            'net_profit': 500000,
            'total_debt': 15000000,
            'total_equity': 5000000,
            'debt_to_equity': 3.0,  # High - should reject
            'interest_coverage': 4.0,
            'profit_margin': 5.0,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        assert result.status == RecommendationStatus.REJECTED
        assert 'High debt-to-equity ratio' in result.reasoning
    
    def test_flag_low_interest_coverage(self):
        """Test flagging due to low interest coverage"""
        entity_data = {
            'name': 'Test Company',
            'sector': 'Manufacturing',
            'turnover': 10000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 10000000,
            'ebitda': 100000,  # Low EBITDA
            'net_profit': 50000,
            'total_debt': 5000000,
            'total_equity': 5000000,
            'debt_to_equity': 1.0,
            'interest_coverage': 0.5,  # Very low - should flag
            'profit_margin': 0.5,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        assert result.status in [RecommendationStatus.FLAGGED, RecommendationStatus.REJECTED]
        assert any('interest coverage' in w.lower() for w in result.warnings)
    
    def test_reject_negative_ebitda(self):
        """Test rejection due to negative EBITDA"""
        entity_data = {
            'name': 'Test Company',
            'sector': 'Manufacturing',
            'turnover': 10000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 8000000,
            'ebitda': -500000,  # Negative
            'net_profit': -800000,
            'total_debt': 3000000,
            'total_equity': 5000000,
            'debt_to_equity': 0.6,
            'interest_coverage': -1.0,
            'profit_margin': -10.0,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        assert result.status == RecommendationStatus.REJECTED
    
    def test_flag_low_turnover(self):
        """Test flagging due to low turnover"""
        entity_data = {
            'name': 'Small Business',
            'sector': 'Retail',
            'turnover': 500000,  # Below minimum
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 500000,
            'ebitda': 50000,
            'net_profit': 25000,
            'total_debt': 100000,
            'total_equity': 200000,
            'debt_to_equity': 0.5,
            'interest_coverage': 2.5,
            'profit_margin': 5.0,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        # Should still be approved but with penalty
        assert 'Turnover below minimum' in result.reasoning
    
    def test_borderline_metrics(self):
        """Test with borderline metrics"""
        entity_data = {
            'name': 'Test Company',
            'sector': 'IT',
            'turnover': 50000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 50000000,
            'ebitda': 5000000,
            'net_profit': 1500000,
            'total_debt': 10000000,
            'total_equity': 10000000,  # D/E = 1.0 - borderline
            'debt_to_equity': 1.0,
            'interest_coverage': 2.0,  # Exactly at threshold
            'profit_margin': 3.0,  # Borderline
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        # Should be either approved or flagged due to borderline
        assert result.status in [RecommendationStatus.APPROVED, RecommendationStatus.FLAGGED]
    
    def test_swot_strengths(self):
        """Test SWOT analysis identifies strengths"""
        entity_data = {
            'name': 'Strong Company',
            'sector': 'Technology',
            'turnover': 100000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 100000000,
            'ebitda': 25000000,
            'net_profit': 15000000,
            'cashflow_from_operations': 20000000,
            'total_debt': 10000000,
            'total_equity': 50000000,
            'debt_to_equity': 0.2,
            'interest_coverage': 10.0,
            'profit_margin': 15.0,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        assert len(result.swot_analysis['strengths']) > 0
        assert any('debt-to-equity' in s.lower() for s in result.swot_analysis['strengths'])
    
    def test_swot_weaknesses(self):
        """Test SWOT analysis identifies weaknesses"""
        entity_data = {
            'name': 'Weak Company',
            'sector': 'Manufacturing',
            'turnover': 5000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 5000000,
            'ebitda': -100000,
            'net_profit': -500000,
            'cashflow_from_operations': -200000,
            'total_debt': 15000000,
            'total_equity': 3000000,
            'debt_to_equity': 5.0,
            'interest_coverage': -0.5,
            'profit_margin': -10.0,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        assert len(result.swot_analysis['weaknesses']) > 0
    
    def test_default_recommendation(self):
        """Test default recommendation when no data"""
        result = self.engine.get_default_recommendation()
        
        assert result.status == RecommendationStatus.FLAGGED
        assert result.score == 50
        assert 'Insufficient data' in result.reasoning
        assert 'Missing financial data' in result.warnings
    
    def test_score_bounds(self):
        """Test that score is always within bounds"""
        # Test with extreme negative values
        entity_data = {
            'name': 'Test',
            'sector': 'Test',
            'turnover': 0,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 0,
            'ebitda': -1000000,
            'net_profit': -1000000,
            'total_debt': 10000000,
            'total_equity': 0,  # Will cause issues
            'debt_to_equity': 100.0,  # Very high
            'interest_coverage': -10.0,
            'profit_margin': -100.0,
        }
        
        result = self.engine.analyze(entity_data, annual_report_data)
        
        # Score should be bounded between 0 and 100
        assert 0 <= result.score <= 100
    
    def test_borrowing_profile_inclusion(self):
        """Test that borrowing profile data is included in analysis"""
        entity_data = {
            'name': 'Test Company',
            'sector': 'Manufacturing',
            'turnover': 10000000,
        }
        
        annual_report_data = {
            'year': 2023,
            'revenue': 10000000,
            'ebitda': 2000000,
            'net_profit': 1000000,
            'total_debt': 2000000,
            'total_equity': 5000000,
            'debt_to_equity': 0.4,
            'interest_coverage': 4.0,
            'profit_margin': 10.0,
        }
        
        borrowing_profile_data = {
            'loan_amount': 5000000,
            'tenure_months': 36,
            'interest_rate': 12.0,
        }
        
        result = self.engine.analyze(
            entity_data, 
            annual_report_data, 
            borrowing_profile_data
        )
        
        # Should still process successfully with borrowing profile
        assert result is not None
        assert result.score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
