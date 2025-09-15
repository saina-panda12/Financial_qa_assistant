import streamlit as st
import pandas as pd
import numpy as np
import time
import re
import json
from typing import Dict, List, Any

# Import document processing libraries
try:
    import PyPDF2
    from openpyxl import load_workbook
    import pdfplumber
except ImportError:
    st.warning("Some required libraries are missing. Please install them using: pip install PyPDF2 openpyxl pdfplumber")

# Set page configuration
st.set_page_config(
    page_title="Financial Document Q&A Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .chat-container {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1.5rem;
        height: 500px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #d4edda;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #ffffff;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .financial-data {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
    }
    .debug-section {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

class FinancialDocumentProcessor:
    """Process financial documents (PDF and Excel) and extract financial data"""
    
    def __init__(self):
        self.extracted_data = {}
        self.document_text = ""
        self.financial_metrics = {}
    
    def process_excel_file(self, file) -> Dict[str, Any]:
        """Process Excel financial documents"""
        try:
            # Read the Excel file
            df = pd.read_excel(file)
            
            # Store the raw data
            self.extracted_data["excel_data"] = df.to_dict()
            
            # Extract text content for LLM processing
            text_content = ""
            for sheet_name in pd.ExcelFile(file).sheet_names:
                df_sheet = pd.read_excel(file, sheet_name=sheet_name)
                text_content += f"Sheet: {sheet_name}\n"
                text_content += df_sheet.to_string() + "\n\n"
            
            self.document_text = text_content
            
            # Try to identify common financial statements
            self._identify_financial_data(df)
            
            # Also extract from text content
            self._extract_financial_metrics_from_text(text_content)
            
            return {
                "success": True,
                "data": self.extracted_data,
                "text": text_content,
                "metrics": self.financial_metrics
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing Excel file: {str(e)}"
            }
    
    def process_pdf_file(self, file) -> Dict[str, Any]:
        """Process PDF financial documents"""
        try:
            text_content = ""
            
            # Try different PDF extraction methods
            try:
                # Method 1: Using pdfplumber (better for text extraction)
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_content += text + "\n\n"
            except:
                # Method 2: Using PyPDF2 as fallback
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n\n"
            
            self.document_text = text_content
            
            # Try to extract tables from PDF
            tables = self._extract_tables_from_pdf(file)
            if tables:
                self.extracted_data["tables"] = tables
            
            # Try to identify financial data
            self._extract_financial_metrics_from_text(text_content)
            
            return {
                "success": True,
                "data": self.extracted_data,
                "text": text_content,
                "metrics": self.financial_metrics
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing PDF file: {str(e)}"
            }
    
    def _extract_tables_from_pdf(self, file) -> List[Any]:
        """Extract tables from PDF using pdfplumber"""
        tables = []
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except:
            pass
        return tables
    
    def _identify_financial_data(self, df: pd.DataFrame) -> None:
        """Identify financial data in DataFrame"""
        # Look for common financial terms in column names
        financial_terms = [
            'revenue', 'sales', 'income', 'expense', 'profit', 'loss',
            'asset', 'liability', 'equity', 'cash', 'balance', 'ebitda',
            'cost', 'margin', 'gross', 'net', 'operating'
        ]
        
        for col in df.columns:
            if isinstance(col, str):
                col_lower = col.lower()
                for term in financial_terms:
                    if term in col_lower:
                        # Try to extract numerical values
                        try:
                            values = pd.to_numeric(df[col], errors='coerce').dropna()
                            if not values.empty:
                                # Get the last value (often the total)
                                self.financial_metrics[col] = values.iloc[-1]
                        except:
                            pass
    
    def _extract_financial_metrics_from_text(self, text: str) -> None:
        """Extract financial metrics from text content with improved pattern matching"""
        # Convert text to lowercase for easier matching
        text_lower = text.lower()
        
        # Improved patterns to look for financial data with better context
        patterns = {
            'revenue': [
                r'(revenue|sales|income).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(revenue|sales|income)'
            ],
            'profit': [
                r'(profit|net income|net profit|earnings).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(profit|net income|net profit|earnings)'
            ],
            'expenses': [
                r'(expenses|costs|operating expenses|cost of goods sold|cogs).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(expenses|costs|operating expenses)'
            ],
            'assets': [
                r'(total assets|assets).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(total assets|assets)'
            ],
            'liabilities': [
                r'(liabilities|debt|total liabilities).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(liabilities|debt)'
            ],
            'equity': [
                r'(equity|shareholders equity|owners equity).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(equity|shareholders equity)'
            ],
            'net income': [
                r'(net income|net profit|bottom line).*?[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?).*?(net income|net profit)'
            ]
        }
        
        # Extract using patterns
        for metric, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    # Get the first match with a valid number
                    for match in matches:
                        if len(match) >= 2 and match[1].replace(',', '').replace('.', '').isdigit():
                            value = match[1]
                            # Clean the value
                            if value.startswith('$'):
                                value = value[1:]
                            self.financial_metrics[metric] = value
                            break
        
        # Fallback: look for numbers near financial terms
        financial_terms = {
            'revenue': ['revenue', 'sales', 'income', 'turnover'],
            'profit': ['profit', 'net income', 'net profit', 'earnings'],
            'expenses': ['expenses', 'costs', 'operating expenses', 'cogs', 'cost of goods sold'],
            'assets': ['assets', 'total assets', 'current assets', 'fixed assets'],
            'liabilities': ['liabilities', 'debt', 'total liabilities', 'current liabilities'],
            'equity': ['equity', 'shareholders equity', 'owners equity'],
            'net income': ['net income', 'net profit', 'bottom line']
        }
        
        # Find all numbers in the text
        number_pattern = r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        numbers = re.findall(number_pattern, text)
        
        # For each number, check if it's near financial terms
        for number in numbers:
            # Get context around the number
            number_pos = text_lower.find(number)
            if number_pos == -1:
                continue
                
            start_pos = max(0, number_pos - 100)
            end_pos = min(len(text_lower), number_pos + len(number) + 100)
            context = text_lower[start_pos:end_pos]
            
            # Check which financial term this number might belong to
            for metric, terms in financial_terms.items():
                if any(term in context for term in terms) and metric not in self.financial_metrics:
                    # Clean the number
                    clean_number = number.replace('$', '').replace(',', '')
                    if clean_number.replace('.', '').isdigit():
                        self.financial_metrics[metric] = number
                        break

class FinancialQASystem:
    """Question-Answering system for financial documents"""
    
    def __init__(self):
        self.conversation_history = []
    
    def generate_response(self, question: str, document_text: str, financial_metrics: Dict[str, Any]) -> str:
        """Generate a response to a financial question with better matching"""
        question_lower = question.lower()
        
        # Check for specific financial queries with better matching
        if any(term in question_lower for term in ['revenue', 'sales', 'income', 'turnover']):
            for key in ['revenue', 'sales', 'income']:
                if key in financial_metrics:
                    return f"Based on the financial document, the {key.replace('_', ' ')} is ${financial_metrics[key]}."
        
        elif any(term in question_lower for term in ['profit', 'net income', 'net profit', 'earnings', 'bottom line']):
            for key in ['profit', 'net income', 'net profit', 'earnings']:
                if key in financial_metrics:
                    return f"The document shows a {key.replace('_', ' ')} of ${financial_metrics[key]}."
        
        elif any(term in question_lower for term in ['expense', 'cost', 'spending', 'cogs']):
            for key in ['expenses', 'costs', 'operating expenses']:
                if key in financial_metrics:
                    return f"Total {key.replace('_', ' ')} are ${financial_metrics[key]} according to the document."
        
        elif any(term in question_lower for term in ['asset', 'property', 'equipment', 'inventory']):
            for key in ['assets', 'total assets', 'current assets']:
                if key in financial_metrics:
                    return f"The document reports {key.replace('_', ' ')} of ${financial_metrics[key]}."
        
        elif any(term in question_lower for term in ['liabilit', 'debt', 'payable', 'loan']):
            for key in ['liabilities', 'debt', 'total liabilities']:
                if key in financial_metrics:
                    return f"The document shows {key.replace('_', ' ')} of ${financial_metrics[key]}."
        
        elif any(term in question_lower for term in ['equity', 'shareholder', 'owner']):
            for key in ['equity', 'shareholders equity']:
                if key in financial_metrics:
                    return f"According to the document, {key.replace('_', ' ')} is ${financial_metrics[key]}."
        
        elif any(term in question_lower for term in ['net income', 'net profit']):
            for key in ['net income', 'net profit']:
                if key in financial_metrics:
                    return f"The document shows {key.replace('_', ' ')} of ${financial_metrics[key]}."
        
        # Show available metrics if no specific match
        if financial_metrics:
            metrics_list = "\n".join([f"• **{k}**: ${v}" for k, v in financial_metrics.items()])
            return f"I found these financial metrics in the document:\n\n{metrics_list}\n\nYou can ask about any of these specific values."
        
        # Default response if no financial data is found
        return "I've analyzed the document but couldn't extract specific financial metrics. The document may use different terminology. You can ask me to look for specific terms or try uploading a different financial document."

def main():
    # Application header
    st.markdown('<h1 class="main-header">📊 Financial Document Q&A Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'document_text' not in st.session_state:
        st.session_state.document_text = ""
    if 'financial_metrics' not in st.session_state:
        st.session_state.financial_metrics = {}
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = FinancialQASystem()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_debug' not in st.session_state:
        st.session_state.show_debug = False
    
    # Sidebar for document upload
    with st.sidebar:
        st.markdown("## 📁 Document Upload")
        st.markdown('<div class="info-box">Upload financial documents in PDF or Excel format for analysis</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a financial document",
            type=['pdf', 'xlsx', 'xls'],
            help="Supported formats: PDF, Excel (XLSX, XLS)"
        )
        
        # Debug toggle
        st.session_state.show_debug = st.checkbox("Show Debug Information", value=False)
        
        if uploaded_file is not None:
            # Display file details
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            st.write(file_details)
            
            # Process document
            processor = FinancialDocumentProcessor()
            
            if uploaded_file.type == "application/pdf":
                result = processor.process_pdf_file(uploaded_file)
            else:
                result = processor.process_excel_file(uploaded_file)
            
            if result["success"]:
                st.session_state.processed = True
                st.session_state.document_text = result["text"]
                st.session_state.financial_metrics = result["metrics"]
                st.success("Document processed successfully!")
                
                # Display extracted metrics
                if st.session_state.financial_metrics:
                    st.markdown("### 📈 Extracted Financial Metrics")
                    for metric, value in st.session_state.financial_metrics.items():
                        st.write(f"**{metric.capitalize()}:** ${value}")
            else:
                st.error(f"Error processing document: {result['error']}")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="sub-header">📋 Document Summary</div>', unsafe_allow_html=True)
        
        if st.session_state.processed:
            st.markdown('<div class="financial-data">', unsafe_allow_html=True)
            st.write("**Document Content Preview:**")
            
            # Show preview of document text
            text_preview = st.session_state.document_text[:500] + "..." if len(st.session_state.document_text) > 500 else st.session_state.document_text
            st.text_area("Extracted Text", text_preview, height=200, label_visibility="collapsed")
            
            # Show financial metrics
            if st.session_state.financial_metrics:
                st.write("**Detected Financial Metrics:**")
                for metric, value in st.session_state.financial_metrics.items():
                    st.write(f"- **{metric.capitalize()}:** ${value}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Debug information
            if st.session_state.show_debug:
                with st.expander("Debug: Extracted Text Preview"):
                    st.text(st.session_state.document_text[:1000] + "..." if len(st.session_state.document_text) > 1000 else st.session_state.document_text)
                
                with st.expander("Debug: Extracted Metrics"):
                    st.json(st.session_state.financial_metrics)
        else:
            st.info("Please upload a financial document to get started. The system supports PDF and Excel files containing financial statements.")
            
            # Example financial data
            st.markdown("### 💡 Example Questions You Can Ask")
            st.write("- What was the total revenue?")
            st.write("- How much profit was reported?")
            st.write("- What were the total expenses?")
            st.write("- What are the company's total assets?")
            st.write("- What is the net income?")
            st.write("- How did the company perform financially?")
    
    with col2:
        st.markdown('<div class="sub-header">💬 Financial Q&A</div>', unsafe_allow_html=True)
        
        if st.session_state.processed:
            # Chat interface
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    # Preserve line breaks in assistant messages
                    formatted_content = message["content"].replace('\n', '<br>')
                    st.markdown(f'<div class="assistant-message">🤖 {formatted_content}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Input for new question
            question = st.text_input("Ask a question about the financial document:", key="question_input", placeholder="e.g., What was the revenue?")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Submit Question") and question:
                    # Add user question to chat history
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    
                    # Generate response
                    with st.spinner("Analyzing document..."):
                        # Simulate processing time
                        time.sleep(0.5)
                        
                        response = st.session_state.qa_system.generate_response(
                            question, 
                            st.session_state.document_text, 
                            st.session_state.financial_metrics
                        )
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Rerun to update the chat display
                    st.rerun()
            
            with col2:
                if st.button("Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()
        else:
            st.info("Please upload a financial document to enable the Q&A feature.")
            
            # Placeholder chat interface
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            st.markdown('<div class="assistant-message">🤖 Please upload a financial document to start asking questions.</div>', unsafe_allow_html=True)
            st.markdown('<div class="assistant-message">🤖 I can help you analyze income statements, balance sheets, and cash flow statements.</div>', unsafe_allow_html=True)
            st.markdown('<div class="assistant-message">🤖 Try asking about revenue, profits, expenses, assets, or other financial metrics.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()