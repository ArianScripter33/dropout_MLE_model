
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Load the datasets
try:
    matricula_df = pd.read_csv('CSV UNRC/Matricula.csv')
    egresados_df = pd.read_csv('CSV UNRC/Egresados.csv')
    titulados_df = pd.read_csv('CSV UNRC/Titulados.csv')
    bajas_df = pd.read_csv('CSV UNRC/Bajas_definitivas.csv')
except FileNotFoundError as e:
    print(f"Error loading CSV files: {e}")
    print("Please make sure the 'CSV UNRC' directory and the CSV files are in the correct location.")
    exit()

# Function to create a proper date
def create_date(df):
    # Drop duplicate rows
    df = df.drop_duplicates()
    # Ensure 'año' and 'trimestre' are integers
    df['año'] = df['año'].astype(int)
    df['trimestre'] = df['trimestre'].astype(int)
    df['date'] = pd.to_datetime(df['año'].astype(str) + '-' + (df['trimestre'] * 3).astype(str))
    df = df.set_index('date')
    df = df.sort_index()
    return df

# Process each dataframe
matricula_df = create_date(matricula_df)
egresados_df = create_date(egresados_df)
titulados_df = create_date(titulados_df)
bajas_df = create_date(bajas_df)

# Calculate cumulative values for egresados and titulados
egresados_df['egresados_acumulados'] = egresados_df['egresados'].cumsum()
titulados_df['titulados_acumulados'] = titulados_df['titulados'].cumsum()

# Create the plot
fig, ax1 = plt.subplots(figsize=(12, 8))

# Plot Matricula on the left Y-axis
color = 'tab:blue'
ax1.set_xlabel('Año')
ax1.set_ylabel('Matrícula Total', color=color)
ax1.plot(matricula_df.index, matricula_df['m_licenciatura'], color=color, label='Matrícula')
ax1.tick_params(axis='y', labelcolor=color)
ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))


# Create a second Y-axis for the other data
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Egresados, Titulados y Bajas', color=color)

# Plot Egresados, Titulados (cumulative), and Bajas on the right Y-axis
ax2.plot(egresados_df.index, egresados_df['egresados_acumulados'], color='tab:green', label='Egresados (Acumulado)')
ax2.plot(titulados_df.index, titulados_df['titulados_acumulados'], color='tab:purple', label='Titulados (Acumulado)')
ax2.plot(bajas_df.index, bajas_df['bajas'], color='tab:orange', label='Bajas')
ax2.tick_params(axis='y', labelcolor=color)
ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))


# Add title and legend
fig.suptitle('Serie Temporal de Datos de la UNRC', fontsize=16)
fig.tight_layout()
fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))


# Save the figure
plt.savefig('exhibit_3_serie_temporal.png')

print("Graph saved as exhibit_3_serie_temporal.png")
