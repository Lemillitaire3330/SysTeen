SysTeen v0.6.0 :
# SysTeen

**SysTeen** est un interpréteur de scripts conçu pour Linux, développé par SLNE Studio. Il permet d'automatiser des tâches, de manipuler des fichiers, de gérer des variables, d'effectuer des calculs et d'exécuter des commandes système à l'aide d'un langage simple.

- **Version :** 0.6.0
- **Langage d'implémentation :** Python 3
- **Plateforme principale :** Linux
- **Licence :** GNU General Public License v3.0 (GPL-3.0)
- **Dépôt :** [Lemillitaire3330/SysTeen](https://github.com/Lemillitaire3330/SysTeen)

---

## Sommaire

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Syntaxe du langage](#syntaxe-du-langage)
- [Variables](#variables)
- [Affichage et saisie](#affichage-et-saisie)
- [Calculs mathématiques](#calculs-mathématiques)
- [Conditions](#conditions)
- [Boucles](#boucles)
- [Gestion des fichiers](#gestion-des-fichiers)
- [Commandes système](#commandes-système)
- [Variables système](#variables-système)
- [Mise à jour](#mise-à-jour)
- [Sécurité](#sécurité)
- [Gestion des erreurs](#gestion-des-erreurs)
- [Licence](#licence)
- [Auteur](#auteur)

## Présentation

SysTeen est un projet qui vise à rendre l'automatisation sous Linux accessible grâce à un langage de script dédié.

Les scripts SysTeen utilisent l'extension `.st` et reposent sur des commandes commençant par `:`.

Chaque script doit commencer par la ligne suivante :

```text
:systeen start
```

Un script se termine normalement avec :

```text
:systeen end
```

SysTeen lit et exécute les commandes du fichier dans l'ordre, tout en permettant l'utilisation de variables, de conditions, de boucles et d'opérations sur le système.

## Fonctionnalités

- Création, modification et suppression de fichiers et de dossiers.
- Gestion de variables et sauvegarde persistante de certaines valeurs.
- Affichage de texte et saisie interactive de l'utilisateur.
- Calculs mathématiques avec un ensemble limité d'opérateurs.
- Conditions avec comparaisons numériques et textuelles.
- Boucles répétitives et boucles par retour à une ligne.
- Exécution de commandes Linux.
- Lancement et arrêt de processus.
- Navigation entre les dossiers.
- Temporisation de scripts.
- Consultation d'informations sur le système.
- Protection configurable contre la suppression de `/` et du dossier personnel.
- Mise à jour du programme et du README avec vérification de signatures PGP.

## Prérequis

Avant d'utiliser SysTeen, assurez-vous de disposer des éléments suivants :

- Linux.
- Python 3.
- GPG (`gpg`) pour les mises à jour vérifiées.
- `sudo` si vous utilisez les commandes de suppression nécessitant des privilèges élevés.

La plupart des fonctionnalités standard utilisent uniquement les bibliothèques intégrées à Python.

## Installation

### 1. Récupérer le projet

Clonez le dépôt GitHub :

```bash
git clone https://github.com/Lemillitaire3330/SysTeen.git
```

Accédez ensuite au dossier :

```bash
cd SysTeen
```

### 2. Vérifier Python

```bash
python3 --version
```

### 3. Afficher l'aide

Depuis le dossier contenant `systeen.py`, exécutez :

```bash
python3 systeen.py --help
```

Pour connaître la version installée :

```bash
python3 systeen.py --version
```

## Utilisation

SysTeen accepte plusieurs modes d'exécution.

| Commande | Description |
|---|---|
| `python3 systeen.py fichier.st` | Exécute un script SysTeen |
| `python3 systeen.py --help` | Affiche l'aide |
| `python3 systeen.py --version` | Affiche la version installée |
| `python3 systeen.py --maj` | Recherche et installe la dernière version |
| `python3 systeen.py --maj 0.4.2` | Demande l'installation d'une version précise |
| `python3 systeen.py --update` | Alias de `--maj` |
| `python3 systeen.py --readme` | Affiche le README installé |

Le fichier `README.md` doit se trouver à côté de `systeen.py` pour être affiché avec `--readme`.

### Exemple de script

Créez un fichier `bonjour.st` :

```text
:systeen start

:say Bonjour !
:say Bienvenue dans SysTeen.

:systeen end
```

Exécutez-le avec :

```bash
python3 systeen.py bonjour.st
```

Au lancement, SysTeen demande une confirmation avant d'exécuter le script. Lors de la première configuration, il demande également si la protection des chemins système doit être activée.

## Syntaxe du langage

Les commandes SysTeen commencent par `:`.

Les lignes vides et les lignes commençant par `#` sont ignorées.

Exemple :

```text
# Ceci est un commentaire
:systeen start

:say Ceci est une commande.

:systeen end
```

## Variables

Les variables permettent de stocker des valeurs et de les réutiliser dans un script.

### Créer une variable

```text
:var add nom
```

Une nouvelle variable reçoit initialement la valeur `X`.

### Modifier une variable

```text
:var nom = Alice
```

### Utiliser une variable

Le caractère `$` permet d'insérer la valeur d'une variable dans un texte.

```text
:say Bonjour $nom !
```

Résultat :

```text
Bonjour Alice !
```

### Supprimer une variable

```text
:var rm nom
```

### Sauvegarder une variable

```text
:var add compteur
:var compteur = 42
:save compteur
```

Les variables sauvegardées sont conservées dans un fichier `.vars` associé au script. Elles sont rechargées lors d'une prochaine exécution.

## Affichage et saisie

### Afficher du texte

```text
:say Bonjour tout le monde !
```

### Demander une saisie

La commande `:say?` permet de poser une question et de stocker la réponse dans une variable existante.

```text
:var add prenom
:say? Quel est votre prénom ? ; prenom
:say Bonjour $prenom !
```

La variable doit être créée avant la saisie.

## Calculs mathématiques

La commande `:math` permet d'évaluer une expression mathématique.

### Afficher un résultat

```text
:math 5 + 3
```

Résultat :

```text
8
```

### Stocker un résultat

```text
:var add resultat
:math 10 * 5 ; resultat
:say Résultat : $resultat
```

Les opérateurs pris en charge sont :

| Opérateur | Signification |
|---|---|
| `+` | Addition |
| `-` | Soustraction |
| `*` | Multiplication |
| `/` | Division |
| `//` | Division entière |
| `%` | Modulo |
| `**` | Puissance |

Les parenthèses peuvent être utilisées pour organiser les expressions.

```text
:math (2 + 3) * 4
```

Les expressions sont évaluées à l'aide d'un analyseur limité aux constantes numériques et aux opérateurs autorisés, et non par l'exécution directe de code Python arbitraire.

## Conditions

Les conditions permettent d'exécuter différentes parties d'un script en fonction d'une valeur.

### Comparaison de valeurs

```text
:systeen start

:var add age
:var age = 18

:if $age >= 18
:say Vous êtes majeur.
:else
:say Vous êtes mineur.
:elsend

:systeen end
```

### Opérateurs de comparaison

- `==` : égalité.
- `!=` : différence.
- `>` : supérieur à.
- `<` : inférieur à.
- `>=` : supérieur ou égal.
- `<=` : inférieur ou égal.

### Conditions textuelles

SysTeen prend également en charge les opérateurs suivants :

- `contains` : vérifie si un texte contient une chaîne.
- `not contains` : vérifie si un texte ne contient pas une chaîne.
- `startswith` : vérifie le début d'une chaîne.
- `endswith` : vérifie la fin d'une chaîne.

Exemple :

```text
:var add message
:var message = Bonjour SysTeen

:if $message contains SysTeen
:say Le nom SysTeen est présent.
:elsend
```

### Vérifier une variable ou un fichier

```text
:if exist $nom
:say La variable existe.
:elsend
```

Pour tester l'existence d'un fichier ou d'un dossier :

```text
:if exist document.txt
:say Le fichier existe.
:elsend
```

Autres conditions disponibles :

- `not exist` : vérifie l'absence d'une variable ou d'un chemin.
- `empty` : vérifie si une variable est vide.
- `notempty` : vérifie si une variable n'est pas vide.

## Boucles

SysTeen propose deux formes de boucles.

### Répéter une commande

```text
:loop 3 say Bonjour !
```

Cette commande affiche `Bonjour !` trois fois.

### Boucle infinie

```text
:loop inf say Le programme tourne.
```

Une boucle infinie se poursuit tant que le programme est en cours d'exécution. Utilisez `Ctrl+C` pour interrompre le programme.

### Boucle par numéro de ligne

```text
:systeen start
:say Répétition
:loop L2-3
:systeen end
```

La syntaxe `L2-3` demande de revenir à la ligne 2 selon le compteur de répétitions de la boucle.

La forme `L2-inf` permet un retour répété sans limite définie.

**Attention :** les boucles infinies peuvent monopoliser le processeur si elles ne comportent aucune temporisation.

## Gestion des fichiers

### Créer un fichier

```text
:crea notes.txt
```

### Créer un dossier

```text
:crea documents
```

### Écrire dans un fichier

```text
:edit notes.txt "Mon texte"
```

La commande `:edit` crée le fichier ou remplace son contenu par le texte indiqué. Elle accepte également du texte réparti sur plusieurs lignes jusqu'au guillemet fermant.

### Supprimer un fichier ou un dossier

```text
:del notes.txt
```

La commande `:del` supprime un fichier ou un dossier. Pour un dossier, son contenu est également supprimé.

Les commandes suivantes sont également disponibles :

- `:del!` : réessaie avec `sudo` en cas de refus d'accès.
- `:rmf` : utilise directement `sudo rm -rf`.

**Attention :** ces commandes peuvent entraîner une perte définitive de données. Vérifiez toujours le chemin avant de les utiliser.

Les protections intégrées bloquent par défaut les suppressions directes de `/` et du dossier personnel lorsque la sécurité est activée. Elles ne constituent toutefois pas une garantie contre toutes les suppressions dangereuses.

## Commandes système

SysTeen permet d'interagir avec le système Linux.

| Commande | Description |
|---|---|
| `:cmd` | Exécute une commande dans un shell |
| `:run` | Lance un programme |
| `:stop` | Demande l'arrêt d'un processus par son nom |
| `:cd` | Change le dossier de travail |
| `:wait` | Met le script en pause |
| `:re` | Demande le redémarrage du système |
| `:off` | Demande l'arrêt du système |

### Exemples

Afficher le contenu d'un dossier :

```text
:cmd ls -la
```

Lancer un programme :

```text
:run firefox
```

Arrêter un processus :

```text
:stop firefox
```

Changer de dossier :

```text
:cd /tmp
```

Attendre cinq secondes :

```text
:wait 5 sec
```

Les unités acceptées par `:wait` sont `sec`, `min`, `h`, `j` et `y`.

**Important :** `:cmd` exécute une commande avec `shell=True`. Les scripts SysTeen doivent donc être considérés comme du code potentiellement dangereux, particulièrement lorsqu'ils proviennent d'une source inconnue.

## Variables système

La commande suivante charge des informations système dans des variables :

```text
:var sys
```

Variables disponibles :

| Variable | Description |
|---|---|
| `$sys.ram` | Mémoire vive totale |
| `$sys.user` | Nom de l'utilisateur |
| `$sys.stockage` | Espace disque libre du dossier du programme |
| `$sys.os` | Nom de la distribution Linux |
| `$sys.perms` | Permissions du fichier Python |
| `$sys.battery` | Niveau de batterie, si disponible |
| `$sys.hostname` | Nom de la machine |
| `$sys.kernel` | Version du noyau |
| `$sys.arch` | Architecture du processeur |
| `$sys.cpu` | Informations sur le processeur |
| `$sys.cores` | Nombre de processeurs logiques détectés |
| `$sys.cwd` | Dossier de travail courant |
| `$sys.script` | Chemin du script `.st` |
| `$sys.home` | Dossier personnel |
| `$sys.python` | Version de Python |
| `$sys.shell` | Shell indiqué par l'environnement |
| `$sys.uptime` | Temps de fonctionnement du système |

Exemple :

```text
:systeen start

:var sys
:say Système : $sys.os
:say Noyau : $sys.kernel
:say Python : $sys.python
:say RAM : $sys.ram

:systeen end
```

Certaines informations peuvent être indisponibles selon l'environnement d'exécution.

## Mise à jour

SysTeen intègre un mécanisme de mise à jour depuis les releases GitHub.

### Mettre à jour vers la dernière version

```bash
python3 systeen.py --maj
```

### Installer une version précise

```bash
python3 systeen.py --maj 0.4.2
```

Cette commande permet notamment de revenir à une version antérieure, si la release demandée existe.

### Vérification cryptographique

Le mécanisme de mise à jour :

1. Récupère les fichiers de la release GitHub.
2. Télécharge les signatures détachées PGP.
3. Vérifie les signatures avec la clé publique intégrée.
4. Contrôle l'empreinte de la clé.
5. Vérifie la syntaxe Python et la version annoncée.
6. Vérifie le contenu minimal du README.
7. Prépare puis installe les fichiers validés.

Les fichiers `systeen.py` et `README.md` doivent être accompagnés de leurs signatures respectives :

- `systeen.py.asc`
- `README.md.asc`

La clé publique et l'empreinte doivent correspondre à celles du mainteneur attendu. Pour une sécurité optimale, vérifiez cette empreinte par un canal indépendant avant de faire confiance au mécanisme de mise à jour.

Une signature valide prouve que le fichier correspond à une signature créée par la clé correspondante ; elle ne garantit pas à elle seule que le code est exempt de vulnérabilités.

## Sécurité

SysTeen intègre plusieurs mécanismes de précaution :

- Confirmation avant le lancement d'un script.
- Protection configurable contre la suppression de `/` et du dossier personnel.
- Configuration de sécurité enregistrée dans `~/.config/systeen/config.json`.
- Permissions restreintes sur le dossier et le fichier de configuration lorsque le système le permet.
- Vérification PGP des fichiers téléchargés lors des mises à jour.

### Bonnes pratiques

- Lisez les scripts `.st` avant de les exécuter.
- N'exécutez pas de script inconnu avec des privilèges élevés.
- Soyez particulièrement prudent avec `:cmd`, `:del!`, `:rmf`, `:re` et `:off`.
- Conservez des sauvegardes de vos données importantes.
- Ne désactivez la protection contre les suppressions dangereuses que si vous comprenez les risques.

La protection des chemins ne remplace pas les permissions Linux, les sauvegardes ou les autres mesures de sécurité du système.

## Gestion des erreurs

Lorsqu'une commande rencontre un problème, SysTeen affiche généralement un message préfixé par `[SysTeen] Erreur`.

Exemples de problèmes possibles :

- Fichier `.st` absent ou invalide.
- Variable inexistante.
- Expression mathématique non autorisée.
- Syntaxe de condition incorrecte.
- Commande inconnue.
- Refus d'accès à un fichier.
- Échec d'une mise à jour ou d'une vérification de signature.

Vérifiez la syntaxe de la commande concernée et assurez-vous que les variables et les fichiers nécessaires existent.

## Licence

SysTeen est distribué sous la licence **GNU General Public License v3.0 (GPL-3.0)**.

Vous pouvez utiliser, étudier, modifier et redistribuer ce logiciel conformément aux conditions de la GPL v3.

Toute redistribution du logiciel, sous forme originale ou modifiée, doit respecter les obligations de la licence, notamment la conservation des mentions de droits d'auteur et de licence applicables ainsi que la fourniture du code source correspondant dans les conditions prévues par la GPL.

Le texte intégral de la licence est disponible ici :

https://www.gnu.org/licenses/gpl-3.0.html

Pour distribuer le projet, il est recommandé d'inclure le texte officiel de la licence dans un fichier `LICENSE` à la racine du dépôt.

## Auteur

**SLNE Studio**

Dépôt officiel : https://github.com/Lemillitaire3330/SysTeen

Merci d'utiliser SysTeen !

---

*SysTeen est un projet en évolution. Les fonctionnalités et la syntaxe décrites dans ce document correspondent à l'implémentation présentée dans le code source de la version 0.6.0.*
