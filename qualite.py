"""Rapport de qualité des réservations — Escale Atlantique (mission FastIA).

Sorti du notebook d'audit pour que `train.py` écrive le même rapport à chaque entraînement.
`profil()` sert de référence au test de non-régression (tests/test_qualite_base.py).

⚠️ `train.py` ne charge que les colonnes utiles au modèle : le rapport qu'il écrit est plus court
que celui du notebook, qui lit toute la table.
"""

from datetime import date
from pathlib import Path

import pandas as pd

from nettoyage import PLAFOND_ADR, PLAFOND_ADULTES

# Bornes « raisonnables » par colonne numérique, reprises de l'audit (tâche 2)
BORNES = {
    "lead_time": (0, 730),
    "adults": (1, 10),
    "children": (0, 10),
    "babies": (0, 5),
    "stays_in_weekend_nights": (0, 20),
    "stays_in_week_nights": (0, 50),
    "adr": (0, 1000),
}

# Combinaisons impossibles ou suspectes pour un hôtel, repérées en tâche 2
INCOHERENCES = {
    "aucun adulte": lambda d: d["adults"] == 0,
    f"plus de {PLAFOND_ADULTES} adultes": lambda d: d["adults"] > PLAFOND_ADULTES,
    "aucune nuit": lambda d: d["stays_in_weekend_nights"] + d["stays_in_week_nights"] == 0,
    "prix nul": lambda d: d["adr"] == 0,
    f"prix au-delà de {PLAFOND_ADR} €": lambda d: d["adr"] > PLAFOND_ADR,
}


def rapport_qualite(d: pd.DataFrame) -> pd.DataFrame:
    """Manquants et valeurs hors bornes, colonne par colonne."""
    lignes = []
    for col in d.columns:
        info = {"colonne": col, "type": str(d[col].dtype),
                "manquants": int(d[col].isna().sum()), "valeurs_distinctes": int(d[col].nunique())}
        if col in BORNES:
            bas, haut = BORNES[col]
            info["hors_bornes"] = int(((d[col] < bas) | (d[col] > haut)).sum())
        lignes.append(info)
    return pd.DataFrame(lignes).set_index("colonne")


def incoherences(d: pd.DataFrame) -> dict[str, int]:
    """Compte chaque combinaison suspecte."""
    return {nom: int(masque(d).sum()) for nom, masque in INCOHERENCES.items()}


def profil(d: pd.DataFrame) -> dict:
    """Empreinte des anomalies, que le test de non-régression compare à sa référence."""
    rapport = rapport_qualite(d)
    hors_bornes = rapport["hors_bornes"] if "hors_bornes" in rapport else pd.Series(dtype="int64")
    return {
        "lignes": len(d),
        "colonnes": sorted(str(c) for c in d.columns),
        # `> 0` et pas `if n` : une colonne sans bornes définies vaut NaN, qui est vrai
        "manquants": {str(c): int(n) for c, n in rapport["manquants"].items() if n > 0},
        "hors_bornes": {str(c): int(n) for c, n in hors_bornes.items() if n > 0},
        "incoherences": incoherences(d),
    }


def _signalees(rapport: pd.DataFrame) -> pd.DataFrame:
    """Ne garde que les colonnes qui ont un manquant ou une valeur hors bornes."""
    hors_bornes = rapport["hors_bornes"] if "hors_bornes" in rapport else 0
    signalees = rapport[(rapport["manquants"] > 0) | (hors_bornes > 0)].copy()
    # Les colonnes sans bornes définies valent NaN : 0 se lit mieux dans le rapport
    if "hors_bornes" in signalees:
        signalees["hors_bornes"] = signalees["hors_bornes"].fillna(0).astype(int)
    return signalees


def _tableau(d: pd.DataFrame) -> str:
    """Un DataFrame en tableau markdown, sans dépendance supplémentaire."""
    if d.empty:
        return "_aucune_"
    entetes = [str(d.index.name or "")] + [str(c) for c in d.columns]
    lignes = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    for index, valeurs in d.iterrows():
        lignes.append("| " + " | ".join([str(index)] + [str(v) for v in valeurs]) + " |")
    return "\n".join(lignes)


def _incoherences_md(d: pd.DataFrame) -> str:
    """Le tableau des incohérences métier, lignes à zéro comprises."""
    table = pd.DataFrame(incoherences(d).items(), columns=["incohérence", "lignes"])
    return _tableau(table.set_index("incohérence"))


def ecrire_rapport(avant: pd.DataFrame, compte_rendu: pd.DataFrame, apres: pd.DataFrame,
                   chemin: Path, version: str) -> None:
    """Écrit l'état de la base avant nettoyage, ce que les règles ont retiré, et l'état après."""
    chemin.write_text(
        f"# Rapport de qualité — modèle v{version}\n\n"
        f"Écrit par `train.py` le {date.today().isoformat()}, sur les {len(avant.columns)} colonnes "
        f"chargées par le modèle. La base en compte davantage : l'audit complet est dans "
        f"`notebooks/01_audit.ipynb`.\n\n"
        f"## Avant nettoyage — {len(avant)} réservations\n\n"
        f"Colonnes signalées :\n\n{_tableau(_signalees(rapport_qualite(avant)))}\n\n"
        f"Incohérences métier :\n\n{_incoherences_md(avant)}\n\n"
        f"## Ce que le nettoyage a retiré\n\n"
        f"{_tableau(compte_rendu.set_index('regle'))}\n\n"
        f"## Après nettoyage — {len(apres)} réservations\n\n"
        f"Colonnes signalées :\n\n{_tableau(_signalees(rapport_qualite(apres)))}\n\n"
        f"Incohérences métier :\n\n{_incoherences_md(apres)}\n",
        encoding="utf-8",
    )
