import csv
import ast
import logging

logging.basicConfig(filename='csv_filter.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def safe_eval(expr):
    try:
        return ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        return expr

def read_categories(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def filter_csv(input_csv, output_csv, categories):
    try:
        with open(input_csv, 'r', newline='', encoding='utf-8') as infile, \
             open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                category_field = row.get('categories', '[]')
                evaluated_field = safe_eval(category_field)
                
                if isinstance(evaluated_field, list):
                    row_categories = set(evaluated_field)
                elif isinstance(evaluated_field, str):
                    row_categories = {evaluated_field}
                else:
                    logging.warning(f"Unexpected category format: {category_field}")
                    continue
                
                if row_categories & categories:  # Check for any intersection
                    writer.writerow(row)
        
        logging.info(f"Filtered CSV saved to {output_csv}")
    
    except IOError as e:
        logging.error(f"Error processing CSV file: {str(e)}")

def main():
    categories_file = 'spatial.txt'
    input_csv = 'amazon_reviews_with_metadata.csv'
    output_csv = 'filtered_amazon_reviews_spatial.csv'
    
    categories = read_categories(categories_file)
    filter_csv(input_csv, output_csv, categories)
    logging.info("CSV filtering completed successfully.")

if __name__ == "__main__":
    main()