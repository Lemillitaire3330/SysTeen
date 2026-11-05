#!/usr/bin/env python3

import ast
import getpass
import json
import operator
import os
import platform
import pwd
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


VERSION = "0.8.1"

# Phrase à taper pour confirmer la désinstallation
UNINSTALL_PHRASE = (
    "iwanttouninstallnowthesysteenexecutable"
    "thesysteenpackageandthesysteenproject"
)

# Profondeur maximale de scripts lancés les uns par les autres avec :go
MAX_GO_DEPTH = 5

# Emplacement de la commande `systeen` (lien vers systeen.py)
BIN_LINK_PATH = Path("/usr/local/bin/systeen")

# Nombre maximal de conseils d'indentation affichés au lancement
MAX_INDENT_WARNINGS = 10

# Taille maximale d'un fichier lu par :read (10 Mo)
MAX_READ_BYTES = 10 * 1024 * 1024

# Commandes connues (utilisé par --check)
KNOWN_COMMANDS = {
    "systeen", "#", "v", "var", "save", "say", "say?", "sayn?", "sayN?",
    "math", "cmd", "run", "stop", "go", "cd", "del", "del!", "rmf",
    "add", "edit", "read", "copy", "paste", "pause", "wait", "re",
    "off", "if", "else", "elsend", "loop", "loopend",
}

# Commandes qui exigent au moins un argument (utilisé par --check)
COMMANDS_WITH_ARGUMENT = {
    "systeen", "var", "save", "say?", "sayn?", "sayN?", "math", "cmd",
    "run", "stop", "go", "cd", "del", "del!", "rmf", "add", "edit",
    "read", "copy", "paste", "wait", "if", "loop",
}

# Commandes internes du shell : `:cmd echo a ; echo b` reste du shell
SHELL_BUILTINS = {
    "cd", "echo", "exit", "true", "false", "pwd", "export", "unset",
    "read", "wait", "set", "source", "type", "test", "exec", "eval",
    "alias", "umask", "ulimit", "trap", "kill", "jobs", "fg", "bg",
    "history", "let", "printf", "return", "shift",
}

# Terminaux graphiques pris en charge par :go, dans l'ordre d'essai.
# Chaque entrée construit les arguments qui suivent le nom du terminal
# pour exécuter la commande `c` (une liste d'arguments).
TERMINAL_STYLES = {
    "xdg-terminal-exec": lambda c: list(c),
    "gnome-terminal": lambda c: ["--"] + list(c),
    "konsole": lambda c: ["-e"] + list(c),
    "xfce4-terminal": lambda c: ["-x"] + list(c),
    "mate-terminal": lambda c: ["-x"] + list(c),
    "lxterminal": lambda c: ["-e"] + list(c),
    "qterminal": lambda c: ["-e", shlex.join(c)],
    "tilix": lambda c: ["-e", shlex.join(c)],
    "terminator": lambda c: ["-x"] + list(c),
    "alacritty": lambda c: ["-e"] + list(c),
    "kitty": lambda c: list(c),
    "wezterm": lambda c: ["start", "--"] + list(c),
    "foot": lambda c: list(c),
    "xterm": lambda c: ["-e"] + list(c),
    "x-terminal-emulator": lambda c: ["-e"] + list(c),
}

# =============================================================
# MISE A JOUR SECURISEE
# =============================================================

GITHUB_REPOSITORY = "Lemillitaire3330/SysTeen"

PGP_PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGrFZBIBEADGhG0k/vykqsCnXokJn0TmEMI99xBUzJK1n+r2mG2pNOcPn0LS
/YmO86HlXPnDz16dbKwWK4SiRc93uO4Lw5fuRIF7jpG/I8dO6/DVD9x2EgAevnTH
90/4cDK27uz5e60he+LFyTNfBxeWqiORlepp3Imivtv+h8utde6f3r8SRdqVYo4q
QNw14hlpyY1nHq7SUqoudYwrF8eyMSSs4OvFIknhETUSk0vm0x+YHNAd2cMP86pb
g7ixxZagFJd15ZlbHybNDLvYH4+uN80lHOb9w73qr+aQzukApZjayp2SolA7/VC5
2buXvjG+bRRWeUcr5LWSKS3f+qfDAafB2a7aR3vbSrJ4B7VE+6rySdwY/XdY20+1
PMzYH0tH7wDbPJ/XdhtWbuBQIY8mclJUEWXLYt54UQtfGjgEXUG1bNk+80f/+5Lu
oSv7zH/c57Y6+mH2S5boxjrCamq2eI+lI6+Sw7WAQwFDl9x32lOTuIzTQsV4PbsE
KvjrlgjEQlslpnwGYMYK7r4T5K2o9RIdrZr+C+ewTpTKnSDFPqwr/Z94y9HifITM
lc4Wkk+Ps/YATB5AwLrUJHtiKVl3MSUW856JRihMbn81Oj4LPTM9zhwaejWBwh4x
eQhPx+9JAcxHvADHgPmDZIV0tatuYiSzeY39TF0WOao+RknHQ/TI1JuIQQARAQAB
tNNTTE5FIFN0dWRpbyAoU0xORSBTdHVkaW8gZXN0IHVuIHN0dWRpbyBkZSBwcm9n
cmFtbWF0aW9uIGZyYW7Dp2Fpcy4gU0xORSBTdHVkaW8gaXMgYSBmcmVuY2ggcHJv
Z3JhbW1hdGlvbiBzdHVkaW8uIE1lcmNpIGQndXRpbGlzZXIgbGVzIHNlcnZpY2Vz
IFNMTkUuIFRoYW5rcyB5b3UgdG9vIHVzZSBTTE5FJ3Mgc2VydmljZXMuKSA8c2xu
ZS1vZmZpY2llbEBwcm90b24ubWU+iQJOBBMBCgA4FiEE9/7ha/423q41B57/D91J
2wesJT4FAmrFZBICGwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQD91J2wes
JT5Gxg/9E0V2PempVLXo5VU4UWY1SzA+ZWCelt23AguiRux4j7zLLdn1bm7pM0yf
liJIKxW0fW2+EKS8KtmqQWWzjeqoIvgZDjV92gDSSmY5IuK5ZMMbT/SqJl+QdaAk
v3eteUO8/ApjTOlPZs5Kypbkn81reGtv4CKHiCQnPbqUzyABC9bTpRnjwBpcKkdu
17fQS7UramFfyjwbahj3n9YLbd0MwRcDhOj08wTB8lhfZ7rPi0HRHYKwnIP5ZhZp
WrPGVBcaXXucd12gzli76/dhX6kNiHeayekEXu55UsEZ/2pNlpscBHHpwGqmNZuU
4LAKGTr8iq0BqK0SBb4j+N9s8cCaFM5KaJpssX0b0LivdQC5KCWp48aHzKC8i2He
IXbdgk2gzq45rtoVO0HEqiSQahbSEWG+PG92AAu/Hkp2/GXYeLPonJFAJ6oLJ1uj
raIcngg3X/6Ia3v7aiho8JxJUP6Ei/d5Bv3dCSnnMMpzDVfNmOl/0vg0vwIyseA8
gjMn+aTfdP8J0dPA8Mftl0JxPZWg/lhZMPfy3CdiDq1q7CmtDSeo29Vvsi9AOGdr
RmallIIkPIO1DMgLjTZVengwwbYtSTDIREXdlxolqSVH4BMjetv2sTZ4JrgrMQbo
XSHex0FXF4QhV+fLcRlwexfxWdRG9n8ysogTzCfUqtPfSddbDaI=
=0o1w
-----END PGP PUBLIC KEY BLOCK-----

