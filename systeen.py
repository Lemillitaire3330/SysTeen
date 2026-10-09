#!/usr/bin/env python3

import ast
import getpass
import json
import operator
import os
import platform
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


VERSION = "0.5.2"

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


class SysTeenError(Exception):
    pass


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
    # =========================================================
    # INITIALISATION
    # =========================================================

    def __init__(self, script_path=None):
        # Chemin du programme SysTeen lui-même (cible des mises à jour)
        self.program_path = Path(__file__).resolve()

        # Redémarrer SysTeen après une mise à jour réussie
        # (désactivé en mode "python systeen.py --maj")
        self.restart_after_install = True

        self.update_fingerprint = None

        if script_path is None:
            # Mode sans script : python systeen.py --maj
            self.script_path = None
            self.lines = []
            self.variables = {}
            self.saved_variables = set()
            self.running = True
            self.finished = False
            self.loop_states = {}
            self.save_file = None
            self.config_dir = Path.home() / ".config" / "systeen"
            self.config_file = self.config_dir / "config.json"
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

        # Configuration persistante
        self.config_dir = Path.home() / ".config" / "systeen"
        self.config_file = self.config_dir / "config.json"

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
        home = Path.home().resolve()

        return resolved == root or resolved == home

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

        pattern = re.compile(r"\$([A-Za-z_][A-Za-z0-9_.]*)")

        def replace_variable(match):
            name = match.group(1)

            if name not in self.variables:
                raise SysTeenError(
                    f"Variable-404 : la variable '{name}' n'existe pas."
                )

            return str(self.variables[name])

        return pattern.sub(replace_variable, text)

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
        condition = condition.strip()

        if condition.startswith("exist "):
            target = condition[6:].strip()

            if not target:
                raise SysTeenError(
                    "Syntaxe : :if exist [variable/fichier]"
                )

            if target.startswith("$"):
                return target[1:] in self.variables

            target = self.interpolate(target)

            return self.condition_path(target).exists()

        if condition.startswith("not exist "):
            target = condition[10:].strip()

            if not target:
                raise SysTeenError(
                    "Syntaxe : :if not exist [variable/fichier]"
                )

            if target.startswith("$"):
                return target[1:] not in self.variables

            target = self.interpolate(target)

            return not self.condition_path(target).exists()

        if condition.startswith("empty "):
            target = condition[6:].strip()

            if not target.startswith("$"):
                raise SysTeenError("empty doit utiliser une variable.")

            return str(self.require_variable(target[1:])) == ""

        if condition.startswith("notempty "):
            target = condition[9:].strip()

            if not target.startswith("$"):
                raise SysTeenError("notempty doit utiliser une variable.")

            return str(self.require_variable(target[1:])) != ""

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

            if not left.startswith("$"):
                raise SysTeenError(
                    "Une condition doit utiliser une variable."
                )

            value = str(self.require_variable(left[1:]))

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

        if not left.startswith("$"):
            raise SysTeenError(
                "Une condition doit utiliser une variable."
            )

        variable_name = left[1:]

        if not variable_name:
            raise SysTeenError("Nom de variable manquant.")

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
    # CREA
    # =========================================================

    def command_crea(self, content):
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

        if not filename:
            raise SysTeenError("Nom de fichier manquant.")

        full_content, last_line = self.find_edit_text(
            line_index, content
        )

        filename = self.interpolate(filename)
        full_content = self.interpolate(full_content)

        path = self.safe_path(filename)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(full_content, encoding="utf-8")

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

    def command_cmd(self, content):
        command = self.interpolate(content.strip())

        if not command:
            raise SysTeenError("Commande Linux manquante.")

        print(
            "[SysTeen] Attention : SysTeen va executer "
            "une commande dans votre terminal."
        )

        print(f"[SysTeen] commande : {command}")

        subprocess.run(command, shell=True)

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
    def _check_signature_file(signature_file):
        """Détecte les erreurs classiques sur le fichier .asc."""
        head = Path(signature_file).read_bytes()[:200].lstrip()

        if not head:
            raise SysTeenError("Le fichier de signature est vide.")

        if head.startswith(b"-----BEGIN PGP SIGNED MESSAGE-----"):
            raise SysTeenError(
                "Le fichier .asc est une signature 'clearsign' "
                "et non une signature détachée.\n"
                "Recréez-la avec : "
                "gpg --armor --detach-sign systeen.py"
            )

        if head.startswith(b"-----BEGIN PGP MESSAGE-----"):
            raise SysTeenError(
                "Le fichier .asc contient un message PGP (--sign) "
                "et non une signature détachée.\n"
                "Recréez-la avec : "
                "gpg --armor --detach-sign systeen.py"
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
        gpg_home
    ):
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

        self._check_signature_file(signature_file)

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
                "SIGNATURE PGP INVALIDE : le fichier ne correspond "
                "pas à celui qui a été signé.\n"
                "Si vous avez modifié systeen.py après la signature, "
                "resignez-le puis republiez les deux assets.\n"
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
                "SIGNATURE PGP INVALIDE : la mise à jour "
                "est refusée.\n"
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

    def restart_after_update(self):
        # En mode --maj, on s'arrête simplement après l'installation
        if not self.restart_after_install:
            return

        arguments = [sys.executable, str(self.program_path)]

        if self.script_path is not None:
            arguments.append(str(self.script_path))

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

        with tempfile.TemporaryDirectory(
            prefix="systeen-update-"
        ) as temporary_directory:

            temp_dir = Path(temporary_directory)

            downloaded_script = temp_dir / UPDATE_SCRIPT_ASSET
            downloaded_signature = temp_dir / UPDATE_SIGNATURE_ASSET
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

            print("[SysTeen] Vérification de la signature PGP...")

            self.verify_gpg_signature(
                public_key_file,
                downloaded_signature,
                downloaded_script,
                gpg_home
            )

            print("[SysTeen] Signature PGP valide.")
            print("[SysTeen] Vérification du fichier Python...")

            self.validate_downloaded_python(
                downloaded_script,
                target_version
            )

            staged_file = self.stage_update(downloaded_script)

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
        if command == "crea":
            self.command_crea(args)

            return line_index + 1

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

                while (
                    line_index < len(self.lines)
                    and self.running
                ):

                    try:

                        line_index = self.execute_line(line_index)

                    except SysTeenError as error:

                        print(f"[SysTeen] Erreur : {error}")

                        line_index += 1

                    except Exception as error:

                        print(
                            "[SysTeen] Erreur inattendue : "
                            f"{error}"
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
    print("  python systeen.py --version       Afficher la version installée")
    print("  python systeen.py --help          Afficher cette aide")


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

    if arguments and arguments[0] in ("--help", "-h"):
        print_usage()
        sys.exit(0)

    if arguments and arguments[0] in ("--version", "-V"):
        print(f"SysTeen {VERSION}")
        sys.exit(0)

    if arguments and arguments[0] in ("--maj", "--update"):
        run_update_mode(arguments[1:])
        sys.exit(0)

    if len(arguments) != 1:

        print_usage()

        sys.exit(1)

    try:

        systeen = SysTeen(arguments[0])

        # Chargement de la préférence de sécurité
        config_exists = systeen.load_security_config()

        if not config_exists:
            systeen.ask_security_preference()

        # Confirmation du lancement
        if not systeen.confirm_script_launch():

            print("[SysTeen] Exécution annulée.")

            sys.exit(0)

        # Exécution
        systeen.run()

    except SysTeenError as error:

        print(f"[SysTeen] Erreur : {error}")

        sys.exit(1)

    except KeyboardInterrupt:

        print("\n[SysTeen] Arrêt.")

        sys.exit(130)


if __name__ == "__main__":
    main()
