import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Backup:
    def run(self):
        backup_time = datetime.strptime(os.environ["BACKUP_TIME_UTC"], "%H:%M").time()
        while True:
            now = datetime.now(timezone.utc)
            next_run = now.replace(hour=backup_time.hour, minute=backup_time.minute, second=0, microsecond=0)
            while next_run <= now:
                next_run += timedelta(days=1)

            print(f"Prochain lancement : {next_run.isoformat()}")
            time.sleep((next_run - now).total_seconds())
            self.backup()

    def backup(self):
        start = time.monotonic()
        print(f"\n{'=' * 60}\nDébut du cycle : {datetime.now(timezone.utc).isoformat()}\n{'=' * 60}")
        config = json.loads(Path("/conf/entries.json").read_text())
        for directory in config.get("directories", []):
            tag = directory["tag"]
            command = ["restic", "backup", "--tag", tag]
            for pattern in directory.get("exclude", []):
                command.extend(["--exclude", pattern])
            command.extend(["--", *directory["paths"]])

            print(f"\n{'-' * 60}\nFichiers : {tag}\n{'-' * 60}")
            result = subprocess.run(command)
            if result.returncode != 0:
                print(f"Échec pour {tag} : code {result.returncode}")

        for database in config.get("databases", []):
            self.backup_database(database)

        duration = timedelta(seconds=round(time.monotonic() - start))
        print(f"\n{'=' * 60}\nFin du cycle — Durée totale : {duration}\n{'=' * 60}\n")

    def backup_database(self, database):
        tag = database["tag"]
        print(f"\n{'-' * 60}\nBase de données : {tag}\n{'-' * 60}")
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", tag)[:80]
        digest = hashlib.sha256(tag.encode()).hexdigest()
        dump = Path(f"/{name}_{digest}.sql")

        variables = [database[key] for key in ("db_name_env", "db_user_env", "db_pass_env")]
        if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", variable) for variable in variables):
            print(f"Échec pour {tag} : nom de variable d'environnement invalide")
            return
        db_name, db_user, db_pass = variables
        command = (
            f'MYSQL_PWD="${{{db_pass}:?}}" exec mariadb-dump '
            f'--user="${{{db_user}:?}}" --single-transaction --quick '
            f'--routines --events --triggers --databases "${{{db_name}:?}}"'
        )

        print(f"Dump de {tag}")
        created = False
        try:
            with dump.open("xb") as output:
                created = True
                result = subprocess.run(
                    ["docker", "exec", database["container"], "sh", "-c", command],
                    stdout=output,
                )
            if result.returncode != 0:
                print(f"Échec du dump pour {tag} : code {result.returncode}")
                return

            print(f"Sauvegarde du dump de {tag}")
            result = subprocess.run(["restic", "backup", "--tag", tag, "--", str(dump)])
            if result.returncode != 0:
                print(f"Échec pour {tag} : code {result.returncode}")
        except OSError as error:
            print(f"Échec pour {tag} : {error}")
        finally:
            if created:
                dump.unlink(missing_ok=True)


if __name__ == "__main__":
    Backup().run()
