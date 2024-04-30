import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from utils import get_cleaned_dataframe_from_csv, Color

# Load the CSV file
file_path = 'data/scopus.csv'
output_path = 'data/'
data = get_cleaned_dataframe_from_csv(file_path)

# Assuming 'Year', 'Cited by', 'IsAgriculture' columns exist after data cleaning
# Calculate average citations per year for general, agriculture, and non-agriculture
def average_citations(data):
    data['Cited by'] = pd.to_numeric(data['Cited by'], errors='coerce')

    # Calculate ignored documents due to missing 'Cited by'
    ignored_general = data['Cited by'].isna().sum()
    ignored_agriculture = data[data['IsAgriculture'] == True]['Cited by'].isna().sum()
    ignored_non_agriculture = data[data['IsAgriculture'] == False]['Cited by'].isna().sum()
    print(f"Ignored general documents due to missing data: {ignored_general}")
    print(f"Ignored agriculture documents due to missing data: {ignored_agriculture}")
    print(f"Ignored non-agriculture documents due to missing data: {ignored_non_agriculture}")
    
    # Drop rows where Cited by is NaN
    data = data.dropna(subset=['Cited by'])

    yearly_data = data.groupby(['Year', 'IsAgriculture'])['Cited by'].mean().unstack(fill_value=0)
    yearly_data.columns = ['Non-Agriculture', 'Agriculture']
    yearly_data['General'] = data.groupby('Year')['Cited by'].mean()

    doc_counts = data.groupby(['Year', 'IsAgriculture']).size().unstack(fill_value=0)
    doc_counts.columns = ['Non-Agriculture', 'Agriculture']
    doc_counts['General'] = data.groupby('Year').size()

    return yearly_data, doc_counts

def plot_citations(yearly_data, doc_counts):
    plt.figure(figsize=(14, 8))
    colors = {'General': Color.GENERAL.value, 'Agriculture': Color.AGRICULTURE.value, 'Non-Agriculture': Color.NON_AGRICULTURE.value}
    for column in yearly_data.columns:
        plt.plot(yearly_data.index, yearly_data[column], marker='o', label=f'Avg Citations {column}', color=colors[column])
        #print(f"Yearly data for {column}:\n{yearly_data[column]}")
    
        # Peak detection
        peaks, _ = find_peaks(yearly_data[column], height=0)
        peak_years = yearly_data.index[peaks]

        for year in peak_years:
            if column == 'Agriculture':
                category_data = data[(data['Year'] == year) & (data['IsAgriculture'] == True) & (data['Cited by'] > 0)]
            elif column == 'Non-Agriculture':
                category_data = data[(data['Year'] == year) & (data['IsAgriculture'] == False) & (data['Cited by'] > 0)]
            else:
                category_data = data[(data['Year'] == year) & (data['Cited by'] > 0)]

            top_papers = category_data.nlargest(3, 'Cited by')

            print(f"\nTop cited papers in {column} for the year {year} among {len(category_data)} papers:")
            for i, paper in enumerate(top_papers.itertuples()):
                # Checking if authors are present
                if pd.isna(paper.Authors) or paper.Authors.strip() == "":
                    author_text = "Unknown Author"
                else:
                    author_text = paper.Authors

                annotation = f"'{paper.Title}' by {author_text}, {paper._13} citations"
                print(annotation)
        
        # Add document counts to the plot
        for year in yearly_data.index:
            heights = {'Agriculture': 1, 'Non-Agriculture': 3, 'General': 5}  # baseline heights for annotations
            for category in ['Agriculture', 'Non-Agriculture', 'General']:
                doc_count = doc_counts.at[year, category] if year in doc_counts.index else 0
                plt.annotate(str(doc_count), (year, heights[category]), color=colors[category], ha='center', va='bottom', fontsize=15)
                #print(f"Document count for {category} in {year}: {doc_count}")


    plt.title('Average Citations per Year')
    plt.xlabel('Year')
    plt.ylabel('Average Citations')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_path}/average_citations_per_year.png")
    # plt.show()


# Run analysis and plotting
yearly_citations, doc_counts = average_citations(data)
plot_citations(yearly_citations, doc_counts)
