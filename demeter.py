import streamlit as st
import pandas as pd
import re
import io

def clean_department_value(department):
    """
    Clean department value: convert to lowercase and remove special characters
    """
    if pd.isna(department) or department == "":
        return ""
    
    # Convert to string and lowercase
    cleaned = str(department).lower()
    
    # Remove special characters, keep only letters, numbers, and spaces
    cleaned = re.sub(r'[^a-z0-9\s]', '', cleaned)
    
    # Remove extra spaces and strip
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()

def to_camel_case(text):
    """
    Convert text to camelCase
    """
    if not text:
        return ""
    
    words = text.split()
    if not words:
        return ""
    
    # First word lowercase, rest title case
    camel_case = words[0].lower()
    for word in words[1:]:
        camel_case += word.capitalize()
    
    return camel_case

def to_camel_case_with_spaces(text):
    """
    Convert text to camelCase with spaces between words
    """
    if not text:
        return ""
    
    words = text.split()
    if not words:
        return ""
    
    # Convert each word: first letter uppercase, rest lowercase
    camel_case_words = []
    for word in words:
        if word:
            camel_case_words.append(word[0].upper() + word[1:].lower())
    
    return ' '.join(camel_case_words)

def extract_product_type(item_name, department):
    """
    Extract product type from item_name based on common product categories
    """
    if pd.isna(item_name):
        return ""
    
    item_lower = str(item_name).lower()
    
    # Common product types by category
    product_types = {
        'electronics': ['phone', 'smartphone', 'tablet', 'laptop', 'computer', 'monitor', 'tv', 'television', 
                       'headphones', 'earbuds', 'speaker', 'camera', 'watch', 'smartwatch', 'charger', 'cable'],
        'clothing': ['shirt', 'pants', 'dress', 'jacket', 'coat', 'sweater', 'hoodie', 'jeans', 'shorts', 
                    'skirt', 'blouse', 'top', 'tshirt', 't-shirt', 'polo', 'cardigan'],
        'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats', 'loafers', 'oxfords', 
                 'athletic', 'running', 'walking', 'dress shoes'],
        'home': ['chair', 'table', 'sofa', 'bed', 'mattress', 'pillow', 'blanket', 'curtain', 'lamp', 
                'mirror', 'rug', 'carpet', 'shelf', 'cabinet'],
        'beauty': ['cream', 'lotion', 'serum', 'cleanser', 'moisturizer', 'foundation', 'lipstick', 
                  'mascara', 'perfume', 'cologne', 'shampoo', 'conditioner'],
        'sports': ['ball', 'bat', 'racket', 'gloves', 'helmet', 'pad', 'equipment', 'gear', 'weights'],
        'kitchen': ['pan', 'pot', 'knife', 'spoon', 'fork', 'plate', 'bowl', 'cup', 'mug', 'blender', 
                   'mixer', 'toaster', 'microwave'],
        'toys': ['toy', 'doll', 'game', 'puzzle', 'blocks', 'car', 'truck', 'action figure', 'plush'],
        'books': ['book', 'novel', 'textbook', 'manual', 'guide', 'dictionary', 'encyclopedia'],
        'automotive': ['tire', 'battery', 'oil', 'filter', 'brake', 'light', 'mirror', 'seat', 'cover']
    }
    
    # Check department-specific product types first
    dept_lower = str(department).lower() if not pd.isna(department) else ""
    
    for category, types in product_types.items():
        if category in dept_lower:
            for product_type in types:
                if product_type in item_lower:
                    return product_type.title()
    
    # If no department match, check all product types
    for category, types in product_types.items():
        for product_type in types:
            if product_type in item_lower:
                return product_type.title()
    
    return ""

