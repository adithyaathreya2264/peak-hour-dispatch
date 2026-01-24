"""
Train XGBoost model for ride denial prediction

This script trains a binary classifier to predict whether a driver will accept or deny a ride
based on trip characteristics, driver state, and contextual features.
"""
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    roc_curve
)
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed
np.random.seed(42)


def load_data():
    """Load training data"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'processed', 'training_data.csv')
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples")
    return df


def prepare_features(df):
    """Prepare features and target"""
    # Feature columns (exclude target and metadata)
    feature_cols = [col for col in df.columns if col not in ['accepted', 'true_acceptance_prob']]
    
    X = df[feature_cols]
    y = df['accepted']
    
    print(f"\nFeatures ({len(feature_cols)}):")
    for col in feature_cols:
        print(f"  - {col}")
    
    print(f"\nTarget distribution:")
    print(f"  Accepted: {y.sum()} ({y.mean()*100:.1f}%)")
    print(f"  Denied: {(1-y).sum()} ({(1-y).mean()*100:.1f}%)")
    
    return X, y, feature_cols


def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost classifier"""
    print("\n" + "="*60)
    print(" Training XGBoost Model")
    print("="*60)
    
    # XGBoost parameters
    params = {
        'objective': 'binary:logistic',
        'eval_metric': ['auc', 'logloss'],
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'min_child_weight': 5,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'tree_method': 'hist',
    }
    
    model = xgb.XGBClassifier(**params)
    
    # Train with early stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=10
    )
    
    print("\n✓ Model training complete!")
    return model


def evaluate_model(model, X_test, y_test, feature_names):
    """Evaluate model performance"""
    print("\n" + "="*60)
    print(" Model Evaluation")
    print("="*60)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Classification metrics
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Denied', 'Accepted']))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(f"                Predicted")
    print(f"              Denied  Accepted")
    print(f"Actual Denied    {cm[0,0]:4d}    {cm[0,1]:4d}")
    print(f"     Accepted    {cm[1,0]:4d}    {cm[1,1]:4d}")
    
    # ROC-AUC
    auc_score = roc_auc_score(y_test, y_pred_proba)
    print(f"\n🎯 ROC-AUC Score: {auc_score:.4f}")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:30s}: {row['importance']:.4f}")
    
    return {
        'auc': auc_score,
        'feature_importance': feature_importance,
        'y_pred_proba': y_pred_proba
    }


def plot_results(model, X_test, y_test, metrics, output_dir):
    """Generate and save evaluation plots"""
    print("\n" + "="*60)
    print(" Generating Visualizations")
    print("="*60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Feature Importance
    fig, ax = plt.subplots(figsize=(10, 8))
    top_features = metrics['feature_importance'].head(15)
    ax.barh(top_features['feature'], top_features['importance'])
    ax.set_xlabel('Importance')
    ax.set_title('Top 15 Feature Importances')
    ax.invert_yaxis()
    plt.tight_layout()
    importance_path = os.path.join(output_dir, 'feature_importance.png')
    plt.savefig(importance_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved feature importance plot: {importance_path}")
    plt.close()
    
    # 2. ROC Curve
    fig, ax = plt.subplots(figsize=(8, 6))
    fpr, tpr, _ = roc_curve(y_test, metrics['y_pred_proba'])
    ax.plot(fpr, tpr, label=f'ROC curve (AUC = {metrics["auc"]:.3f})', linewidth=2)
    ax.plot([0, 1], [0, 1], 'k--', label='Random')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    ax.legend()
    ax.grid(alpha=0.3)
    roc_path = os.path.join(output_dir, 'roc_curve.png')
    plt.savefig(roc_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved ROC curve: {roc_path}")
    plt.close()
    
    # 3. Precision-Recall Curve
    fig, ax = plt.subplots(figsize=(8, 6))
    precision, recall, _ = precision_recall_curve(y_test, metrics['y_pred_proba'])
    ax.plot(recall, precision, linewidth=2)
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_title('Precision-Recall Curve')
    ax.grid(alpha=0.3)
    pr_path = os.path.join(output_dir, 'precision_recall_curve.png')
    plt.savefig(pr_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved precision-recall curve: {pr_path}")
    plt.close()
    
    # 4. Prediction Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(metrics['y_pred_proba'][y_test == 0], bins=50, alpha=0.6, label='Denied (Actual)', color='red')
    ax.hist(metrics['y_pred_proba'][y_test == 1], bins=50, alpha=0.6, label='Accepted (Actual)', color='green')
    ax.set_xlabel('Predicted Acceptance Probability')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Predicted Probabilities')
    ax.legend()
    ax.grid(alpha=0.3)
    dist_path = os.path.join(output_dir, 'prediction_distribution.png')
    plt.savefig(dist_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved prediction distribution: {dist_path}")
    plt.close()


def save_model(model, feature_names, output_dir):
    """Save trained model and metadata"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_dir, 'denial_model.pkl')
    joblib.dump(model, model_path)
    print(f"\n✓ Saved model to: {model_path}")
    
    # Save feature names
    features_path = os.path.join(output_dir, 'feature_names.txt')
    with open(features_path, 'w') as f:
        for feature in feature_names:
            f.write(f"{feature}\n")
    print(f"✓ Saved feature names to: {features_path}")
    
    return model_path


def main():
    print("=" * 60)
    print(" XGBoost Ride Denial Prediction Model Training")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    
    # Split data (70% train, 15% validation, 15% test)
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp)  # 0.176 * 0.85 = 0.15
    
    print(f"\nDataset splits:")
    print(f"  Training:   {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  Validation: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  Test:       {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, feature_names)
    
    # Generate plots
    plots_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ml-notebooks')
    plot_results(model, X_test, y_test, metrics, plots_dir)
    
    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app', 'ml', 'models')
    save_model(model, feature_names, model_dir)
    
    print("\n" + "=" * 60)
    print(" ✅ Model training pipeline complete!")
    print("=" * 60)
    print(f"\n📊 Final Results:")
    print(f"  - ROC-AUC Score: {metrics['auc']:.4f}")
    print(f"  - Model saved and ready for deployment")


if __name__ == "__main__":
    main()
