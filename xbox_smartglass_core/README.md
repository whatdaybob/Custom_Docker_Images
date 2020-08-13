# whatdaybob/xbox-smartglass-core

SmartGlass Core protocol python library now in a docker container [xbox-smartglass-core](https://pypi.org/project/xbox-smartglass-core/).

This is an unofficial build. For official things please refer to the project here [xbox-smartglass-core-python](https://github.com/OpenXbox/xbox-smartglass-core-python).

## Usage
### Docker
``` bash
docker create \
  --name=xboxrestapi \
  -e SERVER=127.0.0.1 \
  -e PORT=5557 \
  -p 5557:5557 \
  --restart unless-stopped \
  whatdaybob/xbox-smartglass-core
```
### Docker Compose
``` yml
version: '3.4'
services:
  xboxrestapi:
    container_name: xboxrestapi
    image: whatdaybob/xbox-smartglass-core
    environment: [
      "SERVER=0.0.0.0",
      "PORT=5557"
    ]
    volumes: [
      '/etc/localtime:/etc/localtime:ro'
    ]
    restart: always
    ports: ['5557:5557']
```


| Parameter | Function |
|---------------------|---------------------------------------------------------|
| -e PORT=5557 | Sets the port to listen on (default 5557) |
| -e SERVER=127.0.0.1 | Sets the IP the server will bind to (default 127.0.0.1) |

If i helped in anyway and you would like to help me, consider donating a lovely beverage with the below.

<a href="https://www.buymeacoffee.com/whatdaybob" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/lato-black.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>
