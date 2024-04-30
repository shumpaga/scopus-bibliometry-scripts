import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import pycountry

# Load the CSV file
file_path = '../data/scopus.csv'
output_path = '../data/'
data = pd.read_csv(file_path)

# Define agriculture-related keywords
agriculture_keywords = [
    "agriculture", "farming", "agritech", "precision agriculture", "smart agriculture",
    "crop monitoring", "crop prediction", "crop disease", "crop yield forecasting",
    "precision farming", "precision agriculture", "site-specific crop management", "variable rate technology",
    "sustainable farming", "conservation agriculture", "agroecology", "organic farming",
    "livestock management", "animal health monitoring", "dairy farming technology", "poultry monitoring",
    "soil health monitoring", "irrigation management", "water usage efficiency", "nutrient management",
    "agricultural drones", "farm robotics", "automated harvesting", "robotic weeding",
    "climate-smart agriculture", "agricultural adaptation to climate change", "weather prediction for farming",
    "agri-food supply chain", "food traceability", "agricultural logistics", "farm to table",
    "pesticide application technology", "herbicide resistance management", "fertilizer optimization",
    "agricultural big data", "farm data analytics", "agricultural informatics", "agricultural decision support systems"
]

# Filter for agriculture-related publications
def is_agriculture_related(text, keywords=agriculture_keywords):
    if pd.isna(text):
        return False
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

data['IsAgriculture'] = data.apply(lambda x: is_agriculture_related(x['Title']) or
                                    is_agriculture_related(x['Abstract']) or
                                    is_agriculture_related(x['Author Keywords']) or
                                    is_agriculture_related(x['Index Keywords']) or
                                    is_agriculture_related(x['Affiliations']), axis=1)

# Extraction of contributions
# Simplified extraction of countries from 'Affiliations' column
# This requires a predefined list or heuristic for identifying countries within affiliation strings
def extract_countries(affiliations):
    if pd.isna(affiliations):
        return 'Unknown'
    
    # Prepare a list of country names and common abbreviations to enhance matching accuracy
    countries_info = [(country.name, country.alpha_2) for country in pycountry.countries]
    # Optionally, add any specific abbreviations or common names not covered by pycountry
    additional_mappings = {
        'USA': 'United States',
        'UK': 'United Kingdom',
        # Add more mappings as needed
    }
    
    # Try to match each country or abbreviation in the affiliation string
    for name, alpha_2 in countries_info:
        if name in affiliations or alpha_2 in affiliations:
            return name
    
    # Attempt to match additional mappings
    for abbreviation, country_name in additional_mappings.items():
        if abbreviation in affiliations:
            return country_name
    
    return 'Unknown'

data['Country'] = data['Affiliations'].apply(extract_countries)

