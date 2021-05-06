# Rubix LoRaWan Wrapper Around Chripstack

## Running in development

- Use [`poetry`](https://github.com/python-poetry/poetry) to manage dependencies
- Simple script to install

    ```bash
    ./setup.sh
    ```

- Join `venv`


    ```
        poetry shell
    ```

- Build local binary

    ```bash
    poetry run pyinstaller run.py -n rubix-lorawan --clean --onefile --add-data pyproject.toml:. --add-data config:config
    ```

  The output is: `dist/rubix-lorawan`

## Docker build

### Build

```bash
./docker.sh
```

The output image is: `rubix-lorawan:dev`

### Run

```bash
docker volume create rubix-lorawan
docker run --rm -it -p 2002:2002 -v rubix-lorawan-data:/data --name rubix-lorawan rubix-lorawan:dev
```

## Deploy on Production

- Download release artifact
- Review help and start

```bash
$ rubix-lorawan -h
Usage: rubix-lorawan [OPTIONS]

Options:
  -p, --port INTEGER              Port  [default: 2002]
  -g, --global-dir PATH           Global dir
  -d, --data-dir PATH             Application data dir
  -c, --conf-dir PATH             Application config dir
  --prod                          Production mode
  -s, --setting-file TEXT         rubix-lorawan: setting ini file
  -l, --logging-conf TEXT         rubix-lorawan: logging config file
  --workers INTEGER               Gunicorn: The number of worker processes for handling requests.
  --gunicorn-config TEXT          Gunicorn: config file(gunicorn.conf.py)
  --log-level [FATAL|ERROR|WARN|INFO|DEBUG]
                                  Logging level
  -h, --help                      Show this message and exit.
```

