import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import Counter
from utils import get_cleaned_dataframe_from_csv, Color

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

# Aggregating contributions for each category based on source title
def aggregate_contributions_and_h_index(data, top_n=10):
    ignored_agriculture = data[data['IsAgriculture'] & (data['Source title'].isna() | data['Cited by'].isna())].shape[0]
    ignored_non_agriculture = data[~data['IsAgriculture'] & (data['Source title'].isna() | data['Cited by'].isna())].shape[0]
    print(f"Ignored agriculture documents due to missing data: {ignored_agriculture}")
    print(f"Ignored non-agriculture documents due to missing data: {ignored_non_agriculture}")

    # Calculate H-index for each source title
    total_h_index = data.groupby('Source title')['Cited by'].apply(lambda x: calculate_h_index(list(x))).to_dict()
    agric_h_index = data[data['IsAgriculture']].groupby('Source title')['Cited by'].apply(lambda x: calculate_h_index(list(x))).to_dict()
    non_agric_h_index = data[~data['IsAgriculture']].groupby('Source title')['Cited by'].apply(lambda x: calculate_h_index(list(x))).to_dict()

    # Count total, agricultural, and non-agricultural publications for each source
    total_counts = Counter(data['Source title'])
    agric_counts = Counter(data[data['IsAgriculture']]['Source title'])
    non_agric_counts = Counter(data[~data['IsAgriculture']]['Source title'])

    # Select top N sources based on total counts
    top_sources = dict(sorted(total_counts.items(), key=lambda x: x[1], reverse=True)[:top_n])

    # Gather counts and H-index for top sources
    top_data = {
        (source[:50] + '...' if len(source) > 50 else source) : {  # Truncate source title to 50 characters
            'total': total_counts[source],
            'agric': agric_counts.get(source, 0),
            'non_agric': non_agric_counts.get(source, 0),
            'total_h_index': total_h_index.get(source, 0),
            'agric_h_index': agric_h_index.get(source, 0),
            'non_agric_h_index': non_agric_h_index.get(source, 0),
        } for source in top_sources
    }
    
    # Print details for top authors
    for source, values in top_data.items():
        print(f"{source}: Total={values['total']}, Agriculture={values['agric']}, Non-Agriculture={values['non_agric']}, "
              f"Total H-index={values['total_h_index']}, Agriculture H-index={values['agric_h_index']}, Non-Agriculture H-index={values['non_agric_h_index']}")

    return top_data

top_n = 15
top_sources_data = aggregate_contributions_and_h_index(data, top_n)

# Plotting function for sources and their H-index
def plot_top_sources_data(top_sources_data, title, output_filename):
    sources = list(top_sources_data.keys())
    y = np.arange(len(sources))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plotting the total, agricultural, and non-agricultural publications
    ax.barh(y - 0.2, [top_sources_data[source]['total'] for source in sources], 0.2, color=Color.GENERAL.value, label='Total Publications')
    ax.barh(y, [top_sources_data[source]['agric'] for source in sources], 0.2, color=Color.AGRICULTURE.value, label='Agricultural')
    ax.barh(y + 0.2, [top_sources_data[source]['non_agric'] for source in sources], 0.2, color=Color.NON_AGRICULTURE.value, label='Non-Agricultural')

    # Add H-index markers
    for i, source in enumerate(sources):
        ax.plot(top_sources_data[source]['total_h_index'], y[i] - 0.2, 'k_', markersize=3, markeredgewidth=8)
        ax.plot(top_sources_data[source]['agric_h_index'], y[i], 'k_', markersize=3, markeredgewidth=8)
        ax.plot(top_sources_data[source]['non_agric_h_index'], y[i] + 0.2, 'k_', markersize=3, markeredgewidth=8)
    
    ax.set_xlabel('Count')
    ax.set_ylabel('Source')
    ax.set_title(title)
    ax.set_yticks(y)
    ax.set_yticklabels(sources)

    # Use a proxy artist for H-index legend entry
    handles, labels = ax.get_legend_handles_labels()
    h_index_legend = Line2D([0], [0], color='k', marker='_', linestyle='None', markersize=10, label='H-index')
    handles.append(h_index_legend)  # Add the custom legend entry
    ax.legend(handles=handles)

    plt.tight_layout()
    plt.savefig(f"{output_path}/{output_filename}.png")
    plt.close()

plot_top_sources_data(top_sources_data, 'Top Journals: Publications and H-index', 'top_journals_h_index')
