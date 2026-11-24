"""Non-régression de la qualité de la base — Escale Atlantique (mission FastIA).

Ces tests ont besoin de la base démarrée, contrairement à ceux de `test_nettoyage.py` :
ils sautent si la connexion échoue, pour que `pytest` reste utilisable sans Docker.

`profil_base.json` est l'empreinte des anomalies relevée à l'audit du 24/11/2026.
Un test rouge signale une anomalie que l'audit n'avait pas vue : la regarder, décider quoi en
faire, puis refiger la référence avec `python tests/test_qualite_base.py`.

Le nombre de lignes n'est volontairement pas vérifié : de nouvelles réservations sont normales,
de nouvelles anomalies ne le sont pas.
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
# Pour que `python tests/test_qualite_base.py` trouve les modules, comme le fait pytest.ini
sys.path.insert(0, str(ROOT))

from nettoyage import PLAFOND_ADR, PLAFOND_ADULTES, nettoyer  # noqa: E402
from qualite import incoherences, profil  # noqa: E402

REFERENCE_PATH = Path(__file__).resolve().parent / "profil_base.json"

# Toute la table, comme le notebook d'audit : le test surveille la base, pas les colonnes du modèle
REQUETE = text("""
    SELECT h.code AS hotel, r.*
    FROM reservations AS r JOIN hotels AS h ON h.hotel_id = r.hotel_id
    ORDER BY r.arrival_date
""")


def charger_base() -> pd.DataFrame:
    """L'historique complet des réservations."""
    load_dotenv(ROOT / ".env")
    engine = create_engine(os.environ["DATABASE_URL"])
    return pd.read_sql(REQUETE, engine, parse_dates=["arrival_date", "reservation_status_date"])


@pytest.fixture(scope="module")
def base() -> pd.DataFrame:
    try:
        return charger_base()
    except Exception as erreur:  # base arrêtée ou .env absent : on saute au lieu d'échouer
        pytest.skip(f"base injoignable ({type(erreur).__name__})")


@pytest.fixture(scope="module")
def courant(base) -> dict:
    return profil(base)


@pytest.fixture(scope="module")
def reference() -> dict:
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def test_le_schema_na_pas_change(courant, reference):
    assert courant["colonnes"] == reference["colonnes"]


def test_aucune_valeur_manquante_nouvelle(courant, reference):
    assert courant["manquants"] == reference["manquants"]


def test_aucune_valeur_hors_bornes_nouvelle(courant, reference):
    assert courant["hors_bornes"] == reference["hors_bornes"]


def test_aucune_incoherence_metier_nouvelle(courant, reference):
    assert courant["incoherences"] == reference["incoherences"]


def test_le_nettoyage_ne_laisse_aucune_anomalie_traitee(base):
    propre, _ = nettoyer(base)

    assert propre["children"].isna().sum() == 0
    assert (propre["adults"] == 0).sum() == 0
    assert (propre["adults"] > PLAFOND_ADULTES).sum() == 0
    assert (propre["adr"] > PLAFOND_ADR).sum() == 0


if __name__ == "__main__":
    # Refige la référence une fois l'anomalie examinée et décidée
    empreinte = profil(charger_base())
    REFERENCE_PATH.write_text(json.dumps(empreinte, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"profil ecrit dans {REFERENCE_PATH} ({empreinte['lignes']} lignes)")
