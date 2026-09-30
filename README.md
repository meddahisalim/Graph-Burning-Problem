# Graph Burning

Implémentation et comparaison de stratégies gloutonnes pour le problème du **Graph Burning** sur des graphes non orientés.

---

## 1. Présentation

Le **Graph Burning Problem** consiste à brûler tous les sommets d'un graphe en utilisant un nombre minimal de tours.

Au début, aucun sommet n'est brûlé.

À chaque tour :

1. Un nouveau sommet est choisi comme **source**.
2. Les sommets déjà brûlés propagent le feu vers leurs voisins non brûlés.
3. Le sommet choisi comme source devient brûlé pendant ce tour.
4. Le processus continue jusqu'à ce que tous les sommets soient brûlés.

Une séquence de sommets

$$
S=(x_1,x_2,\ldots,x_k)
$$

est appelée **séquence de brûlage**.

L'objectif est de minimiser le nombre de tours \(k\).

Le plus petit nombre de tours nécessaire pour brûler entièrement le graphe correspond au **burning number**.

---

## 2. Objectifs

Ce projet permet de :

* charger différents graphes ;
* simuler le processus de Graph Burning ;
* calculer différentes mesures de centralité ;
* construire plusieurs stratégies gloutonnes ;
* comparer leurs performances ;
* visualiser l'évolution du brûlage ;
* exporter les résultats au format CSV ;
* proposer une amélioration permettant de sélectionner la meilleure stratégie gloutonne.

Les trois stratégies principales sont :

* Greedy Degree ;
* Greedy Closeness ;
* Greedy Betweenness.

---

## 3. Architecture du projet

```text
TP1_Graph_Burning/
│
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── 1.txt
│   ├── 2.txt
│   └── 3.txt
│
├── src/
│   ├── __init__.py
│   ├── graph_loader.py
│   ├── burning_simulation.py
│   ├── centrality.py
│   ├── greedy_degree.py
│   ├── greedy_closeness.py
│   ├── greedy_betweenness.py
│   ├── improvements.py
│   └── comparison.py
    └── reference_burning.py
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── dashboard.py
│   ├── graph_view.py
│   ├── algorithm_panel.py
│   ├── comparison_view.py
│   └── styles.py
│
├── tests/
│   ├── __init__.py
│   ├── test_graph_loader.py
│   ├── test_burning_simulation.py
│   ├── test_centrality.py
│
└── results/
    └── comparison.csv
```

---

# 4. Technologies utilisées

Le projet utilise principalement :

* **Python 3.9+**
* **NetworkX** — manipulation et analyse des graphes
* **PyQt5** — interface graphique
* **NumPy**
* **Pandas**
* **Matplotlib**
* **pytest** — tests unitaires

---

# 5. Installation

## 5.1 Créer un environnement virtuel

Sous Windows :

```bash
python -m venv .venv
```

Activer l'environnement :

```bash
.venv\Scripts\activate
```

Sous Linux/macOS :

```bash
source .venv/bin/activate
```

---

## 5.2 Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# 6. Lancement de l'application

Depuis le dossier racine :

```bash
python main.py
```

L'application graphique PyQt5 s'ouvre alors.

---

# 7. Fonctionnement du Graph Burning

Considérons un graphe :

```text
0 ----- 1 ----- 2 ----- 3
```

Si on choisit :

```text
x₁ = 1
```

Au premier tour :

```text
0 ----- 1 ----- 2 ----- 3
```

Au tour suivant, le feu se propage :

```text
0 ----- 1 ----- 2 ----- 3
```

Puis :

```text
0 ----- 1 ----- 2 ----- 3
```

Le nombre de tours dépend donc de la séquence des sources et de la propagation du feu.

---

# 8. Simulation

Le module :

```text
src/burning_simulation.py
```

contient le moteur de simulation.

Les principales structures sont :

### BurningRound

Représente un tour de simulation.

Elle contient notamment :

