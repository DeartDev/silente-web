# Despliegue en nomadservernw

Procedimiento para publicar la web en `https://silente.nordirwork.com` según el contrato de dockerización de `nomad_server` (anexo 96; copia en [`docs/referencias/nomad-96-contrato-de-dockerizacion.md`](../../docs/referencias/nomad-96-contrato-de-dockerizacion.md)). Spec §8.

## Qué hay aquí

| Archivo | Para qué |
|---|---|
| `docker-compose.yml` | El compose de producción. Se copia a `/srv/nomad/silente/` |
| `.env.example` | Host y red, sin secretos. Se copia como `.env` con permisos 600 |

No hay gancho de volcado: la web no tiene base de datos (regla 9).

## Estructura en el servidor

```text
/srv/nomad/silente/
├── docker-compose.yml       copia de deploy/nomad/docker-compose.yml
├── .env                     copia de .env.example, 600, no versionado
├── datos/                   vacío: la web no escribe nada
└── codigo/                  este repositorio (público: git pull sin credenciales)
```

> `git pull` actualiza `codigo/`, **no** el `docker-compose.yml` de arriba. Si cambia, hay que volver a copiarlo y pasar otra vez `revisar_proyecto.sh`.

## Antes del primer despliegue

1. Comprobar que el host y el router siguen libres:

   ```sh
   grep -rn 'Host(' /srv/nomad/*/docker-compose.yml
   grep -rn 'routers.silente' /srv/nomad/*/docker-compose.yml
   ```

2. Preparar el directorio:

   ```sh
   sudo mkdir -p /srv/nomad/silente/datos
   cd /srv/nomad/silente
   git clone https://github.com/DeartDev/silente-web.git codigo
   cp codigo/deploy/nomad/docker-compose.yml .
   cp codigo/deploy/nomad/.env.example .env && chmod 600 .env
   ```

## Despliegue (spec §8.6)

```sh
cd ~/nomad_server
./scripts/revisar_proyecto.sh silente           # en verde
./scripts/11_cloudflared.sh --ruta silente      # solo la primera vez
dig +short silente.nordirwork.com               # → IP de Cloudflare
./scripts/deploy.sh silente --check
./scripts/deploy.sh silente
```

Después:

- Desde fuera, `200` en `/`, `/privacidad` y `/terminos`, con las cabeceras `x-frame-options`, `x-content-type-options`, `referrer-policy` y `content-security-policy`. También se puede pasar `SILENTE_URL=https://silente.nordirwork.com python3 -m unittest tests.test_http`.
- Activar HSTS en Cloudflare para el subdominio, sin `includeSubDomains`.
- Crear un monitor HTTP(s) en Uptime Kuma: `https://silente.nordirwork.com/salud`, cada 60 s.

## Nueva versión

1. Subir `VERSION` y la etiqueta `image:` de `docker-compose.yml` a la misma versión.
2. Tras fusionar, volver a copiar `docker-compose.yml` al servidor y ejecutar `./scripts/deploy.sh silente`.

## Verificado en local

Con la estructura del servidor simulada (`codigo/` enlazado a este repositorio y `.env` en 600), `revisar_proyecto.sh` pasa todas las reglas salvo el registro DNS, que solo existe en el servidor. El contenedor se ha levantado con el mismo endurecimiento que en producción: raíz de solo lectura, `/tmp` en tmpfs, sin capacidades y con `no-new-privileges`. Ver el `compose.yaml` de la raíz.
