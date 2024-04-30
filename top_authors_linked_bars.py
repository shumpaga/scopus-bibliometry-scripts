import plotly.graph_objects as go
from utils import get_cleaned_dataframe_from_csv

# Load and prepare data
file_path = '../data/scopus.csv'
data = get_cleaned_dataframe_from_csv(file_path)

# Correctly explode the 'Authors' column
data['Authors'] = data['Authors'].str.split('; ')
data = data.explode('Authors')

# Define categories
categories = ['Agriculture', 'General', 'Non-Agriculture']

# Find top authors in each category
top_authors = {}
for category in categories:
    if category == 'Agriculture':
        filtered = data[data['IsAgriculture'] == True]
    elif category == 'Non-Agriculture':
        filtered = data[data['IsAgriculture'] == False]
    else:
        filtered = data
    top_authors[category] = filtered['Authors'].value_counts().head(30).index.tolist()

# Prepare nodes and links for Sankey
label_list = []
source = []
target = []
value = []

# Assign indices to labels and create links
index = 0
for i, category in enumerate(categories):
    next_category = categories[i + 1] if i + 1 < len(categories) else None
    for author in top_authors[category]:
        if author not in label_list:
            label_list.append(author)
        if next_category:
            for next_author in top_authors[next_category]:
                if next_author not in label_list:
                    label_list.append(next_author)
                source.append(label_list.index(author))
                target.append(label_list.index(next_author))
                value.append(1)  # Dummy value for visualization

# Create the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=label_list,
        color='blue'
    ),
    link=dict(
        source=source,
        target=target,
        value=value
    ))])

fig.update_layout(title_text="Sankey Diagram of Top Authors by Category", font_size=10)
fig.show()
