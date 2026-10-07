import json
import os
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
        config = json.loads(Path("/conf/entries.json").read_text())
        for directory in config.get("directories", []):
            tag = directory["tag"]
            command = ["restic", "backup", "--tag", tag]
            for pattern in directory.get("exclude", []):
                command.extend(["--exclude", pattern])
            command.extend(["--", *directory["paths"]])

            print(f"Sauvegarde de {tag}")
            result = subprocess.run(command)
            if result.returncode != 0:
                print(f"Échec pour {tag} : code {result.returncode}")

        duration = timedelta(seconds=round(time.monotonic() - start))
        print(f"Durée totale des sauvegardes : {duration}")


if __name__ == "__main__":
    Backup().run()