* numéro du tour ;
* source choisie ;
* sommets touchés par la propagation ;
* nouveaux sommets brûlés ;
* ensemble des sommets brûlés ;
* ensemble des sommets encore non brûlés.

### BurningResult

Contient le résultat complet d'une simulation :

* séquence des sources ;
* nombre de tours ;
* sommets brûlés ;
* sommets non brûlés ;
* nombre total de sommets ;
* état de complétude.

Exemple :

```python
result.number_of_rounds
```

permet d'obtenir le nombre de tours.

---

# 9. Centralités

Le module :

```text
src/centrality.py
```

calcule trois mesures de centralité.

---

## 9.1 Degree Centrality

Dans le contexte du TP, le degré d'un sommet \(i\) est :

$$
CD(i)=\sum_j a_{ij}
$$

où \(a_{ij}\) représente la matrice d'adjacence.

Pour un graphe non orienté, cela correspond au nombre de voisins du sommet.

Un sommet avec un degré élevé est connecté à beaucoup d'autres sommets.

---

## 9.2 Closeness Centrality

La closeness est calculée à partir des distances minimales.

Dans le contexte utilisé par le projet :

$$
CC(i)=
\frac{1}
{\sum_j d(i,j)}
$$

où :

$$
d(i,j)
$$

est la distance minimale entre \(i\) et \(j\).

Plus cette valeur est élevée, plus le sommet est globalement proche des autres sommets.

Pour les sommets isolés, la valeur utilisée est :

$$
CC(i)=0
$$

---

## 9.3 Betweenness Centrality

La betweenness mesure le rôle d'un sommet dans les plus courts chemins.

Elle est basée sur :

$$
CB(i)=
\sum_{j,k}
\frac{\sigma_{jk}(i)}
{\sigma_{jk}}
$$

où :

* \(\sigma_{jk}\) = nombre de plus courts chemins entre \(j\) et \(k\) ;
* \(\sigma_{jk}(i)\) = nombre de ces chemins passant par \(i\).

Un sommet avec une forte betweenness peut donc servir de point de passage entre différentes parties du graphe.

---

# 10. Stratégie Greedy Degree

Fichier :

```text
src/greedy_degree.py
```

La stratégie sélectionne à chaque étape le sommet ayant le plus grand **degré résiduel**.

Le degré résiduel est calculé uniquement par rapport aux sommets qui ne sont pas encore brûlés.

Principe :

```text
1. Identifier les sommets non brûlés.
2. Calculer leur degré vers les sommets non brûlés.
3. Sélectionner le sommet avec le degré maximal.
4. Le sélectionner comme nouvelle source.
5. Continuer jusqu'à la fin de la simulation.
```

En cas d'égalité, un ordre déterministe est utilisé.

---

# 11. Stratégie Greedy Closeness

Fichier :

```text
src/greedy_closeness.py
```

Cette stratégie sélectionne le sommet ayant la meilleure closeness par rapport au graphe résiduel.

Le score est calculé à partir des distances vers les sommets encore pertinents.

Principe :

```text
1. Construire le graphe résiduel.
2. Calculer les distances depuis chaque sommet candidat.
3. Calculer son score de closeness.
4. Sélectionner le meilleur candidat.
5. Répéter.
```

---

# 12. Stratégie Greedy Betweenness

Fichier :

```text
src/greedy_betweenness.py
```

Cette stratégie utilise la betweenness sur le graphe résiduel.

Principe :

```text
1. Construire le graphe résiduel.
2. Calculer la betweenness.
3. Sélectionner le sommet avec le score maximal.
4. Utiliser ce sommet comme source.
5. Continuer jusqu'à ce que le graphe soit brûlé.
```

---

# 13. Amélioration des stratégies

Le module :

```text
src/improvements.py
```

permet de comparer les trois stratégies.

Les stratégies exécutées sont :

```text
Greedy Degree
Greedy Closeness
Greedy Betweenness
```

