import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Dua Inventory Auditing Tool",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for additional gold theming
st.markdown("""
    <style>
    .main-header {
        color: #D4AF37;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #D4AF37;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📦 Dua Internal Auditing Tool</div>', unsafe_allow_html=True)
st.markdown('''
    <div class="sub-header">
    Streamline your inventory auditing process by uploading stock files and audit reports. 
    This tool automatically merges multiple barcode mappings and generates comprehensive 
    found/missing item reports with filtering and export capabilities.
    </div>
''', unsafe_allow_html=True)

st.divider()

# File upload section
st.subheader("📁 Upload Required Files")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**1. Total Stock File**")
    st.caption("Export from ERP system")
    stock_file = st.file_uploader(
        "Choose stock Excel file",
        type=["xlsx", "xls"],
        key="stock",
        help="Upload the complete stock list from your ERP system"
    )
    if stock_file:
        st.success("✓ Stock file uploaded")

with col2:
    st.markdown("**2. Old Barcode Report**")
    st.caption("Audit mapped with old barcode")
    barcode_file = st.file_uploader(
        "Choose old barcode report",
        type=["xlsx", "xls"],
        key="barcode",
        help="Upload audit report mapped using old barcode numbers"
    )
    if barcode_file:
        st.success("✓ Barcode report uploaded")

with col3:
    st.markdown("**3. Label Number Report**")
    st.caption("Audit mapped with label number")
    label_file = st.file_uploader(
        "Choose label number report",
        type=["xlsx", "xls"],
        key="label",
        help="Upload audit report mapped using label numbers"
    )
    if label_file:
        st.success("✓ Label report uploaded")

st.divider()

# Proceed button
all_files_uploaded = stock_file and barcode_file and label_file

if all_files_uploaded:
    st.success("🎉 All files uploaded successfully! Ready to process.")
    
    col_button1, col_button2, col_button3 = st.columns([1, 2, 1])
    with col_button2:
        if st.button("🚀 Process Audit Reports", type="primary", use_container_width=True):
            # Import the handlers
            from utils.file_handler import FileValidator
            from utils.data_processor import DataProcessor
            
            # Load and validate all files
            validation_results = FileValidator.load_and_validate_files(
                stock_file, barcode_file, label_file
            )
            
            if validation_results['success']:
                st.success("🎉 All files validated successfully!")
                
                # Store in session state
                st.session_state['stock_df'] = validation_results['stock_df']
                st.session_state['barcode_df'] = validation_results['barcode_df']
                st.session_state['label_df'] = validation_results['label_df']
                
                st.divider()
                
                # Process the audit data
                with st.spinner("Processing audit data..."):
                    processing_results = DataProcessor.process_audit_data(
                        validation_results['stock_df'],
                        validation_results['barcode_df'],
                        validation_results['label_df']
                    )
                
                # Store results in session state
                st.session_state['processing_results'] = processing_results
                st.session_state['processing_complete'] = True
                
                st.divider()
                
                # Display Summary Statistics
                st.subheader("📈 Audit Summary")
                stats = processing_results['stats']
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Stock Items", stats['total_stock'])
                with col2:
                    st.metric("Total Scanned", stats['total_scanned'])
                with col3:
                    st.metric("Unique Found Items", stats['unique_found'])
                with col4:
                    st.metric("Missing Items", stats['missing'])
                with col5:
                    st.metric("Duplicate Scans", stats['num_duplicates'])
                
                # Calculation explanation
                st.info(f"📊 **Calculation**: Missing Items = Total Stock ({stats['total_stock']}) - Total Scanned ({stats['total_scanned']}) = {stats['missing']}")
                
                # Show duplicates report if there are any
                if stats['num_duplicates'] > 0:
                    st.divider()
                    st.subheader("🔄 Duplicate Items Report")
                    st.warning(f"These {stats['num_duplicates']} items were scanned in BOTH reports (Old Barcode & Label Number)")
                    st.dataframe(
                        processing_results['duplicates_display'],
                        use_container_width=True,
                        height=300
                    )
                    
                    # Download button for duplicates
                    duplicates_csv = processing_results['duplicates_display'].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Duplicates Report (CSV)",
                        data=duplicates_csv,
                        file_name="duplicate_items_report.csv",
                        mime="text/csv",
                    )
                
                # Display Reports
                st.divider()
                st.subheader("📋 Found Items Report")
                st.dataframe(
                    processing_results['found_items'],
                    use_container_width=True,
                    height=400
                )
                
                # Download button for found items
                found_csv = processing_results['found_items'].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Found Items Report (CSV)",
                    data=found_csv,
                    file_name="found_items_report.csv",
                    mime="text/csv",
                )
                
                st.divider()
                st.subheader("❌ Missing Items Report")
                st.dataframe(
                    processing_results['missing_items'],
                    use_container_width=True,
                    height=400
                )
                
                # Download button for missing items
                missing_csv = processing_results['missing_items'].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Missing Items Report (CSV)",
                    data=missing_csv,
                    file_name="missing_items_report.csv",
                    mime="text/csv",
                )
                
                st.success("✅ Processing complete! You can now download the reports above.")
                
            else:
                st.error("❌ File validation failed. Please check the errors above and re-upload.")
                if validation_results['errors']:
                    st.markdown("**Validation Errors:**")
                    for error in validation_results['errors']:
                        st.warning(f"• {error}")
else:
    st.warning("⚠️ Please upload all three files to proceed with the audit.")
    
    # Show which files are missing
    missing_files = []
    if not stock_file:
        missing_files.append("Total Stock File")
    if not barcode_file:
        missing_files.append("Old Barcode Report")
    if not label_file:
        missing_files.append("Label Number Report")
    
    st.info(f"Missing: {', '.join(missing_files)}")

# Display results if already processed (from session state)
if 'processing_complete' in st.session_state and st.session_state['processing_complete']:
    if st.button("🔄 Clear Results and Upload New Files"):
        # Clear session state
        for key in ['stock_df', 'barcode_df', 'label_df', 'processing_results', 'processing_complete']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Footer
st.divider()
st.caption("Dua Internal Tool v1.0 | Inventory Auditing System")
