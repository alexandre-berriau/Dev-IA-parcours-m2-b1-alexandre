# Rapport de qualité — modèle v2.1.0

Écrit par `train.py` le 2026-11-24, sur les 17 colonnes chargées par le modèle. La base en compte davantage : l'audit complet est dans `notebooks/01_audit.ipynb`.

## Avant nettoyage — 78703 réservations

Colonnes signalées :

| colonne | type | manquants | valeurs_distinctes | hors_bornes |
|---|---|---|---|---|
| country | object | 405 | 159 | 0 |
| lead_time | int64 | 0 | 439 | 1 |
| adults | int64 | 0 | 14 | 285 |
| children | float64 | 4 | 5 | 0 |
| adr | float64 | 0 | 6985 | 1 |

Incohérences métier :

| incohérence | lignes |
|---|---|
| aucun adulte | 273 |
| plus de 10 adultes | 12 |
| aucune nuit | 571 |
| prix nul | 1504 |
| prix au-delà de 1000 € | 1 |

## Ce que le nettoyage a retiré

| regle | lignes_touchees | lignes_restantes |
|---|---|---|
| imputer_enfants_manquants | 4 | 78703 |
| supprimer_sans_adulte | 273 | 78430 |
| supprimer_groupes_improbables | 12 | 78418 |
| supprimer_prix_aberrant | 1 | 78417 |

## Après nettoyage — 78417 réservations

Colonnes signalées :

| colonne | type | manquants | valeurs_distinctes | hors_bornes |
|---|---|---|---|---|
| country | object | 399 | 159 | 0 |
| lead_time | int64 | 0 | 439 | 1 |

Incohérences métier :

| incohérence | lignes |
|---|---|
| aucun adulte | 0 |
| plus de 10 adultes | 0 |
| aucune nuit | 535 |
| prix nul | 1395 |
| prix au-delà de 1000 € | 0 |