Le système recherche ensuite le résultat correspondant au plus petit nombre de tours parmi les résultats complets.

Si aucune stratégie ne termine complètement le brûlage, le système prend en compte :

1. le nombre maximal de sommets brûlés ;
2. puis le nombre minimal de tours.

Cette approche permet d'obtenir une stratégie adaptative :

```text
                 Graphe
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
      Degree     Closeness   Betweenness
        │           │           │
        └───────────┼───────────┘
                    ↓
              Comparaison
                    ↓
             Meilleur résultat
```

---

# 14. Comparaison expérimentale

Le module :

```text
src/comparison.py
```

permet d'exécuter automatiquement les trois stratégies sur un graphe.

Pour chaque stratégie, les informations suivantes sont enregistrées :

* nom du graphe ;
* nom de la stratégie ;
* nombre de sommets ;
* nombre d'arêtes ;
* nombre de tours ;
* nombre de sommets brûlés ;
* nombre de sommets non brûlés ;
* état complet ou non ;
* séquence des sources ;
* temps d'exécution.

---

# 15. Export CSV

Les résultats peuvent être exportés dans :

```text
results/comparison.csv
```

Le fichier permet ensuite d'analyser les performances des différentes méthodes avec Excel, Pandas ou un autre outil d'analyse.

Exemple de structure :

```text
graph_name;
strategy_name;
number_of_vertices;
number_of_edges;
number_of_rounds;
burned_count;
unburned_count;
is_complete;
source_sequence;
execution_time_seconds
```

---

# 16. Interface graphique

L'application possède plusieurs parties.

## Dashboard

Affiche les informations générales du graphe :

* nombre de sommets ;
* nombre d'arêtes ;
* nombre de sommets brûlés ;
* nombre de tours ;
* stratégie utilisée.

---

## Visualisation du graphe

Le module :

```text
ui/graph_view.py
```

permet de visualiser le graphe et l'évolution du brûlage.

Les sommets sont différenciés selon leur état :

```text
Sommet non brûlé
        ↓
Sommet brûlé
        ↓
Sommet source
```

La simulation peut être parcourue tour par tour.

---

## Panneau des algorithmes

Le module :

```text
ui/algorithm_panel.py
```

permet de sélectionner :

```text
Greedy Degree
Greedy Closeness
Greedy Betweenness
Best Greedy
```

Puis de lancer la simulation.

Il permet également de naviguer entre les différents tours.

---

## Comparaison

Le module :

```text
ui/comparison_view.py
```

permet de comparer les différentes stratégies sur le même graphe.

---

# 17. Jeux de données

Les graphes utilisés pour le TP se trouvent dans :

```text
data/
```

avec :

```text
data/1.txt
data/2.txt
data/3.txt
```

Chaque fichier représente un graphe utilisé pour les expérimentations.

Le chargement des fichiers est réalisé par :

```text
src/graph_loader.py
```

---

# 18. Tests

Les tests sont regroupés dans :

```text
tests/
```

Lancer tous les tests :

```bash
pytest
```

Avec davantage de détails :

```bash
pytest -v
```

---

# 19. Tests importants

Le projet teste notamment :

### Chargement

```text
test_graph_loader.py
```

Vérifie :

* chargement des graphes ;
* validation des données ;
* gestion des erreurs.

### Simulation

```text
test_burning_simulation.py
```

Vérifie :

* propagation du feu ;
* sélection des sources ;
* nombre de tours ;
* état final du graphe.

### Centralités

```text
test_centrality.py
```

Vérifie :

* degré ;
* closeness ;
* betweenness.

### Algorithmes gloutons

```text
test_greedy_degree.py
test_greedy_closeness.py
test_greedy_betweenness.py
```

Vérifient le comportement des différentes stratégies.

### Amélioration

```text
test_improvements.py
```

Vérifie la sélection du meilleur résultat.

---

