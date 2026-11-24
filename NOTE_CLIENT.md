# Note — Nettoyage des données de réservation

**De :** Alexandre · **Date :** 24 novembre 2026

## Ce que j'ai fait

J'ai passé la base au crible, colonne par colonne puis par combinaisons impossibles. Chaque anomalie trouvée a reçu une décision écrite, et les décisions prises sont devenues du code testé, rejoué à chaque entraînement. J'ai réentraîné le modèle sur les données nettoyées et comparé les deux versions.

## Ce que ça change

Pour le modèle, presque rien. Sur le même jeu de test, le F1 passe de 0,734 à 0,735. Le nettoyage retire 286 réservations sur 78 703, soit 0,36 %, dont 197 dans la période d'apprentissage. Un modèle entraîné sur 58 595 lignes ne bouge pas pour 197 de moins.

Un point à ne pas mal lire dans les deux fiches de modèle. L'écart entre 0,734 et 0,735 vient surtout du jeu de test, qui compte 89 lignes de moins après nettoyage. À examen identique, l'effet du nettoyage est de +0,0003.

Pour le service réservations, un seul cas change. Les réservations sans adulte, 273 dans l'historique, ne sont plus traitées. Le modèle leur répondait déjà un score peu fiable, puisqu'il n'a aucun cas comparable en mémoire. Mieux vaut que l'API les refuse avec un message clair que de renvoyer un chiffre que personne ne sait lire.

Ce que le nettoyage a vraiment changé : on sait maintenant sur quelles données le modèle a appris. C'est écrit dans sa fiche, un rapport de qualité est produit à chaque entraînement, et un test passe au rouge si une anomalie nouvelle entre dans la base.

## Les questions à poser au client

1. **Le type d'acompte est-il saisi à la réservation, ou rempli après coup quand l'annulation est constatée ?** 10 461 réservations, annulées à 99,2 %, soit 36,4 % de toutes les annulations de la base. Si la valeur est connue dès la réservation, c'est la meilleure information dont je dispose. Si elle est écrite après, le modèle triche et la colonne doit sauter. En attendant : je garde la colonne et les lignes, et je le signale dans la fiche.
2. **Une réservation à 0 € est-elle une gratuité commerciale ou un prix non saisi ?** 1 504 lignes, dont 479 dans un segment où 0 € est le tarif normal. En attendant : je garde tout.
3. **La base peut-elle fournir un identifiant de dossier ?** Sans lui, rien ne distingue un car de 50 personnes d'une double saisie. 22 999 lignes sont concernées. En attendant : je garde.
4. **L'hôtel vend-il des chambres à la journée ?** 571 réservations de zéro nuit, presque toutes honorées. En attendant : je garde.
5. **Les réservations sans adulte sont-elles une saisie incomplète, ou un type de ligne que vous connaissez ?** 273 lignes, dont 113 sans aucun occupant. En attendant : je les supprime. Si vous les reconnaissez, la règle saute.

## Ma recommandation

Mettre la v2.1 en service, et garder la v2 en place le temps de la bascule.

Les deux font le même score, le choix ne se joue donc pas sur la performance. La v2.1 est documentée, reproductible et surveillée, la v2 ne l'est pas.

Deux conditions. Ajouter la validation d'entrée sur l'API pour refuser les réservations sans adulte, puisque c'est ce que le nettoyage fait à l'entraînement. Et ne toucher à rien d'autre avant la réponse à la question 1 : si les acomptes non remboursables sont une fuite, c'est le modèle entier qui est à refaire, pas seulement ses données.
