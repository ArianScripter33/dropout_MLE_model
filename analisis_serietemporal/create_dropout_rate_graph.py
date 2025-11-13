
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Load the datasets
try:
    matricula_df = pd.read_csv('CSV UNRC/Matricula.csv')
    bajas_df = pd.read_csv('CSV UNRC/Bajas_definitivas.csv')
except FileNotFoundError as e:
    print(f"Error loading CSV files: {e}")
    print("Please make sure the 'CSV UNRC' directory and the CSV files are in the correct location.")
    exit()

# Function to create a proper date
def create_date(df):
    # Ensure 'año' and 'trimestre' are integers
    df['año'] = df['año'].astype(int)
    df['trimestre'] = df['trimestre'].astype(int)
    df['date'] = pd.to_datetime(df['año'].astype(str) + '-' + (df['trimestre'] * 3).astype(str))
    df = df.set_index('date')
    return df

# Process each dataframe
matricula_df = create_date(matricula_df)
bajas_df = create_date(bajas_df)

# Merge the dataframes
df = pd.merge(matricula_df, bajas_df, on='date', how='inner')

# Calculate dropout rate
df['dropout_rate'] = (df['bajas'] / df['m_licenciatura']) * 100

# Create the plot
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the dropout rate
color = 'tab:red'
ax.set_xlabel('Año')
ax.set_ylabel('Tasa de Bajas (%)', color=color)
ax.plot(df.index, df['dropout_rate'], color=color, label='Tasa de Bajas')
ax.tick_params(axis='y', labelcolor=color)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

# Add title and legend
fig.suptitle('Tasa de Bajas en la UNRC', fontsize=16)
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

# Save the figure
plt.savefig('exhibit_4_dropout_rate.png')

print("Graph saved as exhibit_4_dropout_rate.png")
