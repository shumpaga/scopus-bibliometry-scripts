import numpy as np
import matplotlib.pyplot as plt
from utils import get_cleaned_dataframe_from_csv, Color, extract_countries

# Load the CSV file
file_path = '../data/scopus.csv'
output_path = '../data/'

# Assuming that the 'Cited by' column represents the citation counts
data = get_cleaned_dataframe_from_csv(file_path)

# Use the existing function for extracting countries, modified to handle multiple countries per affiliation correctly
data['Country'] = data['Affiliations'].apply(extract_countries)

# Print the number of ignored rows due to missing countries
print(f"Ignored documents dut to missing affiliation (countries): {data['Country'].isna().sum()}")

# Remove rows with missing countries
data = data.dropna(subset=['Country'])

# Aggregating citation counts for each country
def aggregate(data, top_n=10):
    exploded_data = data.explode('Country')
    
    # Sum citation counts by country
    total = exploded_data.groupby('Country')['Cited by'].sum()
    agric = exploded_data[exploded_data['IsAgriculture']].groupby('Country')['Cited by'].sum()
    non_agric = exploded_data[~exploded_data['IsAgriculture']].groupby('Country')['Cited by'].sum()

    # Select top N countries based on total citation counts
    top_countries = dict(sorted(total.items(), key=lambda x: x[1], reverse=True)[:top_n])

    # Gather citation data for top countries
    top_data = {
        country: {
            'total': total.get(country, 0),
            'agric': agric.get(country, 0),
            'non_agric': non_agric.get(country, 0),
        } for country in top_countries
    }

    # Print details for top countries
    for country, values in top_data.items():
        print(f"{country}: Total Citations={values['total']}, Agriculture={values['agric']}, Non-Agriculture={values['non_agric']}")

    return top_data

top_n = 15
top_countries_data = aggregate(data, top_n)

# Plotting function for countries and their citation counts
def plot_top_countries(top_countries_data, title, output_filename):
    countries = list(top_countries_data.keys())
    x = np.arange(len(countries))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plotting citation data
    ax.barh(x - 0.2, [top_countries_data[country]['total'] for country in countries], 0.2, color=Color.GENERAL.value, label='Total Citations')
    ax.barh(x, [top_countries_data[country]['agric'] for country in countries], 0.2, color=Color.AGRICULTURE.value, label='Agricultural Citations')
    ax.barh(x + 0.2, [top_countries_data[country]['non_agric'] for country in countries], 0.2, color=Color.NON_AGRICULTURE.value, label='Non-Agricultural Citations')
    
    ax.set_xlabel('Citations')
    ax.set_title(title)
    ax.set_yticks(x)
    ax.set_yticklabels(countries)

    ax.legend()

    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"{output_path}/{output_filename}.png")
    plt.close()

plot_top_countries(top_countries_data, 'Top Countries: Citations by Research Focus', 'top_countries_citations')
