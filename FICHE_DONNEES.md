# Fiche du jeu de données — Réservations Escale Atlantique (nettoyées)

## En une phrase

L'historique des réservations des deux établissements, débarrassé des anomalies tranchées en interne, qui sert à entraîner le modèle d'annulation v2.1.0.

## Origine

| | |
|---|---|
| Source | base PostgreSQL `reservations`, tables `reservations` et `hotels`. Extrait de *Hotel Booking Demand* (Antonio, de Almeida, Nunes, 2019), noms d'établissements fictifs |
| Période | arrivées du 1er juillet 2015 au 31 décembre 2016 |
| Nombre de réservations | 78 703 brutes, 78 417 après nettoyage |
| Mise à jour | aucune. Jeu figé, chargé une fois par `docker compose up` depuis `db/init/` |

## Contenu

Le modèle lit 15 colonnes, toutes connues au moment de la réservation.

| Colonne | Ce que c'est |
|---|---|
| `hotel` | lequel des deux établissements |
| `arrival_date_month` | mois d'arrivée |
| `market_segment` | par où la réservation est arrivée : agence en ligne, groupe, direct, entreprise |
| `deposit_type` | acompte demandé : aucun, remboursable, non remboursable |
| `customer_type` | client de passage, sous contrat, en groupe |
| `country` | pays du client |
| `lead_time` | jours entre la réservation et l'arrivée |
| `stays_in_weekend_nights` | nuits de week-end |
| `stays_in_week_nights` | nuits de semaine |
| `adults` | adultes |
| `children` | enfants |
| `adr` | prix moyen de la nuit, en euros |
| `previous_cancellations` | annulations passées de ce client |
| `total_of_special_requests` | demandes particulières formulées |
| `required_car_parking_spaces` | places de parking demandées |

La cible est `is_canceled`, à 1 si la réservation a été annulée. Le pipeline ajoute six variables calculées à partir des colonnes ci-dessus : durée totale du séjour, part de week-end, présence d'enfants, nombre d'occupants, prix par personne, présence de demandes particulières.

Quatre colonnes de la base sont volontairement absentes : `reservation_status`, `reservation_status_date`, `assigned_room_type` et `booking_changes`. Elles ne sont connues qu'après le séjour et donneraient la réponse au modèle.

## Traitements appliqués

| Règle | Lignes concernées | Pourquoi |
|---|---|---|
| enfants manquants mis à 0 | 4 | la réservation sans enfant est de loin le cas le plus fréquent |
| réservations sans adulte supprimées | 273 | une chambre ne se loue pas sans adulte, et le prix par personne se calcule dessus |
| plus de 10 adultes sur une ligne supprimés | 12 | de 20 à 55 personnes, annulées à 93 %, presque toutes à 0 € : des pré-réservations de groupe |
| prix au-delà de 1 000 € supprimé | 1 | une nuit à 5 400 €, quand le deuxième prix le plus haut de la base est 508 € |

286 lignes au total, 0,36 % de la base.

*Rejouables avec `python train.py` ; détail dans `nettoyage.py`.*

## Limites connues

Quatre anomalies sont restées dans le jeu, faute de réponse du client.

- 10 461 réservations avec acompte non remboursable, annulées à 99,2 %. Si la case est remplie après l'annulation, le modèle triche et son score est faux.
- 22 999 lignes en double. Sans identifiant de dossier, rien ne distingue un car de 50 personnes d'une double saisie.
- 1 504 réservations à 0 €, dont 479 dans un segment où la gratuité est le tarif normal.
- 571 séjours de zéro nuit, presque tous honorés.

Trois autres points à connaître.

- Le modèle n'a jamais vu de réservation sans adulte. S'il en reçoit une, il répond quand même, mais par extrapolation. L'API doit les refuser en amont.
- Le jeu s'arrête en décembre 2016. Le taux d'annulation de 36,2 % est celui de cette période.
- Les bornes qui servent à repérer les valeurs aberrantes sont des hypothèses de départ, pas des règles de l'hôtel.

## Données personnelles

Aucune donnée directement identifiante : ni nom, ni adresse, ni téléphone, ni e-mail. Le jeu contient le pays du client, un identifiant numérique d'agence et de société, les dates du séjour et le montant payé.

Une ligne seule n'identifie personne, mais le croisement du pays, des dates et du prix réduit fortement le nombre de clients possibles sur les pays peu représentés. À traiter comme une donnée pseudonymisée.

Accès : base locale au poste de travail, identifiants dans `.env`, qui n'est pas versionné.
