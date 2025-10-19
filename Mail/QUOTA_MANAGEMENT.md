# Gestion des Quotas API

## Limites par défaut

### VirusTotal (Free API)
- **4 appels par minute**
- Reset automatique toutes les 60 secondes
- Utilisé pour : vérifier URLs et hash de fichiers

### URLScan.io (Free API)
- **10 appels par minute**
- Reset automatique toutes les 60 secondes
- Utilisé pour : rechercher URLs dans la base existante

### AbuseIPDB (Free API)
- **1000 appels par jour**
- Reset automatique toutes les 24 heures
- Utilisé pour : vérifier réputation des adresses IP

## Vérifier les quotas

### Avant un scan
```powershell
python check_quota.py
```

Affiche :
- État de chaque API (OK, ATTENTION, DEPASSE)
- Nombre d'appels utilisés / maximum
- Appels restants
- Temps avant réinitialisation

### Pendant un scan
Le programme affiche automatiquement :
- **⚠️ Avertissement** à 80% du quota
- **🔴 Quota dépassé** : pause automatique avec compte à rebours
- Réinitialisation automatique après la période d'attente

### Après un scan
Le résumé affiche :
```
=== API Usage ===
  VirusTotal: 4/4 appels (100%)
    ⚠️  Quota bientot atteint!
  URLScan: 8/10 appels (80%)
  AbuseIPDB: 45/1000 appels (5%)
```

## Comportement en cas de dépassement

### Automatique
Le programme **attend automatiquement** la réinitialisation :
```
⚠️  QUOTA API DEPASSE: virustotal
   Utilise: 4/4 appels par minute
   Attente: 42s avant reinitialisation...
✓  Quota virustotal reinitialise
```

### Impact sur la détection
Quand les quotas sont dépassés :
- ✅ Détection locale continue (patterns, mots-clés, etc.)
- ✅ Cache fonctionne normalement
- ❌ Vérifications API en pause temporairement
- ⚠️ **Score de menace potentiellement moins précis**

## Solutions

### 1. Utiliser le cache
```powershell
# Le cache évite de réanalyser les mêmes emails
python main.py  # Cache activé par défaut
```

Emails déjà analysés = **0 appel API**

### 2. Scanner sans APIs
```powershell
# Utilise uniquement la détection locale
python main.py --no-apis
```

Détection locale :
- Patterns de phishing
- Mots-clés suspects
- Validation SPF/DKIM/DMARC
- IA (si activée)

### 3. Limiter le scope
```powershell
# Scanner un seul dossier à la fois
python main.py --folder Inbox

# Avec dry-run pour prévisualiser
python main.py --dry-run --folder Inbox
```

### 4. Augmenter les limites API

#### VirusTotal
- Free : 4/min
- **Premium** : 1000/min
- Lien : https://www.virustotal.com/gui/user/YOUR_USERNAME/apikey

#### URLScan.io
- Free : 10/min
- **Pro** : 100/min
- Lien : https://urlscan.io/about-api/

#### AbuseIPDB
- Free : 1000/jour
- **Basic** : 3000/jour
- **Pro** : 60000/jour
- Lien : https://www.abuseipdb.com/pricing

Configurer les clés dans `.env` :
```bash
VIRUSTOTAL_API_KEY=your_premium_key
URLSCAN_API_KEY=your_pro_key
ABUSEIPDB_API_KEY=your_basic_key
```

## Estimation des besoins

### Scan Inbox (100 emails)
Avec APIs activées :
- Emails nouveaux : ~100 appels VirusTotal
- URLs uniques : ~50 appels URLScan
- IPs uniques : ~20 appels AbuseIPDB

**Temps avec quotas free** : ~25 minutes (pauses comprises)

### Scan avec cache (100 emails déjà analysés)
- Emails en cache : 0 appel API
- Nouveaux emails seulement

**Temps** : <1 minute

### Recommandations
- **Premier scan** : Faites-le le soir ou en plusieurs étapes
- **Scans suivants** : Rapides grâce au cache
- **Quotidien** : Activez le cache, scannez régulièrement (peu de nouveaux emails)
- **Urgence** : Utilisez `--no-apis` pour analyse immédiate

## Monitoring

### Option 8 du menu interactif
```
options:
1. scan inbox
2. scan inbox + junk
...
8. check api quota  ← Nouveau !
```

Affiche l'état en temps réel des quotas.

### Logs
Tous les événements de quota sont loggés dans `mail_cleaner.log` :
```
2025-10-15 10:45:12 - WARNING - quota virustotal depasse: 4/4 par minute
2025-10-15 10:45:54 - INFO - virustotal: 2 appels restants sur 4
```

## Troubleshooting

### "Quota dépassé mais scan bloqué"
```powershell
# Réinitialiser manuellement les compteurs
python -c "from config import API_RATE_LIMITS; import time; [v.update({'calls': 0, 'last_reset': time.time()}) for v in API_RATE_LIMITS.values()]"
```

### "Scan très lent"
Vérifiez les quotas :
```powershell
python check_quota.py
```

Si dépassés, utilisez `--no-apis` pour finir rapidement.

### "Résultats moins bons sans APIs"
Normal ! Les APIs externes ajoutent :
- Base de données mondiale de menaces
- Détection en temps réel
- Réputation de sources externes

La détection locale reste efficace pour :
- Phishing classiques
- Pièces jointes dangereuses
- Patterns connus
- Validation d'authentification
