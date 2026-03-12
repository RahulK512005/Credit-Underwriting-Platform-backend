import pytest
from app.services.extraction import DocumentExtractionService


class TestDocumentExtraction:
    """Test cases for document extraction service"""
    
    def setup_method(self):
        """Setup test service"""
        self.service = DocumentExtractionService()
    
    def test_classify_annual_report(self):
        """Test classification of annual report document"""
        text = """
        Annual Report FY2023
        
        Financial Statements:
        - Total Revenue: 10,00,00,000
        - EBITDA: 2,00,00,000
        - Net Profit: 1,50,00,000
        - Total Debt: 5,00,00,000
        - Total Equity: 10,00,00,000
        
        The company's balance sheet shows strong performance.
        """
        
        doc_type, confidence = self.service.classify_document(text)
        
        assert doc_type == "annual_report"
        assert confidence > 0.5
    
    def test_classify_borrowing_profile(self):
        """Test classification of borrowing profile document"""
        text = """
        Loan Sanction Letter
        
        Loan Amount: Rs. 50,00,000
        Tenure: 36 months
        Interest Rate: 12% p.a.
        EMI: Rs. 1,63,200
        
        Lender: ABC Bank
        Purpose: Business Expansion
        """
        
        doc_type, confidence = self.service.classify_document(text)
        
        assert doc_type == "borrowing_profile"
        assert confidence > 0.5
    
    def test_classify_unknown_document(self):
        """Test classification of unknown document"""
        text = "This is some random text without specific financial terms."
        
        doc_type, confidence = self.service.classify_document(text)
        
        # Should still classify but with lower confidence
        assert doc_type in ["annual_report", "borrowing_profile", "unknown"]
    
    def test_extract_annual_report_data(self):
        """Test extraction of annual report financial data"""
        text = """
        FY2023 Annual Report
        
        Revenue: 10000000
        EBITDA: 2500000
        Net Profit: 1500000
        Total Debt: 5000000
        Total Equity: 10000000
        Interest Expense: 500000
        """
        
        data = self.service.extract_annual_report_data(text)
        
        assert data['year'] == 2023
        assert data['revenue'] is not None
        assert data['ebitda'] is not None
        assert data['net_profit'] is not None
    
    def test_extract_annual_report_with_crlakh(self):
        """Test extraction with Cr/Lakh notation"""
        text = """
        FY2023 Financials
        
        Revenue: 10 Cr
        EBITDA: 2.5 Cr
        Net Profit: 1.5 Cr
        Total Debt: 5 Cr
        Total Equity: 10 Cr
        """
        
        data = self.service.extract_annual_report_data(text)
        
        # Should extract and convert Cr to actual values
        assert data['revenue'] is not None
        assert data['revenue'] > 0
    
    def test_extract_borrowing_profile_data(self):
        """Test extraction of borrowing profile data"""
        text = """
        Loan Details:
        Loan Amount: 5000000
        Tenure: 36 months
        Interest Rate: 12.5%
        EMI: 163200
        Lender: XYZ Bank
        Purpose: Working Capital
        """
        
        data = self.service.extract_borrowing_profile_data(text)
        
        assert data['loan_amount'] is not None
        assert data['tenure_months'] == 36
        assert data['interest_rate'] is not None
        assert data['emi'] is not None
    
    def test_generate_repayment_schedule(self):
        """Test generation of EMI repayment schedule"""
        schedule = self.service._generate_repayment_schedule(
            principal=1000000,
            tenure_months=12,
            interest_rate=12
        )
        
        assert len(schedule) == 12
        assert schedule[0]['month'] == 1
        assert schedule[0]['principal'] > 0
        assert schedule[0]['interest'] > 0
        assert schedule[0]['emi'] > 0
        assert schedule[-1]['balance'] == 0 or schedule[-1]['balance'] < 1
    
    def test_generate_repayment_schedule_zero_interest(self):
        """Test generation of repayment schedule with zero interest"""
        schedule = self.service._generate_repayment_schedule(
            principal=120000,
            tenure_months=12,
            interest_rate=0
        )
        
        assert len(schedule) == 12
        # Each EMI should be exactly principal/12
        assert schedule[0]['emi'] == 10000
    
    def test_extract_value_with_currency_symbols(self):
        """Test extraction with various currency formats"""
        text = "Revenue: ₹10,00,000"
        
        value = self.service._extract_value(text, r'revenue\s*[:\-]?\s*')
        
        # Should extract numeric value
        assert value is not None
    
    def test_extract_invalid_value(self):
        """Test extraction with invalid pattern"""
        text = "Some text without numbers"
        
        value = self.service._extract_value(text, r'nonexistent\s*pattern')
        
        assert value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
