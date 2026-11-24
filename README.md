# SysTeen

**SysTeen** est un petit langage de script pour Linux, simple et lisible, interprété par `systeen.py` (Python 3).
Il sert à automatiser des tâches système : fichiers, variables, commandes Linux, boucles, conditions, scripts parallèles…

> Version actuelle : **0.9.1**
> Projet : [Lemillitaire3330/SysTeen](https://github.com/Lemillitaire3330/SysTeen)

---

## Sommaire

1. [Installation](#installation)
2. [Premier script](#premier-script)
3. [Exemple complet](#exemple-complet)
4. [Options de `systeen.py`](#options-de-systeenpy)
5. [Sécurité](#sécurité)
6. [Aide-mémoire](#aide-mémoire)
7. [Référence des commandes](#référence-des-commandes)
8. [Variables](#variables)
9. [Commandes abrégées (abv)](#commandes-abrégées-abv)
10. [Fenêtres (wui)](#fenêtres-wui)
11. [Chemins et dossiers de travail](#chemins-et-dossiers-de-travail)
12. [Conditions](#conditions)
13. [Boucles](#boucles)
14. [Erreurs et messages](#erreurs-et-messages)
15. [Vérifier un script](#vérifier-un-script)
16. [Mises à jour](#mises-à-jour)
17. [Fichiers utilisés par SysTeen](#fichiers-utilisés-par-systeen)
18. [Désinstallation](#désinstallation)
19. [Dépannage](#dépannage)
20. [Notes de version](#notes-de-version)

---

## Installation

Prérequis :

- Linux (SysTeen utilise `/proc`, `sudo` et `systemctl`)
- Python 3
- `gpg` (uniquement pour les mises à jour signées)
- `sudo` (uniquement pour `:#`, `:rmf` et `:del!`)
- un terminal graphique et une session graphique X11 ou Wayland (uniquement pour `:go`)
- `tkinter` et une session graphique (uniquement pour `:wui`) : Debian/Ubuntu `sudo apt install python3-tk`, Fedora `sudo dnf install python3-tkinter`, Arch `sudo pacman -S tk`

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
:var add $nom
:say? Comment tu t'appelles ? ; $nom
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

## Exemple complet

Ce script demande un dossier, affiche son nombre d'éléments, puis le copie dans `sauvegardes/` avec la date du jour et l'inscrit dans un journal :

```
:systeen start
# Sauvegarde un dossier dans sauvegardes/ avec la date du jour

:var sys
:var add $dossier
:var add $reponse
:var add $nombre

:say SysTeen $sys.version - $sys.date $sys.time
:say? Quel dossier sauvegarder ? ; $dossier

:if empty $dossier
 :say Aucun dossier indiqué.
 :systeen end
:elsend

:cmd ls $dossier | wc -l ; $nombre
:say $nombre élément(s) dans $dossier

:yN? Lancer la sauvegarde ? ; $reponse
:if $reponse == y
 :copy $dossier
 :paste sauvegardes/$dossier-$sys.date
 :txt +sauvegardes/journal.txt "$sys.date $sys.time : $dossier sauvegardé
"
 :say Sauvegarde terminée.
:else
 :say Annulé.
:elsend

:systeen end
```

Vérifiez-le sans l'exécuter avec `systeen --check sauvegarde.st`, puis lancez-le.

---

## Options de `systeen.py`

| Commande | Effet |
|---|---|
| `python systeen.py fichier.st` | Exécute un script SysTeen |
| `python systeen.py --maj` | Met à jour vers la dernière version |
| `python systeen.py --maj 0.6.0` | Installe une version précise (rollback) |
| `python systeen.py --update` | Alias de `--maj` |
| `python systeen.py --check fichier.st` | Vérifie un script **sans l'exécuter** (voir [Vérifier un script](#vérifier-un-script)) |
| `python systeen.py --install` | Installe la commande `systeen` dans `/usr/local/bin` |
| `python systeen.py --change` | Modifie le choix de la protection de `/` et du dossier personnel |
| `python systeen.py --uninstall` | Désinstalle SysTeen |
| `python systeen.py --readme` | Affiche ce README (celui installé à côté de `systeen.py`) |
| `python systeen.py --version` (ou `-V`) | Affiche la version installée |
| `python systeen.py --help` (ou `-h`) | Affiche l'aide |

Si vous tapez un fichier ou une option qui n'existe pas, SysTeen vous l'indique et vous rappelle que `python systeen.py --help` donne de l'aide.

Trois options **internes** existent aussi (`--no-confirm`, `--go-window`, `--go-depth=N`). Elles sont utilisées par `:go` et `:#` pour relancer SysTeen dans la bonne fenêtre, sans redemander la confirmation et en gardant la limite de profondeur. Ne les utilisez pas à la main.

---

## Sécurité

### Protection de `/` et du dossier personnel

Au premier lancement, SysTeen demande si la protection doit être activée (**oui par défaut**).
Quand elle est active, `:del`, `:del!` et `:rmf` refusent de supprimer `/` et votre dossier personnel.

Le choix est enregistré dans `~/.config/systeen/config.json`.
Il n'est pas définitif : `python systeen.py --change` permet de le modifier à tout moment.

### À savoir

- La protection concerne `:del`, `:del!` et `:rmf`. Pour `:cmd`, elle bloque aussi les `rm -r` évidents visant `/` ou votre dossier personnel (`rm -rf /`, `rm -rf ~`, `rm -rf /*`, `--no-preserve-root`…). Ce n'est **pas** une protection parfaite : une commande déguisée (script, `bash -c`, `find -delete`…) passe à travers.
- `:go` ne redemande **pas** de confirmation : l'avertissement `Y/n` accepté au lancement du premier script vaut pour les scripts qu'il lance. Relisez donc aussi les scripts appelés par `:go`.
- `:# commande` exécute **la commande entière** avec `sudo` (pipes et `&&` compris). Les mêmes protections que `:cmd` s'appliquent (blocage des `rm -r` évidents sur `/` ou le dossier personnel).
- Sous `sudo` (commande `:#`), SysTeen retrouve le vrai utilisateur grâce à `SUDO_USER` pour garder **sa** configuration de sécurité et **son** dossier personnel.
- Ne lancez jamais un script `.st` dont vous ne comprenez pas le contenu.

---

## Aide-mémoire

| Syntaxe | Effet |
|---|---|
| `:systeen start` / `:systeen end` | Début (obligatoire, ligne 1) / fin du script |
| `:#` | Relance **tout le script** en root (à mettre tout en haut) |
| `:# commande [; $variable]` | Exécute **une commande** avec sudo, sans relancer le script |
| `:v` / `:v 0.7.2` | Met à jour SysTeen / installe une version précise |
| `:var add $nom` | Crée une variable **temporaire** (valeur `X`) |
| `:var add !nom` | Crée une variable **permanente** (enregistrée automatiquement) |
| `:var $nom = valeur` / `:var !nom = valeur` | Change la valeur |
| `:var rm $nom` / `:var rm !nom` | Supprime la variable |
| `:var sys` | Crée les variables `$sys.…` |
| `:say texte` | Affiche du texte |
| `:sayr texte` | Remplace la dernière ligne affichée |
| `:say? question ; $variable` | Pose une question |
| `:Yn? question ; $variable` | Question y/n, Entrée = y |
| `:yN? question ; $variable` | Question y/n, Entrée = n |
| `:math expression [; $variable]` | Calcule |
| `:cmd commande [; $variable]` | Exécute une commande Linux (et garde son résultat) |
| `:pause [message]` | Attend la touche Entrée |
| `:run programme` / `:stop programme` | Lance / arrête un programme |
| `:go script.st` | Lance un autre script dans une nouvelle fenêtre |
| `:cd dossier` | Change de dossier |
| `:add nom` | Crée un fichier (avec extension) ou un dossier |
| `:txt fichier "texte"` / `:txt +fichier "texte"` | Écrit / ajoute du texte dans un fichier |
| `:read fichier ; $variable` | Lit un fichier dans une variable |
| `:copy chemin` puis `:paste destination` | Copie un fichier ou un dossier |
| `:wui "titre" {` ... `}` | Ouvre une fenêtre (texte et boutons) |
| `:abv nom {` ... `}` | Crée une commande abrégée `:nom` (enregistrée pour tous les scripts) |
| `:abv rm nom` | Supprime une commande abrégée |
| `:del chemin` / `:del! chemin` / `:rmf chemin` | Supprime (normal / avec sudo si refusé / sudo direct) |
| `:tmp nombre unité` | Pause (`sec`, `min`, `h`, `j`, `y` ; virgule acceptée : `0,6 sec`) |
| `:re` / `:off` | Redémarre / éteint l'ordinateur |
| `:if condition` ... `:else` ... `:elsend` | Condition |
| `:loop N :commande` | Répète une commande N fois (ou `inf`) |
| `:loop N` ... `:loopend` | Répète un bloc N fois (ou `inf`) |
| `:loop L5-3` | Retourne 3 fois à la ligne 5 |
| `# texte` | Commentaire |

---

## Référence des commandes

### Structure

| Commande | Description |
|---|---|
| `:systeen start` | Obligatoire en première ligne |
| `:systeen end` | Arrête le script (les variables permanentes sont déjà enregistrées) |

### Affichage et saisie

| Commande | Description |
|---|---|
| `:say texte` | Affiche un texte (les `$variables` sont remplacées) |
| `:sayr texte` | **Remplace la dernière ligne affichée** par ce texte (chargements, compteurs…) |
| `:say? question ; $variable` | Pose une question et stocke la réponse dans une variable **déjà créée** |
| `:Yn? question ; $variable` | Question à réponse `y` ou `n` uniquement, affichée `(Y/n)` : **Entrée = y** |
| `:yN? question ; $variable` | Pareil, affichée `(y/N)` : **Entrée = n** (choix recommandé pour les actions risquées) |

Exemple de chargement avec `:sayr` :

```
:say Chargement : 0%
:tmp 1 sec
:sayr Chargement : 50%
:tmp 1 sec
:sayr Chargement : 100% terminé !
```

- `:sayr` efface la ligne juste au-dessus du curseur (la dernière chose affichée, par `:say`, `:cmd`, un message SysTeen…) et la remplace. Plusieurs `:sayr` d'affilée se remplacent l'un l'autre.
- Il peut s'utiliser en boucle : `:loop 5 :sayr Patientez...`
- Il n'existe **pas** de `:sayr?`, `:saynr?` ni `:sayNr?` : une question attend une réponse au clavier, elle ne peut donc pas remplacer une ligne.
- Il faut un vrai terminal. Si la sortie est redirigée vers un fichier ou un tube (`systeen script.st > sortie.txt`), le texte est simplement ajouté à la suite.
- Une ligne plus longue que la largeur du terminal (qui passe à la ligne) n'est remplacée que sur sa dernière ligne d'écran : gardez les textes de `:sayr` courts.

Le nom indique la réponse par défaut : le **Y majuscule** de `:Yn?` (« Yes ») est celui qui se choisit en appuyant sur Entrée, le **N majuscule** de `:yN?` (« No ») aussi. Les deux commandes se distinguent donc par leur casse.

Avec `:Yn?` et `:yN?`, la variable reçoit `y` ou `n`, ce qui se teste avec `:if $variable == y`. Toute autre réponse est refusée et la question est reposée.

Pour les trois commandes de question, le **dernier** `;` de la ligne sépare la question de la variable : la question peut donc elle-même contenir des `;`.

### Calcul

```
:math 2 + 3 * 4
:math $a * 2 ; $resultat
```

Opérateurs : `+ - * / // % **` (et `+`/`-` unaires). Sans `; $variable`, le résultat est affiché.
L'expression est évaluée de façon sûre : aucun code Python arbitraire n'est exécuté.

### Fichiers et dossiers

| Commande | Description |
|---|---|
| `:add nom` | Crée un fichier si `nom` a une extension (`notes.txt`), sinon un dossier. Crée aussi les dossiers parents. Erreur si l'élément existe déjà |
| `:txt fichier "texte"` | Écrit le texte dans le fichier (écrase le contenu). Le texte peut s'étendre sur plusieurs lignes, jusqu'au guillemet fermant |
| `:txt +fichier "texte"` | Ajoute le texte **à la fin** du fichier (le crée s'il n'existe pas) |
| `:read fichier ; $variable` | Lit un fichier texte dans une variable **déjà créée** (le retour à la ligne final est retiré, 10 Mo maximum) |
| `:copy chemin` | Mémorise un fichier ou un dossier (comme « copier ») |
| `:paste destination` | Colle l'élément mémorisé par `:copy` (comme « coller ») |
| `:del chemin` | Supprime un fichier ou un dossier |
| `:del! chemin` | Comme `:del`, avec une nouvelle tentative via `sudo` si l'accès est refusé |
| `:rmf chemin` | Supprime directement avec `sudo rm -rf` |
| `:cd dossier` | Change le dossier courant |

Exemple de `:txt` sur plusieurs lignes :

```
:txt notes.txt "Ligne 1
Ligne 2
Ligne 3"
```

> Le texte d'un `:txt` ne peut pas contenir de guillemet `"`.
> L'ancienne commande `:crea` a été renommée `:add`, `:edit` est devenue `:txt`, `:wait` est devenue `:tmp`, `:sayn?` est devenue `:Yn?` et `:sayN?` est devenue `:yN?`.

Exemple de `:copy` / `:paste` :

```
:copy rapport.txt
:paste sauvegardes/            # dossier : collé dedans, même nom
:paste rapport_v2.txt          # sinon : nouveau nom complet
```

- Si la destination est un dossier existant (ou se termine par `/`), l'élément est collé **dedans** avec son nom d'origine. Sinon la destination est le nouveau chemin complet.
- Un même `:copy` peut être collé plusieurs fois.
- Rien n'est jamais écrasé : si la destination existe, c'est une erreur.
- Les dossiers sont copiés avec tout leur contenu (mais pas dans eux-mêmes).

### Programmes et système

| Commande | Description |
|---|---|
| `:cmd commande` | Exécute une commande Linux dans le terminal |
| `:cmd commande ; $variable` | Exécute la commande et met son **résultat** dans une variable **déjà créée** (le retour à la ligne final est retiré) |
| `:pause` / `:pause message` | Attend que l'utilisateur appuie sur Entrée |
| `:run programme` | Lance un programme en arrière-plan |
| `:stop programme` | Arrête un programme par son nom (`pkill -x`) |
| `:tmp nombre unité` | Pause. Unités : `sec`, `min`, `h`, `j`, `y`. Le nombre peut avoir une **virgule ou un point** : `:tmp 0,6 sec`, `:tmp 1.5 sec` |
| `:re` | Redémarre l'ordinateur |
| `:off` | Éteint l'ordinateur |

Exemple de capture :

```
:var add $nom
:cmd whoami ; $nom
:say Connecté en tant que $nom
```

Si ce qui suit le `;` est un programme ou une commande du shell (`:cmd echo a ; ls`), la ligne reste une commande shell normale. Si c'est un mot inconnu (variable oubliée), SysTeen affiche `Variable-404`.

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

### `:#` : sudo, pour une commande ou pour tout le script

**`:# commande`** exécute une seule commande avec `sudo`, **sans relancer le script** :

```
:# apt update
:# systemctl restart nginx
:var add $liste
:# ls /root ; $liste
```

- La commande entière tourne avec `sudo` (`sudo sh -c "…"`) : `:# apt update && apt upgrade -y` fonctionne en entier avec les droits root.
- `; $variable` garde le résultat, comme avec `:cmd`.
- Le mot de passe est demandé par `sudo` (ou pas, selon votre configuration).
- Si vous êtes déjà root, la commande est exécutée directement.

**`:#` seul**, sur une ligne, relance **tout le script** en root :

```
:systeen start
:#
:say Je suis root !
:systeen end
```

Dans l'ordre :

1. `cd` vers le dossier où se trouve `systeen.py` (retrouvé automatiquement) ;
2. `sudo python systeen.py <ce script>` ;
3. arrête le script actuel dès que `sudo` démarre.

Il ne reste plus qu'à saisir le mot de passe root. À savoir :

- Le script **repart depuis la première ligne** en root. Placez donc `:#` **tout en haut**, juste après `:systeen start`, sinon les lignes précédentes seront exécutées deux fois.
- Si vous êtes déjà root, `:#` est ignoré (pas de boucle infinie).
- Les variables permanentes (`!nom`) sont déjà enregistrées, et retrouvées en root.

### Mise à jour depuis un script

| Commande | Description |
|---|---|
| `:v` | Vérifie et installe la dernière version |
| `:v 0.6.0` | Installe une version précise |

---

## Variables

SysTeen a deux sortes de variables, qu'on distingue par leur signe :

| | Temporaire | Permanente |
|---|---|---|
| Créer | `:var add $nom` | `:var add !nom` |
| Utiliser | `$nom` ou `${nom}` | `!nom` ou `!{nom}` |
| Durée de vie | jusqu'à la fin du script | **enregistrée automatiquement**, retrouvée au prochain lancement |

| Commande | Description |
|---|---|
| `:var add $nom` | Crée une variable **temporaire** (valeur initiale : `X`) |
| `:var add !nom` | Crée une variable **permanente**. Si elle existe déjà, elle est conservée telle quelle |
| `:var $nom = valeur` / `:var !nom = valeur` | Modifie une variable existante |
| `:var rm $nom` / `:var rm !nom` | Supprime une variable (la suppression d'une permanente est enregistrée) |
| `:var sys` | Crée les variables système (voir plus bas) |

> La commande `:save` n'existe plus : une variable est permanente dès qu'elle est créée avec `!`.

- **Le signe est obligatoire, partout et tout le temps** : à la création (`:var add $nom`), à la modification (`:var $nom = …`), à la suppression (`:var rm $nom`), après un `;` et dans les textes. Un nom tout seul (`:var add nom`, `; nom`, `:var rm nom`) est toujours une erreur, qui indique le signe à écrire : c'est ce qui permet de distinguer `$nom` de `!nom` sans jamais hésiter.
- Un nom peut contenir lettres, chiffres, `_` et `.`, et peut **commencer par un chiffre** (`:var add $1` puis `$1` ou `${1}`). `:var add` refuse tout autre nom (crochets, `-`, espaces…), car on ne pourrait jamais l'écrire ensuite.
- `$nom` et `!nom` sont **deux variables distinctes** : on peut avoir les deux. Se tromper de signe donne une erreur qui indique le bon (« Elle existe en permanente : écrivez !nom »).
- Les commandes qui prennent une variable après un `;` (`:say?`, `:Yn?`, `:yN?`, `:math`, `:cmd`, `:read`) veulent elle aussi **le signe** : `; $nom` ou `; !nom`.
- Comme le point fait partie du nom, `$nom.txt` cherche la variable `nom.txt` : écrivez **`${nom}.txt`** (ou `!{nom}.txt`) pour délimiter le nom.
- Les crochets des syntaxes de ce document (`[nom]`, `[variable]`) indiquent seulement où mettre une valeur : ils ne s'écrivent pas. On écrit `$nom`, pas `$[nom]`.
- Utiliser une variable qui n'existe pas affiche une erreur `Variable-404`.

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
| `$sys.version` | Version de SysTeen |
| `$sys.date` | Date du jour (`AAAA-MM-JJ`) |
| `$sys.time` | Heure (`HH:MM:SS`) |

Ces valeurs sont lues au moment où `:var sys` s'exécute. Relancez `:var sys` pour les rafraîchir (par exemple l'heure).

### Valeurs : texte et nombres

- Une variable contient du texte. `:var $nom = 3` stocke `3`, et `:say? ...` stocke ce que la personne tape.
- `:math` stocke un nombre (`7 / 2` donne `3.5`).
- Dans une condition, si les deux côtés sont des nombres ils sont comparés comme des nombres, sinon comme du texte. Comparer un nombre et un texte avec `<` ou `>` donne l'erreur « Impossible de comparer ces valeurs ».

### Où le `$` et le `!` sont remplacés

SysTeen remplace `$nom` / `${nom}` et `!nom` / `!{nom}` dans : `:say`, `:sayr`, la question de `:say?` / `:Yn?` / `:yN?`, `:math`, `:cmd`, `:#`, `:run`, `:stop`, `:go`, `:cd`, `:add`, `:txt` (nom et texte), `:read`, `:copy`, `:paste`, `:pause`, `:del`, `:del!`, `:rmf`, la valeur de `:var nom = valeur` et les conditions de `:if`.

Il n'est **pas** remplacé dans `:tmp`, `:v`, ni pour les noms de variables eux-mêmes (`:var add $nom`, la variable après un `;`).

### Écrire un `$` ou un `!` littéral

Un `$` ou un `!` n'est une variable que **si un nom le suit directement**. Sinon (rien derrière, un espace, une ponctuation, `=`…), c'est un caractère normal, sans rien à doubler :

```
:say Bonjour !
:say Ça coûte 5 $
:say a != b
```

Quand un nom suit **vraiment** le caractère et que vous voulez le garder tel quel, doublez-le : `$$` donne `$` et `!!` donne `!`.

```
:say Ça coûte $$5
:say C'est !!important
:cmd echo $$HOME
```

> **Attention avec `:cmd` :** SysTeen remplace les `$nom` **avant** d'envoyer la commande au shell. Une variable du shell comme `$HOME` provoque donc une erreur `Variable-404`. Doublez le `$` pour que le shell la reçoive : `:cmd echo $$HOME` (ou utilisez `~` pour le dossier personnel).
>
> Attention aussi à `Bonjour!Alice` : le `!` est collé à un nom, c'est donc la variable permanente `Alice`.

### Variables permanentes

Une variable créée avec `!` est **enregistrée à chaque modification** (pas seulement à la fin du script) : elle survit même si le script est interrompu.

```
:systeen start
:var add !visites
:if !visites == X
 :var !visites = 0
:elsend
:math !visites + 1 ; !visites
:say Lancement numéro !visites
:systeen end
```

- **Elles sont propres à chaque script.** Le fichier est `~/.local/share/systeen/vars/<nom du script>-<empreinte>.vars`. L'empreinte vient du chemin complet du script : renommer ou déplacer un script le sépare de ses variables. Un script lancé par `:go` a les siennes.
- `:var add !nom` ne réinitialise jamais une variable déjà existante : écrivez la valeur de départ avec un `:if` comme ci-dessus.
- Les valeurs sont du texte ou des nombres. Le fichier est lisible (JSON), avec les droits `600`.
- Le dossier suit le standard XDG : `$XDG_DATA_HOME/systeen` si cette variable est définie, sinon `~/.local/share/systeen`.
- Les fichiers `.vars` sont supprimés par `--uninstall`.

> Dans un `:if`, `exist $nom` / `exist !nom` teste **la variable**, pas un chemin qu'elle contiendrait.

---

## Commandes abrégées (abv)

`:abv` crée vos propres commandes, enregistrées pour **tous** vos scripts :

```
:abv sauve {
 :copy $dossier
 :paste sauvegardes/$dossier-$sys.date
 :say Sauvegarde de $dossier terminée.
}
```

À partir de là, `:sauve` exécute ces lignes, dans ce script comme dans n'importe quel autre, aux lancements suivants :

```
:var sys
:var add $dossier
:var $dossier = projet
:sauve
```

| Syntaxe | Effet |
|---|---|
| `:abv nom {` ... `}` | Crée (ou **remplace**) la commande `:nom` |
| `:abv rm nom` | Supprime la commande `:nom` |

- Le `}` doit être **seul sur sa ligne**. Les lignes d'entre les deux sont des commandes SysTeen normales (`:if`, `:loop`, `:cmd`…). Décalez-les d'un espace, comme pour les `:if`.
- Le nom contient lettres, chiffres et `_`. Il ne peut pas être celui d'une commande existante (`:say`, `:go`…), ni `rm`.
- La commande est créée au moment où la ligne `:abv … {` s'exécute (pas si elle est dans un `:if` faux).
- La commande abrégée travaille **dans le script qui l'appelle** : elle voit ses variables temporaires et permanentes, ses `:copy`, son dossier courant…
- Elle n'accepte pas d'argument. Passez les valeurs par des variables.
- En cas d'erreur, le message indique la ligne **et** la commande : `Erreur ligne 2 de :sauve : …`.
- `:systeen end` dans une commande abrégée arrête tout le script.
- Une commande abrégée peut en appeler d'autres (10 niveaux au maximum).
- `--check` connaît les commandes déjà créées et celles définies plus haut dans le script.
- Chaque commande est un fichier lisible `~/.local/share/systeen/commands/<nom>.scmd` (le corps tel que vous l'avez écrit). Elles sont supprimées par `--uninstall`.

---

## Fenêtres (wui)

`:wui` ouvre une vraie fenêtre graphique, la remplit de texte et de boutons, puis **attend qu'elle soit fermée** :

```
:systeen start
:var add $nom
:var add !choix
:var $nom = Alice
:wui "Ma fenêtre" {
 '300/500'
 'Color:red'
 'Size:16'
 ~Bonjour $nom
 ~Une deuxième ligne
 'Color:blue'
 ~Une ligne en bleu
 S~Saisissez ici votre prénom ; $nom
 B~ oui/non/others ; !choix
}
:say $nom a choisi : !choix
:systeen end
```

| Ligne du bloc | Effet |
|---|---|
| `:wui "titre" {` | Ouvre le bloc. Le titre devient celui de la fenêtre (les variables y sont remplacées) |
| `'hauteur/largeur'` | Taille de la fenêtre en pixels : `'300/500'` = 300 de haut, 500 de large (de 50 à 5000). Par défaut `300/400`. Si plusieurs lignes en donnent une, la dernière compte. **Une fenêtre plus grande que l'écran est réduite à la taille de l'écran** (un message l'indique) |
| `'Color:couleur'` | Couleur du texte et des boutons **qui suivent** : un nom anglais (`red`, `blue`, `darkgreen`…) ou un code `#rrggbb`. `'Couleur:…'` fonctionne aussi |
| `'Size:taille'` | Taille du texte et des boutons **qui suivent**, de 1 à 200 (par défaut 12). `'Taille:…'` fonctionne aussi |
| `~texte` | Une ligne de texte (le `~` est obligatoire). `$nom` et `!nom` y sont remplacés. `~` seul donne une ligne vide |
| `B~ oui/non/others ; $variable` | Une rangée de boutons, un par mot séparé par `/` (ils passent à la ligne suivante si la fenêtre est étroite). Le clic met le texte du bouton dans la variable et **ferme la fenêtre** |
| `S~Texte indicatif ; $variable` | Un **champ de saisie** : une case blanche où le texte indicatif apparaît en **gris** et disparaît dès qu'on clique dedans. Ce qui est tapé est mis dans la variable quand on valide |
| `}` | Ferme le bloc (seul sur sa ligne) |

- **Les paramètres changent en cours de route** : `'Color:…'` et `'Size:…'` s'appliquent à tout ce qui est écrit ensuite, jusqu'au prochain changement. Dans l'exemple, les deux premiers textes sont rouges et le reste est bleu.
- **La variable d'un bouton** est écrite comme partout, avec son signe (`$nom` ou `!nom`), et doit déjà exister. Avec une variable permanente (`!nom`), le choix est même retrouvé au lancement suivant.
- **Valider** : un clic sur un bouton, ou la touche **Entrée** dans un champ de saisie, enregistre **toutes** les saisies et le texte du bouton cliqué dans leurs variables, puis ferme la fenêtre. Un champ laissé vide donne une variable vide (testez-la avec `:if empty $variable`).
- **Sans bouton**, si la fenêtre contient des saisies, un bouton **OK** est ajouté automatiquement.
- **Fermer la fenêtre avec la croix**, sans valider, ne modifie aucune variable.
- **Avec plusieurs rangées `B~`**, un clic sur n'importe quel bouton ferme la fenêtre, et seule la variable du bouton cliqué est modifiée.
- **Tout est vérifié avant l'ouverture** (variables, couleur). En cas d'erreur, aucune fenêtre n'apparaît et le script continue après le `}`.
- Les lignes vides et celles qui commencent par `#` sont ignorées. Les lignes du bloc ne sont pas des commandes (pas de `:` devant) : décalez-les d'un espace, comme dans les autres blocs.
- **La fenêtre reste dans l'écran** : si la taille demandée dépasse la résolution de l'écran, elle est réduite (par exemple `2000/3000` sur un écran 1366×768 donne une fenêtre un peu plus petite que l'écran) et **centrée**, pour qu'aucune partie ne soit hors champ. Le contenu qui ne tient pas défile.
- **Elle s'ouvre toujours tout en haut** : le début du contenu est visible au lancement. La vue ne bouge que quand vous défilez vous-même.
- **Retour à la ligne et défilement** : les textes passent à la ligne selon la **largeur réelle** de la fenêtre (même si vous l'agrandissez ou la réduisez). Quand le contenu est plus grand que la fenêtre, une **barre de défilement** apparaît à droite : on défile avec la molette, la barre, `PageHaut` / `PageBas` ou les flèches `↑` `↓`, jusqu'au dernier bouton.
- Il faut `tkinter` et une session graphique (voir [Installation](#installation)). Sans eux, `:wui` affiche une erreur claire, saute le bloc et le script continue.
- `--check` vérifie les blocs `:wui` (lignes non reconnues, dimensions, variables, `}` manquant).

---

## Chemins et dossiers de travail

| Commande | Un chemin relatif part de… |
|---|---|
| `:add`, `:txt`, `:read`, `:copy`, `:paste`, `:del`, `:del!`, `:rmf`, `:cd` | le **dossier courant** (celui d'où vous avez lancé SysTeen, modifié par `:cd`) |
| `:go` et `exist chemin` dans un `:if` | le **dossier du script** |
| fichier `.vars` (variables permanentes) | `~/.local/share/systeen/vars/`, pas à côté du script |

- `~` est remplacé par votre dossier personnel.
- Un chemin absolu (`/home/user/...`) fonctionne partout.
- `$sys.cwd` donne le dossier courant et `$sys.script` le chemin du script.
- `:cmd` et `:run` sont exécutés dans le dossier courant.

---

## Conditions

```
:if $age >= 18
 :say Majeur
:else
 :say Mineur
:elsend
```

### Combiner des conditions : `and` / `or`

```
:if $age >= 18 and $pays == FR
 :say Majeur en France
:elsend

:if $a == 1 or exist fichier.txt
 :say a vaut 1, ou le fichier existe
:elsend
```

`and` passe avant `or`. Un `and`/`or` n'est reconnu que s'il est suivi d'une vraie condition (`$variable`, `exist`, `empty`, `notempty`) : `:if $texte contains rock and roll` fonctionne donc comme avant.

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

Au lancement, SysTeen signale les lignes mal décalées (ou un `:elsend` / `:loopend` oublié) avec leur numéro. Ce n'est qu'un **conseil** : le script s'exécute normalement. La même présentation s'applique aux boucles en bloc.

Chaque `:if` doit se terminer par un `:elsend`. Le `:else` est facultatif. Les `:if` peuvent être imbriqués.

À gauche d'une condition, il faut toujours une **variable** : `$nom` ou `!nom` (sauf pour `exist chemin`). Les exemples ci-dessous utilisent `$`, mais `!` fonctionne partout de la même façon.

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

Commandes acceptées dans cette forme : `:say`, `:sayr`, `:cmd`, `:math`, `:tmp`, `:run`, `:stop`, `:go`.

### Répéter plusieurs lignes : `:loop N` ... `:loopend`

```
:loop 3
 :say Début du tour
 :loop 2
  :say  petit tour
 :loopend
:loopend
```

- `:loop 5` répète le bloc 5 fois, `:loop inf` à l'infini (sortez avec `:systeen end` dans un `:if`, ou `Ctrl + C`).
- `:loop 0` saute le bloc.
- Les boucles peuvent être imbriquées et contenir des `:if` (et inversement).
- Indentez le contenu d'un espace par niveau, comme pour les `:if`.

### Sauter vers une ligne

```
:loop L5-3
```

Retourne à la **ligne 5**, **3 fois** (`:loop L5-inf` pour l'infini).

Arrêtez un script à tout moment avec `Ctrl + C`.

---

## Erreurs et messages

Quand une ligne échoue, SysTeen affiche le numéro de ligne :

```
[SysTeen] Erreur ligne 12 : Variable-404 : la variable 'nom' n'existe pas.
```

**Une erreur n'arrête pas le script** : la ligne fautive est ignorée et l'exécution continue à la ligne suivante. Pour repérer les problèmes avant de lancer, utilisez [`--check`](#vérifier-un-script).

| Message | Cause |
|---|---|
| `Une variable s'écrit toujours avec son signe` | nom de variable écrit sans `$` ni `!` (`:var add nom`, `; nom`…) : ajoutez le signe |
| `Variable-404 : la variable 'x' n'existe pas` | variable non créée avec `:var add`, `$sys.…` sans `:var sys`, ou `$HOME` dans un `:cmd` (écrire `$$HOME`) |
| `… Elle existe en permanente : écrivez !x` | la variable existe, mais avec l'autre signe (`$` / `!`) |
| `La variable 'x' existe déjà` | `:var add $x` sur une variable temporaire déjà créée |
| `Nom de variable invalide` | `:var add` avec un nom qui contient autre chose que lettres, chiffres, `_` et `.` |
| `La commande :save a été supprimée` | utilisez une variable permanente : `:var add !nom` |
| `La commande :edit a été renommée :txt` | ancien nom de `:txt` |
| `Le nom 'x' est déjà utilisé par une commande SysTeen` | nom refusé par `:abv` |
| `:abv sans } fermant` / `:wui sans } fermant` | le `}` seul sur sa ligne manque |
| `La commande :wait a été renommée :tmp` | ancien nom de `:tmp` |
| `Les commandes :sayn? et :sayN? ont été renommées :Yn? et :yN?` | anciens noms de `:Yn?` et `:yN?` |
| `tkinter est introuvable` | `:wui` a besoin de `tkinter` (voir [Installation](#installation)) |
| `:wui ouvre une fenêtre, mais aucun affichage graphique` | pas de session graphique (SSH, console) |
| `Couleur inconnue : 'x'` | couleur de `'Color:…'` invalide (nom anglais ou `#rrggbb`) |
| `Commande inconnue : :x` | faute de frappe, ou commande qui n'existe pas |
| `:if sans :elsend` / `:loop sans :loopend` | bloc non fermé |
| `Accès refusé. Utilisez :del! ou :rmf.` | `:del` sans les droits nécessaires |
| `... bloquée par la sécurité SysTeen` | suppression de `/` ou du dossier personnel, la protection étant active |
| `Trop de scripts lancés les uns par les autres` | plus de 5 niveaux de `:go` |

Quelques erreurs sont **fatales** et arrêtent SysTeen avant le début (code de sortie `1`) : fichier introuvable, extension autre que `.st`, première ligne différente de `:systeen start`.

`Ctrl + C` arrête un script (code `130`). Les erreurs d'une ligne ne changent pas le code de sortie.

---

## Vérifier un script

La commande est `--check` :

```bash
systeen --check mon_script.st
```

SysTeen analyse le script **sans rien exécuter** et signale :

- les commandes inconnues et les arguments manquants ;
- les `:if` / `:loop` / `:abv` mal fermés (`:elsend`, `:loopend` ou `}` oublié ou en trop) ;
- les variables utilisées avant d'être créées (`:var add`), et `$sys.…` sans `:var sys` ;
- les fichiers de `:go` introuvables ;
- une syntaxe invalide pour `:tmp`, `:loop`, `:say?`, `:read`… ;
- en simple conseil : l'indentation, et l'absence de `:systeen end` (le script recommence alors depuis la première ligne quand il arrive à la fin).

Le code de retour est `1` s'il y a des erreurs, `0` sinon. L'analyse est statique : elle suit l'ordre des lignes, sans exécuter les `:if` ni les boucles, donc une variable créée dans une branche est considérée comme créée.

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

## Fichiers utilisés par SysTeen

| Fichier | Rôle |
|---|---|
| `systeen.py` | Le programme (remplacé par `--maj`) |
| `README.md` | Ce fichier, à côté de `systeen.py` (affiché par `--readme`) |
| `/usr/local/bin/systeen` | Lien vers `systeen.py`, créé par `--install` |
| `~/.config/systeen/config.json` | Choix de la protection de `/` et du dossier personnel (droits `600`) |
| `~/.local/share/systeen/vars/*.vars` | Variables **permanentes** (`!nom`), un fichier par script |
| `~/.local/share/systeen/commands/*.scmd` | Commandes abrégées créées avec `:abv`, un fichier par commande |
| `~/.local/share/systeen/.migration-0.9.0` | Indique que la migration depuis la 0.8.2 a déjà été faite |
| `.systeen.py.update.new`, `.README.md.update.new` | Fichiers temporaires pendant une mise à jour |
| `/tmp/systeen-update-*` | Dossiers temporaires de mise à jour |

Sous `sudo` (commande `:#`), SysTeen utilise toujours la configuration **et les données** du **vrai** utilisateur, pas celles de root.

**Pourquoi `~/.local/share` et pas `/usr` ou `/var` ?** Ces dossiers sont réservés à root : un script lancé en simple utilisateur ne pourrait pas y écrire, et les variables et commandes d'un utilisateur ne doivent pas être partagées avec les autres. `~/.local/share/systeen` est l'emplacement standard (XDG) des données d'une application, et `~/.config/systeen` celui de sa configuration.

### Migration depuis la 0.8.2

Au **premier lancement** de la 0.9.0, SysTeen déplace (`mv`) les anciens fichiers `.vars`, qui étaient à côté des scripts, vers `~/.local/share/systeen/vars/`, et supprime l'ancien registre `vars_registry.json`. Les variables qu'ils contiennent deviennent des variables **permanentes** : dans vos scripts, remplacez `$nom` par `!nom` et supprimez les `:save`.

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
- les variables permanentes (`.vars`) et les commandes abrégées (`.scmd`), donc tout `~/.local/share/systeen/` ;
- la configuration (`~/.config/systeen/`) ;
- les fichiers de cache et de mise à jour temporaires.

Vos scripts `.st` ne sont **jamais** touchés. La clé PGP n'existe que dans le code de `systeen.py` : elle disparaît avec lui.

---

## Dépannage

| Problème | Solution |
|---|---|
| `systeen: command not found` | Lancez `python systeen.py --install`. Si vous avez déplacé `systeen.py`, relancez-le aussi. Vérifiez que `/usr/local/bin` est dans votre `PATH` |
| Le script ne s'arrête jamais | Terminez-le par `:systeen end` (sinon il recommence à la ligne 1), ou faites `Ctrl + C` |
| `La variable 'x' existe déjà` | Le script a recommencé (pas de `:systeen end`) : ajoutez-le, ou créez la variable avec `!` si elle doit survivre |
| `Une variable s'écrit toujours avec son signe` | Ajoutez `$` (temporaire) ou `!` (permanente) devant le nom, partout où il apparaît |
| `Variable-404` dans un `:cmd` | Écrivez `$$HOME` (dollar doublé) pour les variables du shell, ou `~` pour le dossier personnel |
| `$1` ou `${1}` ne donne pas la valeur | La variable doit exister : `:var add $1` puis `:var $1 = valeur`. Écrivez `$1`, pas `$[1]` |
| `Variable-404 … Elle existe en permanente` | Une variable créée avec `!` s'utilise avec `!` : `!nom` et non `$nom` |
| Mes anciennes variables `:save` ont disparu | Elles sont maintenant permanentes : utilisez `!nom` (voir [Migration](#migration-depuis-la-082)) |
| Une variable permanente est vide après avoir déplacé le script | Le fichier est lié au chemin complet du script : copiez `~/.local/share/systeen/vars/<ancien nom>-….vars` sous le nouveau nom, ou refaites la saisie |
| `Le nom 'x' est déjà utilisé par une commande SysTeen` | Choisissez un autre nom pour `:abv` |
| `:wui` affiche « tkinter est introuvable » | Installez-le : `sudo apt install python3-tk` (Debian/Ubuntu), `sudo dnf install python3-tkinter` (Fedora), `sudo pacman -S tk` (Arch) |
| `:go` n'ouvre pas de fenêtre | Il faut une session graphique et l'un des terminaux listés dans [`:go`](#go--lancer-un-second-script-dans-une-nouvelle-fenêtre). Installez par exemple `xterm` |
| `:#` rejoue des lignes déjà exécutées | Le script repart de la ligne 1 en root : placez `:#` juste après `:systeen start` |
| `:del` répond « Accès refusé » | Utilisez `:del!` (ou `:rmf`) |
| `GPG est requis` pendant `--maj` | Installez `gpg` |
| Signature PGP invalide pendant `--maj` | La release GitHub est mal signée ou a été modifiée : rien n'est installé |
| Conseils d'indentation au lancement | Ils ne bloquent rien : décalez les lignes d'un espace par niveau pour les faire disparaître |
| Un script se comporte mal | Lancez `systeen --check script.st` avant de le lancer |

---

## Notes de version

### 0.9.1

- **`:wui`** : les textes passent maintenant à la ligne selon la largeur réelle de la fenêtre, le contenu **défile** (molette, barre, `PageHaut`/`PageBas`, flèches) quand il dépasse, et les boutons se répartissent sur plusieurs lignes si la fenêtre est étroite.
- **`:wui` : champs de saisie** avec `S~Texte indicatif ; $variable` : case blanche, texte indicatif en gris, validation par un bouton ou la touche Entrée (un bouton OK est ajouté s'il n'y en a pas).
- **`:wui` : fenêtre plus grande que l'écran** : elle est réduite à la taille de l'écran et centrée (avant, une partie du contenu pouvait être hors champ). Elle s'ouvre aussi toujours **tout en haut** du contenu.
- **`:sayn?` devient `:Yn?`** et **`:sayN?` devient `:yN?`**. Les anciens noms affichent un message.
- **`:tmp` accepte la virgule** : `:tmp 0,6 sec` (le point reste accepté). Un nombre négatif est refusé.

### 0.9.0

- **`:wait` devient `:tmp`** (mêmes unités : `sec`, `min`, `h`, `j`, `y`). L'ancien nom affiche un message.
- **`:wui`** : crée des fenêtres (texte, couleurs, tailles, boutons qui remplissent une variable). Nécessite `tkinter`.
- **Le signe est obligatoire pour toute variable** : `$nom` (temporaire) ou `!nom` (permanente), à la création, à la modification, à la suppression, après un `;` et dans les textes. Un nom sans signe (`:var add nom`, `:math 1 + 1 ; nom`…) est toujours une erreur, et `--check` le signale. Cela évite toute ambiguïté entre `$nom` et `!nom`.
- **`:edit` devient `:txt`** (`:txt fichier "texte"` et `:txt +fichier "texte"`). L'ancien nom affiche un message.
- **Variables permanentes** : `:var add !nom` crée une variable enregistrée automatiquement, qu'on utilise avec `!nom`. `:var add $nom` crée une variable temporaire. **`:save` est supprimée.** Un `$` ou un `!` sans nom derrière est un caractère normal ; `$$` et `!!` donnent un caractère littéral.
- **`:# commande`** : exécute une commande avec `sudo`, sans relancer le script (`:#` seul relance toujours tout le script en root).
- **`:abv`** : crée des commandes abrégées persistantes (`:abv nom { ... }`, `:abv rm nom`).
- **Nouveaux emplacements** : les variables permanentes (`.vars`) et les commandes (`.scmd`) sont dans `~/.local/share/systeen/`, plus à côté des scripts. Migration automatique (`mv`) au premier lancement.
- `--check` et les conseils d'indentation connaissent les nouveautés (`!nom`, `:abv`, `:txt`).

### 0.8.2

- Nouvelle commande **`:sayr texte`** : remplace la dernière ligne affichée (chargements, compteurs, animations). Il n'existe volontairement pas de `:sayr?`, `:saynr?`… : une question attend une réponse au clavier et ne peut pas remplacer une ligne.

### 0.8.1

- **`:cmd commande ; variable`** : met le résultat de la commande dans une variable existante.
- **`:read fichier ; variable`** : lit un fichier dans une variable. **`:edit +fichier "texte"`** ajoute à la fin d'un fichier.
- **`:copy`** et **`:paste`** : copier un fichier ou un dossier, puis le coller (sans jamais écraser).
- **Boucles en bloc** : `:loop N` ... `:loopend` (imbriquables, `inf` possible).
- **`and` / `or`** dans les conditions.
- **`${nom}`** pour délimiter un nom de variable (`${nom}.txt`).
- **`$sys.version`**, **`$sys.date`**, **`$sys.time`**.
- **`:pause`** : attend la touche Entrée.
- **`--check`** : vérifie un script sans l'exécuter.
- Les erreurs indiquent maintenant le **numéro de ligne**.
- **Sécurité de `:cmd`** : les `rm -r` évidents sur `/` ou le dossier personnel sont bloqués quand la protection est active.
- Correction : la limite de profondeur de `:go` n'était plus transmise après un `:#` (sudo réinitialise l'environnement).
- Les noms de variables peuvent commencer par un chiffre (`$1`, `${1}`) ; `:var add` refuse les noms qu'on ne pourrait pas écrire ensuite (`[variable]`, `mon-nom`…).
- **`$$`** donne un `$` littéral (`:cmd echo $$HOME`, `:say Ça coûte $$5`).
- README complété : exemple complet, aide-mémoire, chemins, remplacement des `$`, erreurs et messages, fichiers utilisés, dépannage.

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
