import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Define paths
BASE_DIR = "/Users/arianstoned/Desktop/dropout_MLE_model"
DATA_DIR = os.path.join(BASE_DIR, "data/raw/longitudinal")
FIGURES_DIR = os.path.join(BASE_DIR, "reports/figures")

# Ensure figures dir exists
os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data():
    try:
        matricula_df = pd.read_csv(os.path.join(DATA_DIR, "Matricula.csv"))
        egresados_df = pd.read_csv(os.path.join(DATA_DIR, "Egresados.csv"))
        titulados_df = pd.read_csv(os.path.join(DATA_DIR, "Titulados.csv"))
        
        # Construct 'Fecha' column from 'año' and 'trimestre'
        def create_date(df):
            # Map Quarter to Month: Q1=1, Q2=4, Q3=7, Q4=10
            # Or simpler: (Trimestre * 3) - 2
            # But let's just use a simple mapping or string construction
            # Assuming trimestre is 1, 2, 3, 4
            # Let's just assume Q1=Jan 1st, Q2=Apr 1st, etc.
            # Actually, let's just use the middle of the quarter or start. Start is fine.
            # Month = (Trimestre - 1) * 3 + 1
            df['month'] = (df['trimestre'] - 1) * 3 + 1
            df['day'] = 1
            df['Fecha'] = pd.to_datetime(df[['año', 'month', 'day']].rename(columns={'año': 'year'}))
            df.drop(columns=['month', 'day'], inplace=True)
            return df

        matricula_df = create_date(matricula_df)
        egresados_df = create_date(egresados_df)
        titulados_df = create_date(titulados_df)
        
        # Rename columns to match expected names if needed
        # Matricula.csv has "m_licenciatura" + "m_posgrados" = Total?
        # Let's check the columns again.
        # Matricula: m_licenciatura, m_posgrados. Total = sum.
        matricula_df['Matrícula Total'] = matricula_df['m_licenciatura'] + matricula_df['m_posgrados']
        
        # Egresados: "egresados" column seems to be the total.
        # Egresados.csv: "egresados"
        egresados_df.rename(columns={'egresados': 'Egresados'}, inplace=True)

        # Titulados: "titulados" column seems to be the total.
        # Titulados.csv: "titulados"
        titulados_df.rename(columns={'titulados': 'Titulados'}, inplace=True)

        return matricula_df, egresados_df, titulados_df
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def create_funnel_chart(matricula_df, egresados_df, titulados_df):
    # Process data for plotting
    # We need cumulative sums for Egresados and Titulados
    egresados_ts = egresados_df.set_index('Fecha')['Egresados'].sort_index().cumsum()
    titulados_ts = titulados_df.set_index('Fecha')['Titulados'].sort_index().cumsum()
    
    # Matricula is a stock, so we just take the value over time
    matricula_ts = matricula_df.set_index('Fecha')['Matrícula Total'].sort_index()

    # Align dates
    all_dates = egresados_ts.index.union(titulados_ts.index).union(matricula_ts.index).sort_values()
    
    # Reindex and fill
    egresados_ts = egresados_ts.reindex(all_dates, method='ffill').fillna(0)
    titulados_ts = titulados_ts.reindex(all_dates, method='ffill').fillna(0)
    matricula_ts = matricula_ts.reindex(all_dates, method='ffill') # Don't fillna with 0 for matricula, maybe just ffill

    # Calculate the Gap (Pendientes)
    # Gap = Egresados (Total pool) - Titulados (Success)
    brecha_ts = egresados_ts - titulados_ts

    # Plotting
    plt.figure(figsize=(14, 8))
    plt.style.use('seaborn-v0_8-whitegrid')

    # Stacked Area: Bottom = Titulados, Top = Brecha. Sum = Egresados.
    plt.stackplot(all_dates, 
                  titulados_ts, 
                  brecha_ts, 
                  labels=['Titulados (Éxito)', 'Brecha: Egresados sin Título'],
                  colors=['#9b59b6', '#e74c3c'], 
                  alpha=0.7)

    # Add Matricula line for context
    # Note: Matricula might be on a different scale or similar. 
    # If Matricula is ~50k and Egresados Cumulative grows to ~50k, it fits.
    plt.plot(all_dates, matricula_ts, label='Matrícula Activa (Contexto)', color='#3498db', linestyle='--', linewidth=2)

    plt.title('Embudo de Eficiencia Terminal: La Brecha de la "Última Milla"', fontsize=16, fontweight='bold')
    plt.ylabel('Número de Estudiantes / Egresados Acumulados', fontsize=12)
    plt.xlabel('Año', fontsize=12)
    
    # Legend
    plt.legend(loc='upper left', fontsize=11, frameon=True, facecolor='white', framealpha=0.9)
    
    # Grid
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Y-axis formatting
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Annotation for final conversion rate
    ultimo_egresados = egresados_ts.iloc[-1]
    ultimo_titulados = titulados_ts.iloc[-1]
    tasa_final = (ultimo_titulados / ultimo_egresados) * 100 if ultimo_egresados > 0 else 0
    
    plt.annotate(f'Tasa de Conversión: {tasa_final:.1f}%',
                 xy=(all_dates[-1], ultimo_titulados),
                 xytext=(all_dates[-1] - pd.Timedelta(days=365*2), ultimo_titulados + (ultimo_egresados*0.1)),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=12, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8))

    # Save
    output_path = os.path.join(FIGURES_DIR, "longitudinal_funnel_gap.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Graph saved to {output_path}")

if __name__ == "__main__":
    matricula, egresados, titulados = load_data()
    create_funnel_chart(matricula, egresados, titulados)