def extract_year_and_pack_info(item_name):
    """
    Extract year and pack information from item_name
    """
    if pd.isna(item_name):
        return "", ""
    
    item_str = str(item_name)
    
    # Extract year (4 digits, typically 20xx or 19xx)
    year_match = re.search(r'\b(19|20)\d{2}\b', item_str)
    year = year_match.group() if year_match else ""
    
    # Extract pack information (number + pack/count/piece/set)
    pack_patterns = [
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*count\b', 
        r'\b(\d+)\s*piece\b',
        r'\b(\d+)\s*set\b',
        r'\b(\d+)\s*pk\b',
        r'\b(\d+)\s*ct\b',
        r'\b(\d+)\s*pcs\b'
    ]
    
    pack_info = ""
    for pattern in pack_patterns:
        match = re.search(pattern, item_str.lower())
        if match:
            number = match.group(1)
            pack_type = re.search(pattern, item_str.lower()).group().split()[-1]
            pack_info = f"{number} {pack_type.title()}"
            break
    
    return year, pack_info

def extract_model_name(item_name, brand, department):
    """
    Extract model name from item_name by removing brand, department, color, size words
    and keeping only meaningful words including inches measurements, formatted in camelCase with spaces,
    with product type at the end and year/pack info at the very end
    """
    if pd.isna(item_name) or item_name == "":
        return ""
    
    # Convert to string for processing
    model_name = str(item_name)
    original_case = model_name  # Keep original for final processing
    model_name_lower = model_name.lower()
    
    # Extract year and pack info first (to be added at the end)
    year, pack_info = extract_year_and_pack_info(item_name)
    
    # Extract product type (to be added before year/pack)
    product_type = extract_product_type(item_name, department)
    
    # Remove year and pack info from processing (we'll add them back later)
    if year:
        model_name_lower = re.sub(r'\b' + re.escape(year) + r'\b', ' ', model_name_lower)
    
    # Remove pack info patterns
    pack_removal_patterns = [
        r'\b\d+\s*pack\b', r'\b\d+\s*count\b', r'\b\d+\s*piece\b',
        r'\b\d+\s*set\b', r'\b\d+\s*pk\b', r'\b\d+\s*ct\b', r'\b\d+\s*pcs\b'
    ]
    for pattern in pack_removal_patterns:
        model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Remove brand words if brand is provided
    if not pd.isna(brand) and str(brand).strip() != "":
        brand_words = str(brand).lower().split()
        for word in brand_words:
            if word.strip() and len(word.strip()) > 1:  # Skip single characters
                # Remove brand word (case insensitive, whole word only)
                pattern = r'\b' + re.escape(word.strip()) + r'\b'
                model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Remove department words if department is provided
    if not pd.isna(department) and str(department).strip() != "":
        dept_words = str(department).lower().split()
        for word in dept_words:
            if word.strip() and len(word.strip()) > 1:  # Skip single characters
                # Remove department word (case insensitive, whole word only)
                pattern = r'\b' + re.escape(word.strip()) + r'\b'
                model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Remove product type from main processing (we'll add it back at the end)
    if product_type:
        pattern = r'\b' + re.escape(product_type.lower()) + r'\b'
        model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Remove common color words
    color_words = [
        'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'white', 'gray', 'grey',
        'navy', 'maroon', 'teal', 'cyan', 'magenta', 'lime', 'olive', 'silver', 'gold', 'beige', 'tan', 'khaki',
        'crimson', 'scarlet', 'azure', 'turquoise', 'violet', 'indigo', 'coral', 'salmon', 'peach', 'mint',
        'rose', 'burgundy', 'emerald', 'ruby', 'sapphire', 'amber', 'ivory', 'cream', 'charcoal', 'slate',
        'multicolor', 'multicolored', 'multi-color', 'multi-colored', 'assorted', 'mixed', 'various'
    ]
    
    for color in color_words:
        pattern = r'\b' + re.escape(color) + r'\b'
        model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Remove common size words
    size_words = [
        'small', 'medium', 'large', 'extra', 'xl', 'xxl', 'xxxl', 'xs', 'sm', 'md', 'lg',
        'tiny', 'mini', 'big', 'huge', 'giant', 'jumbo', 'oversized', 'plus', 'petite',
        'regular', 'standard', 'compact', 'full', 'queen', 'king', 'twin', 'double',
        'narrow', 'wide', 'broad', 'thick', 'thin', 'slim', 'fat', 'skinny',
        'short', 'long', 'tall', 'low', 'high', 'deep', 'shallow'
    ]
    
    for size in size_words:
        pattern = r'\b' + re.escape(size) + r'\b'
        model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Remove common filler words that don't add meaning
    filler_words = [
        'for', 'with', 'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'from', 'by', 'of', 
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'ought',
        'men', 'women', 'mens', 'womens', 'man', 'woman', 'male', 'female', 'unisex',
        'adult', 'adults', 'kid', 'kids', 'child', 'children', 'baby', 'infant', 'toddler',
        'new', 'old', 'used', 'vintage', 'classic', 'modern', 'contemporary', 'traditional',
        'premium', 'deluxe', 'luxury', 'basic', 'standard', 'professional', 'commercial',
        'pack', 'set', 'kit', 'bundle', 'collection', 'series', 'model', 'type', 'style',
        'piece', 'pieces', 'item', 'product', 'brand', 'quality', 'grade', 'level'
    ]
    
    for filler in filler_words:
        pattern = r'\b' + re.escape(filler) + r'\b'
        model_name_lower = re.sub(pattern, ' ', model_name_lower)
    
    # Extract and preserve inches measurements before cleaning
    inches_patterns = re.findall(r'\b\d+\.?\d*\s*(?:inch|inches|in|")\b', model_name_lower)
    inches_measurements = []
    for pattern in inches_patterns:
        # Normalize inches format
        normalized = re.sub(r'\s*(?:inch|inches|in|")\b', ' Inch', pattern.strip())
        inches_measurements.append(normalized)
    
    # Clean up the result
    # Remove special characters but keep alphanumeric and spaces
    model_name_lower = re.sub(r'[^a-z0-9\s]', ' ', model_name_lower)
    
    # Remove extra spaces and split into words
    words = model_name_lower.split()
    
    # Filter out very short words (less than 2 characters) and numbers-only words
    meaningful_words = []
    for word in words:
        if len(word) >= 2 and not word.isdigit():
            meaningful_words.append(word)
        elif len(word) >= 2 and word.isdigit() and len(word) >= 3:  # Keep longer numbers (like model numbers)
            meaningful_words.append(word)
        elif re.match(r'^[a-z]+\d+$|^\d+[a-z]+$', word):  # Keep alphanumeric combinations
            meaningful_words.append(word)
    
    # Add back inches measurements
    meaningful_words.extend(inches_measurements)
    
    # Join the meaningful words
    result = ' '.join(meaningful_words).strip()
    
    # If result is too short or empty, try to extract from original with different approach
    if len(result) < 3:
        # Try to find model-like patterns (letters + numbers)
        model_patterns = re.findall(r'\b[a-zA-Z]*\d+[a-zA-Z]*\b|\b[a-zA-Z]+\d+\b|\b\d+[a-zA-Z]+\b', original_case)
        if model_patterns:
            result = ' '.join(model_patterns)
            # Add inches measurements if found
            if inches_measurements:
                result += ' ' + ' '.join(inches_measurements)
    
    # Build final model name with proper order
    final_parts = []
    
    # Add main model name (converted to camelCase with spaces)
    if result.strip():
        final_parts.append(to_camel_case_with_spaces(result.strip()))
    
    # Add product type
    if product_type:
        final_parts.append(product_type)
    
    # Add year
    if year:
        final_parts.append(year)
    
    # Add pack info
    if pack_info:
        final_parts.append(pack_info)
    
    # Join all parts with spaces
    final_result = ' '.join(final_parts)
    
    return final_result.strip()

def process_department_column(df, department_column):
    """
    Process the department column and fill the existing Final Department column
    """
    if department_column not in df.columns:
        st.error(f"Column '{department_column}' not found")
        return df
    
    # Check if Final Department column exists
    final_dept_columns = [col for col in df.columns if 'final' in col.lower() and 'department' in col.lower()]
    
    if not final_dept_columns:
        st.error("No 'Final Department' column found in the Excel file")
        st.info("Available columns: " + ", ".join(df.columns.tolist()))
        return df
    
    # Use the first matching Final Department column
    final_dept_column = final_dept_columns[0]
    st.info(f"Found and will update column: '{final_dept_column}'")
    
    # Create a copy of the dataframe
    result_df = df.copy()
    
    # Fill the existing Final Department column with cleaned values
    result_df[final_dept_column] = result_df[department_column].apply(clean_department_value)
    
    return result_df, final_dept_column

def process_model_name_extraction(df, item_name_column, brand_column, department_column):
    """
    Extract model names from item_name by removing brand and department words
    """
    # Check if required columns exist
    missing_columns = []
    if item_name_column not in df.columns:
        missing_columns.append(item_name_column)
    if brand_column not in df.columns:
        missing_columns.append(brand_column)
    if department_column not in df.columns:
        missing_columns.append(department_column)
    
    if missing_columns:
        st.error(f"Missing columns: {', '.join(missing_columns)}")
        return df
    
    # Create a copy of the dataframe
    result_df = df.copy()
    
    # Create model_name column
    result_df['model_name'] = ""
    
    # Extract model names
    for index, row in result_df.iterrows():
        item_name = row[item_name_column]
        brand = row[brand_column]
        department = row[department_column]
        
        model_name = extract_model_name(item_name, brand, department)
        result_df.at[index, 'model_name'] = model_name
    
    return result_df

def main():
    st.title("🌾 Demeter - Department & Model Name Processor")
    st.markdown("Clean department values and extract meaningful model names from item names")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Excel file with department, item_name, and brand columns",
        type=['xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        try:
            # Load the Excel file
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ Loaded {len(df)} rows from '{uploaded_file.name}'")
            
            # Show preview
            st.subheader("📊 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            
            # Column selection section
            st.subheader("🎯 Select Columns for Processing")
            
            # Check for Final Department column first
            final_dept_columns = [col for col in df.columns if 'final' in col.lower() and 'department' in col.lower()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Department Processing:**")
                
                if final_dept_columns:
                    st.success(f"✅ Found 'Final Department' column: '{final_dept_columns[0]}'")
                    
                    # Select source department column
                    dept_columns = []
                    for col in df.columns:
                        if any(keyword in col.lower() for keyword in ['department', 'dept', 'category', 'section']):
                            if 'final' not in col.lower():
                                dept_columns.append(col)
                    
                    if dept_columns:
                        department_column = st.selectbox("Select source department column:", dept_columns)
                    else:
                        available_columns = [col for col in df.columns if 'final' not in col.lower()]
                        department_column = st.selectbox("Select source department column:", available_columns)
                else:
                    st.error("❌ No 'Final Department' column found!")
                    department_column = None
            
            with col2:
                st.markdown("**Model Name Extraction:**")
                
                # Select item_name column
                item_name_columns = [col for col in df.columns if 'item' in col.lower() and 'name' in col.lower()]
                if item_name_columns:
                    item_name_column = st.selectbox("Select item_name column:", item_name_columns)
                else:
                    item_name_column = st.selectbox("Select item_name column:", df.columns.tolist())
                
                # Select brand column
                brand_columns = [col for col in df.columns if 'brand' in col.lower()]
                if brand_columns:
                    brand_column = st.selectbox("Select brand column:", brand_columns)
                else:
                    brand_column = st.selectbox("Select brand column:", df.columns.tolist())
            
            # Show sample model name extraction preview
            if all([item_name_column, brand_column, department_column]):
                st.subheader("🔍 Model Name Extraction Preview")
                st.markdown("See how model names will be extracted from item names:")
                
                sample_data = []
                for i in range(min(5, len(df))):
                    row = df.iloc[i]
                    item_name = row[item_name_column]
                    brand = row[brand_column]
                    dept = row[department_column]
                    
                    model_name = extract_model_name(item_name, brand, dept)
                    
                    sample_data.append({
                        'Item Name': str(item_name)[:60] + "..." if len(str(item_name)) > 60 else str(item_name),
                        'Brand': str(brand)[:20] + "..." if len(str(brand)) > 20 else str(brand),
                        'Department': str(dept)[:20] + "..." if len(str(dept)) > 20 else str(dept),
                        'Extracted Model (camelCase)': model_name if model_name else "(no meaningful words found)"
                    })
                
                sample_df = pd.DataFrame(sample_data)
                st.dataframe(sample_df, use_container_width=True)
                
                # Show extraction logic
                with st.expander("🔧 How Model Name Extraction Works"):
                    st.markdown("""
                    **The extraction process:**
                    1. **Remove brand words** from item name
                    2. **Remove department words** from item name  
                    3. **Remove color words** (red, blue, black, white, etc.)
                    4. **Remove size words** (small, medium, large, XL, etc.)
                    5. **Remove filler words** (for, with, and, the, etc.)
                    6. **Preserve inches measurements** (12 inch, 15", etc.)
                    7. **Keep meaningful words** (2+ characters, not just numbers)
                    8. **Prioritize alphanumeric combinations** (like model numbers)
                    9. **Format in camelCase** (firstWordSecond15inch)
                    
                    **Example:**
                    - Item: "Apple iPhone 13 Pro Max Red 128GB for Women Electronics"
                    - Brand: "Apple" 
                    - Department: "Electronics"
                    - Result: "iPhone13ProMax128gb" (removed Apple, Electronics, Red, for, Women)
                    
                    **With inches:**
                    - Item: "Samsung 55 inch Smart TV Black Electronics"
                    - Brand: "Samsung"
                    - Department: "Electronics" 
                    - Result: "55inchSmartTv" (preserved inches measurement)
                    """)
            
            # Processing section
            st.subheader("🚀 Process Data")
            
            if st.button("🔄 Process Both Department & Model Names", type="primary"):
                if department_column and all([item_name_column, brand_column]):
                    with st.spinner("Processing department values and extracting model names..."):
                        # First process department
                        dept_result = process_department_column(df, department_column)
                        
                        if isinstance(dept_result, tuple):
                            temp_df, final_dept_column = dept_result
                            
                            # Then process model names
                            result_df = process_model_name_extraction(temp_df, item_name_column, brand_column, department_column)
                            
                            st.success("🎉 Both department cleaning and model name extraction completed!")
                            
                            # Store results
                            st.session_state['result_df'] = result_df
                            st.session_state['original_filename'] = uploaded_file.name
                            st.session_state['final_dept_column'] = final_dept_column
                            st.session_state['source_dept_column'] = department_column
                            st.session_state['item_name_column'] = item_name_column
                            st.session_state['brand_column'] = brand_column
                            
                            # Show results
                            st.subheader("📊 Processing Results")
                            
                            # Show key columns
                            display_columns = [department_column, final_dept_column, item_name_column, brand_column, 'model_name']
                            available_display_columns = [col for col in display_columns if col in result_df.columns]
                            
                            st.dataframe(result_df[available_display_columns], use_container_width=True)
                            
                           
                            
                            # Show detailed comparison
                            st.subheader("📋 Detailed Before/After Comparison")
                            
                            # Create comparison dataframe
                            comparison_data = []
                            for i in range(min(20, len(result_df))):
                                row = result_df.iloc[i]
                                comparison_data.append({
                                    'Original Item Name': str(row[item_name_column])[:50] + "..." if len(str(row[item_name_column])) > 50 else str(row[item_name_column]),
                                    'Brand': str(row[brand_column]),
                                    'Department': str(row[department_column]),
                                    'Cleaned Department': str(row[final_dept_column]),
                                    'Extracted Model (camelCase)': str(row['model_name']) if row['model_name'] else "(empty)"
                                })
                            
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True)
                        
                        else:
                            st.error("Failed to process department values")
                else:
                    st.error("Please select all required columns")
            
            # Download section
            if 'result_df' in st.session_state:
                st.subheader("💾 Download Processed Files")
                st.markdown("---")
                
                result_df = st.session_state['result_df']
                original_filename = st.session_state['original_filename']
                final_dept_column = st.session_state['final_dept_column']
                source_dept_column = st.session_state['source_dept_column']
                item_name_column = st.session_state['item_name_column']
                brand_column = st.session_state['brand_column']
                
                st.success("✅ Both department cleaning and model name extraction completed!")
                
                # Create download buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Excel download - Complete file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        result_df.to_excel(writer, sheet_name='Processed_Data', index=False)
                        
                        # Add summary sheet
                        total_rows = len(result_df)
                        dept_filled = len(result_df[result_df[final_dept_column] != ""])
                        model_filled = len(result_df[result_df['model_name'] != ""])
                        
                        summary_data = {
                            'Metric': [
                                'Total Rows', 
                                'Departments Cleaned', 
                                'Models Extracted',
                                'Department Success Rate',
                                'Model Success Rate',
                                'Source Department Column',
                                'Final Department Column',
                                'Item Name Column',
                                'Brand Column',
                                'Processing Date'
                            ],
                            'Value': [
                                total_rows,
                                dept_filled,
                                model_filled,
                                f"{(dept_filled/total_rows*100):.1f}%" if total_rows > 0 else "0%",
                                f"{(model_filled/total_rows*100):.1f}%" if total_rows > 0 else "0%",
                                source_dept_column,
                                final_dept_column,
                                item_name_column,
                                brand_column,
                                pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                            ]
                        }
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Processing_Summary', index=False)
                        
                        # Add model name analysis sheet
                        model_analysis = result_df[['model_name']].copy()
                        model_analysis['model_length'] = model_analysis['model_name'].str.len()
                        model_analysis['has_model'] = model_analysis['model_name'] != ""
                        model_analysis.to_excel(writer, sheet_name='Model_Analysis', index=False)
                    
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="📥 Download Complete Excel File",
                        data=excel_data,
                        file_name=f"processed_{original_filename.split('.')[0]}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download complete file with cleaned departments and extracted model names"
                    )
                
                with col2:
                    # CSV download - Complete file
                    csv_data = result_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Complete CSV File",
                        data=csv_data,
                        file_name=f"processed_{original_filename.split('.')[0]}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download complete file as CSV"
                    )
                
                with col3:
                    # Download only model names
                    model_only_df = result_df[['model_name']].copy()
                    model_csv = model_only_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Model Names Only",
                        data=model_csv,
                        file_name=f"model_names_only_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download only the extracted model names"
                    )
                
                # Additional download options
                st.markdown("**Additional Downloads:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download department comparison
                    dept_comparison = result_df[[source_dept_column, final_dept_column]].copy()
                    dept_comparison.columns = ['Original_Department', 'Cleaned_Department']
                    dept_csv = dept_comparison.to_csv(index=False)
                    st.download_button(
                        label="📥 Department Comparison",
                        data=dept_csv,
                        file_name=f"department_comparison_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download before/after department comparison"
                    )
                
                with col2:
                    # Download extraction details
                    extraction_details = result_df[[item_name_column, brand_column, source_dept_column, 'model_name']].copy()
                    extraction_details.columns = ['Item_Name', 'Brand', 'Department', 'Extracted_Model']
                    extraction_csv = extraction_details.to_csv(index=False)
                    st.download_button(
                        label="📥 Extraction Details",
                        data=extraction_csv,
                        file_name=f"extraction_details_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download item name to model name extraction details"
                    )
                
                # Show final preview
                st.subheader("🎯 Final Results Preview")
                
                # Show key columns in final preview
                final_preview_columns = [source_dept_column, final_dept_column, item_name_column, brand_column, 'model_name']
                available_preview_columns = [col for col in final_preview_columns if col in result_df.columns]
                
                st.dataframe(result_df[available_preview_columns].head(20), use_container_width=True)
                
                # Show file info
                st.info(f"📁 All files saved with timestamp: {pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}")
        
        except Exception as e:
            st.error(f"❌ Error reading the Excel file: {str(e)}")
            st.info("Please make sure the file is a valid Excel file (.xlsx or .xls)")
    
    else:
        st.info("👆 Please upload an Excel file to get started")
        
        # Show example of what the processing does
        st.subheader("📋 Expected File Structure")
        st.markdown("""
        **Your Excel file should have:**
        - A source department column (e.g., 'Department', 'Category')
        - A 'Final Department' column (will be filled with cleaned values)
        - An item name column (e.g., 'Item Name', 'Product Name')
        - A brand column (e.g., 'Brand', 'Manufacturer')
        """)
        
        

if __name__ == "__main__":
    main()