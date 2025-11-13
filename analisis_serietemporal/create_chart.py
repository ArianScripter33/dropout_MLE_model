import pandas as pd
import matplotlib.pyplot as plt
import os

# Define file paths
docentes_csv = os.path.abspath('CSV UNRC/Docentes.csv')
matricula_csv = os.path.abspath('CSV UNRC/Matricula.csv')
output_image = os.path.abspath('exhibit_4_carga_docente.png')

# 1. Load CSVs
try:
    df_docentes = pd.read_csv(docentes_csv)
    df_matricula = pd.read_csv(matricula_csv)
except FileNotFoundError as e:
    print(f"Error: {e}. Make sure the CSV files are in the 'CSV UNRC' directory.")
    exit()

# 2. Calculate Ratios
# Sum of all students
total_matricula = df_matricula['m_licenciatura'].sum()

# Sum of teachers for each modality
docentes_presencial = df_docentes['d_licenciatura_PH'].sum()
docentes_distancia = df_docentes['d_licenciatura_D'].sum()

# Calculate ratios
ratio_presencial = total_matricula / docentes_presencial
ratio_distancia = total_matricula / docentes_distancia

# 3. Generate Plot
labels = ['Modalidad Presencial-Híbrida', 'Modalidad a Distancia-Híbrida']
valores = [ratio_presencial, ratio_distancia]

fig, ax = plt.subplots()
bars = ax.bar(labels, valores, color=['skyblue', 'lightgreen'])

# Add labels to the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom') # format to 2 decimal places

ax.set_ylabel('Ratio Estudiantes por Docente')
ax.set_title('Disparidad de Carga Docente por Modalidad')

# 4. Save Plot
plt.savefig(output_image)

print(f"Gráfico guardado en: {output_image}")