"""

PGP_FINGERPRINT = "F7FEE16BFE36DEAE35079EFF0FDD49DB07AC253E"

UPDATE_SCRIPT_ASSET = "systeen.py"
UPDATE_SIGNATURE_ASSET = "systeen.py.asc"

# README.md : téléchargé et vérifié avec la même clé que systeen.py
UPDATE_README_ASSET = "README.md"
UPDATE_README_SIGNATURE_ASSET = "README.md.asc"


class SysTeenError(Exception):
    pass


def get_real_home():
    """
    Retourne le dossier personnel de l'utilisateur réel.

    Quand SysTeen est relancé via sudo (commande :#), Path.home()
    peut valoir /root. On retrouve alors le vrai utilisateur grâce
    à SUDO_USER, pour garder la même configuration de sécurité.
    """

    try:
        if os.geteuid() == 0:
            sudo_user = os.environ.get("SUDO_USER")

            if sudo_user and sudo_user != "root":
                return Path(pwd.getpwnam(sudo_user).pw_dir)

    except Exception:
        pass

    return Path.home()


class SafeMath:
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def evaluate(cls, expression):
        tree = ast.parse(expression, mode="eval")
        return cls._eval(tree.body)

    @classmethod
    def _eval(cls, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise SysTeenError("Valeur mathématique invalide.")

        if isinstance(node, ast.BinOp):
            op = cls.OPERATORS.get(type(node.op))

            if op is None:
                raise SysTeenError("Opérateur mathématique non autorisé.")

            return op(cls._eval(node.left), cls._eval(node.right))

        if isinstance(node, ast.UnaryOp):
            op = cls.OPERATORS.get(type(node.op))

            if op is None:
                raise SysTeenError("Opérateur mathématique non autorisé.")

            return op(cls._eval(node.operand))

        raise SysTeenError("Expression mathématique invalide.")


class SysTeen:
    # $nom, ${nom} (le nom peut commencer par un chiffre : $1, ${1})
    # et $$ qui donne un $ littéral
    VARIABLE_REFERENCE = re.compile(
        r"\$\$"
        r"|\$\{([A-Za-z0-9_][A-Za-z0-9_.]*)\}"
        r"|\$([A-Za-z0-9_][A-Za-z0-9_.]*)"
    )

    # "and" / "or" entre deux conditions (seulement si ce qui suit
    # ressemble à une condition : $var, exist, empty, notempty...)
    CONDITION_SPLIT = re.compile(
        r"\s+(and|or)\s+"
        r"(?=\$|exist\s|not\s+exist\s|empty\s|notempty\s)"
    )

    # ":cmd commande ; variable"
    CMD_CAPTURE = re.compile(
        r"^(.*\S)\s*;\s*([A-Za-z0-9_][A-Za-z0-9_.]*)\s*$",
        re.DOTALL
    )

    # =========================================================
    # INITIALISATION
    # =========================================================

    def __init__(self, script_path=None):
        # Chemin du programme SysTeen lui-même (cible des mises à jour)
        # Retrouvé automatiquement à partir de ce fichier.
        self.program_path = Path(__file__).resolve()

        # Chemin du README.md installé à côté du programme
        self.readme_path = self.program_path.parent / "README.md"

        # Redémarrer SysTeen après une mise à jour réussie
        # (désactivé en mode "python systeen.py --maj")
        self.restart_after_install = True

        # Vrai quand ce script tourne dans la fenêtre ouverte par :go
        # (la fenêtre attend alors une touche avant de se fermer)
        self.window_mode = False

        # Contenu du presse-papiers de :copy / :paste
        self.clipboard = None

        # Boucles en bloc (:loop N ... :loopend) en cours
        self.block_stack = []

        self.update_fingerprint = None

        # Configuration persistante (toujours celle du vrai utilisateur)
        self.config_dir = get_real_home() / ".config" / "systeen"
        self.config_file = self.config_dir / "config.json"
        self.registry_file = self.config_dir / "vars_registry.json"

        if script_path is None:
            # Mode sans script : python systeen.py --maj / --change / ...
            self.script_path = None
            self.lines = []
            self.variables = {}
            self.saved_variables = set()
            self.running = True
            self.finished = False
            self.loop_states = {}
            self.save_file = None
            self.safety_enabled = True
            return

        self.script_path = Path(script_path).resolve()

        if self.script_path.suffix != ".st":
            raise SysTeenError(
                "Le fichier SysTeen doit avoir l'extension .st."
            )

        if not self.script_path.is_file():
            raise SysTeenError("Fichier SysTeen introuvable.")

        self.lines = self.script_path.read_text(
            encoding="utf-8"
        ).splitlines()

        if not self.lines:
            raise SysTeenError("Le fichier SysTeen est vide.")

        if self.lines[0].strip() != ":systeen start":
            raise SysTeenError(
                "La première ligne doit être :systeen start"
            )

        self.variables = {}
        self.saved_variables = set()

        self.running = True
        self.finished = False

        self.loop_states = {}

        self.save_file = Path(str(self.script_path) + ".vars")

        self.safety_enabled = True
        self.update_fingerprint = None

        # Variables sauvegardées
        self.load_saved_variables()

    # =========================================================
    # CONFIGURATION / SECURITE
    # =========================================================

    def ensure_config_directory(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            os.chmod(self.config_dir, 0o700)
        except OSError:
            pass

    def load_security_config(self):
        """
        Charge la préférence de sécurité.

        Si aucune préférence n'existe, la sécurité est
        considérée comme activée par défaut.
        """

        if not self.config_file.exists():
            self.safety_enabled = True
            return False

        try:
            data = json.loads(
                self.config_file.read_text(encoding="utf-8")
            )

            if not isinstance(data, dict):
                self.safety_enabled = True
                return False

            value = data.get("protect_system_paths")

            if isinstance(value, bool):
                self.safety_enabled = value
                return True

        except Exception:
            print(
                "[SysTeen] Attention : impossible de "
                "lire la configuration de sécurité."
            )

        self.safety_enabled = True
        return False

    def save_security_config(self):
        self.ensure_config_directory()

        data = {
            "version": 1,
            "protect_system_paths": self.safety_enabled
        }

        self.config_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        try:
            os.chmod(self.config_file, 0o600)
        except OSError:
            pass

    def ask_security_preference(self):
        print()
        print("[SysTeen] Configuration de sécurité")
        print(
            "[SysTeen] La sécurité empêche :del, :del! "
            "et :rmf de supprimer / et votre dossier personnel."
        )
        print("[SysTeen] Réponse par défaut : OUI.")

        while True:
            answer = input(
                "[SysTeen] Activer cette sécurité ? (Y/n) : "
            ).strip().lower()

            if answer in ("", "y", "yes", "o", "oui"):
                self.safety_enabled = True
                break

            if answer in ("n", "no", "non"):
                self.safety_enabled = False
                break

            print("[SysTeen] Réponse invalide. Répondez Y ou n.")

        self.save_security_config()

        state = "OUI" if self.safety_enabled else "NON"

        print(f"[SysTeen] Sécurité enregistrée : {state}")

    def confirm_script_launch(self):
        """
        Affiche systématiquement un rappel avant l'exécution.
        """

        state = "OUI" if self.safety_enabled else "NON"

        filename = self.script_path.name

        print()
        print(f"[SysTeen] : RAPPEL : Vous avez la sécurité : {state}.")
        print(f"[SysTeen] Vérifiez le code de {filename} avant de le lancer.")
        print(f"[SysTeen] Souhaitez-vous lancer {filename} ? (Y/n)")

        return self.ask_yes_no()

    @staticmethod
    def ask_yes_no():
        while True:
            answer = input("[SysTeen] > ").strip().lower()

            if answer in ("", "y", "yes", "o", "oui"):
                return True

            if answer in ("n", "no", "non"):
                return False

            print("[SysTeen] Réponse invalide. Répondez Y ou n.")

    def is_protected_path(self, path):
        """
        Vérifie si un chemin correspond à / ou au HOME.
        """

        try:
            resolved = path.resolve()
        except Exception:
            resolved = path.absolute()

        root = Path("/").resolve()

        homes = {Path.home().resolve(), get_real_home().resolve()}

        return resolved == root or resolved in homes

    def check_destructive_path(self, path):
        """
        Applique la protection avant une suppression.
        """

        if not self.safety_enabled:
            return

        if self.is_protected_path(path):
            raise SysTeenError(
                "Suppression de / ou du dossier personnel "
                "bloquée par la sécurité SysTeen."
            )

    # =========================================================
    # VARIABLES
    # =========================================================

    def load_saved_variables(self):
        if not self.save_file.exists():
            return

        try:
            data = json.loads(
                self.save_file.read_text(encoding="utf-8")
            )

            if not isinstance(data, dict):
                return

            for name, value in data.items():
                if isinstance(name, str):
                    self.variables[name] = value
                    self.saved_variables.add(name)

        except Exception:
            print(
                "[SysTeen] Erreur : impossible de "
                "charger les variables sauvegardées."
            )

    def read_vars_registry(self):
        """Liste des fichiers .vars connus (pour --uninstall)."""

        try:
            data = json.loads(
                self.registry_file.read_text(encoding="utf-8")
            )

            if isinstance(data, list):
                return [item for item in data if isinstance(item, str)]

        except Exception:
            pass

        return []

    def register_vars_file(self):
        """Mémorise l'emplacement du .vars pour pouvoir le supprimer."""

        try:
            entries = self.read_vars_registry()
            entry = str(self.save_file)

            if entry in entries:
                return

            self.ensure_config_directory()

            entries.append(entry)

            self.registry_file.write_text(
                json.dumps(entries, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

        except OSError:
            pass

    def write_saved_variables(self):
        data = {}

        for name in self.saved_variables:
            if name in self.variables:
                data[name] = self.variables[name]

        if data:
            self.save_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            self.register_vars_file()

        else:
            try:
                self.save_file.unlink()
            except FileNotFoundError:
                pass

    def cleanup_variables(self):
        self.variables.clear()
        self.saved_variables.clear()
        self.loop_states.clear()

    def require_variable(self, name):
        if name not in self.variables:
            raise SysTeenError(
                f"Variable-404 : la variable '{name}' n'existe pas."
            )

        return self.variables[name]

    def create_variable(self, name):
        if not name:
            raise SysTeenError("Nom de variable manquant.")

        # Un nom qu'on ne pourrait jamais écrire avec $nom serait
        # inutilisable : on le refuse tout de suite.
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.]*", name):
            raise SysTeenError(
                f"Nom de variable invalide : '{name}'. Lettres, "
                "chiffres, _ et . uniquement (pas de $, de crochets "
                "ni d'espaces)."
            )

        if name in self.variables:
            raise SysTeenError(f"La variable '{name}' existe déjà.")

        self.variables[name] = "X"

    def set_variable(self, name, value):
        self.require_variable(name)
        self.variables[name] = value

    def remove_variable(self, name):
        self.require_variable(name)

        del self.variables[name]

        self.saved_variables.discard(name)

        self.write_saved_variables()

    def save_variable(self, name):
        self.require_variable(name)

        self.saved_variables.add(name)

        self.write_saved_variables()

    # =========================================================
    # INTERPOLATION
    # =========================================================

    def interpolate(self, text):
        if not isinstance(text, str):
            return text

        pattern = self.VARIABLE_REFERENCE

        def replace_variable(match):
            # $$ -> $ littéral (ex. $$HOME pour le shell)
            if match.group(0) == "$$":
                return "$"

            name = match.group(1) or match.group(2)

            if name not in self.variables:
                raise SysTeenError(
                    f"Variable-404 : la variable '{name}' n'existe pas."
                )

            return str(self.variables[name])

        return pattern.sub(replace_variable, text)

    @staticmethod
    def variable_from_token(text):
        """'$nom' ou '${nom}' -> 'nom' ; sinon None."""

        text = text.strip()

        if text.startswith("${") and text.endswith("}"):
            name = text[2:-1]

        elif text.startswith("$"):
            name = text[1:]

        else:
            return None

        return name or None

    # =========================================================
    # VARIABLES SYSTEME
    # =========================================================

    @staticmethod
    def format_bytes(value):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]

        value = float(value)

        for unit in units:
            if value < 1024:
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} EB"

    def get_os_name(self):
        os_release = Path("/etc/os-release")

        if not os_release.exists():
            return "Linux"

        data = {}

        try:
            for line in os_release.read_text(
                encoding="utf-8"
            ).splitlines():

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)

                data[key] = value.strip('"')

            return data.get("PRETTY_NAME", data.get("NAME", "Linux"))

        except Exception:
            return "Linux"

    def get_ram(self):
        meminfo = Path("/proc/meminfo")

        if not meminfo.exists():
            return "Inconnue"

        values = {}

        try:
            for line in meminfo.read_text().splitlines():

                if ":" not in line:
                    continue

                key, value = line.split(":", 1)

                value = value.strip()

                if value.endswith(" kB"):
                    value = value[:-3]

                values[key] = int(value) * 1024

            return self.format_bytes(values.get("MemTotal", 0))

        except Exception:
            return "Inconnue"

    def get_storage(self):
        try:
            usage = shutil.disk_usage(self.script_path.parent)

            return self.format_bytes(usage.free)

        except Exception:
            return "Inconnue"

    def get_battery(self):
        batteries = list(Path("/sys/class/power_supply").glob("BAT*"))

        if not batteries:
            return "N/A"

        capacity_file = batteries[0] / "capacity"

        if capacity_file.exists():
            try:
                return f"{capacity_file.read_text().strip()}%"
            except Exception:
                pass

        return "Inconnue"

    def get_permissions(self):
        try:
            return stat.filemode(self.script_path.stat().st_mode)
        except Exception:
            return "Inconnues"

    def get_uptime(self):
        uptime_file = Path("/proc/uptime")

        if not uptime_file.exists():
            return "Inconnue"

        try:
            seconds = int(float(uptime_file.read_text().split()[0]))

            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)

            return f"{days}j {hours}h {minutes}min"

        except Exception:
            return "Inconnue"

    def command_var_sys(self):
        variables = {
            "sys.ram": self.get_ram(),
            "sys.user": getpass.getuser(),
            "sys.stockage": self.get_storage(),
            "sys.os": self.get_os_name(),
            "sys.perms": self.get_permissions(),
            "sys.battery": self.get_battery(),
            "sys.hostname": platform.node(),
            "sys.kernel": platform.release(),
            "sys.arch": platform.machine(),
            "sys.cpu": platform.processor() or "Inconnu",
            "sys.cores": os.cpu_count() or 1,
            "sys.cwd": str(Path.cwd()),
            "sys.script": str(self.script_path),
            "sys.home": str(Path.home()),
            "sys.python": platform.python_version(),
            "sys.shell": os.environ.get("SHELL", "Inconnu"),
            "sys.uptime": self.get_uptime(),
            "sys.version": VERSION,
            "sys.date": time.strftime("%Y-%m-%d"),
            "sys.time": time.strftime("%H:%M:%S"),
        }

        for name, value in variables.items():
            self.variables[name] = value

    # =========================================================
    # CONDITIONS
    # =========================================================

    @staticmethod
    def convert_value(value):
        if isinstance(value, (int, float)):
            return value

        text = str(value).strip()

        try:
            if "." in text:
                return float(text)

            return int(text)

        except ValueError:
            return text

    def condition_path(self, path_text):
        path = Path(os.path.expanduser(path_text))

        if not path.is_absolute():
            path = self.script_path.parent / path

        return path

    def parse_condition(self, condition):
        """
        Évalue une condition, avec `and` et `or` (and passe avant or) :
            :if $a > 1 and $b == y
            :if $a == 1 or exist fichier.txt
        """

        parts = self.CONDITION_SPLIT.split(condition.strip())

        groups = [[parts[0]]]

        for position in range(1, len(parts), 2):
            operator_word = parts[position]
            clause = parts[position + 1]

            if operator_word == "or":
                groups.append([clause])

            else:
                groups[-1].append(clause)

        return any(
            all(self.parse_single_condition(clause) for clause in group)
            for group in groups
        )

    def parse_single_condition(self, condition):
        condition = condition.strip()

        if condition.startswith("exist "):
            target = condition[6:].strip()

            if not target:
                raise SysTeenError(
                    "Syntaxe : :if exist [variable/fichier]"
                )

            variable = self.variable_from_token(target)

            if variable is not None:
                return variable in self.variables

            target = self.interpolate(target)

            return self.condition_path(target).exists()

        if condition.startswith("not exist "):
            target = condition[10:].strip()

            if not target:
                raise SysTeenError(
                    "Syntaxe : :if not exist [variable/fichier]"
                )

            variable = self.variable_from_token(target)

            if variable is not None:
                return variable not in self.variables

            target = self.interpolate(target)

            return not self.condition_path(target).exists()

        if condition.startswith("empty "):
            target = condition[6:].strip()

            variable = self.variable_from_token(target)

            if variable is None:
                raise SysTeenError("empty doit utiliser une variable.")

            return str(self.require_variable(variable)) == ""

        if condition.startswith("notempty "):
            target = condition[9:].strip()

            variable = self.variable_from_token(target)

            if variable is None:
                raise SysTeenError("notempty doit utiliser une variable.")

            return str(self.require_variable(variable)) != ""

        text_operators = [
            "not contains",
            "contains",
            "startswith",
            "endswith",
        ]

        for operator_name in text_operators:

            separator = f" {operator_name} "

            if separator not in condition:
                continue

            left, right = condition.split(separator, 1)

            left = left.strip()

            right = self.interpolate(right.strip())

            variable = self.variable_from_token(left)

            if variable is None:
                raise SysTeenError(
                    "Une condition doit utiliser une variable."
                )

            value = str(self.require_variable(variable))

            if operator_name == "contains":
                return right in value

            if operator_name == "not contains":
                return right not in value

            if operator_name == "startswith":
                return value.startswith(right)

            if operator_name == "endswith":
                return value.endswith(right)

        operators = ["==", "!=", ">=", "<=", ">", "<"]

        selected_operator = None

        for op in operators:
            if op in condition:
                selected_operator = op
                break

        if selected_operator is None:
            raise SysTeenError("Condition invalide.")

        left, right = condition.split(selected_operator, 1)

        left = left.strip()
        right = right.strip()

        if not left or not right:
            raise SysTeenError("Condition incomplète.")

        variable_name = self.variable_from_token(left)

        if variable_name is None:
            raise SysTeenError(
                "Une condition doit utiliser une variable."
            )

        left_value = self.require_variable(variable_name)

        right_value = self.interpolate(right)

        left_value = self.convert_value(left_value)
        right_value = self.convert_value(right_value)

        try:
            if selected_operator == "==":
                return left_value == right_value

            if selected_operator == "!=":
                return left_value != right_value

            if selected_operator == ">":
                return left_value > right_value

            if selected_operator == "<":
                return left_value < right_value

            if selected_operator == ">=":
                return left_value >= right_value

            if selected_operator == "<=":
                return left_value <= right_value

        except TypeError:
            raise SysTeenError("Impossible de comparer ces valeurs.")

        return False

    # =========================================================
    # IF / ELSE
    # =========================================================

    def find_if_structure(self, start):
        depth = 0
        else_line = None

        for index in range(start, len(self.lines)):
            line = self.lines[index].strip()

            if not line.startswith(":"):
                continue

            command_line = line[1:].strip()

            if not command_line:
                continue

            command = command_line.split(maxsplit=1)[0]

            if command == "if":
                depth += 1
                continue

            if command == "elsend":

                if depth == 0:
                    return else_line, index

                depth -= 1
                continue

            if command == "else":
                if depth == 0:

                    if else_line is not None:
                        raise SysTeenError(
                            "Plusieurs :else dans le même :if."
                        )

                    else_line = index

        raise SysTeenError(":if sans :elsend.")

    # =========================================================
    # PRESENTATION DES :if / :loop (conseil) ET VERIFICATION
    # =========================================================

    def check_indentation(self):
        """
        Parcourt le script (sans l'exécuter) et retourne une liste
        de (type, ligne, texte) :

          "structure" : :if / :loop mal fermés (vraie erreur)
          "style"     : décalage conseillé, 1 espace par niveau

            :if condition
             :commande
             :if autre_condition
              :commande
             :elsend
            :elsend

        Ne bloque jamais l'exécution d'un script.
        """

        issues = []
        stack = []
        index = 0

        while index < len(self.lines):
            raw = self.lines[index]
            stripped = raw.strip()

            if not stripped.startswith(":"):
                index += 1
                continue

            command_line = stripped[1:].strip()

            if not command_line:
                index += 1
                continue

            parts = command_line.split(maxsplit=1)
            command = parts[0]
            number = index + 1
            indent = len(raw) - len(raw.lstrip())
            depth = len(stack)

            if command == "if":
                expected = {depth}
                stack.append("if")

            elif command == "loop" and self.is_block_loop_line(raw):
                expected = {depth}
                stack.append("loop")

            elif command == "else":
                if not stack or stack[-1] != "if":
                    issues.append(
                        ("structure", number, ":else sans :if.")
                    )

                expected = {max(depth - 1, 0), depth}

            elif command == "elsend":
                if stack and stack[-1] == "if":
                    stack.pop()

                else:
                    issues.append(
                        ("structure", number, ":elsend sans :if.")
                    )

                expected = {len(stack)}

            elif command == "loopend":
                if stack and stack[-1] == "loop":
                    stack.pop()

                else:
                    issues.append(
                        ("structure", number, ":loopend sans :loop.")
                    )

                expected = {len(stack)}

            else:
                expected = {depth}

            if indent not in expected:
                wanted = " ou ".join(
                    str(value) for value in sorted(expected)
                )

                issues.append((
                    "style",
                    number,
                    f"{wanted} espace(s) de décalage conseillé(s), "
                    f"{indent} trouvé(s)."
                ))

            # Un :edit sur plusieurs lignes : le texte entre
            # guillemets n'est pas du code SysTeen.
            if command == "edit":
                try:
                    _, last_line = self.find_edit_text(
                        index,
                        parts[1] if len(parts) > 1 else ""
                    )

                    index = last_line

                except SysTeenError:
                    pass

            index += 1

        unclosed_if = stack.count("if")
        unclosed_loop = stack.count("loop")

        if unclosed_if:
            issues.append((
                "structure", None,
                f"il manque {unclosed_if} :elsend pour fermer "
                "les :if."
            ))

        if unclosed_loop:
            issues.append((
                "structure", None,
                f"il manque {unclosed_loop} :loopend pour fermer "
                "les :loop."
            ))

        return issues

    def command_check(self):
        """
        systeen --check script.st

        Vérifie le script SANS l'exécuter : commandes inconnues,
        :if / :loop mal fermés, variables utilisées avant d'être
        créées, fichiers de :go introuvables, syntaxe de :wait et
        :loop, etc. Retourne le nombre d'erreurs.
        """

        errors = []
        warnings = []

        created = set(self.variables)   # variables déjà sauvegardées
        added = set()
        sys_loaded = False
        has_end = False
        reported = set()

        total = len(self.lines)

        inline_commands = {"say", "cmd", "math", "wait", "run", "stop", "go"}

        wait_units = {"sec", "min", "h", "j", "y"}

        for kind, number, text in self.check_indentation():
            if kind == "structure":
                errors.append((number, text))

            else:
                warnings.append((number, text))

        index = 0

        while index < total:
            raw = self.lines[index]
            stripped = raw.strip()
            number = index + 1

            if not stripped.startswith(":"):
                index += 1
                continue

            command_line = stripped[1:].strip()

            if not command_line:
                index += 1
                continue

            parts = command_line.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            last_line = index
            scan_text = command_line

            if command == "edit":
                try:
                    _, last_line = self.find_edit_text(index, args)

                except SysTeenError as error:
                    errors.append((number, str(error)))

                scan_text = "\n".join(self.lines[index:last_line + 1])

            def require(name, number=number):
                if name not in created:
                    errors.append((
                        number,
                        f"la variable '{name}' n'est pas créée avant "
                        f"cette ligne (:var add {name})."
                    ))

            if command not in KNOWN_COMMANDS:
                if command == "crea":
                    errors.append((
                        number, ":crea a été renommée :add."
                    ))

                else:
                    errors.append((
                        number, f"commande inconnue : :{command}"
                    ))

                index = last_line + 1
                continue

            if command in COMMANDS_WITH_ARGUMENT and not args.strip():
                errors.append((
                    number, f"arguments manquants pour :{command}."
                ))

            if command == "systeen":
                option = args.strip()

                if option == "end":
                    has_end = True

                elif option != "start":
                    errors.append((
                        number, "commande systeen inconnue."
                    ))

            elif command == "var":
                tokens = args.split(maxsplit=2)

                if args.strip() == "sys":
                    sys_loaded = True

                elif len(tokens) == 2 and tokens[0] == "add":
                    if not re.fullmatch(
                        r"[A-Za-z0-9_][A-Za-z0-9_.]*", tokens[1]
                    ):
                        errors.append((
                            number,
                            f"nom de variable invalide : '{tokens[1]}' "
                            "(lettres, chiffres, _ et . uniquement)."
                        ))

                    if tokens[1] in added:
                        warnings.append((
                            number,
                            f":var add {tokens[1]} déjà utilisé plus "
                            "haut : échoue si le script boucle."
                        ))

                    added.add(tokens[1])
                    created.add(tokens[1])

                elif len(tokens) == 2 and tokens[0] == "rm":
                    require(tokens[1])

                elif "=" in args:
                    require(args.split("=", 1)[0].strip())

                elif args.strip():
                    errors.append((number, "syntaxe de :var invalide."))

            elif command == "save":
                require(args.strip())

            elif command in ("say?", "sayn?", "sayN?"):
                if ";" not in args:
                    errors.append((
                        number,
                        f"syntaxe : :{command} [question] ; [variable]"
                    ))

                else:
                    require(args.rsplit(";", 1)[1].strip())

            elif command == "math":
                if ";" in args:
                    require(args.rsplit(";", 1)[1].strip())

            elif command == "read":
                if ";" not in args:
                    errors.append((
                        number, "syntaxe : :read [fichier] ; [variable]"
                    ))

                else:
                    require(args.rsplit(";", 1)[1].strip())

            elif command == "cmd":
                match = self.CMD_CAPTURE.match(args.strip())

                if match is not None:
                    name = match.group(2)

                    if name in created:
                        pass

                    elif (
                        shutil.which(name) is None
                        and name not in SHELL_BUILTINS
                    ):
                        require(name)

            elif command == "go":
                target = args.strip()

                if target and "$" not in target:
                    go_path = Path(os.path.expanduser(target))

                    if not go_path.is_absolute():
                        go_path = self.script_path.parent / go_path

                    if go_path.suffix != ".st":
                        errors.append((
                            number,
                            f":go : {target} n'a pas l'extension .st."
                        ))

                    elif not go_path.is_file():
                        errors.append((
                            number, f":go : fichier introuvable : {target}"
                        ))

            elif command == "wait":
                tokens = args.lower().split()

                valid = len(tokens) == 2 and tokens[1] in wait_units

                if valid:
                    try:
                        float(tokens[0])

                    except ValueError:
                        valid = False

                if args.strip() and not valid:
                    errors.append((
                        number,
                        "syntaxe : :wait [nombre] [sec/min/h/j/y]"
                    ))

            elif command == "loop" and not self.is_block_loop_line(raw):
                tokens = args.split(maxsplit=2)

                if tokens and tokens[0].startswith("L"):
                    data = tokens[0][1:]

                    if "-" not in data:
                        errors.append((
                            number, "syntaxe : :loop L5-2 ou :loop L5-inf"
                        ))

                    else:
                        target_text, count_text = data.split("-", 1)

                        if not (
                            target_text.isdigit()
                            and 1 <= int(target_text) <= total
                        ):
                            errors.append((
                                number,
                                "ligne cible inexistante dans :loop."
                            ))

                        if not (
                            count_text == "inf" or count_text.isdigit()
                        ):
                            errors.append((
                                number, "nombre de boucles invalide."
                            ))

                elif tokens:
                    if len(tokens) < 2:
                        errors.append((
                            number, ":loop doit contenir une commande."
                        ))

                    else:
                        if not (
                            tokens[0] == "inf" or tokens[0].isdigit()
                        ):
                            errors.append((
                                number,
                                "nombre de répétitions invalide."
                            ))

                        inline = tokens[1].lstrip(":")

                        if inline not in inline_commands:
                            errors.append((
                                number,
                                f"commande inline inconnue : :{inline}"
                            ))

            # Variables utilisées ($nom ou ${nom})
            references_text = scan_text

            if command == "if":
                references_text = re.sub(
                    r"(?:not\s+)?exist\s+\$\{?[A-Za-z0-9_][A-Za-z0-9_.]*\}?",
                    "",
                    scan_text
                )

            for match in self.VARIABLE_REFERENCE.finditer(references_text):
                name = match.group(1) or match.group(2)

                if name is None:
                    continue

                if (number, name) in reported:
                    continue

                reported.add((number, name))

                if name.startswith("sys."):
                    if not sys_loaded:
                        errors.append((
                            number,
                            f"${name} utilisée sans :var sys avant."
                        ))

                elif name not in created:
                    errors.append((
                        number,
                        f"la variable '{name}' est utilisée avant "
                        f"d'être créée (:var add {name})."
                    ))

            index = last_line + 1

        if not has_end:
            warnings.append((
                None,
                "pas de :systeen end : le script recommence depuis "
                "la première ligne quand il arrive à la fin."
            ))

        errors.sort(key=lambda item: item[0] or 10 ** 9)
        warnings.sort(key=lambda item: item[0] or 10 ** 9)

        print(
            f"[SysTeen] Vérification de {self.script_path.name} "
            "(le script n'est pas exécuté)"
        )

        if errors:
            print(f"[SysTeen] Erreurs ({len(errors)}) :")

            for number, text in errors:
                print(f"[SysTeen]   {format_issue(number, text)}")

        if warnings:
            print(f"[SysTeen] Conseils ({len(warnings)}) :")

            for number, text in warnings:
                print(f"[SysTeen]   {format_issue(number, text)}")

        if not errors and not warnings:
            print("[SysTeen] Aucun problème détecté.")

        elif not errors:
            print("[SysTeen] Aucune erreur.")

        return len(errors)

    # =========================================================
    # CHEMINS
    # =========================================================

    @staticmethod
    def safe_path(path_text):
        path = Path(os.path.expanduser(path_text))

        if not path.is_absolute():
            path = Path.cwd() / path

        return path.resolve()

    # =========================================================
    # DEL / DEL! / RMF
    # =========================================================

    def delete_path(self, path_text):
        path = self.safe_path(path_text)

        self.check_destructive_path(path)

        if not path.exists() and not path.is_symlink():
            raise SysTeenError(
                f"Fichier ou dossier introuvable : {path}"
            )

        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)

        else:
            path.unlink()

    def delete_with_sudo(self, path_text):
        path = self.safe_path(path_text)

        self.check_destructive_path(path)

        result = subprocess.run(
            ["sudo", "rm", "-rf", "--", str(path)]
        )

        if result.returncode != 0:
            raise SysTeenError(
                f"Échec de la suppression avec sudo : {path}"
            )

    def command_del(self, content, fallback_sudo=False):
        content = self.interpolate(content.strip())

        if not content:
            raise SysTeenError("Fichier ou dossier manquant.")

        try:
            self.delete_path(content)

        except PermissionError:

            if fallback_sudo:
                print(
                    "[SysTeen] Accès refusé. "
                    "Nouvelle tentative avec sudo..."
                )

                self.delete_with_sudo(content)

            else:
                raise SysTeenError(
                    "Accès refusé. Utilisez :del! ou :rmf."
                )

    def command_rmf(self, content):
        content = self.interpolate(content.strip())

        if not content:
            raise SysTeenError("Fichier ou dossier manquant.")

        self.delete_with_sudo(content)

    # =========================================================
    # ADD (ancien :crea)
    # =========================================================

    def command_add(self, content):
        name = self.interpolate(content.strip())

        if not name:
            raise SysTeenError("Nom manquant.")

        path = self.safe_path(name)

        if path.exists():
            raise SysTeenError(
                f"Le fichier ou dossier existe déjà : {path}"
            )

        if Path(name).suffix:
            path.parent.mkdir(parents=True, exist_ok=True)

            path.touch()

        else:
            path.mkdir(parents=True)

    # =========================================================
    # EDIT
    # =========================================================

    def find_edit_text(self, line_index, first_line):
        text = first_line

        first_quote = text.find('"')

        if first_quote == -1:
            raise SysTeenError('Syntaxe : :edit [fichier] "texte"')

        content = text[first_quote + 1:]

        while True:
            closing_quote = content.find('"')

            if closing_quote != -1:
                return content[:closing_quote], line_index

            line_index += 1

            if line_index >= len(self.lines):
                raise SysTeenError(
                    "Guillemet fermant manquant dans :edit."
                )

            content += "\n" + self.lines[line_index]

    def command_edit(self, line_index, content):
        content = content.strip()

        if not content:
            raise SysTeenError('Syntaxe : :edit [fichier] "texte"')

        first_quote = content.find('"')

        if first_quote == -1:
            raise SysTeenError('Syntaxe : :edit [fichier] "texte"')

        filename = content[:first_quote].strip()

        # :edit +fichier "texte" ajoute à la fin au lieu d'écraser
        append = filename.startswith("+")

        if append:
            filename = filename[1:].strip()

        if not filename:
            raise SysTeenError("Nom de fichier manquant.")

        full_content, last_line = self.find_edit_text(
            line_index, content
        )

        filename = self.interpolate(filename)
        full_content = self.interpolate(full_content)

        path = self.safe_path(filename)

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(
            path, "a" if append else "w", encoding="utf-8"
        ) as output:
            output.write(full_content)

        return last_line

    # =========================================================
    # SAY / SAY?
    # =========================================================

    def command_say(self, content):
        print(self.interpolate(content))

    def command_say_input(self, content):
        if ";" not in content:
            raise SysTeenError(
                "Syntaxe : :say? [question] ; [variable]"
            )

        question, variable = content.rsplit(";", 1)

        question = question.strip()
        variable = variable.strip()

        self.require_variable(variable)

        answer = input(self.interpolate(question) + " ")

        self.variables[variable] = answer

    # =========================================================
    # SAYN? / SAYN? : question à réponse y ou n uniquement
    # =========================================================

    def command_say_yes_no(self, content, default_yes):
        """
        :sayn? question ; variable   -> (Y/n) : Entrée = y
        :sayN? question ; variable   -> (y/N) : Entrée = n

        Seules les réponses y ou n sont acceptées (majuscules
        tolérées). La variable reçoit "y" ou "n".
        """

        name = ":sayn?" if default_yes else ":sayN?"

        if ";" not in content:
            raise SysTeenError(
                f"Syntaxe : {name} [question] ; [variable]"
            )

        question, variable = content.rsplit(";", 1)

        question = question.strip()
        variable = variable.strip()

        self.require_variable(variable)

        hint = "(Y/n)" if default_yes else "(y/N)"

        prompt = f"{self.interpolate(question)} {hint} "

        while True:
            answer = input(prompt).strip().lower()

            if answer == "":
                value = "y" if default_yes else "n"
                break

            if answer in ("y", "n"):
                value = answer
                break

            print("[SysTeen] Réponse invalide. Répondez y ou n.")

        self.variables[variable] = value

    # =========================================================
    # MATH
    # =========================================================

    def command_math(self, content):
        target = None

        if ";" in content:
            expression, target = content.rsplit(";", 1)

            expression = expression.strip()
            target = target.strip()

            self.require_variable(target)

        else:
            expression = content.strip()

        expression = self.interpolate(expression)

        result = SafeMath.evaluate(expression)

        if target:
            self.variables[target] = result

        else:
            print(result)

    # =========================================================
    # CMD
    # =========================================================

    def split_cmd_capture(self, content):
        """
        Sépare `commande ; variable`.

        Retourne (commande, variable) ou (commande, None).
        Si ce qui suit le dernier `;` est une variable existante, c'est
        une capture. Si c'est un vrai programme ou une commande du shell
        (`echo a ; ls`), tout reste du shell. Sinon : variable oubliée.
        """

        text = content.strip()

        match = self.CMD_CAPTURE.match(text)

        if match is None:
            return text, None

        command, name = match.group(1).strip(), match.group(2)

        if name in self.variables:
            return command, name

        if shutil.which(name) is not None or name in SHELL_BUILTINS:
            return text, None

        raise SysTeenError(
            f"Variable-404 : la variable '{name}' n'existe pas. "
            "(syntaxe : :cmd commande ; variable)"
        )

    @staticmethod
    def is_dangerous_rm_target(target):
        expanded = os.path.expandvars(os.path.expanduser(target))

        candidate = expanded

        changed = True

        while changed:
            changed = False

            for suffix in ("/*", "/.*", "/."):
                if candidate.endswith(suffix):
                    candidate = candidate[:-len(suffix)] or "/"
                    changed = True

        if not candidate:
            return False

        try:
            resolved = Path(candidate).resolve()

        except Exception:
            return False

        homes = {Path.home().resolve(), get_real_home().resolve()}

        return resolved == Path("/").resolve() or resolved in homes

    def check_dangerous_command(self, command):
        """
        Quand la sécurité est active, refuse les `rm -r` évidents sur
        / ou sur le dossier personnel. Ce n'est pas une protection
        parfaite (un script déguisé la contourne), mais elle évite
        les accidents.
        """

        if not self.safety_enabled:
            return

        for segment in re.split(r"[;&|\n]+", command):

            try:
                tokens = shlex.split(segment)

            except ValueError:
                tokens = segment.split()

            for position, token in enumerate(tokens):

                if Path(token).name != "rm":
                    continue

                recursive = False
                no_preserve_root = False
                only_targets = False
                targets = []

                for argument in tokens[position + 1:]:

                    if only_targets:
                        targets.append(argument)

                    elif argument == "--":
                        only_targets = True

                    elif argument == "--no-preserve-root":
                        no_preserve_root = True

                    elif argument == "--recursive":
                        recursive = True

                    elif argument.startswith("--"):
                        continue

                    elif argument.startswith("-") and len(argument) > 1:
                        if "r" in argument or "R" in argument:
                            recursive = True

                    else:
                        targets.append(argument)

                if no_preserve_root or (
                    recursive
                    and any(
                        self.is_dangerous_rm_target(target)
                        for target in targets
                    )
                ):
                    raise SysTeenError(
                        "Commande bloquée par la sécurité SysTeen : "
                        "elle supprimerait / ou votre dossier personnel."
                    )

    def command_cmd(self, content):
        """
        :cmd commande
            Exécute la commande dans le terminal.

        :cmd commande ; variable
            Met le résultat (sortie) de la commande dans une variable
            existante. Le retour à la ligne final est retiré.
        """

        raw_command, target = self.split_cmd_capture(content)

        command = self.interpolate(raw_command)

        if not command:
            raise SysTeenError("Commande Linux manquante.")

        self.check_dangerous_command(command)

        print(
            "[SysTeen] Attention : SysTeen va executer "
            "une commande dans votre terminal."
        )

        print(f"[SysTeen] commande : {command}")

        if target is None:
            subprocess.run(command, shell=True)
            return

        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE
        )

        output = result.stdout.decode("utf-8", errors="replace")

        if output.endswith("\r\n"):
            output = output[:-2]

        elif output.endswith("\n"):
            output = output[:-1]

        self.variables[target] = output

        if result.returncode != 0:
            print(
                "[SysTeen] La commande a retourné le code "
                f"{result.returncode}."
            )

    # =========================================================
    # READ / COPY / PASTE / PAUSE
    # =========================================================

    def command_read(self, content):
        """:read fichier ; variable"""

        if ";" not in content:
            raise SysTeenError("Syntaxe : :read [fichier] ; [variable]")

        file_text, variable = content.rsplit(";", 1)

        file_text = self.interpolate(file_text.strip())
        variable = variable.strip()

        self.require_variable(variable)

        if not file_text:
            raise SysTeenError("Fichier manquant.")

        path = self.safe_path(file_text)

        if not path.is_file():
            raise SysTeenError(f"Fichier introuvable : {path}")

        try:
            size = path.stat().st_size

            if size > MAX_READ_BYTES:
                raise SysTeenError(
                    f"Fichier trop gros pour :read ({path}) : "
                    f"{MAX_READ_BYTES // (1024 * 1024)} Mo maximum."
                )

            text = path.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            raise SysTeenError(
                f"{path} n'est pas un fichier texte UTF-8."
            )

        except OSError as error:
            raise SysTeenError(
                f"Impossible de lire {path} : {error}"
            )

        if text.endswith("\r\n"):
            text = text[:-2]

        elif text.endswith("\n"):
            text = text[:-1]

        self.variables[variable] = text

    def command_copy(self, content):
        """:copy chemin   (mémorise un fichier ou un dossier)"""

        name = self.interpolate(content.strip())

        if not name:
            raise SysTeenError("Syntaxe : :copy [fichier ou dossier]")

        path = self.safe_path(name)

        if not path.exists():
            raise SysTeenError(
                f"Fichier ou dossier introuvable : {path}"
            )

        self.clipboard = path

    def command_paste(self, content):
        """
        :paste destination
            Colle l'élément mémorisé par :copy.

            - destination = dossier existant (ou terminé par /) :
              l'élément est collé dedans, avec son nom d'origine ;
            - sinon : destination est le nouveau chemin complet.
            Rien n'est jamais écrasé.
        """

        if self.clipboard is None:
            raise SysTeenError(
                "Rien à coller : utilisez d'abord :copy."
            )

        source = self.clipboard

        if not source.exists():
            raise SysTeenError(
                f"L'élément copié n'existe plus : {source}"
            )

        destination_text = self.interpolate(content.strip())

        if not destination_text:
            raise SysTeenError("Syntaxe : :paste [destination]")

        destination = self.safe_path(destination_text)

        if destination.is_dir() or destination_text.endswith("/"):
            destination.mkdir(parents=True, exist_ok=True)

            destination = destination / source.name

        else:
            destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists() or destination.is_symlink():
            raise SysTeenError(
                f"Le fichier ou dossier existe déjà : {destination}"
            )

        if source.is_dir() and (
            destination == source or source in destination.parents
        ):
            raise SysTeenError(
                "Impossible de coller un dossier dans lui-même."
            )

        try:
            if source.is_dir():
                shutil.copytree(source, destination, symlinks=True)

            else:
                shutil.copy2(source, destination)

        except (OSError, shutil.Error) as error:
            raise SysTeenError(
                f"Impossible de coller vers {destination} : {error}"
            )

    def command_pause(self, content):
        """:pause [message]   (attend la touche Entrée)"""

        message = self.interpolate(content.strip())

        if not message:
            message = "[SysTeen] Appuyez sur Entrée pour continuer..."

        try:
            input(message + " ")

        except EOFError:
            pass

    # =========================================================
    # BOUCLES EN BLOC : :loop N ... :loopend
    # =========================================================

    @staticmethod
    def is_block_loop_line(line):
        """Vrai pour ':loop 3' ou ':loop inf' seul sur la ligne."""

        stripped = line.strip()

        if not stripped.startswith(":"):
            return False

        parts = stripped[1:].split()

        return (
            len(parts) == 2
            and parts[0] == "loop"
            and (parts[1] == "inf" or parts[1].isdigit())
        )

    def find_loop_end(self, start):
        depth = 0

        for index in range(start + 1, len(self.lines)):
            line = self.lines[index]

            if self.is_block_loop_line(line):
                depth += 1
                continue

            stripped = line.strip()

            if (
                stripped.startswith(":")
                and stripped[1:].split()[:1] == ["loopend"]
            ):
                if depth == 0:
                    return index

                depth -= 1

        raise SysTeenError(":loop sans :loopend.")

    def start_block_loop(self, line_index, count_text):
        end_line = self.find_loop_end(line_index)

        remaining = None if count_text == "inf" else int(count_text)

        if remaining is not None and remaining <= 0:
            return end_line + 1

        self.block_stack = [
            entry for entry in self.block_stack
            if entry[0] != line_index
        ]

        self.block_stack.append([line_index, remaining])

        return line_index + 1

    def command_loopend(self, line_index):
        if not self.block_stack:
            raise SysTeenError(":loopend sans :loop.")

        entry = self.block_stack[-1]

        start, remaining = entry

        if remaining is None:
            return start + 1

        entry[1] = remaining - 1

        if entry[1] > 0:
            return start + 1

        self.block_stack.pop()

        return line_index + 1

    # =========================================================
    # RUN / STOP
    # =========================================================

    def command_run(self, content):
        program = self.interpolate(content.strip())

        if not program:
            raise SysTeenError("Programme manquant.")

        subprocess.Popen(shlex.split(program))

    def command_stop(self, content):
        program = self.interpolate(content.strip())

        if not program:
            raise SysTeenError("Programme manquant.")

        subprocess.run(["pkill", "-x", program], check=False)

    # =========================================================
    # GO : lancer un second script SysTeen dans une nouvelle fenêtre
    # =========================================================

    @staticmethod
    def has_graphical_session():
        """Vrai si un affichage graphique (X11 ou Wayland) est disponible."""

        return bool(
            os.environ.get("DISPLAY")
            or os.environ.get("WAYLAND_DISPLAY")
        )

    @staticmethod
    def terminal_candidates(command):
        """
        Retourne la liste des (nom, commande complète) de terminaux
        graphiques installés, dans l'ordre d'essai.

        Si la variable d'environnement TERMINAL désigne un terminal
        connu, il passe en premier.
        """

        names = list(TERMINAL_STYLES)

        preferred = os.environ.get("TERMINAL", "").strip()

        if preferred:
            try:
                parts = shlex.split(preferred)
            except ValueError:
                parts = []

            if parts:
                preferred_name = Path(parts[0]).name

                if preferred_name in TERMINAL_STYLES:
                    names.remove(preferred_name)
                    names.insert(0, preferred_name)

        candidates = []

        for name in names:
            binary = shutil.which(name)

            if binary is None:
                continue

            candidates.append(
                (name, [binary] + TERMINAL_STYLES[name](command))
            )

        return candidates

    def open_terminal_window(self, command, env):
        """
        Ouvre une nouvelle fenêtre de terminal visible qui exécute
        `command`. Retourne le nom du terminal utilisé.

        Le terminal est détaché de ce processus (nouvelle session,
        entrées/sorties coupées) : le second script a son propre
        clavier et ne perturbe jamais le terminal d'origine.
        """

        if not self.has_graphical_session():
            raise SysTeenError(
                ":go ouvre une fenêtre de terminal, mais aucun "
                "affichage graphique n'a été détecté "
                "(DISPLAY / WAYLAND_DISPLAY absents)."
            )

        candidates = self.terminal_candidates(command)

        if not candidates:
            raise SysTeenError(
                "Aucun terminal graphique trouvé. Installez-en un "
                "(par exemple xterm, gnome-terminal, konsole ou "
                "xfce4-terminal)."
            )

        for name, argv in candidates:
            try:
                process = subprocess.Popen(
                    argv,
                    env=env,
                    cwd=str(Path.cwd()),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

            except OSError:
                continue

            # Certains terminaux (gnome-terminal...) rendent la main
            # tout de suite avec le code 0 ; d'autres restent ouverts.
            # Un code d'erreur immédiat veut dire que ce terminal n'a
            # pas pu s'ouvrir : on essaie le suivant.
            time.sleep(0.6)

            code = process.poll()

            if code is None or code == 0:
                return name

        raise SysTeenError(
            "Impossible d'ouvrir une fenêtre de terminal "
            "(tous les terminaux testés ont échoué)."
        )

    def command_go(self, content):
        """
        :go fichier.st
            Fichier situé dans le même dossier que le script actuel.

        :go /home/user/fichier.st
            Chemin absolu (le ~ est aussi accepté).

        Le second script s'exécute dans une NOUVELLE FENÊTRE de
        terminal, visible et indépendante, avec son propre clavier.
        La fenêtre attend une touche à la fin pour laisser lire
        les messages. Aucune nouvelle confirmation n'est demandée.
        """

        target = self.interpolate(content.strip())

        if not target:
            raise SysTeenError("Syntaxe : :go [fichier.st]")

        path = Path(os.path.expanduser(target))

        if not path.is_absolute():
            path = self.script_path.parent / path

        path = path.resolve()

        if path.is_dir():
            raise SysTeenError(
                f"{path} est un dossier : indiquez un fichier .st."
            )

        if path.suffix != ".st":
            raise SysTeenError(
                "Le fichier lancé par :go doit avoir l'extension .st."
            )

        if not path.is_file():
            raise SysTeenError(f"Fichier SysTeen introuvable : {path}")

        if path == self.script_path:
            raise SysTeenError(
                "Un script ne peut pas se lancer lui-même avec :go."
            )

        try:
            depth = int(os.environ.get("SYSTEEN_GO_DEPTH", "0"))
        except ValueError:
            depth = 0

        if depth >= MAX_GO_DEPTH:
            raise SysTeenError(
                "Trop de scripts lancés les uns par les autres "
                f"(limite : {MAX_GO_DEPTH})."
            )

        # Pas de nouvelle confirmation : l'avertissement Y/n a déjà
        # été accepté au lancement du script d'origine.
        env = os.environ.copy()
        env["SYSTEEN_GO_DEPTH"] = str(depth + 1)

        command = [
            sys.executable,
            str(self.program_path),
            str(path),
            "--no-confirm",
            "--go-window",
        ]

        terminal = self.open_terminal_window(command, env)

        print(
            f"[SysTeen] {path.name} lancé dans une nouvelle "
            f"fenêtre ({terminal})."
        )

    # =========================================================
    # :# (relance en root puis arrêt du script)
    # =========================================================

    def command_elevate(self):
        """
        1) cd vers le dossier où se trouve systeen.py
        2) sudo python systeen.py <ce script>
        3) le script actuel s'arrête (le processus est remplacé)

        L'utilisateur n'a plus qu'à saisir le mot de passe root.
        """

        if os.geteuid() == 0:
            print(
                "[SysTeen] Vous êtes déjà root : :# ignoré."
            )
            return

        if shutil.which("sudo") is None:
            raise SysTeenError("sudo est introuvable sur ce système.")

        previous_directory = Path.cwd()

        # systeen.py est retrouvé automatiquement (__file__)
        try:
            os.chdir(self.program_path.parent)

        except OSError as error:
            raise SysTeenError(
                f"Impossible d'aller dans {self.program_path.parent} : "
                f"{error}"
            )

        # Les variables sauvegardées doivent être écrites avant l'arrêt
        self.write_saved_variables()

        command = [
            "sudo",
            sys.executable,
            str(self.program_path),
            str(self.script_path),
            "--no-confirm",
        ]

        # Dans une fenêtre ouverte par :go, on garde la pause finale
        if self.window_mode:
            command.append("--go-window")

        # sudo réinitialise l'environnement : la profondeur de :go
        # est donc transmise en argument pour garder la limite.
        go_depth = os.environ.get("SYSTEEN_GO_DEPTH", "0")

        if go_depth.isdigit():
            command.append(f"--go-depth={go_depth}")

        print(
            "[SysTeen] Relance en root : "
            f"cd {self.program_path.parent} && sudo python "
            f"{self.program_path.name} {self.script_path}"
        )

        sys.stdout.flush()

        try:
            # Remplace le processus : le script actuel s'arrête ici
            os.execvp("sudo", command)

        except OSError as error:
            os.chdir(previous_directory)

            raise SysTeenError(
                f"Impossible de lancer sudo : {error}"
            )

    # =========================================================
    # CD
    # =========================================================

    def command_cd(self, content):
        path = self.safe_path(self.interpolate(content.strip()))

        if not path.exists():
            raise SysTeenError(f"Chemin introuvable : {path}")

        if not path.is_dir():
            raise SysTeenError(
                f"Ce chemin n'est pas un dossier : {path}"
            )

        os.chdir(path)

    # =========================================================
    # WAIT
    # =========================================================

    def command_wait(self, content):
        parts = content.strip().lower().split()

        if len(parts) != 2:
            raise SysTeenError(
                "Syntaxe : :wait [nombre] [sec/min/h/j/y]"
            )

        try:
            amount = float(parts[0])

        except ValueError:
            raise SysTeenError("Nombre invalide.")

        unit = parts[1]

        multipliers = {
            "sec": 1,
            "min": 60,
            "h": 3600,
            "j": 86400,
            "y": 31536000
        }

        if unit not in multipliers:
            raise SysTeenError("Unité inconnue.")

        time.sleep(amount * multipliers[unit])

    # =========================================================
    # SYSTEME
    # =========================================================

    def command_reboot(self):
        subprocess.run(["systemctl", "reboot"], check=False)

    def command_shutdown(self):
        subprocess.run(["systemctl", "poweroff"], check=False)

    # =========================================================
    # README
    # =========================================================

    def command_readme(self):
        """
        python systeen.py --readme
            Affiche le README.md installé (vérifié par PGP
            lors de la dernière mise à jour).
        """

        if not self.readme_path.is_file():
            raise SysTeenError(
                "README.md introuvable à côté de systeen.py.\n"
                "Lancez : python systeen.py --maj"
            )

        try:
            text = self.readme_path.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            raise SysTeenError(
                "Le README.md n'est pas un fichier UTF-8 valide."
            )

        except OSError as error:
            raise SysTeenError(
                f"Impossible de lire le README.md : {error}"
            )

        print(text)

    # =========================================================
    # --change : modifier la protection de / et du HOME
    # =========================================================

    def command_change(self):
        """
        python systeen.py --change
            Permet de revenir sur le choix de la sécurité.
        """

        self.load_security_config()

        state = "OUI" if self.safety_enabled else "NON"

        print(f"[SysTeen] Sécurité actuellement : {state}.")

        self.ask_security_preference()

    # =========================================================
    # --install : commande "systeen" dans /usr/local/bin
    # =========================================================

    def bin_link_points_here(self):
        """Vrai si /usr/local/bin/systeen est un lien vers ce systeen.py."""

        try:
            return (
                BIN_LINK_PATH.is_symlink()
                and BIN_LINK_PATH.resolve() == self.program_path
            )

        except OSError:
            return False

    @staticmethod
    def run_privileged(command, error_message):
        """Exécute une commande directement si on est root, sinon via sudo."""

        if os.geteuid() != 0:
            if shutil.which("sudo") is None:
                raise SysTeenError(
                    "sudo est introuvable. Relancez cette commande "
                    "en root."
                )

            command = ["sudo"] + command

        result = subprocess.run(command)

        if result.returncode != 0:
            raise SysTeenError(error_message)

    def command_install(self):
        """
        python systeen.py --install
            Crée le lien /usr/local/bin/systeen -> systeen.py
            (systeen.py reste où il est).

            Ensuite : systeen mon_script.st / systeen --help ...
            Fonctionne dans tous les shells, sous sudo et dans les
            scripts. Il suffit de relancer --install si systeen.py
            est déplacé.
        """

        link = BIN_LINK_PATH

        # systeen.py doit être exécutable (shebang : python3)
        try:
            mode = self.program_path.stat().st_mode

            os.chmod(
                self.program_path,
                mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )

        except OSError as error:
            raise SysTeenError(
                f"Impossible de rendre {self.program_path} "
                f"exécutable : {error}"
            )

        if self.bin_link_points_here():
            print(
                f"[SysTeen] La commande 'systeen' est déjà "
                f"installée ({link})."
            )
            return

        if link.is_symlink():
            print(
                f"[SysTeen] {link} existe déjà et pointe vers :"
            )
            print(f"[SysTeen]   {os.readlink(link)}")
            print("[SysTeen] Le remplacer par ce systeen.py ? (Y/n)")

            if not self.ask_yes_no():
                print("[SysTeen] Aucune modification.")
                return

        elif link.exists():
            raise SysTeenError(
                f"{link} existe déjà et n'est pas un lien SysTeen : "
                "je ne l'écrase pas."
            )

        if not link.parent.is_dir():
            self.run_privileged(
                ["mkdir", "-p", str(link.parent)],
                f"Impossible de créer {link.parent}."
            )

        if os.geteuid() != 0:
            print(
                f"[SysTeen] Écriture dans {link.parent} : "
                "le mot de passe sudo peut être demandé."
            )

        self.run_privileged(
            ["ln", "-sfn", str(self.program_path), str(link)],
            f"Impossible de créer le lien {link}."
        )

        if not self.bin_link_points_here():
            raise SysTeenError(
                f"Le lien {link} n'a pas pu être vérifié."
            )

        print(f"[SysTeen] Commande installée : {link}")
        print(f"[SysTeen]   -> {self.program_path}")

        path_dirs = os.environ.get("PATH", "").split(":")

        if str(link.parent) not in path_dirs:
            print(
                f"[SysTeen] Attention : {link.parent} n'est pas "
                "dans votre PATH."
            )

        print()
        print("[SysTeen] Essayez : systeen --help")
        print("[SysTeen]           systeen mon_script.st")

    def remove_bin_link(self):
        """Retire /usr/local/bin/systeen s'il pointe vers ce programme."""

        if not self.bin_link_points_here():
            return False

        try:
            BIN_LINK_PATH.unlink()

        except PermissionError:
            self.run_privileged(
                ["rm", "-f", str(BIN_LINK_PATH)],
                f"Impossible de supprimer {BIN_LINK_PATH}."
            )

        return True

    # =========================================================
    # --uninstall : désinstallation complète
    # =========================================================

    def collect_uninstall_targets(self):
        """
        Retourne la liste des fichiers/dossiers à supprimer.

        Le programme lui-même est toujours placé en dernier.
        Les scripts .st de l'utilisateur ne sont jamais touchés,
        ni aucun trousseau GPG : la clé SLNE n'existe que dans le
        code de systeen.py (GPG est lancé dans un dossier temporaire).
        """

        program_dir = self.program_path.parent

        candidates = []

        # Fichiers .vars connus (registre) + ceux à côté du programme
        for entry in self.read_vars_registry():
            candidates.append(Path(entry))

        try:
            candidates.extend(program_dir.glob("*.st.vars"))
        except OSError:
            pass

        # README et fichiers de mise à jour temporaires
        candidates.append(self.readme_path)

        candidates.append(
            program_dir / ("." + self.program_path.name + ".update.new")
        )

        candidates.append(
            program_dir / ("." + self.readme_path.name + ".update.new")
        )

        # Cache Python éventuel
        try:
            candidates.extend(
                (program_dir / "__pycache__").glob(
                    self.program_path.stem + ".*.pyc"
                )
            )
        except OSError:
            pass

        # Dossiers temporaires de mise à jour restés sur le disque
        try:
            candidates.extend(
                Path(tempfile.gettempdir()).glob("systeen-update-*")
            )
        except OSError:
            pass

        # Configuration (préférence de sécurité, registre)
        candidates.append(self.config_dir)

        targets = []
        seen = set()

        for candidate in candidates:
            if str(candidate) in seen:
                continue

            seen.add(str(candidate))

            if candidate.exists() or candidate.is_symlink():
                targets.append(candidate)

        # Le programme en dernier
        targets.append(self.program_path)

        return targets

    def command_uninstall(self):
        targets = self.collect_uninstall_targets()

        print("[SysTeen] Désinstallation de SysTeen")
        print("[SysTeen] Les éléments suivants seront supprimés :")

        for target in targets:
            suffix = "/" if target.is_dir() else ""

            print(f"[SysTeen]   - {target}{suffix}")

        has_link = self.bin_link_points_here()

        if has_link:
            print(f"[SysTeen]   - {BIN_LINK_PATH} (commande systeen)")

        print(
            "[SysTeen] Vos scripts .st et la clé SLNE "
            "(hors du code de systeen.py) ne sont pas touchés."
        )
        print()
        print("[SysTeen] Pour confirmer, tapez exactement :")
        print(f"[SysTeen] {UNINSTALL_PHRASE}")

        answer = input("[SysTeen] > ").strip()

        if answer != UNINSTALL_PHRASE:
            print("[SysTeen] Phrase incorrecte : désinstallation annulée.")
            return

        errors = 0

        for target in targets:
            try:
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)

                else:
                    target.unlink()

            except FileNotFoundError:
                continue

            except Exception as error:
                errors += 1

                print(
                    f"[SysTeen] Impossible de supprimer {target} : "
                    f"{error}"
                )

        if has_link:
            try:
                self.remove_bin_link()

            except SysTeenError as error:
                errors += 1

                print(f"[SysTeen] {error}")

        if errors:
            print(
                f"[SysTeen] Désinstallation terminée avec {errors} "
                "erreur(s)."
            )

        else:
            print("[SysTeen] SysTeen a été désinstallé. Au revoir !")

    # =========================================================
    # MISE A JOUR / VERSION
    # =========================================================

    @staticmethod
    def parse_version(version):
        """
        Transforme 0.4.2 ou v0.4.2 en tuple comparable.
        """

        text = str(version).strip()

        if text.startswith("v"):
            text = text[1:]

        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", text)

        if not match:
            raise SysTeenError(f"Version invalide : {version}")

        return tuple(int(value) for value in match.groups())

    @staticmethod
    def normalize_version(version):
        parsed = SysTeen.parse_version(version)

        return ".".join(str(value) for value in parsed)

    def check_update_configuration(self):
        if GITHUB_REPOSITORY == "METTRE_GITHUB_ICI":
            raise SysTeenError(
                "Mise à jour impossible : "
                "GITHUB_REPOSITORY n'est pas configuré."
            )

        if PGP_PUBLIC_KEY == "METTRE_CLE_ICI":
            raise SysTeenError(
                "Mise à jour impossible : "
                "la clé publique PGP n'est pas configurée."
            )

        if PGP_FINGERPRINT == "METTRE_FINGERPRINT_ICI":
            raise SysTeenError(
                "Mise à jour impossible : "
                "l'empreinte PGP n'est pas configurée."
            )

        if "/" not in GITHUB_REPOSITORY:
            raise SysTeenError(
                "GITHUB_REPOSITORY doit être au format "
                "'proprietaire/depot'."
            )

        fingerprint = re.sub(r"\s+", "", PGP_FINGERPRINT).upper()

        if not re.fullmatch(r"[0-9A-F]{40}", fingerprint):
            raise SysTeenError("Empreinte PGP invalide.")

        self.update_fingerprint = fingerprint

    def github_request(self, url):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": f"SysTeen/{VERSION}",
                "Accept": "application/vnd.github+json"
            }
        )

        try:
            with urllib.request.urlopen(
                request, timeout=30
            ) as response:
                return response.read()

        except urllib.error.HTTPError as error:
            raise SysTeenError(
                f"GitHub a répondu avec HTTP {error.code}."
            )

        except urllib.error.URLError as error:
            raise SysTeenError(
                f"Impossible de contacter GitHub : {error.reason}"
            )

        except TimeoutError:
            raise SysTeenError(
                "Délai dépassé lors de la connexion à GitHub."
            )

    def get_github_release(self, target_version=None):
        repository = urllib.parse.quote(GITHUB_REPOSITORY, safe="/")

        if target_version is None:
            url = (
                "https://api.github.com/repos/"
                f"{repository}/releases/latest"
            )

        else:
            normalized = self.normalize_version(target_version)

            tag = urllib.parse.quote(f"v{normalized}", safe="")

            url = (
                "https://api.github.com/repos/"
                f"{repository}/releases/tags/{tag}"
            )

        raw = self.github_request(url)

        try:
            data = json.loads(raw.decode("utf-8"))

        except Exception:
            raise SysTeenError("Réponse GitHub invalide.")

        if not isinstance(data, dict):
            raise SysTeenError("Réponse GitHub invalide.")

        return data

    def get_release_asset(self, release, asset_name):
        assets = release.get("assets")

        if not isinstance(assets, list):
            raise SysTeenError(
                "La release GitHub ne contient "
                "pas de liste d'assets."
            )

        for asset in assets:
            if not isinstance(asset, dict):
                continue

            if asset.get("name") != asset_name:
                continue

            if not isinstance(asset.get("browser_download_url"), str):
                raise SysTeenError(
                    f"L'asset '{asset_name}' "
                    "ne possède pas d'URL valide."
                )

            return asset

        raise SysTeenError(f"Asset GitHub introuvable : {asset_name}")

    def download_file(self, url, destination):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": f"SysTeen/{VERSION}",
                "Accept": "*/*"
            }
        )

        try:
            with urllib.request.urlopen(
                request, timeout=60
            ) as response:

                with open(destination, "wb") as output:

                    while True:
                        chunk = response.read(1024 * 1024)

                        if not chunk:
                            break

                        output.write(chunk)

        except urllib.error.HTTPError as error:
            raise SysTeenError(
                "Impossible de télécharger l'asset "
                f"(HTTP {error.code})."
            )

        except urllib.error.URLError as error:
            raise SysTeenError(
                f"Impossible de télécharger l'asset : {error.reason}"
            )

        except TimeoutError:
            raise SysTeenError(
                "Délai dépassé pendant le téléchargement."
            )

    # ---------------------------------------------------------
    # VERIFICATION GPG
    # ---------------------------------------------------------

    @staticmethod
    def _run_gpg(command, env):
        """Lance GPG en binaire et décode sans jamais planter."""
        result = subprocess.run(
            command,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        return (
            result.returncode,
            result.stdout.decode("utf-8", errors="replace"),
            result.stderr.decode("utf-8", errors="replace")
        )

    @staticmethod
    def _gpg_status_lines(output):
        """Extrait les lignes '[GNUPG:] ...' sous forme de listes."""
        statuses = []

        for line in output.splitlines():
            if line.startswith("[GNUPG:] "):
                statuses.append(line[9:].split())

        return statuses

    @staticmethod
    def _check_signature_file(signature_file, signed_name="systeen.py"):
        """Détecte les erreurs classiques sur le fichier .asc."""
        head = Path(signature_file).read_bytes()[:200].lstrip()

        if not head:
            raise SysTeenError(
                f"Le fichier de signature de {signed_name} est vide."
            )

        if head.startswith(b"-----BEGIN PGP SIGNED MESSAGE-----"):
            raise SysTeenError(
                "Le fichier .asc est une signature 'clearsign' "
                "et non une signature détachée.\n"
                "Recréez-la avec : "
                f"gpg --armor --detach-sign {signed_name}"
            )

        if head.startswith(b"-----BEGIN PGP MESSAGE-----"):
            raise SysTeenError(
                "Le fichier .asc contient un message PGP (--sign) "
                "et non une signature détachée.\n"
                "Recréez-la avec : "
                f"gpg --armor --detach-sign {signed_name}"
            )

        if head.startswith(b"<") or head.lower().startswith(b"not found"):
            raise SysTeenError(
                "Le fichier de signature téléchargé n'est pas "
                "une signature (page HTML/erreur reçue)."
            )

    def verify_gpg_signature(
        self,
        public_key_file,
        signature_file,
        script_file,
        gpg_home,
        signed_name="systeen.py"
    ):
        """
        Vérifie une signature détachée avec la clé intégrée.

        Sert aussi bien pour systeen.py que pour README.md
        (même clé, même empreinte).
        """

        gpg = shutil.which("gpg")

        if gpg is None:
            raise SysTeenError(
                "GPG est requis pour vérifier "
                "la signature de la mise à jour."
            )

        expected = re.sub(r"\s+", "", self.update_fingerprint).upper()

        # Environnement GPG isolé, sortie stable (anglais/ASCII)
        env = os.environ.copy()
        env["GNUPGHOME"] = str(gpg_home)
        env["LC_ALL"] = "C"
        env["LANGUAGE"] = "C"
        env.pop("GPG_AGENT_INFO", None)

        base = [
            gpg,
            "--batch",
            "--no-tty",
            "--no-options",
            "--homedir", str(gpg_home),
        ]

        self._check_signature_file(signature_file, signed_name)

        # 1) Import de la clé publique
        code, out, err = self._run_gpg(
            base + [
                "--status-fd", "1",
                "--import", str(public_key_file)
            ],
            env
        )

        statuses = self._gpg_status_lines(out)

        imported = any(
            s and s[0] in ("IMPORT_OK", "IMPORT_RES")
            for s in statuses
        )

        if code != 0 or not imported:
            raise SysTeenError(
                "Impossible d'importer la clé publique PGP.\n"
                f"Détail GPG : {(err or out).strip()}"
            )

        # 2) Contrôle de l'empreinte (clé primaire uniquement)
        code, out, err = self._run_gpg(
            base + ["--with-colons", "--fingerprint"],
            env
        )

        if code != 0:
            raise SysTeenError(
                "Impossible de lire les empreintes PGP.\n"
                f"Détail GPG : {(err or out).strip()}"
            )

        primary_fingerprints = []
        expect_primary_fpr = False

        for line in out.splitlines():
            fields = line.split(":")
            record = fields[0]

            if record == "pub":
                expect_primary_fpr = True
                continue

            if record == "sub":
                expect_primary_fpr = False
                continue

            if record == "fpr" and expect_primary_fpr:
                if len(fields) > 9 and fields[9].strip():
                    primary_fingerprints.append(
                        fields[9].strip().upper()
                    )

                expect_primary_fpr = False

        if primary_fingerprints != [expected]:
            raise SysTeenError(
                "La clé PGP intégrée ne correspond pas à "
                "l'empreinte configurée.\n"
                f"Attendue : {expected}\n"
                "Trouvée  : "
                f"{', '.join(primary_fingerprints) or 'aucune'}"
            )

        # 3) Vérification de la signature détachée
        code, out, err = self._run_gpg(
            base + [
                "--status-fd", "1",
                "--ignore-time-conflict",
                "--ignore-valid-from",
                "--verify",
                str(signature_file),
                str(script_file),
            ],
            env
        )

        statuses = self._gpg_status_lines(out)
        names = {s[0] for s in statuses if s}
        details = (err or "").strip() or "Aucun détail fourni."

        if "BADSIG" in names:
            raise SysTeenError(
                f"SIGNATURE PGP INVALIDE : {signed_name} ne "
                "correspond pas à celui qui a été signé.\n"
                f"Si vous avez modifié {signed_name} après la "
                "signature, resignez-le puis republiez les "
                "assets.\n"
                f"Détail GPG : {details}"
            )

        if "ERRSIG" in names or "NO_PUBKEY" in names:
            raise SysTeenError(
                "La signature a été faite par une autre clé "
                "que celle configurée.\n"
                f"Détail GPG : {details}"
            )

        for refused in ("EXPSIG", "EXPKEYSIG", "REVKEYSIG"):
            if refused in names:
                raise SysTeenError(
                    f"Signature refusée ({refused}) : clé ou "
                    "signature expirée/révoquée.\n"
                    f"Détail GPG : {details}"
                )

        if "GOODSIG" not in names:
            raise SysTeenError(
                f"SIGNATURE PGP INVALIDE ({signed_name}) : "
                "la mise à jour est refusée.\n"
                f"Détail GPG : {details}"
            )

        valid = next(
            (s for s in statuses if s and s[0] == "VALIDSIG"),
            None
        )

        if valid is None or len(valid) < 2:
            raise SysTeenError(
                "GPG n'a pas confirmé la validité de la signature "
                "(VALIDSIG absent).\n"
                f"Détail GPG : {details}"
            )

        signer = valid[1].upper()
        primary = valid[10].upper() if len(valid) > 10 else signer

        if expected not in (signer, primary):
            raise SysTeenError(
                "La signature est valide mais n'a pas été faite "
                "par la clé attendue.\n"
                f"Signataire : {primary}"
            )

    def validate_downloaded_python(self, script_file, expected_version):
        try:
            source = script_file.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            raise SysTeenError(
                "La nouvelle version n'est pas "
                "un fichier Python UTF-8 valide."
            )

        try:
            compile(source, str(script_file), "exec")

        except SyntaxError as error:
            raise SysTeenError(
                "La nouvelle version contient "
                f"une erreur Python : {error}"
            )

        version_match = re.search(
            r'^\s*VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
            source,
            re.MULTILINE
        )

        if version_match is None:
            raise SysTeenError(
                "La nouvelle version ne contient "
                "pas de VERSION valide."
            )

        downloaded_version = version_match.group(1)

        if (
            self.parse_version(downloaded_version)
            != self.parse_version(expected_version)
        ):
            raise SysTeenError(
                "La version annoncée par le fichier "
                "ne correspond pas à la release GitHub."
            )

        if "PGP_PUBLIC_KEY" not in source:
            raise SysTeenError(
                "La nouvelle version ne contient pas "
                "le mécanisme de vérification PGP."
            )

        if "PGP_FINGERPRINT" not in source:
            raise SysTeenError(
                "La nouvelle version ne contient pas "
                "la vérification d'empreinte PGP."
            )

    def validate_downloaded_readme(self, readme_file):
        try:
            text = readme_file.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            raise SysTeenError(
                "Le nouveau README.md n'est pas "
                "un fichier UTF-8 valide."
            )

        if not text.strip():
            raise SysTeenError("Le nouveau README.md est vide.")

    def stage_update(self, downloaded_script):
        destination = (
            self.program_path.parent
            / ("." + self.program_path.name + ".update.new")
        )

        try:
            if destination.exists():
                destination.unlink()

            shutil.copy2(downloaded_script, destination)

            os.chmod(
                destination,
                stat.S_IMODE(self.program_path.stat().st_mode)
            )

            return destination

        except Exception as error:
            try:
                if destination.exists():
                    destination.unlink()
            except Exception:
                pass

            raise SysTeenError(
                f"Impossible de préparer la mise à jour : {error}"
            )

    def stage_readme(self, downloaded_readme):
        destination = (
            self.readme_path.parent
            / ("." + self.readme_path.name + ".update.new")
        )

        try:
            if destination.exists():
                destination.unlink()

            shutil.copy2(downloaded_readme, destination)

            os.chmod(destination, 0o644)

            return destination

        except Exception as error:
            try:
                if destination.exists():
                    destination.unlink()
            except Exception:
                pass

            raise SysTeenError(
                "Impossible de préparer le README.md : "
                f"{error}"
            )

    def restart_after_update(self):
        # En mode --maj, on s'arrête simplement après l'installation
        if not self.restart_after_install:
            return

        arguments = [sys.executable, str(self.program_path)]

        if self.script_path is not None:
            arguments.append(str(self.script_path))

            # Dans une fenêtre ouverte par :go, on garde la fenêtre
            # (sans reposer la question de lancement)
            if self.window_mode:
                arguments.extend(["--no-confirm", "--go-window"])

        try:
            os.execv(sys.executable, arguments)

        except OSError as error:
            raise SysTeenError(
                "La mise à jour a été installée, "
                "mais SysTeen n'a pas pu redémarrer : "
                f"{error}"
            )

    def install_update(self, release, target_version):
        script_asset = self.get_release_asset(
            release, UPDATE_SCRIPT_ASSET
        )

        signature_asset = self.get_release_asset(
            release, UPDATE_SIGNATURE_ASSET
        )

        readme_asset = self.get_release_asset(
            release, UPDATE_README_ASSET
        )

        readme_signature_asset = self.get_release_asset(
            release, UPDATE_README_SIGNATURE_ASSET
        )

        with tempfile.TemporaryDirectory(
            prefix="systeen-update-"
        ) as temporary_directory:

            temp_dir = Path(temporary_directory)

            downloaded_script = temp_dir / UPDATE_SCRIPT_ASSET
            downloaded_signature = temp_dir / UPDATE_SIGNATURE_ASSET
            downloaded_readme = temp_dir / UPDATE_README_ASSET
            downloaded_readme_signature = (
                temp_dir / UPDATE_README_SIGNATURE_ASSET
            )
            public_key_file = temp_dir / "systeen-update-key.asc"
            gpg_home = temp_dir / "gnupg"

            gpg_home.mkdir(mode=0o700)

            # Tolérant à l'indentation éventuelle de la clé
            public_key_file.write_text(
                "\n".join(
                    line.strip()
                    for line in PGP_PUBLIC_KEY.strip().splitlines()
                ) + "\n",
                encoding="utf-8"
            )

            print(
                "[SysTeen] Téléchargement de "
                f"SysTeen {target_version}..."
            )

            self.download_file(
                script_asset["browser_download_url"],
                downloaded_script
            )

            self.download_file(
                signature_asset["browser_download_url"],
                downloaded_signature
            )

            print("[SysTeen] Téléchargement du README.md...")

            self.download_file(
                readme_asset["browser_download_url"],
                downloaded_readme
            )

            self.download_file(
                readme_signature_asset["browser_download_url"],
                downloaded_readme_signature
            )

            print("[SysTeen] Vérification de la signature PGP...")

            self.verify_gpg_signature(
                public_key_file,
                downloaded_signature,
                downloaded_script,
                gpg_home,
                UPDATE_SCRIPT_ASSET
            )

            print("[SysTeen] Signature PGP de systeen.py valide.")

            self.verify_gpg_signature(
                public_key_file,
                downloaded_readme_signature,
                downloaded_readme,
                gpg_home,
                UPDATE_README_ASSET
            )

            print("[SysTeen] Signature PGP du README.md valide.")
            print("[SysTeen] Vérification des fichiers...")

            self.validate_downloaded_python(
                downloaded_script,
                target_version
            )

            self.validate_downloaded_readme(downloaded_readme)

            # Tout est vérifié : on prépare les deux fichiers
            staged_readme = self.stage_readme(downloaded_readme)

            try:
                staged_file = self.stage_update(downloaded_script)

            except SysTeenError:
                try:
                    if staged_readme.exists():
                        staged_readme.unlink()
                except Exception:
                    pass

                raise

        # Installation : README d'abord, programme ensuite
        try:
            os.replace(staged_readme, self.readme_path)

        except Exception as error:

            for leftover in (staged_readme, staged_file):
                try:
                    if leftover.exists():
                        leftover.unlink()
                except Exception:
                    pass

            raise SysTeenError(
                f"Impossible d'installer le README.md : {error}"
            )

        try:
            os.replace(staged_file, self.program_path)

        except Exception as error:

            try:
                if staged_file.exists():
                    staged_file.unlink()
            except Exception:
                pass

            raise SysTeenError(
                f"Impossible d'installer la mise à jour : {error}"
            )

        print("[SysTeen] Mise à jour installée avec succès.")

        if self.restart_after_install:
            print("[SysTeen] Redémarrage de SysTeen...")

        self.restart_after_update()

    def command_version(self, content):
        """
        :v
            Vérifie et installe la dernière version.

        :v 0.4.2
            Installe précisément la version demandée.
            Permet notamment un rollback.
        """

        self.check_update_configuration()

        target = content.strip()

        if target:
            target_version = self.normalize_version(target)

            target_tuple = self.parse_version(target_version)
            current_tuple = self.parse_version(VERSION)

            if target_tuple == current_tuple:
                print(
                    f"[SysTeen] Vous utilisez déjà SysTeen {VERSION}."
                )
                return

            print(
                "[SysTeen] Recherche de la release "
                f"v{target_version}..."
            )

            release = self.get_github_release(target_version)

            release_tag = release.get("tag_name")

            if not isinstance(release_tag, str):
                raise SysTeenError(
                    "La release GitHub ne possède pas de tag valide."
                )

            release_version = self.normalize_version(release_tag)

            if release_version != target_version:
                raise SysTeenError(
                    "La version demandée ne correspond "
                    "pas au tag GitHub."
                )

            print(f"[SysTeen] Installation de SysTeen {target_version}...")

            self.install_update(release, target_version)

            return

        print("[SysTeen] Recherche de la dernière version...")

        release = self.get_github_release()

        release_tag = release.get("tag_name")

        if not isinstance(release_tag, str):
            raise SysTeenError(
                "La release GitHub ne possède pas de tag valide."
            )

        latest_version = self.normalize_version(release_tag)

        current_tuple = self.parse_version(VERSION)
        latest_tuple = self.parse_version(latest_version)

        if latest_tuple == current_tuple:

            # À jour, mais README.md absent (ex. mise à jour
            # faite avec une ancienne version de SysTeen) :
            # on réinstalle la version courante, vérifiée.
            if not self.readme_path.is_file():
                print(
                    f"[SysTeen] SysTeen {VERSION} est à jour, "
                    "mais README.md est absent."
                )

                self.install_update(release, latest_version)

                return

            print(f"[SysTeen] SysTeen {VERSION} est déjà à jour.")
            return

        if latest_tuple < current_tuple:
            print(
                "[SysTeen] La dernière release GitHub "
                f"({latest_version}) est antérieure à v{VERSION}."
            )

            print("[SysTeen] Aucun downgrade automatique.")

            return

        print(
            f"[SysTeen] Nouvelle version disponible : {latest_version}"
        )

        self.install_update(release, latest_version)

    # =========================================================
    # LOOP
    # =========================================================

    def execute_inline_loop(self, count_text, command):
        if not command.strip():
            raise SysTeenError(
                ":loop doit être suivi d'une commande."
            )

        if count_text == "inf":
            while self.running:
                self.execute_inline_command(command)

            return

        try:
            count = int(count_text)

        except ValueError:
            raise SysTeenError("Nombre de répétitions invalide.")

        if count < 0:
            raise SysTeenError("Nombre négatif interdit.")

        for _ in range(count):
            if not self.running:
                break

            self.execute_inline_command(command)

    def execute_inline_command(self, command):
        command = command.strip()

        if command.startswith(":"):
            command = command[1:].strip()

        if not command:
            raise SysTeenError("Commande inline vide.")

        parts = command.split(maxsplit=1)

        name = parts[0]

        args = parts[1] if len(parts) > 1 else ""

        if name == "say":
            self.command_say(args)
            return

        if name == "cmd":
            self.command_cmd(args)
            return

        if name == "math":
            self.command_math(args)
            return

        if name == "wait":
            self.command_wait(args)
            return

        if name == "run":
            self.command_run(args)
            return

        if name == "stop":
            self.command_stop(args)
            return

        if name == "go":
            self.command_go(args)
            return

        raise SysTeenError(f"Commande inline inconnue : :{name}")

    def execute_jump_loop(self, line_index, target, count_text):
        try:
            target_line = int(target) - 1

        except ValueError:
            raise SysTeenError("Ligne cible invalide.")

        if target_line < 0 or target_line >= len(self.lines):
            raise SysTeenError("Ligne cible inexistante.")

        if count_text == "inf":
            return target_line

        try:
            count = int(count_text)

        except ValueError:
            raise SysTeenError("Nombre de boucles invalide.")

        if count < 0:
            raise SysTeenError("Nombre négatif interdit.")

        state = self.loop_states.get(line_index)

        if state is None:
            self.loop_states[line_index] = count

        if self.loop_states[line_index] <= 0:

            del self.loop_states[line_index]

            return line_index + 1

        self.loop_states[line_index] -= 1

        return target_line

    def command_loop(self, line_index, content):
        content = content.strip()

        if not content:
            raise SysTeenError(
                ":loop doit être suivi d'une commande."
            )

        parts = content.split(maxsplit=2)

        first = parts[0]

        # :loop 3 / :loop inf seul sur la ligne -> boucle en bloc
        if len(parts) == 1 and (first == "inf" or first.isdigit()):
            return self.start_block_loop(line_index, first)

        if first.startswith("L"):

            if len(parts) != 1:
                raise SysTeenError("Syntaxe : :loop L5-2")

            loop_data = first[1:]

            if "-" not in loop_data:
                raise SysTeenError(
                    "Syntaxe : :loop L5-2 ou :loop L5-inf"
                )

            target, count = loop_data.split("-", 1)

            return self.execute_jump_loop(line_index, target, count)

        if len(parts) < 2:
            raise SysTeenError(
                ":loop doit contenir une commande."
            )

        count_text = parts[0]

        command = parts[1]

        if len(parts) == 3:
            command += " " + parts[2]

        self.execute_inline_loop(count_text, command)

        return line_index + 1

    # =========================================================
    # EXECUTION D'UNE LIGNE
    # =========================================================

    def execute_line(self, line_index):
        raw_line = self.lines[line_index]

        line = raw_line.strip()

        if not line:
            return line_index + 1

        if line.startswith("#"):
            return line_index + 1

        if not line.startswith(":"):
            return line_index + 1

        command_line = line[1:].strip()

        if not command_line:
            return line_index + 1

        parts = command_line.split(maxsplit=1)

        command = parts[0]

        args = parts[1] if len(parts) > 1 else ""

        # SYSTEME
        if command == "systeen":

            option = args.strip()

            if option == "start":
                return line_index + 1

            if option == "end":
                self.write_saved_variables()

                self.running = False
                self.finished = True

                return line_index + 1

            raise SysTeenError("Commande systeen inconnue.")

        # RELANCE EN ROOT (:#)
        if command == "#":
            self.command_elevate()

            return line_index + 1

        # VERSION / MISE A JOUR
        if command == "v":
            self.command_version(args)

            return line_index + 1

        # VARIABLES
        if command == "var":
            self.command_var(args)

            return line_index + 1

        if command == "save":
            self.save_variable(args.strip())

            return line_index + 1

        # SAY
        if command == "say":
            self.command_say(args)

            return line_index + 1

        if command == "say?":
            self.command_say_input(args)

            return line_index + 1

        if command == "sayn?":
            self.command_say_yes_no(args, default_yes=True)

            return line_index + 1

        if command == "sayN?":
            self.command_say_yes_no(args, default_yes=False)

            return line_index + 1

        # MATH
        if command == "math":
            self.command_math(args)

            return line_index + 1

        # LINUX
        if command == "cmd":
            self.command_cmd(args)

            return line_index + 1

        if command == "run":
            self.command_run(args)

            return line_index + 1

        if command == "stop":
            self.command_stop(args)

            return line_index + 1

        if command == "go":
            self.command_go(args)

            return line_index + 1

        if command == "cd":
            self.command_cd(args)

            return line_index + 1

        # SUPPRESSION
        if command == "del":
            self.command_del(args, fallback_sudo=False)

            return line_index + 1

        if command == "del!":
            self.command_del(args, fallback_sudo=True)

            return line_index + 1

        if command == "rmf":
            self.command_rmf(args)

            return line_index + 1

        # FICHIERS
        if command == "add":
            self.command_add(args)

            return line_index + 1

        if command == "crea":
            raise SysTeenError(
                "La commande :crea a été renommée :add."
            )

        if command == "edit":
            return self.command_edit(line_index, args) + 1

        # WAIT
        if command == "wait":
            self.command_wait(args)

            return line_index + 1

        # SYSTEME
        if command == "re":
            self.command_reboot()

            return line_index + 1

        if command == "off":
            self.command_shutdown()

            return line_index + 1

        # IF
        if command == "if":

            result = self.parse_condition(args)

            else_line, end_line = self.find_if_structure(
                line_index + 1
            )

            if result:
                return line_index + 1

            if else_line is not None:
                return else_line + 1

            return end_line + 1

        # ELSE
        if command == "else":

            _, end_line = self.find_if_structure(line_index + 1)

            return end_line + 1

        # ELSEND
        if command == "elsend":
            return line_index + 1

        # LOOP
        if command == "loop":
            return self.command_loop(line_index, args)

        if command == "loopend":
            return self.command_loopend(line_index)

        # LECTURE / COPIE
        if command == "read":
            self.command_read(args)

            return line_index + 1

        if command == "copy":
            self.command_copy(args)

            return line_index + 1

        if command == "paste":
            self.command_paste(args)

            return line_index + 1

        if command == "pause":
            self.command_pause(args)

            return line_index + 1

        raise SysTeenError(f"Commande inconnue : :{command}")

    # =========================================================
    # VAR
    # =========================================================

    def command_var(self, args):

        if not args:
            raise SysTeenError("Syntaxe : :var add [nom]")

        if args.strip() == "sys":
            self.command_var_sys()
            return

        parts = args.split(maxsplit=2)

        if parts[0] == "add":

            if len(parts) != 2:
                raise SysTeenError("Syntaxe : :var add [nom]")

            self.create_variable(parts[1])

            return

        if parts[0] == "rm":

            if len(parts) != 2:
                raise SysTeenError("Syntaxe : :var rm [nom]")

            self.remove_variable(parts[1])

            return

        if "=" in args:

            name, value = args.split("=", 1)

            name = name.strip()
            value = value.strip()

            self.set_variable(name, self.interpolate(value))

            return

        raise SysTeenError(
            "Syntaxe : :var add [nom], "
            ":var [nom] = [valeur], "
            ":var rm [nom] "
            "ou :var sys"
        )

    # =========================================================
    # EXECUTION GENERALE
    # =========================================================

    def run(self):

        try:

            while self.running:

                line_index = 0

                self.block_stack = []

                while (
                    line_index < len(self.lines)
                    and self.running
                ):

                    try:

                        line_index = self.execute_line(line_index)

                    except SysTeenError as error:

                        print(
                            f"[SysTeen] Erreur ligne {line_index + 1} : "
                            f"{error}"
                        )

                        line_index += 1

                    except Exception as error:

                        print(
                            "[SysTeen] Erreur inattendue ligne "
                            f"{line_index + 1} : {error}"
                        )

                        line_index += 1

                if self.finished:
                    break

                continue

        except KeyboardInterrupt:

            print("\n[SysTeen] Programme interrompu.")

        finally:

            self.write_saved_variables()

            self.cleanup_variables()


# =============================================================
# MAIN
# =============================================================

def print_usage():
    print("Utilisation :")
    print("  python systeen.py fichier.st      Exécuter un script SysTeen")
    print("  python systeen.py --maj           Mettre à jour vers la dernière version")
    print("  python systeen.py --maj 0.4.2     Installer une version précise (rollback)")
    print("  python systeen.py --update        Alias de --maj")
    print("  python systeen.py --change        Modifier la protection de / et du dossier personnel")
    print("  python systeen.py --check f.st    Vérifier un script sans l'exécuter")
    print("  python systeen.py --install       Installer la commande 'systeen' (/usr/local/bin)")
    print("  python systeen.py --uninstall     Désinstaller SysTeen")
    print("  python systeen.py --readme        Afficher le README.md")
    print("  python systeen.py --version       Afficher la version installée")
    print("  python systeen.py --help          Afficher cette aide")


def format_issue(number, text):
    return f"ligne {number} : {text}" if number else text


def wait_before_closing():
    """
    Pause finale dans la fenêtre ouverte par :go, pour que
    l'utilisateur ait le temps de lire les messages avant que
    la fenêtre ne se ferme.
    """

    print()

    try:
        input(
            "[SysTeen] Script terminé. "
            "Appuyez sur Entrée pour fermer cette fenêtre..."
        )

    except (EOFError, KeyboardInterrupt):
        pass


def run_simple_mode(arguments, action):
    """
    Modes sans script ni argument : --readme, --change, --uninstall.
    `action` reçoit l'objet SysTeen.
    """

    if arguments:
        print_usage()
        sys.exit(1)

    systeen = SysTeen(None)

    try:
        action(systeen)

    except SysTeenError as error:
        print(f"[SysTeen] Erreur : {error}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n[SysTeen] Arrêt.")
        sys.exit(130)

    except BrokenPipeError:
        # sortie coupée (ex. `systeen --readme | head`) : pas une erreur
        sys.exit(0)

    except Exception as error:
        print(f"[SysTeen] Erreur inattendue : {error}")
        sys.exit(1)


def run_check_mode(arguments, invoked):
    """
    python systeen.py --check script.st
    """

    if len(arguments) != 1:
        print_usage()
        sys.exit(1)

    target = os.path.expanduser(arguments[0])

    if not Path(target).exists():
        print(
            f"[SysTeen] Erreur : il n'y a aucun fichier "
            f"nommé '{arguments[0]}'."
        )
        print(
            "[SysTeen] Si vous voulez de l'aide, tapez : "
            f"{invoked} --help"
        )
        sys.exit(1)

    try:
        systeen = SysTeen(target)

        errors = systeen.command_check()

    except SysTeenError as error:
        print(f"[SysTeen] Erreur : {error}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n[SysTeen] Arrêt.")
        sys.exit(130)

    sys.exit(1 if errors else 0)


def run_update_mode(arguments):
    """
    python systeen.py --maj [version]
    """

    if len(arguments) > 1:
        print_usage()
        sys.exit(1)

    target = arguments[0] if arguments else ""

    systeen = SysTeen(None)
    systeen.restart_after_install = False

    try:
        systeen.command_version(target)

    except SysTeenError as error:
        print(f"[SysTeen] Erreur : {error}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n[SysTeen] Arrêt.")
        sys.exit(130)

    except Exception as error:
        print(f"[SysTeen] Erreur inattendue : {error}")
        sys.exit(1)


def main():

    arguments = sys.argv[1:]

    # Nom à afficher dans les messages d'aide : "systeen" si lancé
    # par la commande installée avec --install
    invoked = (
        "systeen"
        if Path(sys.argv[0]).name == "systeen"
        else "python systeen.py"
    )

    # Options internes (non documentées) :
    #   --no-confirm : utilisée par :go et :# pour ne pas redemander
    #                  la confirmation de lancement.
    #   --go-window  : indique que ce script tourne dans la fenêtre
    #                  ouverte par :go (pause avant fermeture).
    no_confirm = "--no-confirm" in arguments
    window_mode = "--go-window" in arguments

    #   --go-depth=N : profondeur de :go transmise par :# (sudo
    #                  réinitialise l'environnement).
    cleaned = []

    for argument in arguments:
        if argument in ("--no-confirm", "--go-window"):
            continue

        if argument.startswith("--go-depth="):
            depth_value = argument.split("=", 1)[1]

            if depth_value.isdigit():
                os.environ["SYSTEEN_GO_DEPTH"] = depth_value

            continue

        cleaned.append(argument)

    arguments = cleaned

    if arguments and arguments[0] in ("--help", "-h"):
        print_usage()
        sys.exit(0)

    if arguments and arguments[0] in ("--version", "-V"):
        print(f"SysTeen {VERSION}")
        sys.exit(0)

    if arguments and arguments[0] in ("--maj", "--update"):
        run_update_mode(arguments[1:])
        sys.exit(0)

    if arguments and arguments[0] == "--readme":
        run_simple_mode(arguments[1:], lambda s: s.command_readme())
        sys.exit(0)

    if arguments and arguments[0] == "--change":
        run_simple_mode(arguments[1:], lambda s: s.command_change())
        sys.exit(0)

    if arguments and arguments[0] == "--check":
        run_check_mode(arguments[1:], invoked)

    if arguments and arguments[0] == "--install":
        run_simple_mode(arguments[1:], lambda s: s.command_install())
        sys.exit(0)

    if arguments and arguments[0] == "--uninstall":
        run_simple_mode(arguments[1:], lambda s: s.command_uninstall())
        sys.exit(0)

    if len(arguments) != 1:

        print_usage()

        sys.exit(1)

    target = arguments[0]

    # Option inconnue (ex. --truc)
    if target.startswith("-"):
        print(f"[SysTeen] Erreur : option inconnue '{target}'.")
        print(
            "[SysTeen] Pour obtenir de l'aide, tapez : "
            f"{invoked} --help"
        )
        sys.exit(1)

    # Fichier inexistant
    if not Path(os.path.expanduser(target)).exists():
        print(
            f"[SysTeen] Erreur : il n'y a aucun fichier "
            f"ou dossier nommé '{target}'."
        )
        print(
            "[SysTeen] Si vous voulez de l'aide, tapez : "
            f"{invoked} --help"
        )

        if window_mode:
            wait_before_closing()

        sys.exit(1)

    exit_code = 0

    try:

        systeen = SysTeen(os.path.expanduser(target))
        systeen.window_mode = window_mode

        # Chargement de la préférence de sécurité
        config_exists = systeen.load_security_config()

        if not config_exists and not no_confirm:
            systeen.ask_security_preference()

        # Confirmation du lancement
        # (sautée pour :go et :#, déjà confirmés par l'utilisateur)
        if not no_confirm and not systeen.confirm_script_launch():

            print("[SysTeen] Exécution annulée.")

            sys.exit(0)

        # Conseil de présentation des :if / :loop (non bloquant)
        issues = systeen.check_indentation()

        if issues:
            print()
            print(
                "[SysTeen] Conseil : décalez d'un espace chaque "
                "niveau de :if et de :loop."
            )

            for _, number, text in issues[:MAX_INDENT_WARNINGS]:
                print(f"[SysTeen]   {format_issue(number, text)}")

            hidden = len(issues) - MAX_INDENT_WARNINGS

            if hidden > 0:
                print(f"[SysTeen]   ... et {hidden} autre(s).")

            print()

        if window_mode:
            print(
                "[SysTeen] Fenêtre ouverte par :go : "
                f"{systeen.script_path.name}"
            )
            print()

        # Exécution
        systeen.run()

    except SysTeenError as error:

        print(f"[SysTeen] Erreur : {error}")

        exit_code = 1

    except KeyboardInterrupt:

        print("\n[SysTeen] Arrêt.")

        exit_code = 130

    # Fenêtre de :go : on laisse le temps de lire avant de fermer
    if window_mode:
        wait_before_closing()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