# 20. Exemple d'utilisation Python

Il est possible d'utiliser les algorithmes sans l'interface graphique.

Exemple :

```python
import networkx as nx

from src.greedy_degree import run_greedy_degree

graph = nx.path_graph(5)

result = run_greedy_degree(graph)

print("Sources :", result.source_sequence)
print("Nombre de tours :", result.number_of_rounds)
print("Complet :", result.is_complete)
```

---

# 21. Exemple conceptuel

Pour un graphe :

```text
0 ----- 1 ----- 2
        |
        3
```

Une stratégie peut choisir :

```text
x₁ = 1
```

Le sommet 1 devient alors source.

Lors des tours suivants, le feu se propage progressivement vers les sommets voisins.

Une autre stratégie pourrait choisir un autre sommet comme première source.

L'objectif de l'expérimentation est précisément de comparer l'effet de ces choix.

---

# 22. Comparaison des stratégies

L'analyse expérimentale doit permettre d'observer :

| Stratégie          | Critère principal                     |
| ------------------ | ------------------------------------- |
| Greedy Degree      | Degré résiduel                        |
| Greedy Closeness   | Proximité aux autres sommets          |
| Greedy Betweenness | Position dans les plus courts chemins |
| Best Greedy        | Comparaison des trois stratégies      |

Il est important de distinguer :

* la qualité de la solution obtenue ;
* le nombre de tours ;
* le nombre de sommets brûlés ;
* le temps d'exécution.

Une stratégie plus coûteuse en calcul peut produire une séquence différente d'une stratégie plus simple.

---

# 23. Structure logique du système

```text
                         ┌──────────────┐
                         │  Fichiers    │
                         │  1.txt ...   │
                         └──────┬───────┘
                                │
                                ▼
                     ┌────────────────────┐
                     │   Graph Loader     │
                     └─────────┬──────────┘
                               │
                               ▼
                         ┌───────────┐
                         │   Graph   │
                         └─────┬─────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        ┌─────────┐       ┌───────────┐    ┌─────────────┐
        │ Degree  │       │ Closeness │    │ Betweenness │
        └────┬────┘       └─────┬─────┘    └──────┬──────┘
             │                  │                 │
             └──────────────────┼─────────────────┘
                                ▼
                       ┌────────────────┐
                       │   Simulation   │
                       └───────┬────────┘
                               │
                               ▼
                       ┌────────────────┐
                       │   Comparison   │
                       └───────┬────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              Interface GUI          CSV Results
```

---

# 24. Principe de conception

Le projet sépare volontairement :

### Logique métier

```text
src/
```

Contient :

* chargement ;
* simulation ;
* centralités ;
* algorithmes ;
* comparaison.

### Interface utilisateur

```text
ui/
```

Contient uniquement les composants PyQt5 et la présentation des résultats.

### Tests

```text
tests/
```

Contient les tests unitaires.

Cette séparation permet de modifier l'interface sans modifier les algorithmes.

---

# 25. Commandes utiles

Lancer l'application :

```bash
python main.py
```

Lancer les tests :

```bash
pytest
```

Lancer les tests avec détails :

```bash
pytest -v
```

Vérifier uniquement les tests de simulation :

```bash
pytest tests/test_burning_simulation.py -v
```

Vérifier les tests des algorithmes :

```bash
pytest tests/test_greedy_*.py -v
```

---

# 26. Résultat attendu

À la fin du TP, le système doit permettre de :

```text
Charger un graphe
      ↓
Visualiser le graphe
      ↓
Choisir une stratégie
      ↓
Lancer le Graph Burning
      ↓
Visualiser chaque tour
      ↓
Obtenir la séquence des sources
      ↓
Mesurer le nombre de tours
      ↓
Comparer les stratégies
      ↓
Exporter les résultats
```

Le projet fournit ainsi une architecture complète pour étudier expérimentalement différentes heuristiques du problème de **Graph Burning**.
