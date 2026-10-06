import os
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Backup:
    def run(self):
        backup_time = datetime.strptime(os.getenv("BACKUP_TIME_UTC", "04:00"), "%H:%M").time()
        while True:
            now = datetime.now(timezone.utc)
            next_run = now.replace(hour=backup_time.hour, minute=backup_time.minute, second=0, microsecond=0)
            while next_run <= now:
                next_run += timedelta(days=1)

            print(f"Prochain lancement : {next_run.isoformat()}")
            time.sleep((next_run - now).total_seconds())
            self.backup()

    def backup(self):
        for source in sorted(Path("/sources").iterdir()):
            if not source.is_dir():
                continue

            print(f"Sauvegarde de {source.name}")
            result = subprocess.run(
                ["restic", "backup", str(source), "--tag", source.name]
            )
            if result.returncode != 0:
                print(f"Échec pour {source.name} : code {result.returncode}")


if __name__ == "__main__":
    Backup().run()
