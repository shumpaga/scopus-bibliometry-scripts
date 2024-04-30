import pandas as pd

def get_cleaned_dataframe_from_csv(csv_file_path, start_year=2012):
    # Load the dataset
    data = pd.read_csv(csv_file_path)

    # Pre-processing to filter data from 2012 onwards
    data['Year'] = pd.to_numeric(data['Year'], errors='coerce')  # Ensure the 'Year' column is numeric
    data = data.dropna(subset=['Year'])  # Drop rows where Year is NaN
    data['Year'] = data['Year'].astype(int)  # Convert Year to integer
    
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
    
    # Compile a single string pattern for faster search
    pattern = '|'.join(agriculture_keywords)
    
    # Calculate the agriculture mask
    data['IsAgriculture'] = data[['Title', 'Abstract', 'Author Keywords', 'Index Keywords', 'Affiliations']].apply(
        lambda x: x.str.contains(pattern, case=False, na=False).any(), axis=1)
    
    # Count total documents, agriculture, and non-agriculture documents
    print(f"Stats in general: Total documents {data.shape[0]}, Agriculture documents {data['IsAgriculture'].sum()}, Non-agriculture documents {data[~data['IsAgriculture']].shape[0]}")
    
    # Return the modified dataframe
    start_year = 2012
    data = data[data['Year'] >= start_year]
    print(f"Stats after filtering from {start_year} onwards: Total documents {data.shape[0]}, Agriculture documents {data['IsAgriculture'].sum()}, Non-agriculture documents {data[~data['IsAgriculture']].shape[0]}")
    
    # Print data column names as JSON
    print(data.columns.to_list())

    return data

# Example usage:
# csv_file_path = '../data/scopus.csv'
# data = get_cleaned_dataframe_from_csv(csv_file_path)
