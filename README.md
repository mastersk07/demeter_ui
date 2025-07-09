# demeter_ui
🌾 Demeter - Department & Model Name Processor
Overview
Demeter is a Streamlit-based web application designed to clean department data and extract meaningful model names from product item names. It's particularly useful for e-commerce data processing, inventory management, and product catalog standardization.

How It Works
1. File Upload & Data Loading
Upload Excel files (.xlsx or .xls) containing product data
Automatically loads and displays a preview of your data (first 10 rows)
Shows total number of rows loaded
2. Column Selection & Validation
The app intelligently identifies and helps you select the required columns:

Department Processing:

Automatically detects "Final Department" columns (looks for columns containing "final" and "department")
Helps you select the source department column to clean
Shows success/error messages for column detection
Model Name Extraction:

Auto-detects item name columns (containing "item" and "name")
Auto-detects brand columns (containing "brand")
Allows manual selection if auto-detection fails
3. Preview & Processing Logic
Model Name Extraction Preview:

Shows a sample of how model names will be extracted from the first 5 rows
Displays before/after comparison in a table format
Includes an expandable section explaining the extraction logic
Extraction Process:

Removes brand words from item names
Removes department words from item names
Removes color words (red, blue, black, white, etc.)
Removes size words (small, medium, large, XL, etc.)
Removes filler words (for, with, and, the, etc.)
Preserves inches measurements (12 inch, 15", etc.)
Keeps meaningful words (2+ characters, not just numbers)
Prioritizes alphanumeric combinations (model numbers)
Formats in camelCase with spaces (First Word Second)
Adds product type, year, and pack info at the end
4. Data Processing
When you click "🔄 Process Both Department & Model Names":

Department Cleaning:

Converts to lowercase
Removes special characters
Removes extra spaces
Fills the existing "Final Department" column
Model Name Extraction:

Creates a new "model_name" column
Applies the extraction logic to each row
Handles missing/empty values gracefully
5. Results Display
After processing, you'll see:

Processing Results: Key columns showing original and processed data
Detailed Before/After Comparison: First 20 rows with side-by-side comparison
Success confirmation with processing statistics
6. Download Options
Multiple download formats available:

Main Downloads:

Complete Excel File: All data with multiple sheets (processed data, summary, analysis)
Complete CSV File: All processed data in CSV format
Model Names Only: Just the extracted model names
Additional Downloads:

Department Comparison: Before/after department cleaning
Extraction Details: Item name to model name mapping
7. File Structure Requirements
Your Excel file should contain:

A source department column (e.g., 'Department', 'Category')
A 'Final Department' column (will be filled with cleaned values)
An item name column (e.g., 'Item Name', 'Product Name')
A brand column (e.g., 'Brand', 'Manufacturer')
Example Workflow
Input Item: "Apple iPhone 13 Pro Max Red 128GB for Women Electronics"
Brand: "Apple"
Department: "Electronics"

Processing Steps:
1. Remove "Apple" (brand)
2. Remove "Electronics" (department)
3. Remove "Red" (color)
4. Remove "for", "Women" (filler words)
5. Keep meaningful words: "iPhone", "13", "Pro", "Max", "128GB"
6. Format: "IPhone 13 Pro Max 128gb"
7. Add product type: "IPhone 13 Pro Max 128gb Phone"



Key Features
Intelligent Column Detection: Automatically finds relevant columns
Preview Before Processing: See results before committing
Comprehensive Cleaning: Removes noise while preserving important information
Multiple Export Formats: Excel, CSV, and specialized exports
Processing Summary: Detailed statistics and success rates
Error Handling: Graceful handling of missing data and edge cases
User-Friendly Interface: Clear instructions and visual feedback
Use Cases
E-commerce Catalog Cleaning: Standardize product names and departments
Inventory Management: Extract clean model names for better organization
Data Migration: Clean data before importing to new systems
Product Matching: Create standardized identifiers for product matching
Analytics Preparation: Clean data for better reporting and analysis
The app is designed to handle large datasets efficiently while providing transparency into the processing logic and results.


