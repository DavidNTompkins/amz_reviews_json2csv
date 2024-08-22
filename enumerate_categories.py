import csv
import ast
from collections import Counter
import logging

logging.basicConfig(filename='category_extraction.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def safe_eval(expr):
    try:
        return ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        return expr

def extract_categories(csv_file):
    categories = set()
    category_counter = Counter()
    problematic_entries = []

    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                category_field = row.get('categories', '[]')
                evaluated_field = safe_eval(category_field)

                if isinstance(evaluated_field, list):
                    for category in evaluated_field:
                        categories.add(category)
                        category_counter[category] += 1
                elif isinstance(evaluated_field, str):
                    # Handle case where it's a single string (not in a list)
                    categories.add(evaluated_field)
                    category_counter[evaluated_field] += 1
                else:
                    problematic_entries.append((row_num, category_field))
                    logging.warning(f"Unexpected category format in row {row_num}: {category_field}")

    except IOError as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        return None, None, None

    return sorted(list(categories)), category_counter, problematic_entries

def save_categories(categories, category_counter, problematic_entries):
    try:
        with open('all_categories.txt', 'w', encoding='utf-8') as f:
            for category in categories:
                f.write(f"{category}\n")
        logging.info("All categories saved to 'all_categories.txt'")

        with open('top_categories.txt', 'w', encoding='utf-8') as f:
            f.write("Top 100 most common categories:\n")
            for category, count in category_counter.most_common(100):
                f.write(f"{category}: {count}\n")
        logging.info("Top 100 categories saved to 'top_categories.txt'")

        with open('category_stats.txt', 'w', encoding='utf-8') as f:
            f.write(f"Total number of unique categories: {len(categories)}\n")
            f.write(f"Total number of category assignments: {sum(category_counter.values())}\n")
            f.write(f"Number of problematic entries: {len(problematic_entries)}\n")
        logging.info("Category statistics saved to 'category_stats.txt'")

        if problematic_entries:
            with open('problematic_entries.txt', 'w', encoding='utf-8') as f:
                for row_num, entry in problematic_entries:
                    f.write(f"Row {row_num}: {entry}\n")
            logging.info("Problematic entries saved to 'problematic_entries.txt'")

    except IOError as e:
        logging.error(f"Error writing to file: {str(e)}")

def main():
    csv_file = 'amazon_reviews_with_metadata.csv'
    categories, category_counter, problematic_entries = extract_categories(csv_file)

    if categories is not None:
        save_categories(categories, category_counter, problematic_entries)
        logging.info("Category extraction completed successfully.")
    else:
        logging.error("Failed to extract categories.")

if __name__ == "__main__":
    main()