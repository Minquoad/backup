# BACKUP

## initialisation

```bash
docker compose run --rm --build --entrypoint restic restic init
```

## listing

Lister les stapshots avec un filtre sur le tag "example"

```bash
docker compose exec restic restic snapshots --tag example
```

Lister les ficheirs présents dans la snapshot d'ID "bb4f131a"

```bash
docker compose exec restic restic ls bb4f131a
```

## recover

Récupérer tout le snapshot dans ./recover :

```bash
docker compose exec restic restic restore bb4f131a --target /recover
```

Pour récupérer un fichier précis :

```bash
docker compose exec restic restic restore bb4f131a \
  --target /recover \
  --include /sources/example/nom_du_fichier
```
