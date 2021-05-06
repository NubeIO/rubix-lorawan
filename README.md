# Rubix Pi GPIO App


## Rubix Compute GPIO

## STM 32 reset
```
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, GPIO.LOW)
sleep(2)
GPIO.output(12, GPIO.HIGH)
GPIO.cleanup()

```

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
    poetry run pyinstaller run.py -n rubix-pi-gpio --clean --onefile --add-data pyproject.toml:. --add-data config:config
    ```

  The output is: `dist/rubix-pi-gpio`

## Docker build

### Build

```bash
./docker.sh
```

The output image is: `rubix-pi-gpio:dev`

### Run

```bash
docker volume create rubix-pi-gpio
docker run --rm -it -p 2001:2001 -v rubix-pi-gpio-data:/data --name rubix-pi-gpio rubix-pi-gpio:dev
```

## Deploy on Production

- Download release artifact
- Review help and start

```bash
$ rubix-pi-gpio -h
Usage: rubix-pi-gpio [OPTIONS]

Options:
  -p, --port INTEGER              Port  [default: 2001]
  -g, --global-dir PATH           Global dir
  -d, --data-dir PATH             Application data dir
  -c, --conf-dir PATH             Application config dir
  --prod                          Production mode
  -s, --setting-file TEXT         rubix-pi-gpio: setting ini file
  -l, --logging-conf TEXT         rubix-pi-gpio: logging config file
  --workers INTEGER               Gunicorn: The number of worker processes for handling requests.
  --gunicorn-config TEXT          Gunicorn: config file(gunicorn.conf.py)
  --log-level [FATAL|ERROR|WARN|INFO|DEBUG]
                                  Logging level
  -h, --help                      Show this message and exit.
```

