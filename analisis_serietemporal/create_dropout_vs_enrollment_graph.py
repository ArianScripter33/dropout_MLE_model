
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
df['tasa_bajas'] = (df['bajas'] / df['m_licenciatura']) * 100

# Calculate quarterly percentage change in enrollment
df['crecimiento_matricula'] = df['m_licenciatura'].pct_change() * 100

# Create the plot
fig, ax1 = plt.subplots(figsize=(12, 8))

# Plot dropout rate on the left Y-axis
color = 'tab:red'
ax1.set_xlabel('Año')
ax1.set_ylabel('Tasa de Bajas (%)', color=color)
line1 = ax1.plot(df.index, df['tasa_bajas'], color=color, label='Tasa de Bajas')
ax1.tick_params(axis='y', labelcolor=color)
ax1.yaxis.set_major_formatter(mticker.PercentFormatter())

# Create a second Y-axis for the enrollment growth
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Crecimiento de Matrícula (%)', color=color)
line2 = ax2.plot(df.index, df['crecimiento_matricula'], color=color, label='Crecimiento de Matrícula')
ax2.tick_params(axis='y', labelcolor=color)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter())

# Add title and legend
fig.suptitle('Tasa de Bajas vs. Crecimiento de Matrícula', fontsize=16)
fig.tight_layout(rect=[0, 0, 0.9, 1])

# Combine legends
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')

# Save the figure
plt.savefig('tasa_bajas_vs_crecimiento_matricula.png')

print("Graph saved as tasa_bajas_vs_crecimiento_matricula.png")
