# SysTeen

**SysTeen** est un petit langage de script pour Linux, simple et lisible, interprété par `systeen.py` (Python 3).
Il sert à automatiser des tâches système : fichiers, variables, commandes Linux, boucles, conditions, scripts parallèles…

> Version actuelle : **0.7.2**
> Projet : [Lemillitaire3330/SysTeen](https://github.com/Lemillitaire3330/SysTeen)

---

## Sommaire

1. [Installation](#installation)
2. [Premier script](#premier-script)
3. [Options de `systeen.py`](#options-de-systeenpy)
4. [Sécurité](#sécurité)
5. [Référence des commandes](#référence-des-commandes)
6. [Variables](#variables)
7. [Conditions](#conditions)
8. [Boucles](#boucles)
9. [Mises à jour](#mises-à-jour)
10. [Désinstallation](#désinstallation)
11. [Notes de version](#notes-de-version)

---

## Installation

Prérequis :

- Linux
- Python 3
- `gpg` (uniquement pour les mises à jour signées)
- `sudo` (uniquement pour `:#`, `:rmf` et `:del!`)
- un terminal graphique et une session graphique X11 ou Wayland (uniquement pour `:go`)

Placez `systeen.py` dans un dossier de votre choix, puis :

```bash
python systeen.py --help
```

### La commande `systeen`

Pour taper simplement `systeen mon_script.st` ou `systeen --help` depuis n'importe où :

```bash
python systeen.py --install
```

Cela crée un lien `/usr/local/bin/systeen` vers `systeen.py`, qui **reste où il est** (le mot de passe `sudo` peut être demandé). Ça fonctionne dans tous les shells, sous `sudo` et dans les scripts.

- Si vous déplacez `systeen.py`, relancez simplement `--install`.
- SysTeen n'écrase jamais un fichier `systeen` qui ne vient pas de lui.
- `--uninstall` retire aussi ce lien.

---

## Premier script

Un script SysTeen est un fichier avec l'extension **`.st`**.

- La **première ligne** doit être `:systeen start`.
- Chaque commande commence par `:`.
- Une ligne qui commence par `#` est un commentaire.
- Les lignes vides, et les lignes qui ne commencent pas par `:`, sont ignorées.

```
:systeen start

# Mon premier script
:var add nom
:say? Comment tu t'appelles ? ; nom
:say Bonjour $nom !

:systeen end
```

Lancement :

```bash
python systeen.py mon_script.st
```

> **Important : un script recommence à la ligne 1 quand il arrive à la fin.**
> Pour qu'il s'arrête, terminez-le par `:systeen end`.

Avant chaque lancement, SysTeen rappelle l'état de la sécurité et demande confirmation (`Y/n`). Relisez toujours le code d'un script avant de l'exécuter.

---

## Options de `systeen.py`

| Commande | Effet |
|---|---|
| `python systeen.py fichier.st` | Exécute un script SysTeen |
| `python systeen.py --maj` | Met à jour vers la dernière version |
| `python systeen.py --maj 0.6.0` | Installe une version précise (rollback) |
| `python systeen.py --update` | Alias de `--maj` |
| `python systeen.py --install` | Installe la commande `systeen` dans `/usr/local/bin` |
| `python systeen.py --change` | Modifie le choix de la protection de `/` et du dossier personnel |
| `python systeen.py --uninstall` | Désinstalle SysTeen |
| `python systeen.py --readme` | Affiche ce README (celui installé à côté de `systeen.py`) |
| `python systeen.py --version` (ou `-V`) | Affiche la version installée |
| `python systeen.py --help` (ou `-h`) | Affiche l'aide |

Si vous tapez un fichier ou une option qui n'existe pas, SysTeen vous l'indique et vous rappelle que `python systeen.py --help` donne de l'aide.

---

## Sécurité

### Protection de `/` et du dossier personnel

Au premier lancement, SysTeen demande si la protection doit être activée (**oui par défaut**).
Quand elle est active, `:del`, `:del!` et `:rmf` refusent de supprimer `/` et votre dossier personnel.

Le choix est enregistré dans `~/.config/systeen/config.json`.
Il n'est pas définitif : `python systeen.py --change` permet de le modifier à tout moment.

### À savoir

- La protection ne concerne **que** `:del`, `:del!` et `:rmf`. Elle ne filtre **pas** ce que fait `:cmd`, qui exécute une commande shell telle quelle.
- `:go` ne redemande **pas** de confirmation : l'avertissement `Y/n` accepté au lancement du premier script vaut pour les scripts qu'il lance. Relisez donc aussi les scripts appelés par `:go`.
- Sous `sudo` (commande `:#`), SysTeen retrouve le vrai utilisateur grâce à `SUDO_USER` pour garder **sa** configuration de sécurité et **son** dossier personnel.
- Ne lancez jamais un script `.st` dont vous ne comprenez pas le contenu.

---

## Référence des commandes

### Structure

| Commande | Description |
|---|---|
| `:systeen start` | Obligatoire en première ligne |
| `:systeen end` | Arrête le script et sauvegarde les variables |

### Affichage et saisie

| Commande | Description |
|---|---|
| `:say texte` | Affiche un texte (les `$variables` sont remplacées) |
| `:say? question ; variable` | Pose une question et stocke la réponse dans une variable **déjà créée** |
| `:sayn? question ; variable` | Question à réponse `y` ou `n` uniquement, affichée `(Y/n)` : **Entrée = y** |
| `:sayN? question ; variable` | Pareil, affichée `(y/N)` : **Entrée = n** (choix recommandé pour les actions risquées) |

Avec `:sayn?` et `:sayN?`, la variable reçoit `y` ou `n`, ce qui se teste avec `:if $variable == y`. Toute autre réponse est refusée et la question est reposée.

### Calcul

```
:math 2 + 3 * 4
:math $a * 2 ; resultat
```

Opérateurs : `+ - * / // % **` (et `+`/`-` unaires). Sans `; variable`, le résultat est affiché.
L'expression est évaluée de façon sûre : aucun code Python arbitraire n'est exécuté.

### Fichiers et dossiers

| Commande | Description |
|---|---|
| `:add nom` | Crée un fichier si `nom` a une extension (`notes.txt`), sinon un dossier. Crée aussi les dossiers parents. Erreur si l'élément existe déjà |
| `:edit fichier "texte"` | Écrit le texte dans le fichier (écrase le contenu). Le texte peut s'étendre sur plusieurs lignes, jusqu'au guillemet fermant |
| `:del chemin` | Supprime un fichier ou un dossier |
| `:del! chemin` | Comme `:del`, avec une nouvelle tentative via `sudo` si l'accès est refusé |
| `:rmf chemin` | Supprime directement avec `sudo rm -rf` |
| `:cd dossier` | Change le dossier courant |

Exemple de `:edit` sur plusieurs lignes :

```
:edit notes.txt "Ligne 1
Ligne 2
Ligne 3"
```

> Le texte d'un `:edit` ne peut pas contenir de guillemet `"`.
> L'ancienne commande `:crea` a été renommée `:add`.

### Programmes et système

| Commande | Description |
|---|---|
| `:cmd commande` | Exécute une commande Linux dans le terminal |
| `:run programme` | Lance un programme en arrière-plan |
| `:stop programme` | Arrête un programme par son nom (`pkill -x`) |
| `:wait nombre unité` | Pause. Unités : `sec`, `min`, `h`, `j`, `y` |
| `:re` | Redémarre l'ordinateur |
| `:off` | Éteint l'ordinateur |

### `:go` : lancer un second script dans une nouvelle fenêtre

```
:go autre.st
:go /home/user/scripts/autre.st
:go ~/scripts/autre.st
```

- Un chemin relatif est cherché **dans le dossier du script actuel**.
- Le second script s'ouvre dans une **nouvelle fenêtre de terminal visible**, avec son propre clavier : les deux scripts ne se perturbent plus (`:say?` compris).
- Le script d'origine continue sans attendre.
- À la fin du second script, la fenêtre affiche « Appuyez sur Entrée pour fermer cette fenêtre » pour laisser le temps de lire les messages.
- Le fichier doit exister et avoir l'extension `.st`.
- Un script ne peut pas se relancer lui-même avec `:go`.
- Les scripts lancés les uns par les autres sont limités à **5 niveaux**.
- Aucune nouvelle confirmation n'est demandée : l'avertissement `Y/n` du premier script suffit.

Terminaux pris en charge, essayés dans cet ordre : `xdg-terminal-exec`, `gnome-terminal`, `konsole`, `xfce4-terminal`, `mate-terminal`, `lxterminal`, `qterminal`, `tilix`, `terminator`, `alacritty`, `kitty`, `wezterm`, `foot`, `xterm`, `x-terminal-emulator`.
Si la variable d'environnement `TERMINAL` désigne l'un d'eux, il passe en premier.

Sans session graphique (SSH, console pure) ou sans terminal installé, `:go` affiche une erreur claire et ne lance rien.

### `:#` : relancer le script en root

```
:systeen start
:#
:say Je suis root !
:systeen end
```

`:#` fait, dans l'ordre :

1. `cd` vers le dossier où se trouve `systeen.py` (retrouvé automatiquement) ;
2. `sudo python systeen.py <ce script>` ;
3. arrête le script actuel dès que `sudo` démarre.

Il ne reste plus qu'à saisir le mot de passe root.

À savoir :

- Le script **repart depuis la première ligne** en root. Placez donc `:#` **tout en haut**, juste après `:systeen start`, sinon les lignes précédentes seront exécutées deux fois.
- Si vous êtes déjà root, `:#` est ignoré (pas de boucle infinie).
- Les variables sauvegardées avec `:save` sont écrites avant le passage en root.

### Mise à jour depuis un script

| Commande | Description |
|---|---|
| `:v` | Vérifie et installe la dernière version |
| `:v 0.6.0` | Installe une version précise |

---

## Variables

| Commande | Description |
|---|---|
| `:var add nom` | Crée une variable (valeur initiale : `X`) |
| `:var nom = valeur` | Modifie une variable existante |
| `:var rm nom` | Supprime une variable |
| `:var sys` | Crée les variables système (voir plus bas) |
| `:save nom` | Sauvegarde la variable dans un fichier `.vars` pour les prochains lancements |

On utilise une variable avec `$` : `:say Bonjour $nom`.
Un nom de variable peut contenir lettres, chiffres, `_` et `.`.
Utiliser une variable qui n'existe pas affiche une erreur `Variable-404`.

Les variables sauvegardées sont stockées à côté du script, dans `monscript.st.vars`, et rechargées automatiquement.

### Variables système (`:var sys`)

| Variable | Contenu |
|---|---|
| `$sys.user` | Nom de l'utilisateur |
| `$sys.hostname` | Nom de la machine |
| `$sys.os` | Distribution Linux |
| `$sys.kernel` | Version du noyau |
| `$sys.arch` | Architecture |
| `$sys.cpu` | Processeur |
| `$sys.cores` | Nombre de cœurs |
| `$sys.ram` | Mémoire totale |
| `$sys.stockage` | Espace libre là où se trouve le script |
| `$sys.battery` | Niveau de batterie (`N/A` si aucune) |
| `$sys.uptime` | Temps depuis le démarrage |
| `$sys.cwd` | Dossier courant |
| `$sys.script` | Chemin du script en cours |
| `$sys.perms` | Permissions du script |
| `$sys.home` | Dossier personnel |
| `$sys.shell` | Shell de l'utilisateur |
| `$sys.python` | Version de Python |

---

## Conditions

```
:if $age >= 18
 :say Majeur
:else
 :say Mineur
:elsend
```

### Présentation conseillée : 1 espace de plus par niveau

Pour se repérer facilement, décalez d'un espace tout ce qui se trouve dans un `:if`, et encore d'un espace pour chaque `:if` imbriqué. Le `:elsend` se place au niveau de son `:if`.

```
:if $a == 1
 :say a vaut 1
 :if $b == 2
  :say et b vaut 2
 :else
  :say mais b ne vaut pas 2
 :elsend
:else
 :say a ne vaut pas 1
:elsend
```

Au lancement, SysTeen signale les lignes mal décalées (ou un `:elsend` oublié) avec leur numéro. Ce n'est qu'un **conseil** : le script s'exécute normalement.

Chaque `:if` doit se terminer par un `:elsend`. Le `:else` est facultatif. Les `:if` peuvent être imbriqués.

À gauche d'une condition, il faut toujours une **variable** (sauf pour `exist`).

| Condition | Vrai quand… |
|---|---|
| `$a == valeur` / `$a != valeur` | égal / différent |
| `$a > valeur`, `<`, `>=`, `<=` | comparaison (numérique si possible) |
| `$a contains texte` | contient le texte |
| `$a not contains texte` | ne contient pas le texte |
| `$a startswith texte` | commence par le texte |
| `$a endswith texte` | finit par le texte |
| `empty $a` | la variable est vide |
| `notempty $a` | la variable n'est pas vide |
| `exist $a` | la variable existe |
| `exist chemin` | le fichier ou dossier existe (chemin relatif au script) |
| `not exist $a` / `not exist chemin` | l'inverse |

---

## Boucles

### Répéter une commande

```
:loop 3 :say Salut
:loop inf :say Ça tourne...
```

Commandes acceptées dans une boucle : `:say`, `:cmd`, `:math`, `:wait`, `:run`, `:stop`, `:go`.

### Sauter vers une ligne

```
:loop L5-3
```

Retourne à la **ligne 5**, **3 fois** (`:loop L5-inf` pour l'infini).

Arrêtez un script à tout moment avec `Ctrl + C`.

---

## Mises à jour

SysTeen se met à jour depuis les **releases GitHub** du projet, avec vérification **PGP** :

```bash
python systeen.py --maj
```

La mise à jour télécharge `systeen.py` et `README.md` avec leurs signatures, puis :

1. vérifie que la clé PGP intégrée correspond à l'empreinte attendue ;
2. vérifie les deux signatures détachées ;
3. contrôle que la version du fichier correspond à la release ;
4. n'installe qu'ensuite, en remplaçant les fichiers.

En cas de problème, rien n'est installé. `gpg` doit être présent sur la machine.

Empreinte de la clé de signature :

```
F7FE E16B FE36 DEAE 3507  9EFF 0FDD 49DB 07AC 253E
```

### Publier une version (mainteneur)

Chaque release `vX.Y.Z` doit contenir exactement ces quatre fichiers :

```bash
gpg --armor --detach-sign systeen.py
gpg --armor --detach-sign README.md
```

| Asset | Rôle |
|---|---|
| `systeen.py` | Le programme |
| `systeen.py.asc` | Sa signature détachée |
| `README.md` | Ce fichier |
| `README.md.asc` | Sa signature détachée |

Le tag doit correspondre à la variable `VERSION` de `systeen.py`. Toute modification d'un fichier après signature oblige à le re-signer.

---

## Désinstallation

```bash
python systeen.py --uninstall
```

SysTeen affiche la liste de ce qui sera supprimé, puis demande de taper exactement :

```
iwanttouninstallnowthesysteenexecutablethesysteenpackageandthesysteenproject
```

Éléments supprimés :

- `systeen.py` et `README.md` ;
- la commande `systeen` (`/usr/local/bin/systeen`) si elle a été installée avec `--install` ;
- les fichiers `.vars` créés par vos scripts ;
- la configuration (`~/.config/systeen/`) ;
- les fichiers de cache et de mise à jour temporaires.

Vos scripts `.st` ne sont **jamais** touchés. La clé PGP n'existe que dans le code de `systeen.py` : elle disparaît avec lui.

---

## Notes de version

### 0.7.2

- Nouvelle option **`--install`** : ajoute la commande `systeen` dans `/usr/local/bin` (lien vers `systeen.py`, qui ne bouge pas). On peut alors taper `systeen script.st` ou `systeen --help` partout.
- **`:go` ne redemande plus de confirmation** : l'avertissement `Y/n` du premier script suffit.
- Nouvelles commandes **`:sayn?`** (défaut y) et **`:sayN?`** (défaut n) : questions à réponse `y` ou `n` uniquement.
- Présentation des `:if` : décalage d'un espace par niveau, avec des conseils au lancement si ce n'est pas respecté (non bloquant).
- **`--uninstall`** : nouvelle phrase de confirmation, et suppression de la commande `systeen`. Les scripts `.st` ne sont jamais touchés, les `.vars` sont supprimés.
- Les messages d'aide affichent `systeen --help` quand SysTeen est lancé par la commande installée.

### 0.7.1

- **`:go` ouvre maintenant une nouvelle fenêtre de terminal** visible pour le second script, au lieu de le lancer dans le même terminal (fin des erreurs d'entrée clavier).
- La fenêtre attend une touche à la fin du script pour laisser lire les messages.
- Détection automatique du terminal graphique installé, avec essai du suivant si l'un échoue.
- Message d'erreur clair quand il n'y a pas de session graphique ou pas de terminal.

### 0.7.0

- `:crea` devient **`:add`**.
- Nouvelle commande **`:go`** : lance un second script en parallèle.
- Nouvelle commande **`:#`** : relance le script en root via `sudo`.
- Nouvelle option **`--change`** : modifier le choix de protection de `/` et du dossier personnel.
- Nouvelle option **`--uninstall`** : désinstallation complète avec phrase de confirmation.
- Un fichier ou une option inexistants affichent un message clair et renvoient vers `--help`.
- La configuration de sécurité reste celle de l'utilisateur réel, même sous `sudo`.

---

## Licence et contact

Projet développé par **SLNE Studio**, un studio de programmation français.
Merci d'utiliser les services SLNE.
