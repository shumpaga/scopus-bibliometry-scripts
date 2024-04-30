import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import linregress

from utils import get_cleaned_dataframe_from_csv, Color

# Load the CSV file
file_path = '../data/scopus.csv'
data = get_cleaned_dataframe_from_csv(file_path)

# Filter data from start_year onwards
start_year = 2012
data = data[data['Year'] >= start_year]

# Calculate the number of publications per year
total_publications_per_year = data['Year'].value_counts().sort_index()
agri_publications_per_year = data[data['IsAgriculture']]['Year'].value_counts().sort_index()
non_agri_publications_per_year = data[~data['IsAgriculture']]['Year'].value_counts().sort_index()

# Print total document counts
print(f"Total documents from {start_year} to 2024: {total_publications_per_year.sum()}")
print(f"Agriculture documents from {start_year} to 2024: {agri_publications_per_year.sum()}")
print(f"Non-Agriculture documents from {start_year} to 2024: {non_agri_publications_per_year.sum()}")

# Calculate and print yearly growth rates
total_growth_rate = total_publications_per_year.pct_change().fillna(0) * 100
agri_growth_rate = agri_publications_per_year.pct_change().fillna(0) * 100
non_agri_growth_rate = non_agri_publications_per_year.pct_change().fillna(0) * 100
print(f"Average annual growth rate of total publications: {total_growth_rate.mean():.2f}%")
print(f"Average annual growth rate of agriculture-related publications: {agri_growth_rate.mean():.2f}%")
print(f"Average annual growth rate of non-agriculture publications: {non_agri_growth_rate.mean():.2f}%")

# Identify peak years
peak_year_total = total_publications_per_year.idxmax()
peak_year_agri = agri_publications_per_year.idxmax()
peak_year_non_agri = non_agri_publications_per_year.idxmax()

# Print peak years and counts
print(f"Peak year for total publications: {peak_year_total} with {total_publications_per_year.max()} publications")
print(f"Peak year for agriculture-related publications: {peak_year_agri} with {agri_publications_per_year.max()} publications")
print(f"Peak year for non-agriculture publications: {peak_year_non_agri} with {non_agri_publications_per_year.max()} publications")

# Filling missing years with 0 for a continuous timeline from 2012 onwards
timeline = np.arange(2012, total_publications_per_year.index.max()+1)
total_publications_per_year = total_publications_per_year.reindex(timeline, fill_value=0)
agri_publications_per_year = agri_publications_per_year.reindex(timeline, fill_value=0)
non_agri_publications_per_year = non_agri_publications_per_year.reindex(timeline, fill_value=0)
print(f"timeline: {timeline}")
print(f"total_publications_per_year: {total_publications_per_year}")
print(f"agri_publications_per_year: {agri_publications_per_year}")
print(f"non_agri_publications_per_year: {non_agri_publications_per_year}")

# Calculate linear regression (trend line) for total publications
slope_total, intercept_total, _, _, _ = linregress(timeline, total_publications_per_year.values)
total_trend_y = intercept_total + slope_total * timeline

# Calculate linear regression (trend line) for agriculture publications
slope_agri, intercept_agri, _, _, _ = linregress(timeline, agri_publications_per_year.values)
agri_trend_y = intercept_agri + slope_agri * timeline

# Calculate the percentage of agriculture-related publications
slope_non_agri, intercept_non_agri, _, _, _ = linregress(timeline, non_agri_publications_per_year.values)
non_agri_trend_y = intercept_non_agri + slope_non_agri * timeline

# Plotting
plt.figure(figsize=(14, 8))
plt.plot(timeline, total_publications_per_year.values, 'o-', label='Total Publications', color=Color.GENERAL.value)
plt.plot(timeline, total_trend_y, '--', color='royalblue', label='Trend: Total Publications', alpha=0.5)
plt.plot(timeline, agri_publications_per_year.values, 'x-', label='Agriculture-related Publications', color=Color.AGRICULTURE.value)
plt.plot(timeline, agri_trend_y, '--', color='darkorange', label='Trend: Agriculture-related Publications', alpha=0.5)
plt.plot(timeline, non_agri_publications_per_year.values, 's-', label='Non-agriculture Publications', color=Color.NON_AGRICULTURE.value)
plt.plot(timeline, non_agri_trend_y, '--', color='forestgreen', label='Trend: Non-agriculture Publications', alpha=0.5)

# Adding annotations for data points
for year in timeline:
    total_count = total_publications_per_year[year]
    agri_count = agri_publications_per_year[year]
    non_agri_count = non_agri_publications_per_year[year]
    plt.text(year, total_count + 100, str(total_count), ha='center', color=Color.GENERAL.value) 
    plt.text(year, non_agri_count + 30, str(non_agri_count), ha='center', color=Color.NON_AGRICULTURE.value)
    plt.text(year, agri_count - 80, str(agri_count), ha='center', color=Color.AGRICULTURE.value)

plt.title('Volume of Literature on AI via IoT Over Time (2012 Onwards)')
plt.xlabel('Year')
plt.ylabel('Number of Publications')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(timeline)
plt.tight_layout()

# Save the plot
plt.savefig('../data/volume_per_year.png')  # Update your_output_path to your desired path
# plt.show()
