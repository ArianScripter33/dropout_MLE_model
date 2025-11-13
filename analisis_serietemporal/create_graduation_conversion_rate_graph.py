
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Load the datasets
try:
    egresados_df = pd.read_csv('CSV UNRC/Egresados.csv')
    titulados_df = pd.read_csv('CSV UNRC/Titulados.csv')
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
egresados_df = create_date(egresados_df)
titulados_df = create_date(titulados_df)

# Calculate cumulative values
egresados_df['egresados_acumulados'] = egresados_df['egresados'].cumsum()
titulados_df['titulados_acumulados'] = titulados_df['titulados'].cumsum()

# Merge the dataframes
df = pd.merge(egresados_df, titulados_df, on='date', how='inner')

# Calculate conversion rate
df['tasa_conversion'] = (df['titulados_acumulados'] / df['egresados_acumulados']) * 100

# Create the plot
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the conversion rate
color = 'tab:green'
ax.set_xlabel('Año')
ax.set_ylabel('Tasa de Conversión a Titulación (%)', color=color)
ax.plot(df.index, df['tasa_conversion'], color=color, label='Tasa de Conversión a Titulación')
ax.tick_params(axis='y', labelcolor=color)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

# Add title and legend
fig.suptitle('Tasa de Conversión a Titulación Histórica', fontsize=16)
fig.tight_layout()
fig.legend(loc='upper left')

# Save the figure
plt.savefig('tasa_conversion_titulacion.png')

print("Graph saved as tasa_conversion_titulacion.png")
