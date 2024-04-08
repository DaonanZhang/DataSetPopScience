import os
import csv
import nltk
from nltk.tokenize import word_tokenize
from textstat import flesch_reading_ease

# Download NLTK data if not already downloaded
nltk.download('punkt')

def analyze_corpus(folder_path):
    file_results = {}

    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)  # Skip header row
                term_results = []

                # Analyze each row in the CSV file
                for row in csvreader:
                    term = row[0]
                    explanation = row[1]

                    # Count
                    word_count = len(word_tokenize(explanation))

                    # Readability score
                    readability_score = flesch_reading_ease(explanation)

                    # Complexity of the word / Simplicity of the explanation
                    term_complexity = len(term.split())
                    explanation_complexity = word_count

                    term_results.append((term, word_count, readability_score, term_complexity / explanation_complexity))

                file_results[filename] = term_results

    return file_results

def main():
    data_folder = "data"
    corpus_analysis = analyze_corpus(data_folder)

    with open("lexical_analysis_results.txt", "w") as output_file:
        for filename, term_results in corpus_analysis.items():
            output_file.write(f"Analysis for {filename}:\n")
            total_count = 0
            total_explanation_length = 0
            total_readability_score = 0
            total_complexity_ratio = 0

            for term, word_count, readability_score, complexity_ratio in term_results:
                total_count += 1
                total_explanation_length += word_count
                total_readability_score += readability_score
                total_complexity_ratio += complexity_ratio

            avg_explanation_length = total_explanation_length / total_count
            avg_readability_score = total_readability_score / total_count
            avg_complexity_ratio = total_complexity_ratio / total_count

            output_file.write(f"Total terms: {total_count}\n")
            output_file.write(f"Avg. length of explanation: {avg_explanation_length:.2f} words\n")
            output_file.write(f"Avg. readability score: {avg_readability_score:.2f}\n")
            output_file.write(f"Avg. complexity ratio: {avg_complexity_ratio:.2f}\n\n")

if __name__ == "__main__":
    main()
