"""
Projet : Analyse Statistique et Modélisation de Données
Module : Inférence statistique et modélisation

Ce script réalise une analyse statistique complète incluant :
- Analyse descriptive et estimation ponctuelle
- Intervalles de confiance
- Tests d'hypothèses
- Modélisation par régression linéaire

Dataset : Données sur la santé cardiaque
Variables : âge, cholestérol, fréquence cardiaque, pression artérielle, maladie cardiaque
"""

# Configuration de l'encodage pour Windows
import sys
import os
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if sys.stdout.encoding != 'utf-8':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class AnalyseStatistique:
    """Classe principale pour l'analyse statistique complète"""

    def __init__(self, data_path):
        """
        Initialisation avec le chemin vers les données

        Parameters:
        -----------
        data_path : str
            Chemin vers le fichier CSV contenant les données
        """
        self.data = pd.read_csv(data_path)
        self.results = {}

    def analyse_descriptive(self):
        """
        A. ANALYSE DESCRIPTIVE ET ESTIMATION PONCTUELLE

        Calcule les statistiques descriptives :
        - Moyenne empirique : X̄ₙ = (1/n) Σ Xᵢ
        - Variance empirique : S² = (1/(n-1)) Σ (Xᵢ - X̄ₙ)²
        - Écart-type empirique : S = √S²
        """
        print("="*80)
        print("A. ANALYSE DESCRIPTIVE ET ESTIMATION PONCTUELLE")
        print("="*80)

        # Sélection des variables quantitatives
        vars_quant = ['age', 'cholesterol', 'heart_rate', 'blood_pressure']

        stats_desc = {}
        for var in vars_quant:
            data_var = self.data[var].dropna()
            n = len(data_var)

            # Statistiques de base
            moyenne = np.mean(data_var)  # X̄ₙ
            variance = np.var(data_var, ddof=1)  # S²
            ecart_type = np.std(data_var, ddof=1)  # S

            stats_desc[var] = {
                'n': n,
                'moyenne': moyenne,
                'variance': variance,
                'ecart_type': ecart_type,
                'min': np.min(data_var),
                'max': np.max(data_var),
                'mediane': np.median(data_var),
                'Q1': np.percentile(data_var, 25),
                'Q3': np.percentile(data_var, 75)
            }

            print(f"\n{var.upper()}")
            print(f"  n = {n}")
            print(f"  Moyenne (X_bar) = {moyenne:.2f}")
            print(f"  Variance (S^2) = {variance:.2f}")
            print(f"  Ecart-type (S) = {ecart_type:.2f}")
            print(f"  Mediane = {stats_desc[var]['mediane']:.2f}")
            print(f"  [Min, Max] = [{stats_desc[var]['min']:.2f}, {stats_desc[var]['max']:.2f}]")

        self.results['stats_descriptives'] = stats_desc

        # Visualisations
        self._plot_histogrammes(vars_quant)

        return stats_desc

    def _plot_histogrammes(self, variables):
        """Trace les histogrammes pour visualiser les distributions"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.ravel()

        for i, var in enumerate(variables):
            data_var = self.data[var].dropna()

            axes[i].hist(data_var, bins=30, alpha=0.7, edgecolor='black', density=True)
            axes[i].axvline(np.mean(data_var), color='red', linestyle='--',
                           linewidth=2, label=f'Moyenne = {np.mean(data_var):.2f}')
            axes[i].set_xlabel(var.capitalize())
            axes[i].set_ylabel('Densité')
            axes[i].set_title(f'Distribution de {var}')
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('figures/histogrammes.png', dpi=300, bbox_inches='tight')
        print("\n✓ Histogrammes sauvegardés dans figures/histogrammes.png")
        plt.close()

    def estimation_parametres(self, variable='cholesterol'):
        """
        MÉTHODES D'ESTIMATION ÉLABORÉES

        Propose une loi Normale N(μ, σ²) et estime les paramètres par :
        1. Méthode des moments
        2. Méthode du Maximum de Vraisemblance (MLE)

        Parameters:
        -----------
        variable : str
            Variable à analyser (par défaut 'cholesterol')
        """
        print("\n" + "="*80)
        print("ESTIMATION DES PARAMÈTRES - LOI NORMALE")
        print("="*80)

        data_var = self.data[variable].dropna().values
        n = len(data_var)

        print(f"\nVariable analysée : {variable}")
        print(f"Hypothèse : {variable} ~ N(μ, σ²)")

        # 1. MÉTHODE DES MOMENTS
        print("\n1. MÉTHODE DES MOMENTS")
        print("-" * 40)
        print("Principe : E[X] = μ  et  Var(X) = σ²")
        print("          X̄ₙ = μ̂  et  S² = σ̂²")

        mu_moments = np.mean(data_var)
        sigma2_moments = np.var(data_var, ddof=1)

        print(f"\nEstimateurs des moments :")
        print(f"  μ̂_MM = {mu_moments:.4f}")
        print(f"  σ̂²_MM = {sigma2_moments:.4f}")

        # 2. MÉTHODE DU MAXIMUM DE VRAISEMBLANCE
        print("\n2. MÉTHODE DU MAXIMUM DE VRAISEMBLANCE (MLE)")
        print("-" * 40)
        print("Log-vraisemblance : ℓ(μ,σ²) = -n/2·log(2π) - n/2·log(σ²) - 1/(2σ²)·Σ(xᵢ-μ)²")

        # Fonction de log-vraisemblance négative (à minimiser)
        def neg_log_likelihood(params):
            mu, log_sigma = params
            sigma = np.exp(log_sigma)  # Pour garantir σ > 0
            ll = -n/2 * np.log(2*np.pi) - n * log_sigma - 0.5/sigma**2 * np.sum((data_var - mu)**2)
            return -ll

        # Optimisation
        result = minimize(neg_log_likelihood, x0=[np.mean(data_var), np.log(np.std(data_var))],
                         method='BFGS')

        mu_mle = result.x[0]
        sigma2_mle = np.exp(result.x[1])**2

        print(f"\nEstimateurs du MLE :")
        print(f"  μ̂_MLE = {mu_mle:.4f}")
        print(f"  σ̂²_MLE = {sigma2_mle:.4f}")

        # 3. COMPARAISON DES ESTIMATEURS
        print("\n3. COMPARAISON DES ESTIMATEURS")
        print("-" * 40)

        # Simulation pour calculer biais et MSE
        n_sim = 1000
        mu_true = mu_mle
        sigma_true = np.sqrt(sigma2_mle)

        estimates_mm_mu = []
        estimates_mle_mu = []

        for _ in range(n_sim):
            sample = np.random.normal(mu_true, sigma_true, n)
            estimates_mm_mu.append(np.mean(sample))
            estimates_mle_mu.append(np.mean(sample))

        biais_mm = np.mean(estimates_mm_mu) - mu_true
        biais_mle = np.mean(estimates_mle_mu) - mu_true
        mse_mm = np.mean((np.array(estimates_mm_mu) - mu_true)**2)
        mse_mle = np.mean((np.array(estimates_mle_mu) - mu_true)**2)

        print(f"\nPour l'estimateur de μ (sur {n_sim} simulations) :")
        print(f"  Méthode des Moments :")
        print(f"    Biais = {biais_mm:.6f}")
        print(f"    MSE = {mse_mm:.6f}")
        print(f"  Maximum de Vraisemblance :")
        print(f"    Biais = {biais_mle:.6f}")
        print(f"    MSE = {mse_mle:.6f}")

        # Test d'ajustement (Kolmogorov-Smirnov)
        ks_stat, p_value = stats.kstest(data_var, 'norm', args=(mu_mle, np.sqrt(sigma2_mle)))
        print(f"\nTest d'ajustement de Kolmogorov-Smirnov :")
        print(f"  Statistique KS = {ks_stat:.4f}")
        print(f"  p-value = {p_value:.4f}")
        print(f"  Conclusion : {'Ajustement acceptable' if p_value > 0.05 else 'Ajustement rejeté'} (α=0.05)")

        self.results['estimation'] = {
            'variable': variable,
            'mu_moments': mu_moments,
            'sigma2_moments': sigma2_moments,
            'mu_mle': mu_mle,
            'sigma2_mle': sigma2_mle,
            'biais_mm': biais_mm,
            'biais_mle': biais_mle,
            'mse_mm': mse_mm,
            'mse_mle': mse_mle
        }

        # Visualisation de l'ajustement
        self._plot_ajustement(data_var, mu_mle, sigma2_mle, variable)

        return self.results['estimation']

    def _plot_ajustement(self, data, mu, sigma2, variable):
        """Visualise l'ajustement de la loi normale aux données"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Histogramme
        ax.hist(data, bins=30, alpha=0.6, density=True, edgecolor='black', label='Données empiriques')

        # Loi normale ajustée
        x = np.linspace(data.min(), data.max(), 200)
        y = stats.norm.pdf(x, mu, np.sqrt(sigma2))
        ax.plot(x, y, 'r-', linewidth=2, label=f'N({mu:.2f}, {sigma2:.2f})')

        ax.set_xlabel(variable.capitalize())
        ax.set_ylabel('Densité')
        ax.set_title(f'Ajustement de la loi normale pour {variable}')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'figures/ajustement_{variable}.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Graphique d'ajustement sauvegardé dans figures/ajustement_{variable}.png")
        plt.close()

    def intervalles_confiance(self, alpha=0.05):
        """
        B. INTERVALLES DE CONFIANCE

        Construit des IC à (1-α)×100% pour :
        - La moyenne μ (loi de Student)
        - La variance σ² (loi du χ²)
        - Une proportion p (approximation normale)

        Parameters:
        -----------
        alpha : float
            Niveau de risque (par défaut 0.05 pour IC à 95%)
        """
        print("\n" + "="*80)
        print(f"B. INTERVALLES DE CONFIANCE (niveau {(1-alpha)*100:.0f}%)")
        print("="*80)

        ic_results = {}

        # IC pour la moyenne (loi de Student)
        print("\n1. INTERVALLE DE CONFIANCE POUR LA MOYENNE μ")
        print("-" * 50)

        variable = 'cholesterol'
        data_var = self.data[variable].dropna().values
        n = len(data_var)
        mean = np.mean(data_var)
        std = np.std(data_var, ddof=1)
        se = std / np.sqrt(n)

        # Quantile de Student
        t_crit = stats.t.ppf(1 - alpha/2, df=n-1)

        ic_mean_lower = mean - t_crit * se
        ic_mean_upper = mean + t_crit * se

        print(f"Variable : {variable}")
        print(f"  n = {n}")
        print(f"  X̄ = {mean:.2f}")
        print(f"  S = {std:.2f}")
        print(f"  Erreur standard = S/√n = {se:.4f}")
        print(f"  Quantile t_{{n-1;{1-alpha/2}}} = {t_crit:.4f}")
        print(f"\n  IC_{(1-alpha)*100:.0f}%(μ) = [{ic_mean_lower:.2f}, {ic_mean_upper:.2f}]")
        print(f"\n  Interprétation : Avec {(1-alpha)*100:.0f}% de confiance, la vraie moyenne")
        print(f"  du {variable} se situe entre {ic_mean_lower:.2f} et {ic_mean_upper:.2f}.")

        ic_results['mean'] = {
            'variable': variable,
            'estimate': mean,
            'lower': ic_mean_lower,
            'upper': ic_mean_upper,
            'confidence': 1-alpha
        }

        # IC pour la variance (loi du χ²)
        print("\n2. INTERVALLE DE CONFIANCE POUR LA VARIANCE σ²")
        print("-" * 50)

        var = np.var(data_var, ddof=1)
        chi2_lower = stats.chi2.ppf(alpha/2, df=n-1)
        chi2_upper = stats.chi2.ppf(1-alpha/2, df=n-1)

        ic_var_lower = (n-1) * var / chi2_upper
        ic_var_upper = (n-1) * var / chi2_lower

        print(f"  S² = {var:.2f}")
        print(f"  χ²_{{n-1;{alpha/2}}} = {chi2_lower:.4f}")
        print(f"  χ²_{{n-1;{1-alpha/2}}} = {chi2_upper:.4f}")
        print(f"\n  IC_{(1-alpha)*100:.0f}%(σ²) = [{ic_var_lower:.2f}, {ic_var_upper:.2f}]")
        print(f"\n  IC_{(1-alpha)*100:.0f}%(σ) = [{np.sqrt(ic_var_lower):.2f}, {np.sqrt(ic_var_upper):.2f}]")

        ic_results['variance'] = {
            'estimate': var,
            'lower': ic_var_lower,
            'upper': ic_var_upper
        }

        # IC pour une proportion (variable qualitative binaire)
        print("\n3. INTERVALLE DE CONFIANCE POUR UNE PROPORTION p")
        print("-" * 50)

        # Proportion de personnes avec maladie cardiaque
        n_total = len(self.data)
        n_success = sum(self.data['heart_disease'] == 1)
        p_hat = n_success / n_total

        # Approximation normale
        z_crit = stats.norm.ppf(1 - alpha/2)
        se_p = np.sqrt(p_hat * (1 - p_hat) / n_total)

        ic_p_lower = p_hat - z_crit * se_p
        ic_p_upper = p_hat + z_crit * se_p

        print(f"Proportion de personnes avec maladie cardiaque :")
        print(f"  n = {n_total}")
        print(f"  Succès = {n_success}")
        print(f"  p̂ = {p_hat:.4f} ({p_hat*100:.2f}%)")
        print(f"  Erreur standard = √[p̂(1-p̂)/n] = {se_p:.4f}")
        print(f"  Quantile z_{{1-alpha/2}} = {z_crit:.4f}")
        print(f"\n  IC_{(1-alpha)*100:.0f}%(p) = [{ic_p_lower:.4f}, {ic_p_upper:.4f}]")
        print(f"               = [{ic_p_lower*100:.2f}%, {ic_p_upper*100:.2f}%]")

        ic_results['proportion'] = {
            'estimate': p_hat,
            'lower': ic_p_lower,
            'upper': ic_p_upper,
            'n_success': n_success,
            'n_total': n_total
        }

        self.results['intervalles_confiance'] = ic_results

        # Visualisation des IC
        self._plot_intervalles_confiance(ic_results)

        return ic_results

    def _plot_intervalles_confiance(self, ic_results):
        """Visualise les intervalles de confiance"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # IC pour la moyenne
        axes[0].errorbar([0], [ic_results['mean']['estimate']],
                        yerr=[[ic_results['mean']['estimate'] - ic_results['mean']['lower']],
                              [ic_results['mean']['upper'] - ic_results['mean']['estimate']]],
                        fmt='o', markersize=10, capsize=10, capthick=2, linewidth=2)
        axes[0].set_xlim(-1, 1)
        axes[0].set_xticks([])
        axes[0].set_ylabel('Cholestérol')
        axes[0].set_title('IC 95% pour la moyenne μ')
        axes[0].grid(True, alpha=0.3)
        axes[0].axhline(ic_results['mean']['estimate'], color='red', linestyle='--', alpha=0.5)

        # IC pour la variance
        axes[1].errorbar([0], [ic_results['variance']['estimate']],
                        yerr=[[ic_results['variance']['estimate'] - ic_results['variance']['lower']],
                              [ic_results['variance']['upper'] - ic_results['variance']['estimate']]],
                        fmt='o', markersize=10, capsize=10, capthick=2, linewidth=2)
        axes[1].set_xlim(-1, 1)
        axes[1].set_xticks([])
        axes[1].set_ylabel('Variance')
        axes[1].set_title('IC 95% pour la variance σ²')
        axes[1].grid(True, alpha=0.3)
        axes[1].axhline(ic_results['variance']['estimate'], color='red', linestyle='--', alpha=0.5)

        # IC pour la proportion
        axes[2].errorbar([0], [ic_results['proportion']['estimate']],
                        yerr=[[ic_results['proportion']['estimate'] - ic_results['proportion']['lower']],
                              [ic_results['proportion']['upper'] - ic_results['proportion']['estimate']]],
                        fmt='o', markersize=10, capsize=10, capthick=2, linewidth=2)
        axes[2].set_xlim(-1, 1)
        axes[2].set_xticks([])
        axes[2].set_ylabel('Proportion')
        axes[2].set_title('IC 95% pour la proportion p')
        axes[2].grid(True, alpha=0.3)
        axes[2].axhline(ic_results['proportion']['estimate'], color='red', linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.savefig('figures/intervalles_confiance.png', dpi=300, bbox_inches='tight')
        print("\n✓ Graphique des IC sauvegardé dans figures/intervalles_confiance.png")
        plt.close()

    def tests_hypotheses(self, alpha=0.05):
        """
        C. TESTS D'HYPOTHÈSES

        Réalise plusieurs tests :
        1. Test de Student sur une moyenne
        2. Test de Student pour comparer deux moyennes
        3. Test de Fisher pour comparer deux variances
        4. ANOVA pour comparer plusieurs groupes

        Parameters:
        -----------
        alpha : float
            Seuil de significativité (par défaut 0.05)
        """
        print("\n" + "="*80)
        print(f"C. TESTS D'HYPOTHÈSES (α = {alpha})")
        print("="*80)

        test_results = {}

        # 1. TEST DE STUDENT SUR UNE MOYENNE
        print("\n1. TEST DE STUDENT SUR UNE MOYENNE")
        print("-" * 50)
        print("H₀ : μ = μ₀  vs  H₁ : μ ≠ μ₀")

        variable = 'cholesterol'
        mu_0 = 200  # Valeur de référence (par exemple, seuil médical)
        data_var = self.data[variable].dropna().values
        n = len(data_var)
        mean = np.mean(data_var)
        std = np.std(data_var, ddof=1)

        # Statistique de test
        t_stat = (mean - mu_0) / (std / np.sqrt(n))
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n-1))

        print(f"\nVariable : {variable}")
        print(f"  H₀ : μ = {mu_0}")
        print(f"  X̄ = {mean:.2f}")
        print(f"  S = {std:.2f}")
        print(f"  Statistique t = (X̄ - μ₀)/(S/√n) = {t_stat:.4f}")
        print(f"  Degrés de liberté = {n-1}")
        print(f"  p-value = {p_value:.4f}")
        print(f"\n  Décision : {'Rejeter H₀' if p_value < alpha else 'Ne pas rejeter H₀'} (α = {alpha})")
        print(f"  Conclusion : La moyenne {'est significativement différente' if p_value < alpha else 'n est pas significativement différente'} de {mu_0}")

        test_results['test_mean'] = {
            'variable': variable,
            'mu_0': mu_0,
            't_stat': t_stat,
            'p_value': p_value,
            'reject_h0': p_value < alpha
        }

        # 2. COMPARAISON DE DEUX MOYENNES (TEST DE STUDENT)
        print("\n2. COMPARAISON DE DEUX MOYENNES")
        print("-" * 50)
        print("H₀ : μ₁ = μ₂  vs  H₁ : μ₁ ≠ μ₂")

        # Comparer le cholestérol entre malades et non-malades
        group1 = self.data[self.data['heart_disease'] == 0]['cholesterol'].dropna()
        group2 = self.data[self.data['heart_disease'] == 1]['cholesterol'].dropna()

        t_stat_2, p_value_2 = stats.ttest_ind(group1, group2)

        print(f"\nComparaison : Cholestérol (sans maladie vs avec maladie)")
        print(f"  Groupe 1 (sans maladie) : n₁ = {len(group1)}, X̄₁ = {np.mean(group1):.2f}")
        print(f"  Groupe 2 (avec maladie) : n₂ = {len(group2)}, X̄₂ = {np.mean(group2):.2f}")
        print(f"  Statistique t = {t_stat_2:.4f}")
        print(f"  p-value = {p_value_2:.4f}")
        print(f"\n  Décision : {'Rejeter H₀' if p_value_2 < alpha else 'Ne pas rejeter H₀'}")
        print(f"  Conclusion : Les moyennes {'sont significativement différentes' if p_value_2 < alpha else 'ne sont pas significativement différentes'}")

        test_results['test_two_means'] = {
            'groups': ['sans maladie', 'avec maladie'],
            't_stat': t_stat_2,
            'p_value': p_value_2,
            'reject_h0': p_value_2 < alpha
        }

        # 3. COMPARAISON DE DEUX VARIANCES (TEST DE FISHER)
        print("\n3. COMPARAISON DE DEUX VARIANCES (TEST DE FISHER)")
        print("-" * 50)
        print("H₀ : σ₁² = σ₂²  vs  H₁ : σ₁² ≠ σ₂²")

        var1 = np.var(group1, ddof=1)
        var2 = np.var(group2, ddof=1)

        # Statistique F (toujours var_max / var_min)
        if var1 > var2:
            f_stat = var1 / var2
            df1, df2 = len(group1) - 1, len(group2) - 1
        else:
            f_stat = var2 / var1
            df1, df2 = len(group2) - 1, len(group1) - 1

        p_value_f = 2 * min(stats.f.cdf(f_stat, df1, df2), 1 - stats.f.cdf(f_stat, df1, df2))

        print(f"  S₁² = {var1:.2f}")
        print(f"  S₂² = {var2:.2f}")
        print(f"  Statistique F = {f_stat:.4f}")
        print(f"  Degrés de liberté = ({df1}, {df2})")
        print(f"  p-value = {p_value_f:.4f}")
        print(f"\n  Décision : {'Rejeter H₀' if p_value_f < alpha else 'Ne pas rejeter H₀'}")
        print(f"  Conclusion : Les variances {'sont significativement différentes' if p_value_f < alpha else 'sont homogènes'}")

        test_results['test_variances'] = {
            'f_stat': f_stat,
            'p_value': p_value_f,
            'reject_h0': p_value_f < alpha
        }

        # 4. ANALYSE DE LA VARIANCE (ANOVA)
        print("\n4. ANALYSE DE LA VARIANCE (ANOVA)")
        print("-" * 50)
        print("H₀ : μ₁ = μ₂ = ... = μₖ  vs  H₁ : Au moins une moyenne diffère")

        # Créer des groupes par catégorie d'âge
        self.data['age_group'] = pd.cut(self.data['age'], bins=[0, 40, 55, 100],
                                        labels=['<40', '40-55', '>55'])

        groups = [self.data[self.data['age_group'] == cat]['cholesterol'].dropna()
                 for cat in ['<40', '40-55', '>55']]

        # ANOVA
        f_stat_anova, p_value_anova = stats.f_oneway(*groups)

        # Calcul manuel des sommes des carrés
        grand_mean = np.mean(np.concatenate(groups))

        # Somme des carrés inter-groupes (SS_inter)
        ss_inter = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)

        # Somme des carrés intra-groupes (SS_intra)
        ss_intra = sum(np.sum((g - np.mean(g))**2) for g in groups)

        # Somme des carrés totale
        ss_total = ss_inter + ss_intra

        # Degrés de liberté
        k = len(groups)  # Nombre de groupes
        n_total = sum(len(g) for g in groups)
        df_inter = k - 1
        df_intra = n_total - k

        # Carrés moyens
        ms_inter = ss_inter / df_inter
        ms_intra = ss_intra / df_intra

        print(f"\nComparaison du cholestérol entre 3 groupes d'âge :")
        for i, (cat, g) in enumerate(zip(['<40', '40-55', '>55'], groups)):
            print(f"  Groupe {i+1} ({cat} ans) : n = {len(g)}, X̄ = {np.mean(g):.2f}")

        print(f"\nTable ANOVA :")
        print(f"  Source          | SS       | df  | MS       | F        | p-value")
        print(f"  ----------------|----------|-----|----------|----------|---------")
        print(f"  Inter-groupes   | {ss_inter:8.2f} | {df_inter:3d} | {ms_inter:8.2f} | {f_stat_anova:8.4f} | {p_value_anova:.4f}")
        print(f"  Intra-groupes   | {ss_intra:8.2f} | {df_intra:3d} | {ms_intra:8.2f} |          |")
        print(f"  Total           | {ss_total:8.2f} | {n_total-1:3d} |          |          |")

        print(f"\n  Statistique F = MS_inter / MS_intra = {f_stat_anova:.4f}")
        print(f"  p-value = {p_value_anova:.4f}")
        print(f"\n  Décision : {'Rejeter H₀' if p_value_anova < alpha else 'Ne pas rejeter H₀'}")
        print(f"  Conclusion : {'Au moins un groupe diffère significativement' if p_value_anova < alpha else 'Pas de différence significative entre les groupes'}")

        test_results['anova'] = {
            'f_stat': f_stat_anova,
            'p_value': p_value_anova,
            'ss_inter': ss_inter,
            'ss_intra': ss_intra,
            'ss_total': ss_total,
            'reject_h0': p_value_anova < alpha
        }

        self.results['tests_hypotheses'] = test_results

        # Visualisations
        self._plot_tests_hypotheses(groups)

        return test_results

    def _plot_tests_hypotheses(self, groups):
        """Visualise les résultats des tests d'hypothèses"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Boxplot pour comparaison des groupes
        data_plot = []
        labels = []
        for i, (cat, g) in enumerate(zip(['<40 ans', '40-55 ans', '>55 ans'], groups)):
            data_plot.append(g)
            labels.append(cat)

        axes[0].boxplot(data_plot, labels=labels)
        axes[0].set_ylabel('Cholestérol (mg/dL)')
        axes[0].set_title('Comparaison du cholestérol par groupe d\'âge')
        axes[0].grid(True, alpha=0.3)

        # Comparaison maladie/pas maladie
        group1 = self.data[self.data['heart_disease'] == 0]['cholesterol'].dropna()
        group2 = self.data[self.data['heart_disease'] == 1]['cholesterol'].dropna()

        axes[1].boxplot([group1, group2], labels=['Sans maladie', 'Avec maladie'])
        axes[1].set_ylabel('Cholestérol (mg/dL)')
        axes[1].set_title('Cholestérol : Malades vs Non-malades')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('figures/tests_hypotheses.png', dpi=300, bbox_inches='tight')
        print("\n✓ Graphique des tests sauvegardé dans figures/tests_hypotheses.png")
        plt.close()

    def regression_lineaire(self, alpha=0.05):
        """
        D. MODÉLISATION PAR RÉGRESSION LINÉAIRE

        Modèle : Y = β₀ + β₁X + ε
        - Estimation par moindres carrés
        - Test de Fisher global
        - Tests de Student sur les coefficients
        - Intervalle de prévision

        Parameters:
        -----------
        alpha : float
            Seuil de significativité
        """
        print("\n" + "="*80)
        print("D. MODÉLISATION PAR RÉGRESSION LINÉAIRE")
        print("="*80)

        # Variable dépendante : blood_pressure
        # Variable indépendante : age
        print("\nModèle : blood_pressure = β₀ + β₁·age + ε")

        # Préparation des données
        data_clean = self.data[['age', 'blood_pressure']].dropna()
        X = data_clean['age'].values.reshape(-1, 1)
        y = data_clean['blood_pressure'].values
        n = len(y)

        # Visualisation du nuage de points
        print("\n1. VÉRIFICATION DE LA LINÉARITÉ")
        print("-" * 50)
        self._plot_scatter(X, y)
        print("  ✓ Nuage de points tracé (voir figures/scatter_plot.png)")

        # Estimation par moindres carrés
        print("\n2. ESTIMATION DU MODÈLE (Moindres Carrés)")
        print("-" * 50)

        # Calcul manuel
        x_mean = np.mean(X)
        y_mean = np.mean(y)

        beta_1 = np.sum((X.flatten() - x_mean) * (y - y_mean)) / np.sum((X.flatten() - x_mean)**2)
        beta_0 = y_mean - beta_1 * x_mean

        print(f"  β̂₀ (Intercept) = {beta_0:.4f}")
        print(f"  β̂₁ (Slope) = {beta_1:.4f}")
        print(f"\n  Équation estimée : blood_pressure = {beta_0:.2f} + {beta_1:.4f}·age")

        # Prédictions
        y_pred = beta_0 + beta_1 * X.flatten()
        residuals = y - y_pred

        # Qualité du modèle
        print("\n3. QUALITÉ DU MODÈLE")
        print("-" * 50)

        # Somme des carrés
        ss_total = np.sum((y - y_mean)**2)
        ss_residual = np.sum(residuals**2)
        ss_regression = ss_total - ss_residual

        # R² (coefficient de détermination)
        r2 = 1 - (ss_residual / ss_total)

        print(f"  Somme des carrés totale (SST) = {ss_total:.2f}")
        print(f"  Somme des carrés résiduelle (SSR) = {ss_residual:.2f}")
        print(f"  Somme des carrés expliquée (SSE) = {ss_regression:.2f}")
        print(f"\n  R² = 1 - (SSR/SST) = {r2:.4f}")
        print(f"  Interprétation : {r2*100:.2f}% de la variabilité de la pression artérielle")
        print(f"                   est expliquée par l'âge.")

        # Variance résiduelle
        sigma2_hat = ss_residual / (n - 2)

        # 4. TEST DE FISHER GLOBAL
        print("\n4. TEST DE FISHER GLOBAL")
        print("-" * 50)
        print("  H₀ : β₁ = 0  (pas de relation linéaire)")
        print("  H₁ : β₁ ≠ 0  (relation linéaire significative)")

        f_stat = (ss_regression / 1) / (ss_residual / (n - 2))
        p_value_f = 1 - stats.f.cdf(f_stat, 1, n - 2)

        print(f"\n  Statistique F = (SSE/1) / (SSR/(n-2)) = {f_stat:.4f}")
        print(f"  Degrés de liberté = (1, {n-2})")
        print(f"  p-value = {p_value_f:.6f}")
        print(f"\n  Décision : {'Rejeter H₀' if p_value_f < alpha else 'Ne pas rejeter H₀'}")
        print(f"  Conclusion : Le modèle est {'significatif' if p_value_f < alpha else 'non significatif'}")

        # 5. TESTS DE STUDENT SUR LES COEFFICIENTS
        print("\n5. TESTS DE STUDENT SUR LES COEFFICIENTS")
        print("-" * 50)

        # Erreurs standards
        se_beta_1 = np.sqrt(sigma2_hat / np.sum((X.flatten() - x_mean)**2))
        se_beta_0 = np.sqrt(sigma2_hat * (1/n + x_mean**2 / np.sum((X.flatten() - x_mean)**2)))

        # Statistiques t
        t_beta_0 = beta_0 / se_beta_0
        t_beta_1 = beta_1 / se_beta_1

        # p-values
        p_beta_0 = 2 * (1 - stats.t.cdf(abs(t_beta_0), df=n-2))
        p_beta_1 = 2 * (1 - stats.t.cdf(abs(t_beta_1), df=n-2))

        print(f"\n  Coefficient β₀ (Intercept) :")
        print(f"    Estimation = {beta_0:.4f}")
        print(f"    Erreur standard = {se_beta_0:.4f}")
        print(f"    Statistique t = {t_beta_0:.4f}")
        print(f"    p-value = {p_beta_0:.6f}")
        print(f"    Significatif : {'Oui' if p_beta_0 < alpha else 'Non'}")

        print(f"\n  Coefficient β₁ (age) :")
        print(f"    Estimation = {beta_1:.4f}")
        print(f"    Erreur standard = {se_beta_1:.4f}")
        print(f"    Statistique t = {t_beta_1:.4f}")
        print(f"    p-value = {p_beta_1:.6f}")
        print(f"    Significatif : {'Oui' if p_beta_1 < alpha else 'Non'}")

        # 6. INTERVALLE DE PRÉVISION
        print("\n6. INTERVALLE DE PRÉVISION")
        print("-" * 50)

        # Prévision pour un nouvel individu d'âge 50 ans
        x_new = 50
        y_pred_new = beta_0 + beta_1 * x_new

        # Erreur de prévision
        se_pred = np.sqrt(sigma2_hat * (1 + 1/n + (x_new - x_mean)**2 / np.sum((X.flatten() - x_mean)**2)))

        t_crit = stats.t.ppf(1 - alpha/2, df=n-2)

        pred_lower = y_pred_new - t_crit * se_pred
        pred_upper = y_pred_new + t_crit * se_pred

        print(f"  Pour un individu d'âge x = {x_new} ans :")
        print(f"    Prédiction ŷ = {y_pred_new:.2f}")
        print(f"    Erreur standard de prévision = {se_pred:.4f}")
        print(f"    IC_{(1-alpha)*100:.0f}% de prévision = [{pred_lower:.2f}, {pred_upper:.2f}]")
        print(f"\n  Interprétation : Pour un individu de {x_new} ans, on prédit avec {(1-alpha)*100:.0f}%")
        print(f"                   de confiance que sa pression artérielle sera entre")
        print(f"                   {pred_lower:.2f} et {pred_upper:.2f} mmHg.")

        # Sauvegarde des résultats
        self.results['regression'] = {
            'beta_0': beta_0,
            'beta_1': beta_1,
            'r2': r2,
            'f_stat': f_stat,
            'p_value_f': p_value_f,
            't_beta_0': t_beta_0,
            'p_beta_0': p_beta_0,
            't_beta_1': t_beta_1,
            'p_beta_1': p_beta_1,
            'prediction': {
                'x_new': x_new,
                'y_pred': y_pred_new,
                'lower': pred_lower,
                'upper': pred_upper
            }
        }

        # Visualisations
        self._plot_regression(X, y, beta_0, beta_1, x_new, pred_lower, pred_upper)
        self._plot_residuals(X, residuals)

        return self.results['regression']

    def _plot_scatter(self, X, y):
        """Trace le nuage de points"""
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.scatter(X, y, alpha=0.5, edgecolors='black')
        ax.set_xlabel('Âge (années)')
        ax.set_ylabel('Pression artérielle (mmHg)')
        ax.set_title('Relation entre l\'âge et la pression artérielle')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('figures/scatter_plot.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_regression(self, X, y, beta_0, beta_1, x_new, pred_lower, pred_upper):
        """Visualise la régression linéaire"""
        fig, ax = plt.subplots(figsize=(12, 7))

        # Nuage de points
        ax.scatter(X, y, alpha=0.5, edgecolors='black', label='Données observées')

        # Droite de régression
        x_line = np.linspace(X.min(), X.max(), 100)
        y_line = beta_0 + beta_1 * x_line
        ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'ŷ = {beta_0:.2f} + {beta_1:.4f}·x')

        # Point de prévision
        y_pred_new = beta_0 + beta_1 * x_new
        ax.plot(x_new, y_pred_new, 'go', markersize=12, label=f'Prévision (x={x_new})')
        ax.vlines(x_new, pred_lower, pred_upper, colors='green', linewidth=2,
                 label=f'IC 95% de prévision')
        ax.plot(x_new, pred_lower, 'g_', markersize=10)
        ax.plot(x_new, pred_upper, 'g_', markersize=10)

        ax.set_xlabel('Âge (années)')
        ax.set_ylabel('Pression artérielle (mmHg)')
        ax.set_title('Régression linéaire : Pression artérielle vs Âge')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('figures/regression_lineaire.png', dpi=300, bbox_inches='tight')
        print("  ✓ Graphique de régression sauvegardé dans figures/regression_lineaire.png")
        plt.close()

    def _plot_residuals(self, X, residuals):
        """Analyse des résidus"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Résidus vs valeurs prédites
        axes[0].scatter(X, residuals, alpha=0.5, edgecolors='black')
        axes[0].axhline(0, color='red', linestyle='--', linewidth=2)
        axes[0].set_xlabel('Âge')
        axes[0].set_ylabel('Résidus')
        axes[0].set_title('Analyse des résidus')
        axes[0].grid(True, alpha=0.3)

        # QQ-plot pour normalité des résidus
        stats.probplot(residuals, dist="norm", plot=axes[1])
        axes[1].set_title('QQ-plot (normalité des résidus)')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('figures/analyse_residus.png', dpi=300, bbox_inches='tight')
        print("  ✓ Analyse des résidus sauvegardée dans figures/analyse_residus.png")
        plt.close()

    def sauvegarder_resultats(self):
        """Sauvegarde tous les résultats dans un fichier texte"""
        import json

        # Fonction pour convertir les types numpy en types Python natifs
        def convert_to_native(obj):
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj

        with open('results/resultats_complets.txt', 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RÉSULTATS DE L'ANALYSE STATISTIQUE COMPLÈTE\n")
            f.write("="*80 + "\n\n")

            f.write("Dataset : Données sur la santé cardiaque\n")
            f.write(f"Nombre d'observations : {len(self.data)}\n\n")

            # Écrire tous les résultats en convertissant les types numpy
            results_native = convert_to_native(self.results)
            f.write(json.dumps(results_native, indent=2, ensure_ascii=False))

        print("\n✓ Résultats complets sauvegardés dans results/resultats_complets.txt")

    def generer_rapport_complet(self):
        """Exécute toutes les analyses dans l'ordre"""
        print("\n" + "="*80)
        print("DÉBUT DE L'ANALYSE STATISTIQUE COMPLÈTE")
        print("="*80)

        # A. Analyse descriptive
        self.analyse_descriptive()
        self.estimation_parametres(variable='cholesterol')

        # B. Intervalles de confiance
        self.intervalles_confiance(alpha=0.05)

        # C. Tests d'hypothèses
        self.tests_hypotheses(alpha=0.05)

        # D. Régression linéaire
        self.regression_lineaire(alpha=0.05)

        # Sauvegarde
        self.sauvegarder_resultats()

        print("\n" + "="*80)
        print("ANALYSE TERMINÉE AVEC SUCCÈS")
        print("="*80)
        print("\nFichiers générés :")
        print("  - figures/histogrammes.png")
        print("  - figures/ajustement_cholesterol.png")
        print("  - figures/intervalles_confiance.png")
        print("  - figures/tests_hypotheses.png")
        print("  - figures/scatter_plot.png")
        print("  - figures/regression_lineaire.png")
        print("  - figures/analyse_residus.png")
        print("  - results/resultats_complets.txt")


def main():
    """Fonction principale pour exécuter l'analyse"""

    # Chemin vers les données
    data_path = 'data/heart_health_data.csv'

    # Création de l'instance d'analyse
    analyse = AnalyseStatistique(data_path)

    # Génération du rapport complet
    analyse.generer_rapport_complet()


if __name__ == "__main__":
    main()
