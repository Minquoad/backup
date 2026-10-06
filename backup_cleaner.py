import argparse
import os
import re
from datetime import datetime, timezone


class BackupCleaner:

    @staticmethod
    def run(dir_path: str, gap_pow: int = 4):
        path_day_map: dict[str, int] = {}
        for entry in os.scandir(dir_path):
            if os.path.isfile(entry):
                date_str = match = re.search(r'\d{4}-\d{2}-\d{2}', entry.name)
                if date_str:
                    timestamp = datetime.strptime(match.group(), "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
                    path_day_map[entry.path] = round(timestamp / (3600 * 24))

        paths_to_keep: set[str] = set()

        for p in range(0, 20):  # avec 20 on est tranquil jusqu'à l'an 3405
            gap = gap_pow ** p
            gap_paths = []
            for path, day in path_day_map.items():
                if day % gap == 0:
                    gap_paths.append(path)

            gap_paths.sort(key=lambda path: -path_day_map[path])
            for path in gap_paths[:2]:
                paths_to_keep.add(path)

        for path in path_day_map.keys():
            if path not in paths_to_keep:
                os.remove(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean backups')
    parser.add_argument('path', nargs='?', default='.', help='Path to backup directory (default: .)')
    args = parser.parse_args()
    BackupCleaner.run(args.path)
