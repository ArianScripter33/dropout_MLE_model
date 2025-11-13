import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Load the datasets
try:
    matricula_df = pd.read_csv('CSV UNRC/Matricula.csv')
    docentes_df = pd.read_csv('CSV UNRC/Docentes.csv')
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
docentes_df = create_date(docentes_df)

# Merge the dataframes
df = pd.merge(matricula_df, docentes_df, on='date', how='inner')

# --- ASSUMPTION ---
# Assuming a 50/50 split of students between 'Presencial-Híbrida' and 'Distancia-Híbrida'
df['m_presencial'] = df['m_licenciatura'] * 0.5
df['m_distancia'] = df['m_licenciatura'] * 0.5

# Calculate the ratios, handling division by zero
df['ratio_presencial'] = df['m_presencial'].divide(df['d_licenciatura_PH']).replace(np.inf, np.nan)
df['ratio_distancia'] = df['m_distancia'].divide(df['d_licenciatura_D']).replace(np.inf, np.nan)


# Calculate disparity
df['disparidad'] = (df['ratio_distancia'] / df['ratio_presencial']) - 1
df['disparidad'] = df['disparidad'].replace(np.inf, np.nan)


# Create the plot
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the ratios
ax.plot(df.index, df['ratio_presencial'], label='Ratio Presencial-Híbrida')
ax.plot(df.index, df['ratio_distancia'], label='Ratio Distancia-Híbrida')

# Add KPIs
last_quarter = df.index[-1]
ratio_p = df['ratio_presencial'].iloc[-1]
ratio_d = df['ratio_distancia'].iloc[-1]
percentage_diff = ((ratio_d / ratio_p) - 1) * 100
kpi_text = f"Disparidad Actual ({last_quarter.strftime('Q%q %Y')}): {percentage_diff:.2f}%"
ax.text(0.05, 0.95, kpi_text, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

avg_disparity = df['disparidad'].mean() * 100
avg_kpi_text = f"Disparidad Promedio Histórica: {avg_disparity:.2f}%"
ax.text(0.05, 0.85, avg_kpi_text, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

max_disparity = df['disparidad'].max() * 100
max_disparity_date = df['disparidad'].idxmax()
max_kpi_text = f"Disparidad Máxima Histórica ({max_disparity_date.strftime('Q%q %Y')}): {max_disparity:.2f}%"
ax.text(0.05, 0.75, max_kpi_text, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))


# Add title and legend
ax.set_xlabel('Año')
ax.set_ylabel('Ratio Estudiantes/Docente')
fig.suptitle('Evolución de la Carga Docente por Modalidad (Asumiendo 50/50 de Matrícula)', fontsize=16)
ax.legend()

# Save the figure
plt.savefig('evolucion_carga_docente.png')

print("Graph saved as evolucion_carga_docente.png")
print("\n---")
print("IMPORTANTE: El gráfico se generó asumiendo una distribución del 50/50 de la matrícula entre las modalidades 'Presencial-Híbrida' y 'Distancia-Híbrida'.")
print("Si dispone de los datos reales de matrícula por modalidad, por favor proporciónelos para generar un gráfico más preciso.")
