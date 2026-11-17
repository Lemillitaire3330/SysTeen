# SysTeen

**SysTeen** est un petit langage de script pour Linux, simple et lisible, interprété par `systeen.py` (Python 3).
Il sert à automatiser des tâches système : fichiers, variables, commandes Linux, boucles, conditions, scripts parallèles…

> Version actuelle : **0.8.3**
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
9. [Abréviations](#abréviations)
10. [Chemins et dossiers de travail](#chemins-et-dossiers-de-travail)
11. [Conditions](#conditions)
12. [Boucles](#boucles)
13. [Erreurs et messages](#erreurs-et-messages)
14. [Vérifier un script](#vérifier-un-script)
15. [Mises à jour](#mises-à-jour)
16. [Fichiers utilisés par SysTeen](#fichiers-utilisés-par-systeen)
17. [Désinstallation](#désinstallation)
18. [Dépannage](#dépannage)
19. [Notes de version](#notes-de-version)

---

## Installation

Prérequis :

- Linux (SysTeen utilise `/proc`, `sudo` et `systemctl`)
- Python 3
- `gpg` (uniquement pour les mises à jour signées)
- `sudo` (pour `:#`, `:rmf`, `:del!` et pour créer `/var/lib/systeen` au premier lancement)
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

- La **première ligne** doit être `:sys start`.
- Chaque commande commence par `:`.
- Une ligne qui commence par `#` est un commentaire.
- Les lignes vides, et les lignes qui ne commencent pas par `:`, sont ignorées.

```
:sys start

# Mon premier script
:var add $nom
:say? Comment tu t'appelles ? ; nom
:say Bonjour $nom !

:sys end
```

Lancement :

```bash
python systeen.py mon_script.st
```

> **Important : un script recommence à la ligne 1 quand il arrive à la fin.**
> Pour qu'il s'arrête, terminez-le par `:sys end`.

Avant chaque lancement, SysTeen rappelle l'état de la sécurité et demande confirmation (`Y/n`). Relisez toujours le code d'un script avant de l'exécuter.

---

## Exemple complet

Ce script demande un dossier, affiche son nombre d'éléments, puis le copie dans `sauvegardes/` avec la date du jour et l'inscrit dans un journal :

```
:sys start
# Sauvegarde un dossier dans sauvegardes/ avec la date du jour

:var sys
:var add $dossier
:var add $reponse
:var add $nombre

:say SysTeen $sys.version - $sys.date $sys.time
:say? Quel dossier sauvegarder ? ; dossier

:if empty $dossier
 :say Aucun dossier indiqué.
 :sys end
:eif

:cmd ls $dossier | wc -l ; nombre
:say $nombre élément(s) dans $dossier

:yN? Lancer la sauvegarde ? ; reponse
:if $reponse == y
 :cpy $dossier
 :pst sauvegardes/$dossier-$sys.date
 :txt +sauvegardes/journal.txt "$sys.date $sys.time : $dossier sauvegardé
"
 :say Sauvegarde terminée.
:els
 :say Annulé.
:eif

:sys end
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

Le choix est enregistré dans `/var/lib/systeen/<utilisateur>/config.json`.
Il n'est pas définitif : `python systeen.py --change` permet de le modifier à tout moment.

### À savoir

- La protection concerne `:del`, `:del!` et `:rmf`. Pour `:cmd` et `:# commande`, elle bloque aussi les `rm -r` évidents visant `/` ou votre dossier personnel (`rm -rf /`, `rm -rf ~`, `rm -rf /*`, `--no-preserve-root`…). Ce n'est **pas** une protection parfaite : une commande déguisée (script, `bash -c`, `find -delete`…) passe à travers.
- `:go` ne redemande **pas** de confirmation : l'avertissement `Y/n` accepté au lancement du premier script vaut pour les scripts qu'il lance. Relisez donc aussi les scripts appelés par `:go`.
- Sous `sudo` (commande `:#`), SysTeen retrouve le vrai utilisateur grâce à `SUDO_USER` pour garder **sa** configuration de sécurité, **ses** données et **son** dossier personnel.
- Les [abréviations](#abréviations) (`:abv`) restent enregistrées d'un lancement à l'autre : relisez aussi le contenu des scripts qui en définissent.
- Ne lancez jamais un script `.st` dont vous ne comprenez pas le contenu.

---

## Aide-mémoire

| Syntaxe | Effet |
|---|---|
| `:sys start` / `:sys end` | Début (obligatoire, ligne 1) / fin du script |
| `:#` | Relance le script en root (à mettre tout en haut) |
| `:# commande` | Exécute **une seule** ligne de commande Linux en root |
| `:v` / `:v 0.7.2` | Met à jour SysTeen / installe une version précise |
| `:var add $nom` | Crée une variable (valeur `X`) |
| `:var add !nom` | Crée une variable **permanente** (gardée entre deux lancements) |
| `:var nom = valeur` | Change la valeur |
| `:var rm nom` | Supprime la variable |
| `:var sys` | Crée les variables `$sys.…` |
| `:abv nom {` ... `}` | Crée une abréviation (un raccourci : ensuite `:nom`) |
| `:say texte` | Affiche du texte |
| `:syr texte` | Remplace la dernière ligne affichée |
| `:say? question ; variable` | Pose une question |
| `:yn? question ; variable` | Question y/n, Entrée = y |
| `:yN? question ; variable` | Question y/n, Entrée = n |
| `:cal expression [; variable]` | Calcule |
| `:cmd commande [; variable]` | Exécute une commande Linux (et garde son résultat) |
| `:pau [message]` | Attend la touche Entrée |
| `:run programme` / `:kil programme` | Lance / arrête un programme |
| `:go script.st` | Lance un autre script dans une nouvelle fenêtre |
| `:cd dossier` | Change de dossier |
| `:add nom` | Crée un fichier (avec extension) ou un dossier |
| `:txt fichier "texte"` / `:txt +fichier "texte"` | Écrit / ajoute du texte dans un fichier |
| `:get fichier ; variable` | Lit un fichier dans une variable |
| `:cpy chemin` puis `:pst destination` | Copie un fichier ou un dossier |
| `:del chemin` / `:del! chemin` / `:rmf chemin` | Supprime (normal / avec sudo si refusé / sudo direct) |
| `:wai nombre unité` | Pause (`sec`, `min`, `h`, `j`, `y`) |
| `:re` / `:off` | Redémarre / éteint l'ordinateur |
| `:if condition` ... `:if+ condition` ... `:els` ... `:eif` | Condition (`:if+` = « sinon si ») |
| `:rep N :commande` | Répète une commande N fois (ou `inf`) |
| `:rep N` ... `:erp` | Répète un bloc N fois (ou `inf`) |
| `:rep L5-3` | Retourne 3 fois à la ligne 5 |
| `# texte` | Commentaire |

---

## Référence des commandes

### Structure

| Commande | Description |
|---|---|
| `:sys start` | Obligatoire en première ligne |
| `:sys end` | Arrête le script et sauvegarde les variables permanentes |

### Affichage et saisie

| Commande | Description |
|---|---|
| `:say texte` | Affiche un texte (les `$variables` sont remplacées) |
| `:syr texte` | **Remplace la dernière ligne affichée** par ce texte (chargements, compteurs…) |
| `:say? question ; variable` | Pose une question et stocke la réponse dans une variable **déjà créée** |
| `:yn? question ; variable` | Question à réponse `y` ou `n` uniquement, affichée `(Y/n)` : **Entrée = y** |
| `:yN? question ; variable` | Pareil, affichée `(y/N)` : **Entrée = n** (choix recommandé pour les actions risquées) |

Exemple de chargement avec `:syr` :

```
:say Chargement : 0%
:wai 1 sec
:syr Chargement : 50%
:wai 1 sec
:syr Chargement : 100% terminé !
```

- `:syr` efface la ligne juste au-dessus du curseur (la dernière chose affichée, par `:say`, `:cmd`, un message SysTeen…) et la remplace. Plusieurs `:syr` d'affilée se remplacent l'un l'autre.
- Il peut s'utiliser en boucle : `:rep 5 :syr Patientez...`
- Il n'existe **pas** de `:syr?` : une question attend une réponse au clavier, elle ne peut donc pas remplacer une ligne.
- Il faut un vrai terminal. Si la sortie est redirigée vers un fichier ou un tube (`systeen script.st > sortie.txt`), le texte est simplement ajouté à la suite.
- Une ligne plus longue que la largeur du terminal (qui passe à la ligne) n'est remplacée que sur sa dernière ligne d'écran : gardez les textes de `:syr` courts.

Avec `:yn?` et `:yN?`, la variable reçoit `y` ou `n`, ce qui se teste avec `:if $variable == y`. Toute autre réponse est refusée et la question est reposée.

Pour les trois commandes de question, le **dernier** `;` de la ligne sépare la question de la variable : la question peut donc elle-même contenir des `;`.

### Calcul

```
:cal 2 + 3 * 4
:cal $a * 2 ; resultat
```

Opérateurs : `+ - * / // % **` (et `+`/`-` unaires). Sans `; variable`, le résultat est affiché.
L'expression est évaluée de façon sûre : aucun code Python arbitraire n'est exécuté.

### Fichiers et dossiers

| Commande | Description |
|---|---|
| `:add nom` | Crée un fichier si `nom` a une extension (`notes.txt`), sinon un dossier. Crée aussi les dossiers parents. Erreur si l'élément existe déjà |
| `:txt fichier "texte"` | Écrit le texte dans le fichier (écrase le contenu). Le texte peut s'étendre sur plusieurs lignes, jusqu'au guillemet fermant |
| `:txt +fichier "texte"` | Ajoute le texte **à la fin** du fichier (le crée s'il n'existe pas) |
| `:get fichier ; variable` | Lit un fichier texte dans une variable **déjà créée** (le retour à la ligne final est retiré, 10 Mo maximum) |
| `:cpy chemin` | Mémorise un fichier ou un dossier (comme « copier ») |
| `:pst destination` | Colle l'élément mémorisé par `:cpy` (comme « coller ») |
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

Exemple de `:cpy` / `:pst` :

```
:cpy rapport.txt
:pst sauvegardes/            # dossier : collé dedans, même nom
:pst rapport_v2.txt          # sinon : nouveau nom complet
```

- Si la destination est un dossier existant (ou se termine par `/`), l'élément est collé **dedans** avec son nom d'origine. Sinon la destination est le nouveau chemin complet.
- Un même `:cpy` peut être collé plusieurs fois.
- Rien n'est jamais écrasé : si la destination existe, c'est une erreur.
- Les dossiers sont copiés avec tout leur contenu (mais pas dans eux-mêmes).

### Programmes et système

| Commande | Description |
|---|---|
| `:cmd commande` | Exécute une commande Linux dans le terminal |
| `:cmd commande ; variable` | Exécute la commande et met son **résultat** dans une variable **déjà créée** (le retour à la ligne final est retiré) |
| `:# commande` | Comme `:cmd`, mais **en root** (via `sudo`) : une seule ligne, le script continue ensuite normalement |
| `:pau` / `:pau message` | Attend que l'utilisateur appuie sur Entrée |
| `:run programme` | Lance un programme en arrière-plan |
| `:kil programme` | Arrête un programme par son nom (`pkill -x`) |
| `:wai nombre unité` | Pause. Unités : `sec`, `min`, `h`, `j`, `y` |
| `:re` | Redémarre l'ordinateur |
| `:off` | Éteint l'ordinateur |

Exemple de capture :

```
:var add $nom
:cmd whoami ; nom
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

### `:#` : le mode root

`:#` a deux formes.

**1. Seul sur sa ligne : relancer tout le script en root**

```
:sys start
:#
:say Je suis root !
:sys end
```

`:#` fait, dans l'ordre :

1. `cd` vers le dossier où se trouve `systeen.py` (retrouvé automatiquement) ;
2. `sudo python systeen.py <ce script>` ;
3. arrête le script actuel dès que `sudo` démarre.

Il ne reste plus qu'à saisir le mot de passe root.

À savoir :

- Le script **repart depuis la première ligne** en root. Placez donc `:#` **tout en haut**, juste après `:sys start`, sinon les lignes précédentes seront exécutées deux fois.
- Si vous êtes déjà root, `:#` est ignoré (pas de boucle infinie).
- Les variables permanentes (`!`) sont écrites avant le passage en root.

**2. Suivi d'une commande : une seule ligne en root**

```
:# apt update
:# cat /etc/shadow | wc -l ; nombre
```

La commande est exécutée avec `sudo`, **seulement pour cette ligne** : le reste du script continue avec vos droits normaux. Comme `:cmd`, elle accepte `; variable` pour garder le résultat, les `$variables` sont remplacées (`$$` pour un `$` du shell) et les `rm -r` évidents sur `/` ou le dossier personnel sont bloqués quand la protection est active. Si vous êtes déjà root, la commande est simplement exécutée.

### Mise à jour depuis un script

| Commande | Description |
|---|---|
| `:v` | Vérifie et installe la dernière version |
| `:v 0.6.0` | Installe une version précise |

---

## Variables

| Commande | Description |
|---|---|
| `:var add $nom` | Crée une variable (valeur initiale : `X`) |
| `:var add !nom` | Crée une variable **permanente** : elle est sauvegardée et retrouvée au prochain lancement |
| `:var nom = valeur` | Modifie une variable existante |
| `:var rm nom` | Supprime une variable (et sa sauvegarde si elle était permanente) |
| `:var sys` | Crée les variables système (voir plus bas) |

Pour **créer** une variable, on écrit le symbole directement devant le nom : `$` pour une variable normale, `!` pour une variable permanente. Les crochets des syntaxes de ce document (`[nom]`, `[variable]`) indiquent seulement où mettre une valeur : ils ne s'écrivent pas.

Ensuite, on utilise la variable avec `$`, dans les deux cas : `:say Bonjour $nom`.
Un nom de variable peut contenir lettres, chiffres, `_` et `.`, et peut **commencer par un chiffre** (`:var add $1` puis `$1` ou `${1}`). `:var add` refuse tout autre nom (crochets, `$`, `-`, espaces…), car on ne pourrait jamais l'écrire ensuite avec `$nom`.
Comme le point fait partie du nom, `$nom.txt` cherche la variable `nom.txt` : écrivez **`${nom}.txt`** pour délimiter le nom.
Utiliser une variable qui n'existe pas affiche une erreur `Variable-404`.

### Variables permanentes (`!`)

```
:sys start
:if not exist $visites
 :var add !visites
 :var visites = 0
:eif
:cal $visites + 1 ; visites
:say Lancement numéro $visites
:sys end
```

- Les variables permanentes sont écrites dans le dossier de données de l'utilisateur, `/var/lib/systeen/<utilisateur>/`, dans un fichier `.vars` propre à chaque script (nom du script + empreinte de son chemin). Elles sont rechargées automatiquement.
- La valeur est enregistrée à la fin du script (`:sys end`, `Ctrl + C` ou fin normale) et aussi à la création.
- `:var add !nom` sur une variable permanente **déjà rechargée** ne fait rien (pas d'erreur « existe déjà »). Pour savoir si elle vient d'être créée, testez avant avec `:if not exist $nom`, comme ci-dessus.
- Il n'y a plus de commande `:save` : c'est le `!` à la création qui rend une variable permanente.
- `:var rm nom` supprime aussi la sauvegarde. Les fichiers `.vars` sont supprimés par `--uninstall`.

> Dans un `:if`, `exist $nom` teste **la variable**, pas un chemin qu'elle contiendrait.

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

- Une variable contient du texte. `:var nom = 3` stocke `3`, et `:say? ...` stocke ce que la personne tape.
- `:cal` stocke un nombre (`7 / 2` donne `3.5`).
- Dans une condition, si les deux côtés sont des nombres ils sont comparés comme des nombres, sinon comme du texte. Comparer un nombre et un texte avec `<` ou `>` donne l'erreur « Impossible de comparer ces valeurs ».

### Où le `$` est remplacé

SysTeen remplace `$nom` (ou `${nom}`) dans : `:say`, la question de `:say?` / `:yn?` / `:yN?`, `:cal`, `:cmd`, `:#` (avec commande), `:run`, `:kil`, `:go`, `:cd`, `:add`, `:txt` (nom et texte), `:get`, `:cpy`, `:pst`, `:pau`, `:del`, `:del!`, `:rmf`, la valeur de `:var nom = valeur` et les conditions de `:if` / `:if+`.

Il n'est **pas** remplacé dans `:wai`, `:v`, ni pour les noms de variables eux-mêmes (`:var add $nom`, la variable après un `;`).

> **Attention avec `:cmd` et `:#` :** SysTeen remplace les `$nom` **avant** d'envoyer la commande au shell. Une variable du shell comme `$HOME` provoque donc une erreur `Variable-404`. Doublez le `$` pour que le shell la reçoive : `:cmd echo $$HOME`. (`~` fonctionne aussi pour le dossier personnel.)

### Écrire un `$` littéral : `$$`

`$$` donne un `$` simple, sans remplacement :

```
:say Ça coûte $$5
:cmd echo $$HOME
```

Sans le doublement, `$5` est lu comme la variable `5` et provoque une erreur `Variable-404` si elle n'existe pas.

---

## Abréviations

Une **abréviation** est un raccourci : vous donnez un nom à une suite de commandes, puis vous l'appelez avec `:nom`.

```
:abv bonjour {
 :say Bonjour $nom !
 :say Nous sommes le $sys.date
}

:var sys
:var add $nom
:var nom = Alice
:bonjour
```

- Syntaxe : `:abv nom {` sur la première ligne, les commandes ensuite, puis `}` **seul sur sa ligne**.
- Le nom commence par une lettre et peut contenir lettres, chiffres et `_`. Il ne peut pas être celui d'une commande existante (`:say`, `:if`, `:rep`…).
- Appeler `:nom` exécute les commandes du raccourci, à cet endroit du script. Il n'accepte pas d'argument.
- Le raccourci utilise **les variables du script qui l'appelle** : elles doivent exister à ce moment-là.
- Le corps peut contenir n'importe quelles commandes (`:if`, `:rep`, `:txt` sur plusieurs lignes…), y compris l'appel d'une autre abréviation (10 niveaux maximum). `:sys end` dans une abréviation arrête tout le script.
- Les commandes du corps ne sont **pas** exécutées à l'endroit du `:abv` : la définition ne fait que créer le raccourci.
- Indentez le corps d'un espace, comme pour `:if` (simple conseil, non bloquant).

### Où sont-elles enregistrées ?

Chaque abréviation est écrite dans un fichier `nom.csys` dans `/var/lib/systeen/<utilisateur>/abv/`. Elle est donc **retrouvée à chaque lancement et dans tous vos scripts**, même sans la redéfinir. Si un script redéfinit un `:abv` existant, le fichier est mis à jour.

Pour supprimer une abréviation, effacez son fichier `.csys` (ou faites `--uninstall` pour tout retirer).

---

## Chemins et dossiers de travail

| Commande | Un chemin relatif part de… |
|---|---|
| `:add`, `:txt`, `:get`, `:cpy`, `:pst`, `:del`, `:del!`, `:rmf`, `:cd` | le **dossier courant** (celui d'où vous avez lancé SysTeen, modifié par `:cd`) |
| `:go` et `exist chemin` dans un `:if` | le **dossier du script** |
| fichiers `.vars` et `.csys` | `/var/lib/systeen/<utilisateur>/` |

- `~` est remplacé par votre dossier personnel.
- Un chemin absolu (`/home/user/...`) fonctionne partout.
- `$sys.cwd` donne le dossier courant et `$sys.script` le chemin du script.
- `:cmd`, `:#` (avec commande) et `:run` sont exécutés dans le dossier courant.

---

## Conditions

```
:if $age >= 18
 :say Majeur
:els
 :say Mineur
:eif
```

### Plusieurs cas : `:if+`

`:if+` est le « sinon si » : il se place entre le `:if` et le `:els`, autant de fois que voulu. Les conditions sont testées dans l'ordre et **seule la première branche vraie** est exécutée.

```
:if $note >= 16
 :say Très bien
:if+ $note >= 12
 :say Bien
:if+ $note >= 10
 :say Passable
:els
 :say Insuffisant
:eif
```

- `:if+` s'écrit avec les mêmes conditions que `:if` (`and`, `or`, `exist`, `contains`…).
- Un seul `:eif` ferme l'ensemble.
- `:els` reste facultatif, mais doit être **en dernier** : un `:if+` après un `:els` est une erreur.

### Combiner des conditions : `and` / `or`

```
:if $age >= 18 and $pays == FR
 :say Majeur en France
:eif

:if $a == 1 or exist fichier.txt
 :say a vaut 1, ou le fichier existe
:eif
```

`and` passe avant `or`. Un `and`/`or` n'est reconnu que s'il est suivi d'une vraie condition (`$variable`, `exist`, `empty`, `notempty`) : `:if $texte contains rock and roll` fonctionne donc comme avant.

### Présentation conseillée : 1 espace de plus par niveau

Pour se repérer facilement, décalez d'un espace tout ce qui se trouve dans un `:if`, et encore d'un espace pour chaque `:if` imbriqué. Le `:if+`, le `:els` et le `:eif` se placent au niveau de leur `:if`.

```
:if $a == 1
 :say a vaut 1
 :if $b == 2
  :say et b vaut 2
 :els
  :say mais b ne vaut pas 2
 :eif
:if+ $a == 2
 :say a vaut 2
:els
 :say a ne vaut ni 1 ni 2
:eif
```

Au lancement, SysTeen signale les lignes mal décalées (ou un `:eif` / `:erp` / `}` oublié) avec leur numéro. Ce n'est qu'un **conseil** : le script s'exécute normalement. La même présentation s'applique aux boucles en bloc et aux abréviations.

Chaque `:if` doit se terminer par un `:eif`. Le `:els` est facultatif. Les `:if` peuvent être imbriqués.

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
:rep 3 :say Salut
:rep inf :say Ça tourne...
```

Commandes acceptées dans cette forme : `:say`, `:syr`, `:cmd`, `:cal`, `:wai`, `:run`, `:kil`, `:go`.

### Répéter plusieurs lignes : `:rep N` ... `:erp`

```
:rep 3
 :say Début du tour
 :rep 2
  :say  petit tour
 :erp
:erp
```

- `:rep 5` répète le bloc 5 fois, `:rep inf` à l'infini (sortez avec `:sys end` dans un `:if`, ou `Ctrl + C`).
- `:rep 0` saute le bloc.
- Les boucles peuvent être imbriquées et contenir des `:if` (et inversement).
- Indentez le contenu d'un espace par niveau, comme pour les `:if`.

### Sauter vers une ligne

```
:rep L5-3
```

Retourne à la **ligne 5**, **3 fois** (`:rep L5-inf` pour l'infini).

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
| `Variable-404 : la variable 'x' n'existe pas` | variable non créée avec `:var add $x`, `$sys.…` sans `:var sys`, ou `$HOME` dans un `:cmd` |
| `La variable 'x' existe déjà` | `:var add $x` sur une variable déjà créée (ou `!x` sur une variable normale du même nom) |
| `Syntaxe : :var add $nom ...` | `:var add nom` sans le `$` ou le `!` devant le nom |
| `Nom de variable invalide` | `:var add` avec un nom qui contient autre chose que lettres, chiffres, `_` et `.` |
| `Commande inconnue : :x` | faute de frappe, ou commande qui n'existe pas |
| `La commande :x a été renommée :y` | script écrit pour une version avant la 0.8.3 (voir les notes de version) |
| `:if sans :eif` / `:rep sans :erp` / `:abv sans }` | bloc non fermé |
| `Accès refusé. Utilisez :del! ou :rmf.` | `:del` sans les droits nécessaires |
| `... bloquée par la sécurité SysTeen` | suppression de `/` ou du dossier personnel, la protection étant active |
| `Trop de scripts lancés les uns par les autres` | plus de 5 niveaux de `:go` |
| `Trop d'abréviations appelées les unes par les autres` | plus de 10 niveaux d'abréviations |

Quelques erreurs sont **fatales** et arrêtent SysTeen avant le début (code de sortie `1`) : fichier introuvable, extension autre que `.st`, première ligne différente de `:sys start`.

`Ctrl + C` arrête un script (code `130`). Les erreurs d'une ligne ne changent pas le code de sortie.

---

## Vérifier un script

La commande est `--check` :

```bash
systeen --check mon_script.st
```

SysTeen analyse le script **sans rien exécuter** et signale :

- les commandes inconnues, les anciens noms de commandes et les arguments manquants ;
- les `:if` / `:rep` / `:abv` mal fermés (`:eif`, `:erp` ou `}` oublié ou en trop, `:if+` / `:els` sans `:if`) ;
- les variables utilisées avant d'être créées (`:var add`), et `$sys.…` sans `:var sys` ;
- les fichiers de `:go` introuvables ;
- une syntaxe invalide pour `:wai`, `:rep`, `:say?`, `:get`, `:abv`… ;
- en simple conseil : l'indentation, et l'absence de `:sys end` (le script recommence alors depuis la première ligne quand il arrive à la fin).

Le code de retour est `1` s'il y a des erreurs, `0` sinon. L'analyse est statique : elle suit l'ordre des lignes, sans exécuter les `:if` ni les boucles, donc une variable créée dans une branche est considérée comme créée. Les abréviations déjà enregistrées et celles définies plus haut dans le script sont reconnues comme des commandes.

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
| `/var/lib/systeen/` | Dossier commun (droits `1777`), créé une fois avec `sudo` au premier lancement |
| `/var/lib/systeen/<utilisateur>/` | Dossier privé de l'utilisateur (droits `700`) : tout ce qui suit |
| `…/config.json` | Choix de la protection de `/` et du dossier personnel (droits `600`) |
| `…/nomscript-xxxxxxxx.vars` | Variables permanentes (`!`) d'un script (`xxxxxxxx` : empreinte du chemin du script) |
| `…/abv/nom.csys` | Une abréviation (`:abv nom { … }`) |
| `.systeen.py.update.new`, `.README.md.update.new` | Fichiers temporaires pendant une mise à jour |
| `/tmp/systeen-update-*` | Dossiers temporaires de mise à jour |

Sous `sudo` (commande `:#`), SysTeen utilise toujours le dossier du **vrai** utilisateur (`SUDO_USER`), pas celui de root, et lui rend la propriété des fichiers qu'il écrit.

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
- votre dossier `/var/lib/systeen/<utilisateur>/` : configuration, fichiers `.vars` et abréviations `.csys` ;
- `/var/lib/systeen/` lui-même, **seulement s'il est vide** (les données des autres utilisateurs ne sont pas touchées) ;
- les fichiers de cache et de mise à jour temporaires.

Vos scripts `.st` ne sont **jamais** touchés. La clé PGP n'existe que dans le code de `systeen.py` : elle disparaît avec lui.

---

## Dépannage

| Problème | Solution |
|---|---|
| `systeen: command not found` | Lancez `python systeen.py --install`. Si vous avez déplacé `systeen.py`, relancez-le aussi. Vérifiez que `/usr/local/bin` est dans votre `PATH` |
| Le script ne s'arrête jamais | Terminez-le par `:sys end` (sinon il recommence à la ligne 1), ou faites `Ctrl + C` |
| `La variable 'x' existe déjà` | Le script a recommencé : testez avec `:if not exist $x` avant `:var add $x` (les variables permanentes `!x` n'ont pas ce problème) |
| `Syntaxe : :var add $nom` | Il faut écrire `$` (normale) ou `!` (permanente) devant le nom : `:var add $nom` |
| `La commande :x a été renommée :y` | Le script date d'avant la 0.8.3 : remplacez l'ancien nom (voir les [notes de version](#notes-de-version)) |
| Mot de passe `sudo` demandé au premier lancement | Normal : SysTeen crée `/var/lib/systeen` (une seule fois) |
| `Variable-404` dans un `:cmd` | Écrivez `$$HOME` (dollar doublé) pour les variables du shell, ou `~` pour le dossier personnel |
| `$1` ou `${1}` ne donne pas la valeur | La variable doit exister : `:var add $1` puis `:var 1 = valeur`. Écrivez `$1`, pas `$[1]` |
| `:nom` (abréviation) donne `Variable-404` | Elle utilise les variables du script qui l'appelle : créez-les avant de l'appeler |
| `:go` n'ouvre pas de fenêtre | Il faut une session graphique et l'un des terminaux listés dans [`:go`](#go--lancer-un-second-script-dans-une-nouvelle-fenêtre). Installez par exemple `xterm` |
| `:#` rejoue des lignes déjà exécutées | Le script repart de la ligne 1 en root : placez `:#` juste après `:sys start` (pour une seule commande, utilisez `:# commande`) |
| `:del` répond « Accès refusé » | Utilisez `:del!` (ou `:rmf`) |
| `GPG est requis` pendant `--maj` | Installez `gpg` |
| Signature PGP invalide pendant `--maj` | La release GitHub est mal signée ou a été modifiée : rien n'est installé |
| Conseils d'indentation au lancement | Ils ne bloquent rien : décalez les lignes d'un espace par niveau pour les faire disparaître |
| Un script se comporte mal | Lancez `systeen --check script.st` avant de le lancer |

---

## Notes de version

### 0.8.3

**Commandes renommées sur 3 lettres.** Les anciens noms ne fonctionnent plus : SysTeen répond « La commande :x a été renommée :y » (et `--check` aussi).

| Avant | Maintenant |
|---|---|
| `:systeen start` / `:systeen end` | `:sys start` / `:sys end` |
| `:sayr` | `:syr` |
| `:sayn?` / `:sayN?` | `:yn?` / `:yN?` |
| `:math` | `:cal` |
| `:stop` | `:kil` |
| `:edit` | `:txt` |
| `:read` | `:get` |
| `:copy` / `:paste` | `:cpy` / `:pst` |
| `:pause` | `:pau` |
| `:wait` | `:wai` |
| `:else` / `:elsend` | `:els` / `:eif` |
| `:loop` / `:loopend` | `:rep` / `:erp` |

Les commandes qui avaient déjà 3 lettres ou moins (`:say`, `:say?`, `:var`, `:cmd`, `:run`, `:go`, `:cd`, `:del`, `:del!`, `:rmf`, `:add`, `:re`, `:off`, `:if`, `:v`, `:#`) ne changent pas.

**Nouveautés**

- **`:abv nom {` ... `}`** : crée une abréviation (un raccourci), enregistrée dans un fichier `.csys` et utilisable dans tous les scripts avec `:nom`.
- **`:if+`** : « sinon si », avec autant de `:if+` que voulu entre `:if` et `:els`.
- **`:# commande`** : exécute une seule ligne de commande Linux en root (`:#` seul relance toujours le script en root).
- **Variables** : plus de `:save`. `:var add $nom` crée une variable normale, `:var add !nom` une variable **permanente**.
- **Données dans `/var/lib/systeen/<utilisateur>/`** au lieu de `~/.config/systeen/` et du dossier du script : configuration, fichiers `.vars` et abréviations `.csys`. Le dossier est créé une seule fois avec `sudo`. Plus de registre des `.vars` : `--uninstall` supprime simplement ce dossier.

**Migration depuis la 0.8.2**

- Remplacez les anciens noms de commandes dans vos scripts (tableau ci-dessus) et écrivez `:var add $nom` à la place de `:var add nom`. Lancez `systeen --check script.st` pour trouver ce qui reste.
- Les variables sauvegardées avec `:save` (fichiers `monscript.st.vars` à côté de vos scripts) ne sont pas reprises : recréez-les avec `:var add !nom`. Vous pouvez supprimer ces anciens fichiers et l'ancien dossier `~/.config/systeen/`.
- Le choix de la sécurité est redemandé une fois (`--change` pour le modifier).

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
