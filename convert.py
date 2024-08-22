import datasets
import csv
import json
from tqdm import tqdm

def load_dataset_safely(name, subset, **kwargs):
    try:
        return datasets.load_dataset(name, subset, **kwargs)
    except Exception as e:
        print(f"Error loading dataset {name} - {subset}: {str(e)}")
        return None

def process_datasets():
    # Suppress unnecessary outputs
    datasets.logging.set_verbosity_error()

    # Load the review dataset
    review_dataset = load_dataset_safely("McAuley-Lab/Amazon-Reviews-2023", "raw_review_Toys_and_Games", trust_remote_code=True)
    if review_dataset is None:
        return

    # Load the metadata dataset
    meta_dataset = load_dataset_safely("McAuley-Lab/Amazon-Reviews-2023", "raw_meta_Toys_and_Games", split="full", trust_remote_code=True)
    if meta_dataset is None:
        return

    # Create a dictionary to store metadata indexed by parent_asin
    meta_dict = {item['parent_asin']: item for item in meta_dataset}

    # Prepare the output CSV file
    output_file = 'amazon_reviews_with_metadata.csv'

    # Get all field names from both datasets
    review_fields = list(review_dataset['full'].features.keys())
    meta_fields = list(meta_dataset.features.keys())

    # Remove duplicate fields and sort
    all_fields = sorted(set(review_fields + meta_fields))

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fields)
            writer.writeheader()

            # Iterate through the review dataset
            for review in tqdm(review_dataset['full'], desc="Processing reviews"):
                try:
                    # Create a dictionary for the current row
                    row = {field: review.get(field, '') for field in review_fields}
                    
                    # Get metadata for the current review using parent_asin
                    meta = meta_dict.get(review['parent_asin'], {})
                    
                    # Add metadata to the row
                    for field in meta_fields:
                        if field not in row:
                            value = meta.get(field, '')
                            # Handle potential JSON strings in metadata
                            if field == 'details' and isinstance(value, str):
                                try:
                                    value = json.dumps(json.loads(value))
                                except json.JSONDecodeError:
                                    pass
                            row[field] = value

                    # Write the row to the CSV file
                    writer.writerow(row)
                except Exception as e:
                    print(f"Error processing review: {str(e)}")
                    continue

        print(f"CSV file '{output_file}' has been created successfully.")
    except IOError as e:
        print(f"IOError while writing to CSV: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    process_datasets()