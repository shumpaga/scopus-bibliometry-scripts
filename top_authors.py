import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import Counter
from utils import get_cleaned_dataframe_from_csv, Color

# Assuming the dataset has a 'Cited by' column for each publication
# Load the CSV file
file_path = '../data/scopus.csv'
output_path = '../data/'
data = pd.read_csv(file_path)

data = get_cleaned_dataframe_from_csv(file_path)

# Function to calculate the H-index for a list of citation counts
def calculate_h_index(citations):
    citations.sort(reverse=True)
    h_index = 0
    for citation in citations:
        if citation >= h_index + 1:
            h_index += 1
        else:
            break
    return h_index

# Aggregating contributions for each category
def aggregate_contributions_and_h_index(data, top_n=10):
    # Expand author columns into separate rows and keep 'Cited by' for H-index calculation
    expanded_data = data[['Authors', 'Cited by', 'IsAgriculture']].dropna(subset=['Authors']).copy()
    expanded_data['Authors'] = expanded_data['Authors'].str.split('; ')
    expanded_data = expanded_data.explode('Authors')

    ignored_agriculture = data[data['IsAgriculture'] & (data['Authors'].isna() | data['Cited by'].isna())].shape[0]
    ignored_non_agriculture = data[~data['IsAgriculture'] & (data['Authors'].isna() | data['Cited by'].isna())].shape[0]
    print(f"Ignored agriculture documents due to missing data: {ignored_agriculture}")
    print(f"Ignored non-agriculture documents due to missing data: {ignored_non_agriculture}")

    # Calculate H-index for each author
    total_h_index = expanded_data.groupby('Authors')['Cited by'].apply(lambda x: calculate_h_index(list(x))).to_dict()
    agric_h_index = expanded_data[expanded_data['IsAgriculture']].groupby('Authors')['Cited by'].apply(lambda x: calculate_h_index(list(x))).to_dict()
    non_agric_h_index = expanded_data[~expanded_data['IsAgriculture']].groupby('Authors')['Cited by'].apply(lambda x: calculate_h_index(list(x))).to_dict()

    # Count total, agricultural, and non-agricultural publications for each author
    total_counts = Counter(expanded_data['Authors'])
    agric_counts = Counter(expanded_data[expanded_data['IsAgriculture']]['Authors'])
    non_agric_counts = Counter(expanded_data[~expanded_data['IsAgriculture']]['Authors'])

    # Select top N authors based on total counts
    top_authors = dict(sorted(total_counts.items(), key=lambda x: x[1], reverse=True)[:top_n])

    # Gather counts and H-index for top authors
    top_data = {
        author: {
            'total': total_counts[author],
            'agric': agric_counts.get(author, 0),
            'non_agric': non_agric_counts.get(author, 0),
            'total_h_index': total_h_index.get(author, 0),
            'agric_h_index': agric_h_index.get(author, 0),
            'non_agric_h_index': non_agric_h_index.get(author, 0),
        } for author in top_authors
    }

    # Print details for top authors
    for author, values in top_data.items():
        print(f"{author}: Total={values['total']}, Agriculture={values['agric']}, Non-Agriculture={values['non_agric']}, "
              f"Total H-index={values['total_h_index']}, Agriculture H-index={values['agric_h_index']}, Non-Agriculture H-index={values['non_agric_h_index']}")

    return top_data

top_n = 30
top_authors_data = aggregate_contributions_and_h_index(data, top_n)

# Plotting function for authors and their H-index
def plot_top_authors_data(top_authors_data, title, output_filename):
    authors = list(top_authors_data.keys())
    x = np.arange(len(authors))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plotting the total, agricultural, and non-agricultural publications
    ax.bar(x - 0.2, [top_authors_data[author]['total'] for author in authors], 0.2, color=Color.GENERAL.value, label='Total Publications')
    ax.bar(x, [top_authors_data[author]['agric'] for author in authors], 0.2, color=Color.AGRICULTURE.value, label='Agricultural')
    ax.bar(x + 0.2, [top_authors_data[author]['non_agric'] for author in authors], 0.2, color=Color.NON_AGRICULTURE.value, label='Non-Agricultural')

    # Add H-index markers and create a single legend entry for all H-indices
    for i, author in enumerate(authors):
        ax.plot(x[i] - 0.2, top_authors_data[author]['total_h_index'], 'k_', markersize=15, markeredgewidth=3)
        ax.plot(x[i], top_authors_data[author]['agric_h_index'], 'k_', markersize=15, markeredgewidth=3)
        ax.plot(x[i] + 0.2, top_authors_data[author]['non_agric_h_index'], 'k_', markersize=15, markeredgewidth=3)
    
    ax.set_xlabel('Author')
    ax.set_ylabel('Count')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(authors, rotation=45, ha="right")

    # Use a proxy artist for H-index legend entry
    handles, labels = ax.get_legend_handles_labels()
    h_index_legend = Line2D([0], [0], color='k', marker='_', linestyle='None', markersize=10, label='H-index')
    handles.append(h_index_legend)  # Add the custom legend entry
    ax.legend(handles=handles)

    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"{output_path}/{output_filename}.png")
    plt.close()

plot_top_authors_data(top_authors_data, 'Top Authors: Publications and H-index', 'top_authors_h_index')
