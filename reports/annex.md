# Anexo Técnico: Metodología y Validación Estadística

Este anexo detalla la metodología científica, las pruebas estadísticas y los modelos predictivos utilizados en el desarrollo del sistema de prevención de deserción estudiantil. Se prioriza el rigor matemático y la reproducibilidad de los resultados.

## A. Fuente de Datos y Preprocesamiento

Para la validación de las hipótesis y el entrenamiento del modelo, se utilizó un **Dataset Proxy** de alta calidad proveniente del *UCI Machine Learning Repository* (Predict Students' Dropout and Academic Success), que comparte características demográficas y socioeconómicas similares a la población objetivo.

### Pipeline de Procesamiento

El pipeline de limpieza de datos (`src/utils/data_processing.py`) implementó las siguientes etapas críticas para asegurar la integridad del análisis:

1. **Manejo de Valores Nulos:** Imputación de variables numéricas mediante la mediana y categóricas mediante la moda para preservar la distribución original.
2. **Codificación de Variables:** Transformación de variables categóricas nominales utilizando *One-Hot Encoding* y variables ordinales mediante *Label Encoding*.
3. **Escalado:** Normalización de variables numéricas (e.g., edad, tasa de inflación) para optimizar la convergencia de los algoritmos basados en gradiente.
4. **Balanceo de Clases:** Aplicación de **SMOTE (Synthetic Minority Over-sampling Technique)** en el conjunto de entrenamiento para mitigar el desbalance de la clase minoritaria (*Dropout*), mejorando la sensibilidad del modelo.

---

## B. Pruebas Estadísticas

Se realizaron pruebas de hipótesis para validar estadísticamente las relaciones entre variables críticas y la deserción.

### B.1 Prueba de Independencia Chi-Cuadrado ($\chi^2$)

Utilizada para evaluar la asociación entre variables categóricas (e.g., Rendimiento Académico, Expectativas) y la variable objetivo (*Abandono*).

**Fórmula:**
$$ \chi^2 = \sum \frac{(O_i - E_i)^2}{E_i} $$
Donde $O_i$ es la frecuencia observada y $E_i$ es la frecuencia esperada.

#### Resultados Empíricos

**Hipótesis 1: Rendimiento Académico vs. Abandono**

* **Estadístico $\chi^2$:** 5.8101
* **P-valor:** 0.0547
* **Conclusión:** El p-valor es ligeramente superior a 0.05, lo que sugiere una asociación marginalmente no significativa en esta muestra específica, aunque la tendencia es observable.

**Hipótesis 3: Expectativas de Carrera vs. Abandono**

* **Estadístico $\chi^2$:** 6.7594
* **P-valor:** 0.0341
* **Conclusión:** Se rechaza la hipótesis nula ($p < 0.05$). Existe una dependencia estadísticamente significativa entre las expectativas alineadas con la carrera y la retención.

**Snippet de Implementación (`src/analysis/chi_square/src/02_hipotesis_rendimiento.py`):**

```python
from scipy.stats import chi2_contingency
import pandas as pd

def analizar_chi_cuadrado(df, col_independiente, col_objetivo='Target'):
    contingency_table = pd.crosstab(df[col_independiente], df[col_objetivo])
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    return chi2, p

# Ejemplo de uso
chi2_val, p_val = analizar_chi_cuadrado(df, 'Rendimiento_Semestre_Anterior')
```

### B.2 Prueba H de Kruskal-Wallis

Utilizada para comparar las medianas de una variable ordinal (Frecuencia de Pensamientos de Abandono) a través de diferentes grupos, sin asumir normalidad en los datos.

**Fórmula:**
$$ H = (N-1) \frac{\sum_{i=1}^{g} n_i (\bar{r}_{i\cdot} - \bar{r})^2}{\sum_{i=1}^{g} \sum_{j=1}^{n_i} (r_{ij} - \bar{r})^2} $$

#### Resultados Empíricos

**Análisis: Frecuencia de Pensamientos vs. Rendimiento Académico**

* **Estadístico H:** 8.3955
* **P-valor:** 0.0150
* **Conclusión:** Diferencia significativa ($p < 0.05$). Los estudiantes con menor rendimiento reportan una frecuencia significativamente mayor de pensamientos de abandono.

**Snippet de Implementación (`src/analysis/chi_square/src/05_analisis_ordinal.py`):**

```python
from scipy.stats import kruskal

def prueba_kruskal(df, grupo_col, valor_col):
    grupos = [grupo[valor_col].values for nombre, grupo in df.groupby(grupo_col)]
    stat, p = kruskal(*grupos)
    return stat, p
```

---

## C. Modelado Predictivo (XGBoost Binario)

Se seleccionó **XGBoost (Extreme Gradient Boosting)** por su robustez frente a datos desbalanceados y su capacidad de interpretabilidad. A diferencia de enfoques anteriores multiclase, se optimizó un **modelo binario** (*Dropout* vs. *No Dropout*) para maximizar la precisión en la detección de casos de riesgo, que es la prioridad operativa.

### Configuración del Modelo

El modelo fue configurado con una función objetivo logística binaria para predecir la probabilidad de deserción.

```python
model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    n_estimators=2000,
    learning_rate=0.02,
    max_depth=10,
    use_label_encoder=False,
    random_state=42
)
```

### C.1 Métricas de Desempeño

El modelo binario demostró una mejora sustancial en la identificación de la clase minoritaria (*Dropout*) en comparación con el modelo base.

* **AUC-ROC:** **0.9301** (Excelente capacidad de discriminación).
* **F1-Score (Clase Dropout):** **0.81** (Balance óptimo entre precisión y exhaustividad).
* **Precision (Clase Dropout):** **0.85** (Alta confiabilidad en las alertas generadas).

**Matriz de Confusión del Conjunto de Prueba:**

* **Verdaderos Positivos (Detectados):** 221 estudiantes (Riesgo real identificado).
* **Falsos Negativos (Omitidos):** 63 estudiantes (Riesgo no detectado).
* **Falsos Positivos (Falsa Alarma):** 40 estudiantes.
* **Verdaderos Negativos:** 561 estudiantes.

*Nota: Se priorizó la minimización de Falsos Negativos (Maximizar Recall) mediante el ajuste del umbral de decisión.*

### C.2 Importancia de Variables (Feature Importance)

Las 5 variables más determinantes para la predicción del riesgo, según la ganancia de información del modelo, son:

1. **Ratio_Aprobacion_S2:** Rendimiento académico reciente (2do semestre).
2. **Tuition fees up to date:** Estado de pago de matrículas (indicador financiero).
3. **Curricular units 1st sem (enrolled):** Carga académica inicial.
4. **Ratio_Aprobacion_S1:** Rendimiento académico histórico (1er semestre).
5. **Socioeconomico_Riesgo:** Índice compuesto de vulnerabilidad socioeconómica.

---

## D. Análisis Comparativo de Costos (Buy vs. Build)

Se presenta la proyección financiera para una matrícula de **57,000 estudiantes**, contrastando el desarrollo interno (*In-House*) frente al licenciamiento comercial (*SaaS Enterprise*).

| Concepto de Costo | Desarrollo In-House (Build) | Solución SaaS (Buy) | Diferencia |
| :--- | :--- | :--- | :--- |
| **Modelo de Costo** | Equipo de Desarrollo (Nómina Local) + Nube | Licenciamiento por Estudiante ($5 USD/año) | - |
| **Costo Inicial (Año 1)** | **~$135,000 USD** (Equipo "Tiger Team" + Setup AWS) | **~$385,000 USD** (Licencias + Cuota de Implementación) | **Ahorro In-House: ~65%** |
| **Costo Recurrente (Año 2+)** | **~$80,000 USD** (Mantenimiento y Nube) | **~$285,000 USD** (Renovación de Licencias Anual) | **Ahorro In-House: ~72%** |
| **Propiedad Intelectual** | **100% UNRC** (Activo Institucional) | **0%** (Alquiler de Software) | **Estratégico** |
| **Dependencia** | **Baja** (Código Abierto / Estándares) | **Alta** (Vendor Lock-in / Dolarizado) | **Riesgo** |

**Conclusión Financiera:**
Aunque el desarrollo interno conlleva un esfuerzo de gestión inicial, la estrategia *In-House* representa un **ahorro acumulado superior a $500,000 USD en 3 años** y elimina la exposición al riesgo cambiario de las licencias dolarizadas, alineándose con la austeridad institucional.

---

> **E. Declaración de Reproducibilidad y Acceso al Código**
>
> Con el objetivo de garantizar la transparencia metodológica y permitir la auditoría independiente de los resultados, el código fuente completo, los notebooks de exploración y el pipeline de procesamiento de datos se encuentran disponibles en el repositorio oficial del proyecto.
>
> El repositorio ha sido estructurado como un **compendio digital** que acompaña a este informe, donde se pueden consultar:
>
> * **Notebooks Secuenciales:** Desde la limpieza de datos (`02-Preprocessing`) hasta la evaluación del modelo binario (`04-Evaluation`).
> * **Scripts de Validación:** Código fuente de las pruebas Chi-Cuadrado y Kruskal-Wallis.
> * **Dashboard:** Código del prototipo funcional de intervención.
>
> **Enlace al Repositorio:** [Insertar URL de GitHub Aquí]
