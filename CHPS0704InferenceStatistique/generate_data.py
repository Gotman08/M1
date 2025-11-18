"""
Script pour générer le dataset synthétique sur la santé cardiaque

Ce dataset contient :
- Variables quantitatives : age, cholesterol, heart_rate, blood_pressure
- Variable qualitative binaire : heart_disease (0=non, 1=oui)
"""

import numpy as np
import pandas as pd

# Fixer la graine pour reproductibilité
np.random.seed(42)

# Nombre d'observations
n = 500

# Génération des données
data = {
    # Âge : distribution normale centrée sur 55 ans
    'age': np.random.normal(loc=55, scale=12, size=n).clip(25, 85).astype(int),

    # Cholestérol : distribution normale avec moyenne 210 mg/dL
    'cholesterol': np.random.normal(loc=210, scale=40, size=n).clip(120, 350).round(1),

    # Fréquence cardiaque : distribution normale
    'heart_rate': np.random.normal(loc=75, scale=12, size=n).clip(50, 120).astype(int),

    # Pression artérielle : corrélée avec l'âge
    'blood_pressure': None,  # sera calculé ci-dessous

    # Maladie cardiaque : variable binaire
    'heart_disease': None  # sera calculé ci-dessous
}

# Créer le DataFrame temporaire
df_temp = pd.DataFrame({k: v for k, v in data.items() if v is not None})

# Pression artérielle corrélée avec l'âge (pour la régression linéaire)
# Relation : BP = 90 + 0.8 * age + bruit
blood_pressure_base = 90 + 0.8 * df_temp['age']
blood_pressure_noise = np.random.normal(0, 10, n)
data['blood_pressure'] = (blood_pressure_base + blood_pressure_noise).clip(90, 180).astype(int)

# Maladie cardiaque : probabilité augmente avec âge, cholestérol élevé
# Modèle logistique simplifié ajusté pour avoir ~35% de malades
risk_score = (
    0.05 * (df_temp['age'] - 55) +
    0.01 * (df_temp['cholesterol'] - 200) +
    0.02 * (df_temp['heart_rate'] - 75) - 0.5
)
prob_disease = 1 / (1 + np.exp(-risk_score))
data['heart_disease'] = (prob_disease > np.random.uniform(0, 1, n)).astype(int)

# Créer le DataFrame final
df = pd.DataFrame(data)

# Sauvegarder
df.to_csv('data/heart_health_data.csv', index=False)

print("Dataset généré avec succès !")
print(f"\nNombre d'observations : {len(df)}")
print(f"\nAperçu des données :")
print(df.head(10))
print(f"\nStatistiques descriptives :")
print(df.describe())
print(f"\nValeurs manquantes :")
print(df.isnull().sum())
print(f"\nRépartition des maladies cardiaques :")
print(df['heart_disease'].value_counts())
print(f"\nFichier sauvegardé : data/heart_health_data.csv")