# Aggregating contributions for each category
def aggregate_contributions(data, column_name, top_n=10):
    if column_name == 'Authors':
        # Expand the DataFrame to count each co-author as a separate row
        expanded_data = data.dropna(subset=['Authors']).copy()
        expanded_data['Authors'] = expanded_data['Authors'].str.split('; ')
        expanded_data = expanded_data.explode('Authors')
        
        # Proceed with the adjusted data for authors
        data = expanded_data
    
    # Filter out rows where the column has 'nan' or 'Unknown' before aggregation
    filtered_data = data[(data[column_name].notna()) & (data[column_name] != 'Unknown')]
    # Count ignored 'nan' and 'Unknown' for general and agriculture data
    ignored_general = data[(~data['IsAgriculture']) & (data[column_name].isna() | (data[column_name] == 'Unknown'))].shape[0]
    ignored_agri = data[(data['IsAgriculture']) & (data[column_name].isna() | (data[column_name] == 'Unknown'))].shape[0]
    general_data = filtered_data[~filtered_data['IsAgriculture']]
    agri_data = filtered_data[filtered_data['IsAgriculture']]
    
    general_counts = Counter(general_data[column_name])
    agri_counts = Counter(agri_data[column_name])

    # Sort and select top N
    general_sorted = sorted(general_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    agri_sorted = sorted(agri_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Split keys and values for plotting
    general_categories, general_values = zip(*general_sorted) if general_sorted else ([], [])
    agri_categories, agri_values = zip(*agri_sorted) if agri_sorted else ([], [])
    return general_categories, general_values, agri_categories, agri_values, ignored_general, ignored_agri

def plot_individual_horizontal_bar_chart(categories, data, title, xlabel, top_n):
    y = np.arange(len(categories))  # Position for each category on the y-axis
    
    # Adjust the figure size if necessary to accommodate long category names
    fig, ax = plt.subplots(figsize=(20, 0.5 * len(categories)))
    rects = ax.barh(y, data, height=0.35, label=title, alpha=0.8, color='royalblue' if 'General' in title else 'darkorange')

    ax.set_xlabel('Publications', fontsize=12)
    ax.set_title(f"Top {top_n} {title}", fontsize=14)
    ax.set_yticks(y)
    ax.set_yticklabels(categories, fontsize=10)
    ax.legend()
    
    # Function to auto-label the bars with their count value
    def autolabel(rects):
        """Attach a text label beside each bar in *rects*, displaying its width."""
        for rect in rects:
            width = rect.get_width()
            ax.annotate('{}'.format(width),
                        xy=(width, rect.get_y() + rect.get_height() / 2),
                        xytext=(3, 0),  # 3 points horizontal offset
                        textcoords="offset points",
                        ha='left', va='center')

    # Call the autolabel function for each set of bars
    autolabel(rects)

    # Additional plot customizations
    plt.ylabel(xlabel, fontsize=12)  # xlabel now serves as ylabel in a horizontal bar chart
    plt.tight_layout()
    plt.savefig(f"{output_path}/top_{'general' if 'General' in title else 'agriculture'}_{xlabel.lower().replace(' ', '_')}.png")  # Saving the figure as a file


def plot_individual_vertical_bar_chart(categories, data, title, xlabel, top_n):
    # Determine positions for each bar
    x = np.arange(len(categories))  # label locations
    width = 0.35  # bar width
    
    # Plot bars for general and agriculture-related data
    fig, ax = plt.subplots(figsize=(10, 8))
    rects = ax.bar(x, data, width, label=title, alpha=0.8, color='royalblue' if 'General' in title else 'darkorange')

    ax.set_ylabel('Publications', fontsize=12)
    ax.set_title(f"Top {top_n} {title}", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha="right", fontsize=10)
    ax.legend()
    
    # Function to auto-label the bars with their count value
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Call the autolabel function for each set of bars
    autolabel(rects)

    # Additional plot customizations 
    plt.xlabel(xlabel, fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{output_path}/top_{'general' if 'General' in title else 'agriculture'}_{xlabel.lower().replace(' ', '_')}.png")  # Saving the figure as a file

def print_discussion_points(categories_general, values_general, categories_agri, values_agri, ignored_general, ignored_agri, category_name):
    print(f"\nDiscussion Points for {category_name} Contributions:")
    print(f"General - Top {len(categories_general)} {category_name}: {categories_general}")
    print(f"General - Contributions: {values_general}")
    print(f"Agriculture - Top {len(categories_agri)} {category_name}: {categories_agri}")
    print(f"Agriculture - Contributions: {values_agri}")
    print(f"Ignored in General due to NaN or Unknown: {ignored_general}")
    print(f"Ignored in Agriculture due to NaN or Unknown: {ignored_agri}")

# Plotting contributions separately
top_n = 10  # Adjust this to change the number of top contributors displayed
for category in ['Country', 'Authors', 'Source title']:
    print(f"----------------\nPlotting contributions by {category}...")
    general_categories, general_values, agri_categories, agri_values, ignored_general, ignored_agri  = aggregate_contributions(data, category, top_n)

    # Prepare discussion points
    print_discussion_points(general_categories, general_values, agri_categories, agri_values, ignored_general, ignored_agri, category)

    if general_values:  # Check if there's data to plot
        if category == 'Source title':
            plot_individual_horizontal_bar_chart(general_categories, general_values, f'General Contributions by {category}', category, top_n)
        else:
            plot_individual_vertical_bar_chart(general_categories, general_values, f'General Contributions by {category}', category, top_n)
    
    if agri_values:  # Check if there's data to plot
        if category == 'Source title':
            plot_individual_horizontal_bar_chart(agri_categories, agri_values, f'Agriculture Contributions by {category}', category, top_n)
        else:
            plot_individual_vertical_bar_chart(agri_categories, agri_values, f'Agriculture Contributions by {category}', category, top_n)