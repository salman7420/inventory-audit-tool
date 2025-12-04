import pandas as pd
import streamlit as st
from typing import Tuple, Optional

class FileValidator:
    """Handles file validation and reading for the auditing tool"""
    
    @staticmethod
    def read_excel_file(uploaded_file) -> Optional[pd.DataFrame]:
        """
        Read Excel file and return DataFrame
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            DataFrame or None if error occurs
        """
        try:
            df = pd.read_excel(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Error reading file {uploaded_file.name}: {str(e)}")
            return None
    
    @classmethod
    def validate_stock_file(cls, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate total stock file structure
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if df is None or df.empty:
            return False, "File is empty or could not be read"
        
        # Check for Label No column (critical identifier)
        if 'Label No' not in df.columns:
            return False, "Missing required column: 'Label No'"
        
        # Check other critical columns
        required_cols = ['Item Name', 'Metal ID', 'Gross Wt.', 'Net Wt.', 
                        'Pcs', 'Location', 'Old BarCode No', 'Voucher Date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}"
        
        # Check if Label No has values
        if df['Label No'].isna().all():
            return False, "Label No column has no values"
        
        return True, "Stock file validation passed"
    
    @classmethod
    def validate_report_file(cls, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate audit report file structure
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if df is None or df.empty:
            return False, "File is empty or could not be read"
        
        # Check for critical columns
        required_cols = ['Stock Menu', 'Label No', 'Item Name', 'Location']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}"
        
        # Check if Stock Menu column exists and has 'Found' values
        if 'Stock Menu' in df.columns:
            found_items = df[df['Stock Menu'] == 'Found']
            if found_items.empty:
                return False, "No 'Found' items in Stock Menu column"
        
        # Check if Label No has values
        if df['Label No'].isna().all():
            return False, "Label No column has no values"
        
        return True, "Report file validation passed"
    
    @classmethod
    def load_and_validate_files(cls, stock_file, barcode_file, label_file) -> dict:
        """
        Load and validate all three files
        
        Args:
            stock_file: Total stock Excel file
            barcode_file: Old barcode report file
            label_file: Label number report file
            
        Returns:
            Dictionary with DataFrames and validation status
        """
        results = {
            'success': False,
            'stock_df': None,
            'barcode_df': None,
            'label_df': None,
            'errors': []
        }
        
        # Load stock file
        with st.spinner("Loading stock file..."):
            stock_df = cls.read_excel_file(stock_file)
            if stock_df is not None:
                is_valid, message = cls.validate_stock_file(stock_df)
                if is_valid:
                    results['stock_df'] = stock_df
                    st.success(f"✓ Stock file loaded: {len(stock_df)} items")
                else:
                    results['errors'].append(f"Stock file error: {message}")
                    st.error(f"Stock file error: {message}")
        
        # Load barcode report file
        with st.spinner("Loading old barcode report..."):
            barcode_df = cls.read_excel_file(barcode_file)
            if barcode_df is not None:
                is_valid, message = cls.validate_report_file(barcode_df)
                if is_valid:
                    results['barcode_df'] = barcode_df
                    st.success(f"✓ Old barcode report loaded: {len(barcode_df)} items")
                else:
                    results['errors'].append(f"Barcode report error: {message}")
                    st.error(f"Barcode report error: {message}")
        
        # Load label report file
        with st.spinner("Loading label number report..."):
            label_df = cls.read_excel_file(label_file)
            if label_df is not None:
                is_valid, message = cls.validate_report_file(label_df)
                if is_valid:
                    results['label_df'] = label_df
                    st.success(f"✓ Label number report loaded: {len(label_df)} items")
                else:
                    results['errors'].append(f"Label report error: {message}")
                    st.error(f"Label report error: {message}")
        
        # Check if all files loaded successfully
        if all([results['stock_df'] is not None, 
                results['barcode_df'] is not None, 
                results['label_df'] is not None]):
            results['success'] = True
        
        return results
