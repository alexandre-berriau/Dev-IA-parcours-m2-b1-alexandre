"""Tests des règles de nettoyage : un petit DataFrame construit à la main par règle."""

import pandas as pd

import nettoyage
from nettoyage import (
    imputer_enfants_manquants,
    nettoyer,
    supprimer_groupes_improbables,
    supprimer_prix_aberrant,
    supprimer_sans_adulte,
)


def test_imputer_enfants_manquants():
    df = pd.DataFrame({"children": [0, None, 2, None]})

    out, touchees = imputer_enfants_manquants(df)

    assert out["children"].tolist() == [0, 0, 2, 0]
    assert touchees == 2
    assert df["children"].isna().sum() == 2   # l'entrée n'a pas été modifiée


def test_supprimer_sans_adulte():
    df = pd.DataFrame({"adults": [2, 0, 1, 0]})

    out, touchees = supprimer_sans_adulte(df)

    assert out["adults"].tolist() == [2, 1]
    assert touchees == 2
    assert len(df) == 4   # l'entrée n'a pas été modifiée


def test_supprimer_groupes_improbables():
    # 10 est la dernière valeur acceptée, 11 la première refusée
    df = pd.DataFrame({"adults": [2, 10, 11, 55]})

    out, touchees = supprimer_groupes_improbables(df)

    assert out["adults"].tolist() == [2, 10]
    assert touchees == 2
    assert len(df) == 4


def test_supprimer_prix_aberrant():
    # 1 000 € est accepté, le prix nul aussi : seul le 5 400 € part
    df = pd.DataFrame({"adr": [0.0, 95.5, 1000.0, 5400.0]})

    out, touchees = supprimer_prix_aberrant(df)

    assert out["adr"].tolist() == [0.0, 95.5, 1000.0]
    assert touchees == 1
    assert len(df) == 4


def test_nettoyer_produit_un_compte_rendu():
    df = pd.DataFrame({"children": [None, 1], "adults": [2, 2], "adr": [80.0, 80.0]})

    out, compte_rendu = nettoyer(df)

    assert list(compte_rendu.columns) == ["regle", "lignes_touchees", "lignes_restantes"]
    assert len(compte_rendu) == len(nettoyage.REGLES)


def test_nettoyer_enchaine_les_regles():
    # une ligne par règle : la première survit, les trois autres tombent une à une
    df = pd.DataFrame({
        "children": [None, 0, 0, 0],
        "adults": [2, 0, 11, 2],
        "adr": [80.0, 80.0, 80.0, 5400.0],
    })

    out, compte_rendu = nettoyer(df)

    assert out["children"].tolist() == [0]
    assert compte_rendu["lignes_touchees"].tolist() == [1, 1, 1, 1]
    assert compte_rendu["lignes_restantes"].tolist() == [4, 3, 2, 1]
