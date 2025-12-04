import pandas as pd
import streamlit as st
from typing import Tuple, Dict

class DataProcessor:
    """Handles data cleaning, merging, and comparison logic"""
    
    @staticmethod
    def clean_report_file(df: pd.DataFrame, report_name: str) -> pd.DataFrame:
        """
        Clean and filter report file to keep only 'Found' items
        
        Args:
            df: Report DataFrame
            report_name: Name for logging purposes
            
        Returns:
            Cleaned DataFrame with only Found items
        """
        # Filter only 'Found' items
        found_items = df[df['Stock Menu'] == 'Found'].copy()
        
        # Select relevant columns
        columns_to_keep = [
            'Label No', 'Old BarCode No', 'Item Name', 
            'Gross Wt.', 'Net Wt.', 'Location', 'Remark'
        ]
        
        # Keep only columns that exist
        available_cols = [col for col in columns_to_keep if col in found_items.columns]
        found_items = found_items[available_cols]
        
        # Remove rows where Label No is null/empty
        found_items = found_items[found_items['Label No'].notna()]
        found_items = found_items[found_items['Label No'] != '']
        
        st.info(f"{report_name}: {len(found_items)} found items after filtering")
        
        return found_items
    
    @staticmethod
    def merge_audit_reports(barcode_df: pd.DataFrame, label_df: pd.DataFrame) -> Dict:
        """
        Merge both audit reports and identify duplicates
        
        Args:
            barcode_df: Old barcode report DataFrame
            label_df: Label number report DataFrame
            
        Returns:
            Dictionary with merged data and duplicate information
        """
        # Clean both reports
        barcode_clean = DataProcessor.clean_report_file(barcode_df, "Old Barcode Report")
        label_clean = DataProcessor.clean_report_file(label_df, "Label Number Report")
        
        # Add source column to track where items came from
        barcode_clean['Source'] = 'Old Barcode Report'
        label_clean['Source'] = 'Label Number Report'
        
        # Concatenate both reports
        combined = pd.concat([barcode_clean, label_clean], ignore_index=True)
        
        st.info(f"Combined reports: {len(combined)} total items")
        
        # Find duplicates (items scanned in BOTH reports)
        duplicate_labels = combined[combined.duplicated(subset=['Label No'], keep=False)]['Label No'].unique()
        duplicates_df = combined[combined['Label No'].isin(duplicate_labels)].copy()
        duplicates_df = duplicates_df.sort_values('Label No')
        
        # Get unique items (remove duplicates, keep first occurrence)
        unique_items = combined.drop_duplicates(subset=['Label No'], keep='first')
        
        num_duplicates = len(duplicate_labels)
        st.warning(f"⚠️ Found {num_duplicates} duplicate items scanned in both reports")
        st.success(f"✓ Merged audit reports: {len(unique_items)} unique found items")
        
        return {
            'combined_all': combined,
            'unique_items': unique_items,
            'duplicates': duplicates_df,
            'num_duplicates': num_duplicates,
            'total_scanned': len(combined),
            'unique_count': len(unique_items)
        }
    
    @staticmethod
    def compare_with_stock(stock_df: pd.DataFrame, unique_items_df: pd.DataFrame, 
                          total_scanned: int) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
        """
        Compare found items with total stock to identify found and missing items
        
        Args:
            stock_df: Total stock DataFrame from ERP
            unique_items_df: Unique found items from audit reports
            total_scanned: Total number of scans (including duplicates)
            
        Returns:
            Tuple of (found_items_report, missing_items_report, comparison_stats)
        """
        # Perform INNER JOIN to identify found items
        found_report = stock_df.merge(
            unique_items_df[['Label No']], 
            on='Label No', 
            how='inner'
        )
        
        # Perform LEFT JOIN with indicator to identify missing items
        comparison = stock_df.merge(
            unique_items_df[['Label No']], 
            on='Label No', 
            how='left',
            indicator=True
        )
        
        # Filter for missing items (items in stock but not found)
        missing_report = comparison[comparison['_merge'] == 'left_only'].copy()
        missing_report = missing_report.drop(columns=['_merge'])
        
        # Calculate statistics
        total_stock = len(stock_df)
        found_count = len(found_report)
        missing_count = len(missing_report)
        
        # Verify the math
        expected_missing = total_stock - total_scanned
        
        comparison_stats = {
            'total_stock': total_stock,
            'total_scanned': total_scanned,
            'found_in_stock': found_count,
            'missing': missing_count,
            'expected_missing': expected_missing
        }
        
        st.success(f"✓ Found items in stock: {found_count}")
        st.warning(f"⚠️ Missing items: {missing_count}")
        st.info(f"📊 Total scanned (including duplicates): {total_scanned}")
        st.info(f"📊 Expected missing (Stock - Total Scanned): {expected_missing}")
        
        return found_report, missing_report, comparison_stats
    
    @staticmethod
    def prepare_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare DataFrame for display with selected columns and formatting
        
        Args:
            df: DataFrame to prepare
            
        Returns:
            Formatted DataFrame for display
        """
        # Define columns to display (in order)
        display_columns = [
            'Label No', 'Item Name', 'Metal ID', 'Gross Wt.', 'Net Wt.', 
            'Pcs', 'Location', 'Old BarCode No', 'Remark', 'Voucher Date'
        ]
        
        # Keep only columns that exist
        available_cols = [col for col in display_columns if col in df.columns]
        display_df = df[available_cols].copy()
        
        # Fill NaN values for better display
        display_df = display_df.fillna('')
        
        return display_df
    
    @classmethod
    def process_audit_data(cls, stock_df: pd.DataFrame, barcode_df: pd.DataFrame, 
                          label_df: pd.DataFrame) -> dict:
        """
        Complete processing pipeline for audit data
        
        Args:
            stock_df: Total stock DataFrame
            barcode_df: Old barcode report DataFrame
            label_df: Label number report DataFrame
            
        Returns:
            Dictionary with processed reports
        """
        try:
            results = {}
            
            # Step 1: Merge audit reports
            st.subheader("📊 Step 1: Merging Audit Reports")
            merge_results = cls.merge_audit_reports(barcode_df, label_df)
            
            results['merged_found_items'] = merge_results['unique_items']
            results['duplicates'] = merge_results['duplicates']
            results['num_duplicates'] = merge_results['num_duplicates']
            
            # Step 2: Compare with stock
            st.subheader("🔍 Step 2: Comparing with Total Stock")
            found_report, missing_report, comparison_stats = cls.compare_with_stock(
                stock_df, 
                merge_results['unique_items'],
                merge_results['total_scanned']
            )
            
            # Step 3: Prepare display dataframes
            results['found_items'] = cls.prepare_display_dataframe(found_report)
            results['missing_items'] = cls.prepare_display_dataframe(missing_report)
            
            # Prepare duplicates report with available columns
            if not merge_results['duplicates'].empty:
                dup_display_cols = ['Label No', 'Item Name', 'Location', 'Source']
                available_dup_cols = [col for col in dup_display_cols if col in merge_results['duplicates'].columns]
                results['duplicates_display'] = merge_results['duplicates'][available_dup_cols].fillna('')
            else:
                results['duplicates_display'] = pd.DataFrame()
            
            # Summary statistics
            results['stats'] = {
                'total_stock': comparison_stats['total_stock'],
                'total_scanned': comparison_stats['total_scanned'],
                'unique_found': merge_results['unique_count'],
                'found_in_stock': comparison_stats['found_in_stock'],
                'missing': comparison_stats['missing'],
                'num_duplicates': merge_results['num_duplicates'],
                'found_percentage': round((comparison_stats['found_in_stock'] / comparison_stats['total_stock']) * 100, 2) if comparison_stats['total_stock'] > 0 else 0
            }
            
            # THIS WAS MISSING - RETURN THE RESULTS!
            return results
            
        except Exception as e:
            st.error(f"Error processing audit data: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return None
