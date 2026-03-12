import re
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import PyPDF2
import pandas as pd
from io import BytesIO


class DocumentExtractionService:
    """Service for extracting financial data from PDF and Excel documents"""
    
    # Keywords for document classification
    ANNUAL_REPORT_KEYWORDS = [
        "annual report", "financial statements", "balance sheet", 
        "profit and loss", "cash flow", "income statement",
        "revenue", "ebitda", "net profit", "total equity"
    ]
    
    BORROWING_PROFILE_KEYWORDS = [
        "loan", "borrowing", "lender", "EMI", "repayment",
        "principal", "interest rate", "sanction", "credit facility"
    ]
    
    # Financial metrics patterns
    METRIC_PATTERNS = {
        'revenue': r'(?:total\s+)?revenue|sales|turnover',
        'ebitda': r'ebitda|earnings\s+before\s+interest',
        'net_profit': r'net\s+(?:profit|income)|profit\s+after\s+tax',
        'cashflow': r'cash\s+flow\s+from|cash\s+generated',
        'total_debt': r'total\s+debt|borrowings?|loans?',
        'total_equity': r'total\s+equity|shareholders?\s+funds?',
    }
    
    def classify_document(self, text: str) -> Tuple[str, float]:
        """
        Classify document as annual_report or borrowing_profile
        Returns (document_type, confidence_score)
        """
        text_lower = text.lower()
        
        annual_score = sum(1 for kw in self.ANNUAL_REPORT_KEYWORDS if kw in text_lower)
        borrowing_score = sum(1 for kw in self.BORROWING_PROFILE_KEYWORDS if kw in text_lower)
        
        total_score = annual_score + borrowing_score
        if total_score == 0:
            return "unknown", 0.0
        
        if annual_score > borrowing_score:
            confidence = min(annual_score / total_score, 1.0)
            return "annual_report", confidence
        elif borrowing_score > 0:
            confidence = min(borrowing_score / total_score, 1.0)
            return "borrowing_profile", confidence
        
        return "unknown", 0.0
    
    def extract_annual_report_data(self, text: str) -> Dict[str, Any]:
        """
        Extract financial metrics from annual report text
        Returns dict with year, revenue, ebitda, net_profit, etc.
        """
        data = {
            'year': datetime.now().year - 1,
            'revenue': None,
            'ebitda': None,
            'net_profit': None,
            'cashflow_from_operations': None,
            'total_debt': None,
            'total_equity': None,
            'debt_to_equity': None,
            'interest_coverage': None,
            'profit_margin': None,
        }
        
        # Extract year
        year_match = re.search(r'(?:fy|year)\s*[:\-]?\s*(\d{4})', text, re.IGNORECASE)
        if year_match:
            data['year'] = int(year_match.group(1))
        
        # Extract financial metrics
        for metric, pattern in self.METRIC_PATTERNS.items():
            value = self._extract_value(text, pattern)
            if value is not None and metric in ['total_debt', 'total_equity']:
                if metric == 'total_debt':
                    data['total_debt'] = value
                elif metric == 'total_equity':
                    data['total_equity'] = value
        
        # Extract all currency values and try to assign them
        currency_values = self._extract_all_currency_values(text)
        
        if len(currency_values) >= 1:
            data['revenue'] = currency_values[0] if data['revenue'] is None else data['revenue']
        if len(currency_values) >= 2:
            data['ebitda'] = currency_values[1] if data['ebitda'] is None else data['ebitda']
        if len(currency_values) >= 3:
            data['net_profit'] = currency_values[2] if data['net_profit'] is None else data['net_profit']
        if len(currency_values) >= 4:
            data['total_debt'] = currency_values[3] if data['total_debt'] is None else data['total_debt']
        if len(currency_values) >= 5:
            data['total_equity'] = currency_values[4] if data['total_equity'] is None else data['total_equity']
        
        # Calculate derived metrics
        if data['total_debt'] and data['total_equity'] and data['total_equity'] > 0:
            data['debt_to_equity'] = round(data['total_debt'] / data['total_equity'], 2)
        
        if data['ebitda'] and data.get('interest_expense'):
            data['interest_coverage'] = round(data['ebitda'] / data['interest_expense'], 2)
        
        if data['revenue'] and data['net_profit'] and data['revenue'] > 0:
            data['profit_margin'] = round((data['net_profit'] / data['revenue']) * 100, 2)
        
        return data
    
    def extract_borrowing_profile_data(self, text: str) -> Dict[str, Any]:
        """
        Extract borrowing profile data from loan document
        Returns dict with loan_amount, tenure, interest_rate, etc.
        """
        data = {
            'loan_amount': None,
            'tenure_months': None,
            'interest_rate': None,
            'emi': None,
            'purpose': None,
            'lender_name': None,
            'repayment_schedule': [],
        }
        
        # Extract loan amount
        loan_amount = self._extract_value(text, r'(?:loan|sanction|facility)\s+(?:amount|of)?\s*[:\-]?\s*')
        if loan_amount:
            data['loan_amount'] = loan_amount
        
        # Extract tenure
        tenure = re.search(r'(\d+)\s*(?:months?|years?)', text, re.IGNORECASE)
        if tenure:
            tenure_value = int(tenure.group(1))
            if 'year' in tenure.group(0).lower():
                tenure_value *= 12
            data['tenure_months'] = tenure_value
        
        # Extract interest rate
        interest_rate = self._extract_value(text, r'(?:interest\s+rate|rate\s+of\s+interest)\s*[:\-]?\s*')
        if interest_rate:
            data['interest_rate'] = interest_rate
        
        # Extract EMI
        emi = self._extract_value(text, r'(?:emi|monthly\s+installment)\s*[:\-]?\s*')
        if emi:
            data['emi'] = emi
        
        # Generate repayment schedule if we have loan details
        if data['loan_amount'] and data['tenure_months'] and data['interest_rate']:
            data['repayment_schedule'] = self._generate_repayment_schedule(
                data['loan_amount'],
                data['tenure_months'],
                data['interest_rate']
            )
        
        return data
    
    def _extract_value(self, text: str, pattern: str) -> Optional[float]:
        """Extract numeric value from text using regex pattern"""
        match = re.search(pattern + r'([\d,]+\.?\d*)', text, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1).replace(',', '')
                return float(value_str)
            except (ValueError, AttributeError):
                pass
        return None
    
    def _extract_all_currency_values(self, text: str) -> list:
        """Extract all currency values from text"""
        # Match currency values like 1,00,000 or 1000000 or 1.5 Cr
        pattern = r'(?:₹|Rs\.?|INR)?\s*([\d,]+\.?\d*)\s*(?:Cr|Lac|Lakh|Million|Billion)?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        values = []
        for match in matches:
            try:
                value = float(match.replace(',', ''))
                # Convert to actual number based on suffix
                if 'cr' in text.lower():
                    value *= 10000000
                elif 'lac' in text.lower() or 'lakh' in text.lower():
                    value *= 100000
                elif 'million' in text.lower():
                    value *= 1000000
                elif 'billion' in text.lower():
                    value *= 1000000000
                values.append(value)
            except (ValueError, AttributeError):
                continue
        
        return values
    
    def _generate_repayment_schedule(
        self, 
        principal: float, 
        tenure_months: int, 
        interest_rate: float
    ) -> list:
        """Generate EMI repayment schedule"""
        monthly_rate = interest_rate / 12 / 100
        
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / \
                  ((1 + monthly_rate) ** tenure_months - 1)
        
        schedule = []
        balance = principal
        
        for month in range(1, tenure_months + 1):
            interest_payment = balance * monthly_rate
            principal_payment = emi - interest_payment
            balance -= principal_payment
            
            schedule.append({
                'month': month,
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'emi': round(emi, 2),
                'balance': round(max(0, balance), 2)
            })
        
        return schedule
    
    def extract_from_pdf(self, file_bytes: bytes) -> Tuple[Dict[str, Any], str, float]:
        """
        Extract data from PDF file
        Returns (extracted_data, document_type, confidence)
        """
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            return {"error": str(e)}, "unknown", 0.0
        
        document_type, confidence = self.classify_document(text)
        
        if document_type == "annual_report":
            data = self.extract_annual_report_data(text)
        elif document_type == "borrowing_profile":
            data = self.extract_borrowing_profile_data(text)
        else:
            data = {"error": "Unable to classify document"}
        
        return data, document_type, confidence
    
    def extract_from_excel(self, file_bytes: bytes) -> Tuple[Dict[str, Any], str, float]:
        """
        Extract data from Excel file
        Returns (extracted_data, document_type, confidence)
        """
        try:
            df = pd.read_excel(BytesIO(file_bytes))
            text = df.to_string()
        except Exception as e:
            return {"error": str(e)}, "unknown", 0.0
        
        document_type, confidence = self.classify_document(text)
        
        if document_type == "annual_report":
            data = self._extract_from_dataframe(df, "annual_report")
        elif document_type == "borrowing_profile":
            data = self._extract_from_dataframe(df, "borrowing_profile")
        else:
            data = {"error": "Unable to classify document"}
        
        return data, document_type, confidence
    
    def _extract_from_dataframe(self, df: pd.DataFrame, doc_type: str) -> Dict[str, Any]:
        """Extract data from pandas DataFrame"""
        data = {}
        
        if doc_type == "annual_report":
            data = {
                'year': datetime.now().year - 1,
                'revenue': None,
                'ebitda': None,
                'net_profit': None,
                'cashflow_from_operations': None,
                'total_debt': None,
                'total_equity': None,
                'debt_to_equity': None,
                'interest_coverage': None,
                'profit_margin': None,
            }
            
            # Try to find financial metrics in the dataframe
            for idx, row in df.iterrows():
                row_str = str(row.values).lower()
                
                if 'revenue' in row_str or 'sales' in row_str or 'turnover' in row_str:
                    for val in row.values:
                        if isinstance(val, (int, float)) and val > 0:
                            data['revenue'] = float(val)
                            break
                            
                elif 'ebitda' in row_str:
                    for val in row.values:
                        if isinstance(val, (int, float)):
                            data['ebitda'] = float(val)
                            break
                            
                elif 'net profit' in row_str or 'profit after tax' in row_str:
                    for val in row.values:
                        if isinstance(val, (int, float)):
                            data['net_profit'] = float(val)
                            break
        
        elif doc_type == "borrowing_profile":
            data = {
                'loan_amount': None,
                'tenure_months': None,
                'interest_rate': None,
                'emi': None,
                'purpose': None,
                'lender_name': None,
                'repayment_schedule': [],
            }
            
            # Look for loan details in dataframe
            for idx, row in df.iterrows():
                row_str = str(row.values).lower()
                
                if 'loan amount' in row_str or 'sanction' in row_str:
                    for val in row.values:
                        if isinstance(val, (int, float)) and val > 0:
                            data['loan_amount'] = float(val)
                            break
        
        return data


# Singleton instance
extraction_service = DocumentExtractionService()
