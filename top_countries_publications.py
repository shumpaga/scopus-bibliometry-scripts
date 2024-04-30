import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from utils import get_cleaned_dataframe_from_csv, Color, extract_countries

# Load the CSV file
file_path = '../data/scopus.csv'
output_path = '../data/'
data = get_cleaned_dataframe_from_csv(file_path)

# Example usage:
data['Country'] = data['Affiliations'].apply(extract_countries)

# Print the number of ignored rows due to missing countries
print(f"Ignored documents dut to missing affiliation (countries): {data['Country'].isna().sum()}")

# Remove rows with missing countries
data = data.dropna(subset=['Country'])

# Aggregating contributions for each country
def aggregate_contributions(data, top_n=10):
    # Explode the country list into separate rows
    exploded_data = data.explode('Country')
    
    # Count total, agricultural, and non-agricultural publications for each country
    total_counts = Counter(exploded_data['Country'])
    agric_counts = Counter(exploded_data[exploded_data['IsAgriculture']]['Country'])
    non_agric_counts = Counter(exploded_data[~exploded_data['IsAgriculture']]['Country'])

    # Select top N countries based on total counts
    top_countries = dict(sorted(total_counts.items(), key=lambda x: x[1], reverse=True)[:top_n])

    # Gather counts for top countries
    top_data = {
        country: {
            'total': total_counts[country],
            'agric': agric_counts.get(country, 0),
            'non_agric': non_agric_counts.get(country, 0),
        } for country in top_countries
    }

    # Print details for top countries
    for country, values in top_data.items():
        print(f"{country}: Total={values['total']}, Agriculture={values['agric']}, Non-Agriculture={values['non_agric']}")

    return top_data

top_n = 15
top_countries_data = aggregate_contributions(data, top_n)

# Plotting function for countries and their publication counts
def plot_top_countries_data(top_countries_data, title, output_filename):
    countries = list(top_countries_data.keys())
    x = np.arange(len(countries))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plotting the total, agricultural, and non-agricultural publications
    ax.barh(x - 0.2, [top_countries_data[country]['total'] for country in countries], 0.2, color=Color.GENERAL.value, label='Total Publications')
    ax.barh(x, [top_countries_data[country]['agric'] for country in countries], 0.2, color=Color.AGRICULTURE.value, label='Agricultural')
    ax.barh(x + 0.2, [top_countries_data[country]['non_agric'] for country in countries], 0.2, color=Color.NON_AGRICULTURE.value, label='Non-Agricultural')
    
    ax.set_xlabel('Publications')
    ax.set_title(title)
    ax.set_yticks(x)
    ax.set_yticklabels(countries)

    ax.legend()

    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"{output_path}/{output_filename}.png")
    plt.close()

plot_top_countries_data(top_countries_data, 'Top Countries: Publications by Research Focus', 'top_countries_publications')
