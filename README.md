A powerful Streamlit web application that processes financial documents (PDF and Excel formats) and provides an interactive question-answering system for querying financial data using natural language.

https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white
https://img.shields.io/badge/Python-3.8%252B-blue?style=for-the-badge&logo=python
https://img.shields.io/badge/License-MIT-green?style=for-the-badge

✨ Features
📄 Multi-Format Support: Process both PDF and Excel financial documents

💬 Natural Language Q&A: Ask questions about financial data in plain English

🔍 Smart Data Extraction: Automatically detects revenue, profits, expenses, assets, and liabilities

🎨 Intuitive Interface: Clean, user-friendly web interface with real-time chat

📊 Financial Metrics: Visual display of extracted financial data

🐛 Debug Mode: See exactly what's being extracted from your documents

⚡ Local Processing: No cloud dependencies - everything runs locally

🚀 Quick Start
Prerequisites
Python 3.8 or higher

pip (Python package manager)

Installation
Clone the repository

bash
git clone git@github.com:saina-panda12/Financial_qa_assistant.git
cd financial-qa-assistant
Create and activate virtual environment

bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install dependencies

bash
pip install -r requirements.txt
Run the application

bash
streamlit run financial_qa_assistant.py
Open your browser and navigate to http://localhost:8501

📋 Usage Guide
1. Upload Documents
Use the sidebar to upload PDF or Excel files containing financial statements

Supported formats: .pdf, .xlsx, .xls

The system automatically processes and extracts financial data

2. View Extracted Data
See detected financial metrics in the left panel

Review extracted text content

Enable debug mode to see processing details

3. Ask Questions
Use natural language to query your financial data:

💰 Revenue Questions:

"What was the total revenue?"

"Show me the sales figures"

"How much income was generated?"

📈 Profit Questions:

"What was the net profit?"

"How much earnings were reported?"

"Show me the bottom line"

💸 Expense Questions:

"What were the total expenses?"

"How much were operating costs?"

"Show me cost breakdown"

🏦 Asset Questions:

"What are the total assets?"

"Show me current assets"

"What's the property value?"

📉 Liability Questions:

"What are the total liabilities?"

"How much debt does the company have?"

"Show me accounts payable"

📊 General Questions:

"How did the company perform financially?"

"Give me a financial summary"

"Show me all financial metrics"

🏗️ Project Structure
text
financial-qa-assistant/
├── financial_qa_assistant.py  # Main application
├── requirements.txt           # Python dependencies
├── README.md                 # Documentation
├── .gitignore               # Git ignore rules
├── sample_financials.xlsx    # Example Excel file
├── sample_statement.pdf      # Example PDF file
└── LICENSE                   # MIT License
🔧 Technical Details
Document Processing
PDF Files: Uses pdfplumber and PyPDF2 for text extraction

Excel Files: Uses pandas and openpyxl for data extraction

Financial Detection: Regex patterns to identify financial metrics

Supported Document Types
Income Statements

Balance Sheets

Cash Flow Statements

Financial Reports

Annual Reports

Quarterly Statements

Dependencies
txt
streamlit==1.28.1    # Web framework
pandas==2.0.3        # Data processing
numpy==1.24.3        # Numerical operations
PyPDF2==3.0.1        # PDF processing
openpyxl==3.1.2      # Excel handling
pdfplumber==0.10.3   # Advanced PDF extraction
plotly==5.15.0       # Data visualization
Pillow==10.0.0       # Image processing
🐛 Troubleshooting
Common Issues
Port already in use:

bash
streamlit run financial_qa_assistant.py --server.port 8502
Missing dependencies:

bash
pip install -r requirements.txt
PDF extraction issues:

Try different PDF files

Enable debug mode in sidebar

Check if PDF is text-based (not scanned images)

Excel file issues:

Ensure files are not password protected

Check for compatible Excel formats (.xlsx, .xls)

Debug Mode
Enable debug mode in the sidebar to see:

Raw extracted text from documents

Detected financial metrics

Processing errors and warnings

📸 Screenshots
<img width="1360" height="671" alt="image" src="https://github.com/user-attachments/assets/d1a444fb-a46f-4aa5-8d08-ab28895b8203" />


Main interface with document upload

Financial metrics display

Q&A chat interface

Debug information panel

🤝 Contributing
We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

Fork the repository

Create your feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Built with Streamlit

Financial document processing with PyPDF2 and pdfplumber

Excel file handling with pandas and openpyxl

Inspired by the need for better financial document analysis tools

📞 Support
If you have any questions or need help:

Check the troubleshooting section

Open an issue

Contact the development team

⭐ If you find this project useful, please give it a star on GitHub!

Note: This application processes documents locally and doesn't require internet connection for document analysis. However, for optimal performance, ensure you have the required dependencies installed.

