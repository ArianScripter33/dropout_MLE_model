"""
Script to generate all binary model visualizations for the scientific annex.
This script will:
1. Generate the binary confusion matrix from the main model
2. Extract ROC/AUC curve from explicacion_auc_roc.ipynb
3. Extract F1 score visualization from explicacion_f1_score.ipynb
4. Save all figures to reports/figures/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_curve, 
    auc,
    f1_score,
    precision_score,
    recall_score
)
from xgboost import XGBClassifier
import sys
import os

# Set up paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configuration
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams['font.size'] = 12

def load_and_prepare_data():
    """Load and prepare binary classification data"""
    print("📊 Loading data...")
    df = pd.read_parquet('../data/processed/preprocessed_data.parquet')
    
    # Separate features and target
    X = df.drop('Target', axis=1)
    y = df['Target']
    
    # Binarize: 1 if 'Dropout', 0 otherwise
    y = y.apply(lambda x: 1 if x == 'Dropout' else 0)
    
    # Convert any object columns to numeric (one-hot encode if needed)
    print("🔄 Converting data types...")
    for col in X.columns:
        if X[col].dtype == 'object':
            print(f"  - Converting {col} from object to numeric")
           # Try to convert to numeric first
            try:
                X[col] = pd.to_numeric(X[col])
            except:
                # If that fails, use label encoding
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✓ Data loaded: {df.shape}")
    print(f"✓ Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"✓ All features are numeric: {X_train.dtypes.nunique() <= 3}")  # int, float, bool
    
    return X_train, X_test, y_train, y_test

def train_binary_model(X_train, y_train):
    """Train binary XGBoost model"""
    print("\n🔧 Training binary model...")
    
    model = XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        use_label_encoder=False,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    print("✓ Model trained successfully")
    
    return model

def generate_confusion_matrix(y_test, y_pred, save_path):
    """Generate and save binary confusion matrix"""
    print("\n📈 Generando Matriz de Confusión...")
    
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='RdYlGn_r',
        xticklabels=['Sin Deserción', 'Deserción'],
        yticklabels=['Sin Deserción', 'Deserción'],
        cbar_kws={'label': 'Cantidad'},
        linewidths=2,
        linecolor='black'
    )
    plt.xlabel('Etiqueta Predicha', fontsize=14, fontweight='bold')
    plt.ylabel('Etiqueta Real', fontsize=14, fontweight='bold')
    plt.title('Matriz de Confusión del Modelo Binario\n(Detección de Deserción)', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add text annotations with percentages
    total = cm.sum()
    for i in range(2):
        for j in range(2):
            pct = (cm[i, j] / total) * 100
            plt.text(j + 0.5, i + 0.7, f'({pct:.1f}%)', 
                    ha='center', va='center', fontsize=10, color='gray')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado en: {save_path}")
    plt.close()

def generate_roc_curve(y_test, y_pred_proba, save_path):
    """Generate and save ROC/AUC curve"""
    print("\n📈 Generando Curva ROC/AUC...")
    
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='#FF6B35', lw=3, 
             label=f'Modelo Binario (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', 
             label='Clasificador Aleatorio (AUC = 0.50)')
    
    # Fill area under curve
    plt.fill_between(fpr, tpr, alpha=0.2, color='#FF6B35')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Tasa de Falsos Positivos (1 - Especificidad)', fontsize=12, fontweight='bold')
    plt.ylabel('Tasa de Verdaderos Positivos (Sensibilidad)', fontsize=12, fontweight='bold')
    plt.title('Curva ROC - Predicción de Deserción Binaria', 
              fontsize=14, fontweight='bold', pad=15)
    plt.legend(loc='lower right', fontsize=11, frameon=True, shadow=True)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado en: {save_path}")
    print(f"✓ Puntaje AUC: {roc_auc:.4f}")
    plt.close()

def generate_f1_comparison(y_test, y_pred, save_path):
    """Generate F1 score comparison visualization"""
    print("\n📈 Generando Análisis de F1-Score...")
    
    # Calculate metrics
    precision_0 = precision_score(y_test, y_pred, pos_label=0, zero_division=0)
    recall_0 = recall_score(y_test, y_pred, pos_label=0, zero_division=0)
    f1_0 = f1_score(y_test, y_pred, pos_label=0, zero_division=0)
    
    precision_1 = precision_score(y_test, y_pred, pos_label=1, zero_division=0)
    recall_1 = recall_score(y_test, y_pred, pos_label=1, zero_division=0)
    f1_1 = f1_score(y_test, y_pred, pos_label=1, zero_division=0)
    
    # Create comparison plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Metrics by class
    metrics_data = pd.DataFrame({
        'Sin Deserción': [precision_0, recall_0, f1_0],
        'Deserción': [precision_1, recall_1, f1_1]
    }, index=['Precisión', 'Exhaustividad', 'F1-Score'])
    
    metrics_data.plot(kind='bar', ax=axes[0], color=['#4ECDC4', '#FF6B6B'], width=0.7)
    axes[0].set_title('Comparación de Métricas por Clase', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Puntaje', fontsize=12)
    axes[0].set_ylim([0, 1])
    axes[0].legend(title='Clase', frameon=True, shadow=True)
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)
    
    # Add value labels on bars
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt='%.3f', padding=3, fontsize=9)
    
    # Plot 2: F1-Score breakdown for Dropout class
    components = pd.DataFrame({
        'Value': [precision_1, recall_1, f1_1]
    }, index=['Precisión\n(Calidad)', 'Exhaustividad\n(Cobertura)', 'F1-Score\n(Balance)'])
    
    colors_comp = ['#FFD93D', '#6BCF7F', '#FF6B35']
    components.plot(kind='barh', ax=axes[1], color=colors_comp, legend=False, width=0.6)
    axes[1].set_title('Desglose de Métricas - Clase Deserción', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Puntaje', fontsize=12)
    axes[1].set_xlim([0, 1])
    axes[1].grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, v in enumerate(components['Value']):
        axes[1].text(v + 0.02, i, f'{v:.3f}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado en: {save_path}")
    print(f"✓ F1-Score (Deserción): {f1_1:.3f}")
    plt.close()

def generate_feature_importance(model, feature_names, save_path):
    """Generate feature importance visualization"""
    print("\n📈 Generando Importancia de Variables...")
    
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False).head(20)
    
    plt.figure(figsize=(10, 8))
    bars = plt.barh(range(len(importance_df)), importance_df['Importance'], color='#4ECDC4')
    
    # Color gradient
    for i, bar in enumerate(bars):
        bar.set_color(plt.cm.viridis(i / len(importance_df)))
    
    plt.yticks(range(len(importance_df)), importance_df['Feature'])
    plt.xlabel('Importancia (Ganancia)', fontsize=12, fontweight='bold')
    plt.ylabel('Variable', fontsize=12, fontweight='bold')
    plt.title('Top 20 Variables Más Importantes\nModelo Binario de Predicción de Deserción', 
              fontsize=14, fontweight='bold', pad=15)
    plt.gca().invert_yaxis()
    plt.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado en: {save_path}")
    plt.close()

def print_classification_report(y_test, y_pred):
    """Print detailed classification report"""
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT - BINARY MODEL")
    print("="*60)
    report = classification_report(
        y_test, y_pred, 
        target_names=['No Dropout', 'Dropout'],
        digits=4
    )
    print(report)
    print("="*60)

def main():
    """Main execution function"""
    print("🚀 Starting visualization generation for Binary Model...\n")
    
    # Paths
    figures_dir = '../reports/figures'
    os.makedirs(figures_dir, exist_ok=True)
    
    # Load data
    X_train, X_test, y_train, y_test = load_and_prepare_data()
    
    # Train model
    model = train_binary_model(X_train, y_train)
    
    # Predictions
    print("\n🔮 Making predictions...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Print classification report
    print_classification_report(y_test, y_pred)
    
    # Generate all visualizations
    generate_confusion_matrix(
        y_test, y_pred, 
        os.path.join(figures_dir, 'binary_confusion_matrix.png')
    )
    
    generate_roc_curve(
        y_test, y_pred_proba,
        os.path.join(figures_dir, 'roc_auc_curve.png')
    )
    
    generate_f1_comparison(
        y_test, y_pred,
        os.path.join(figures_dir, 'f1_score_analysis.png')
    )
    
    generate_feature_importance(
        model, X_train.columns,
        os.path.join(figures_dir, 'binary_feature_importance.png')
    )
    
    print("\n" + "="*60)
    print("✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"\nFigures saved to: {os.path.abspath(figures_dir)}")
    print("\nGenerated files:")
    print("  1. binary_confusion_matrix.png")
    print("  2. roc_auc_curve.png")
    print("  3. f1_score_analysis.png")
    print("  4. binary_feature_importance.png")

if __name__ == "__main__":
    main()
