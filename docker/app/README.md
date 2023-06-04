# Container for bkdnojv2 `app`

1. Containerize:
```sh
bash ./scripts/dockerize.sh
```

2. Run image:
```sh
docker run --name bkdnojv2 --env-file etc/bkndojv2.env --net host bkdnoj-v2/backend
```
