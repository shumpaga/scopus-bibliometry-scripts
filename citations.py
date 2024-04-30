import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from collections import Counter

# Load the dataset
file_path = '../data/scopus.csv'
data = pd.read_csv(file_path)

# Initial data overview
print(f"Total publications before filtering: {len(data)}")

# Select publications from 2012 onwards
data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
data = data[data['Year'] >= 2012]
print(f"Total publications from 2012 onwards: {len(data)}")

# Convert 'Cited by' to numeric, handling missing values
# Ensure 'Year' is numeric and filter for years >= 2012
data['Cited by'] = pd.to_numeric(data['Cited by'], errors='coerce').fillna(0)

# Print 'References' column of first row to understand the data, do not truncate the text
pd.set_option('display.max_colwidth', None)
print(data['References'].iloc[0])

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
print(f"Total agriculture-related publications: {data['IsAgriculture'].sum()}")


# Group by year and calculate average citations
average_citations_per_year = data.groupby('Year')['Cited by'].mean()
average_citations_per_year_agri = data[data['IsAgriculture']].groupby('Year')['Cited by'].mean()

print("\nAverage citations per year (General):")
print(average_citations_per_year)
print("\nAverage citations per year (Agriculture):")
print(average_citations_per_year_agri)

# Detect peaks
peaks_general, _ = find_peaks(average_citations_per_year.values)
peaks_agri, _ = find_peaks(average_citations_per_year_agri.values)

def explain_peak_year(year, is_agri=False):
    year_data = data[(data['Year'] == year) & (data['IsAgriculture'] == is_agri)]
    if not year_data.empty:
        # Highly cited papers
        top_cited_paper = year_data.loc[year_data['Cited by'].idxmax()]
        # Trending topics
        keywords = ';'.join(year_data['Author Keywords'].fillna('') + ';' + year_data['Index Keywords'].fillna('')).split(';')
        keyword_counts = Counter(kw.strip().lower() for kw in keywords if kw)
        trending_topics = ', '.join(kw for kw, _ in keyword_counts.most_common(3))
        # Top sources
        top_sources = ', '.join(year_data['Source title'].value_counts().head(3).index.tolist())
        explanation = f"Top cited: {top_cited_paper['Title'][:50]}..., Topics: {trending_topics}, Sources: {top_sources}"
    else:
        explanation = "No data"
    return explanation

def explain_peak_year(year, is_agri=False):
    year_data = data[(data['Year'] == year) & (data['IsAgriculture'] == is_agri)]
    if not year_data.empty:
        # Sort by 'Cited by' to find highly cited papers
        sorted_data = year_data.sort_values(by='Cited by', ascending=False).head(3)
        
        # Print top 3 cited papers in the console
        print(f"\nTop 3 cited papers in {year} ({'Agriculture' if is_agri else 'General'}):")
        for i, row in sorted_data.iterrows():
            authors = row['Authors'].split(';')[0] + " et al." if row['Authors'] else "Unknown authors"
            title = row['Title'][:100] + "..." if len(row['Title']) > 100 else row['Title']
            cited_by = row['Cited by']
            print(f"    - {authors} ({year}). {title}. Cited by: {cited_by}")

        # Trending topics
        keywords = ';'.join(year_data['Author Keywords'].fillna('') + ';' + year_data['Index Keywords'].fillna('')).split(';')
        keyword_counts = Counter(kw.strip().lower() for kw in keywords if kw)
        trending_topics = ', '.join(kw for kw, _ in keyword_counts.most_common(3))
        print(f"Trending topics: {trending_topics}")

        # Top sources
        top_sources = ', '.join(year_data['Source title'].value_counts().head(3).index.tolist())
        print(f"Top sources: {top_sources}")

        explanation = f"Year {year}: High citations in {len(sorted_data)} papers, Trending topics: {trending_topics}, Top sources: {top_sources}"
    else:
        explanation = "No data"
    return explanation


# Plotting
plt.figure(figsize=(14, 7))
plt.plot(average_citations_per_year.index, average_citations_per_year.values, label='General', marker='o')
plt.plot(average_citations_per_year_agri.index, average_citations_per_year_agri.values, label='Agriculture', marker='x')

# Annotating peaks with explanations
for peak in peaks_general:
    year = average_citations_per_year.index[peak]
    explanation = explain_peak_year(year)
    #print(f"Peak year for general publications: {year}: {explanation}")
    #plt.annotate(explanation, (year, average_citations_per_year.values[peak]),
    #             textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, arrowprops=dict(arrowstyle="->"))

for peak in peaks_agri:
    year = average_citations_per_year_agri.index[peak]
    explanation = explain_peak_year(year, is_agri=True)
    #print(f"Peak year for agriculture-related publications: {year}: {explanation}")
    #plt.annotate(explanation, (year, average_citations_per_year_agri.values[peak]),
    #             textcoords="offset points", xytext=(0,-15), ha='center', fontsize=8, arrowprops=dict(arrowstyle="->"))

plt.title('Average Citations Per Year')
plt.xlabel('Year')
plt.ylabel('Average Citations')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('average_citations_per_year.png')
plt.show()
