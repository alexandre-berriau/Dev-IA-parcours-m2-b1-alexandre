"""Règles de nettoyage des réservations — Escale Atlantique (mission FastIA).

Une fonction par règle : elle reçoit un DataFrame, renvoie un NOUVEAU DataFrame (jamais modifié en place)
et le nombre de lignes qu'elle a touchées. `nettoyer()` les enchaîne et produit un compte rendu.

⚠️ `train.py` ne charge que les colonnes utiles au modèle (voir sa requête SQL). Une règle qui a besoin
d'une autre colonne impose de l'ajouter à la requête.
"""

import pandas as pd

# Plafonds retenus en tâche 3, au-delà desquels la ligne n'est plus une réservation de chambre
PLAFOND_ADULTES = 10
PLAFOND_ADR = 1000


# --- Exemple fourni : une règle, sa justification, son test (tests/test_nettoyage.py) -------------------

def imputer_enfants_manquants(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """`children` manquant → 0.

    Justification : quelques lignes seulement, et une réservation sans enfant renseigné est,
    de loin, le cas le plus fréquent. Décision réversible : la valeur d'origine est perdue,
    mais le compte rendu garde la trace du nombre de lignes concernées.
    """
    manquants = df["children"].isna()
    out = df.copy()
    out.loc[manquants, "children"] = 0
    return out, int(manquants.sum())


# --- Les règles décidées en tâche 3 ---------------------------------------------------------------------

def supprimer_sans_adulte(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """`adults` à 0 → ligne supprimée.

    Justification : 273 lignes, dont 113 sans aucun occupant. Un hôtel ne loue pas de chambre
    sans adulte, et le pipeline calcule `guests` et `adr_per_guest` à partir de cette colonne.
    Posée au client en question 5 : s'il reconnaît ce type de ligne, la règle saute.
    """
    a_garder = df["adults"] > 0
    return df[a_garder].copy(), int((~a_garder).sum())


def supprimer_groupes_improbables(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Plus de PLAFOND_ADULTES adultes sur une ligne → ligne supprimée.

    Justification : 12 lignes de 20 à 55 adultes, annulées à 93 % et presque toutes à 0 €.
    Des pré-réservations de groupe, pas des chambres. Le `StandardScaler` du pipeline cale
    son échelle sur ces extrêmes.
    """
    a_garder = df["adults"] <= PLAFOND_ADULTES
    return df[a_garder].copy(), int((~a_garder).sum())


def supprimer_prix_aberrant(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """`adr` au-delà de PLAFOND_ADR euros → ligne supprimée.

    Justification : une seule ligne à 5 400 € la nuit, quand le deuxième prix le plus haut
    de la base est 508 €. Les prix nuls ne sont pas touchés, 479 sont des gratuités assumées.
    """
    a_garder = df["adr"] <= PLAFOND_ADR
    return df[a_garder].copy(), int((~a_garder).sum())


# Ordre d'application : l'imputation d'abord, puis les suppressions du plus gros volume au plus petit
REGLES = [
    imputer_enfants_manquants,
    supprimer_sans_adulte,
    supprimer_groupes_improbables,
    supprimer_prix_aberrant,
]


def nettoyer(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Applique toutes les règles dans l'ordre.

    Renvoie le DataFrame nettoyé et un compte rendu : une ligne par règle,
    avec le nombre de lignes touchées et le nombre de lignes restantes.
    """
    compte_rendu = []
    for regle in REGLES:
        df, touchees = regle(df)
        compte_rendu.append({"regle": regle.__name__, "lignes_touchees": touchees, "lignes_restantes": len(df)})
    return df, pd.DataFrame(compte_rendu)
