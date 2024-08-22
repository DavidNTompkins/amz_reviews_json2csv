import csv
import os
from collections import defaultdict
from tqdm import tqdm

def clean_filename(filename):
    """Clean the filename to make it suitable for file systems."""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_')).rstrip()

def split_csv_by_category(input_file):
    # Dictionary to store file handlers for each category
    category_files = {}
    # Dictionary to store writers for each category
    category_writers = {}
    # Counter for rows in each category
    category_counters = defaultdict(int)

    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            total_rows = sum(1 for row in csvfile)  # Count total rows for tqdm
            csvfile.seek(0)  # Reset file pointer
            next(reader)  # Skip header row

            for row in tqdm(reader, total=total_rows - 1, desc="Processing rows"):
                categories = eval(row.get('categories', '[]'))
                if not categories:
                    categories = ['Uncategorized']

                for category in categories:
                    clean_category = clean_filename(category)
                    if clean_category not in category_files:
                        # Create new file for this category
                        category_files[clean_category] = open(f"{clean_category}.csv", 'w', newline='', encoding='utf-8')
                        category_writers[clean_category] = csv.DictWriter(category_files[clean_category], fieldnames=reader.fieldnames)
                        category_writers[clean_category].writeheader()

                    # Write the row to the appropriate category file
                    category_writers[clean_category].writerow(row)
                    category_counters[clean_category] += 1

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close all open file handlers
        for file in category_files.values():
            file.close()

    # Print summary
    print("\nCategory-wise file creation summary:")
    for category, count in category_counters.items():
        print(f"{category}: {count} rows")

if __name__ == "__main__":
    input_file = 'amazon_reviews_with_metadata.csv'
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
    else:
        split_csv_by_category(input_file)
        print("CSV splitting complete.")