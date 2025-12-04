# 📦 Dua Inventory Auditing Tool

A Streamlit-based web application for streamlining inventory auditing processes by merging multiple barcode mappings and generating comprehensive found/missing item reports.

## Features

- ✅ Upload and validate ERP stock files and audit reports
- 🔄 Merge reports from multiple barcode systems (Old Barcode & Label Number)
- 📊 Identify duplicate scans across reports
- 📈 Generate found/missing item reports with statistics
- 💾 Export reports to CSV format
- 🎨 Clean, gold-themed UI matching company branding

## Installation

1. Clone this repository:
git clone:  
cd inventory-audit-tool

2. Create virtual environment:
python3 -m venv venv
source venv/bin/activate # On Mac/Linux

3. Install dependencies:
pip install -r requirements.txt

4. Run the app:
streamlit run app.py

## Usage

1. Upload three Excel files:
   - **Total Stock File**: ERP export with all inventory
   - **Old Barcode Report**: Audit scanned with old barcode numbers
   - **Label Number Report**: Audit scanned with label numbers

2. Click "Process Audit Reports"

3. View and download:
   - Found items report
   - Missing items report
   - Duplicate scans report

## File Structure

inventory-audit-tool/
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── utils/
│ ├── init.py
│ ├── file_handler.py # File validation & reading
│ └── data_processor.py # Data merging & comparison
├── .streamlit/
│ └── config.toml # Streamlit theme configuration
└── README.md

text

## Technologies Used

- Python 3.8+
- Streamlit
- Pandas
- OpenPyXL

## License

MIT License
