import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from utils import get_cleaned_dataframe_from_csv, Color, extract_countries

# Load the CSV file
file_path = '../data/scopus.csv'
output_path = '../data/'
data = get_cleaned_dataframe_from_csv(file_path)

# Apply the function to extract countries
data['Country'] = data['Affiliations'].apply(extract_countries)
# Print the number of ignored rows due to missing countries
print(f"Ignored documents dut to missing affiliation (countries): {data['Country'].isna().sum()}")
# Print the number of ignored rows due to missing countries for Agriculture
print(f"Ignored agriculture documents due to missing data: {data[data['IsAgriculture'] & data['Country'].isna()].shape[0]}")
# Print the number of ignored rows due to missing countries for Non-Agriculture
print(f"Ignored non-agriculture documents due to missing data: {data[~data['IsAgriculture'] & data['Country'].isna()].shape[0]}")
data = data.dropna(subset=['Country']).explode('Country')

# Function to aggregate data for plotting
def aggregate_data(data, is_citations=False):
    if is_citations:
        data_grouped = data.groupby('Country').agg({'Cited by': 'sum', 'IsAgriculture': 'sum'}).rename(columns={'Cited by': 'total'})
        data_grouped['non_agric'] = data_grouped['total'] - data_grouped['IsAgriculture']
        data_grouped['agric'] = data_grouped.pop('IsAgriculture')
    else:
        data_grouped = data.groupby(['Country', 'IsAgriculture']).size().unstack(fill_value=0)
        data_grouped.columns = ['non_agric', 'agric']
        data_grouped['total'] = data_grouped['agric'] + data_grouped['non_agric']

    data_grouped['agric_ratio'] = data_grouped['agric'] / data_grouped['total'] * 100
    data_grouped['non_agric_ratio'] = data_grouped['non_agric'] / data_grouped['total'] * 100

    # Citations per publication calculation if applicable
    if is_citations:
        publication_data_temp = aggregate_data(data, is_citations=False)
        data_grouped['citations_per_publication'] = data_grouped['total'] / publication_data_temp['total']
    
    top_countries = data_grouped.sort_values(by='total', ascending=False).head(15)
    print("\nDetailed Country Stats:\n" + f"is_citations={is_citations}\n", top_countries)  # Printing detailed stats
    return top_countries[['total', 'agric', 'non_agric', 'agric_ratio', 'non_agric_ratio', 'citations_per_publication'] if is_citations else ['total', 'agric', 'non_agric', 'agric_ratio', 'non_agric_ratio']]


# Aggregate publication and citation data
publication_data = aggregate_data(data.copy(), is_citations=False)
citation_data = aggregate_data(data.copy(), is_citations=True)

# Plotting function for countries with their publication and citation counts
def plot_combined_data(publication_data, citation_data, title, output_filename):
    countries = publication_data.index
    x = np.arange(len(countries))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Publications bars
    bars_agr = ax1.bar(x - width/2, publication_data['agric'], width/3, label='Agricultural Publications', color=Color.AGRICULTURE.value, bottom=publication_data['non_agric'])
    bars_non_agr = ax1.bar(x - width/2, publication_data['non_agric'], width/3, label='Non-Agricultural Publications', color=Color.NON_AGRICULTURE.value)
    
    # Set up the second y-axis for citations
    ax2 = ax1.twinx()
    bars_cit_agr = ax2.bar(x + width/2, citation_data['agric'], width/3, label='Agricultural Citations', color='navy', bottom=citation_data['non_agric'])
    bars_cit_non_agr = ax2.bar(x + width/2, citation_data['non_agric'], width/3, label='Non-Agricultural Citations', color='lightsteelblue')

    # Create a single legend for both axes
    ax1.legend(loc='upper right')
    ax2.legend(loc='center right')

    ax1.set_xlabel('Countries')
    ax1.set_ylabel('Publication Counts')
    ax1.set_xticks(x)
    ax1.set_xticklabels(countries, rotation=45)
    ax2.set_ylabel('Citation Counts')

    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"{output_path}/{output_filename}.png")
    #plt.show()

plot_combined_data(publication_data, citation_data, 'Top Countries: Publications and Citations by Research Focus', 'top_countries_combined')
