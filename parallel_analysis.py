import os
import pandas as pd

def extract_score(score_str):
    score_index = score_str.find("score:")
    if score_index != -1:
        score_str = score_str[score_index + len("score:"):]
        score_str = score_str.split(',')[0].strip()
        return float(score_str)
    else:
        return 0

def calculate_statistics(csv_file):
    df = pd.read_csv(csv_file)

    count = len(df)
    unique_terms = set()
    total_abstract_length = 0
    total_full_text_length = 0
    total_similarity_score = df['simirality'].sum()
    total_fk_score = df['fk_score'].apply(extract_score).sum()
    total_ari_score = df['ari_score'].apply(extract_score).sum()

    for abstract in df['abstract']:
        total_abstract_length += len(abstract.split())
        unique_terms.update(abstract.split())

    # Fill NaN values in 'article_full_text' with an empty string
    df['article_full_text'] = df['article_full_text'].fillna('')

    for full_text in df['article_full_text']:
        total_full_text_length += len(full_text.split())

    # Calculate average abstract length
    avg_abstract_length = total_abstract_length / count if count != 0 else 0

    # Calculate average full-text length
    avg_full_text_length = total_full_text_length / count if count != 0 else 0

    # Count unique terms
    num_unique_terms = len(unique_terms)

    return {
        "File": os.path.basename(csv_file),
        "Count": count,
        "Unique terms": num_unique_terms,
        "Total terms": total_abstract_length + total_full_text_length,
        "Avg. article abstract length": avg_abstract_length,
        "Avg. article full-text length": avg_full_text_length,
        "Avg. similarity score": total_similarity_score / count if count != 0 else 0,
        "Avg. FK score": total_fk_score / count if count != 0 else 0,
        "Avg. ARI score": total_ari_score / count if count != 0 else 0
    }

def write_statistics(statistics, output_file):
    with open(output_file, "a") as file:
        file.write(f"File: {statistics['File']}\n")
        for key, value in statistics.items():
            if key != "File":
                file.write(f"{key}: {value}\n")
        file.write("\n")

# Directory containing CSV files
data_dir = "data_parallel"
output_filename = "parallel_analysis_results.txt"

# Iterate through each file in the directory
for filename in os.listdir(data_dir):
    if filename.endswith(".csv"):
        csv_file = os.path.join(data_dir, filename)
        
        # Calculate statistics
        statistics = calculate_statistics(csv_file)

        # Write statistics to the text file
        write_statistics(statistics, output_filename)
