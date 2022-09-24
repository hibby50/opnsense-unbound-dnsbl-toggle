# opnsense-unbound-dnsbl-toggle
A very basic flask webapp to enable and disable to Unbound adblock feature in OPNsense.

Must set env vars for:
OPNSENSE_API_KEY
OPNSENSE_API_SECRET
OPNSENSE_API_HOSTNAME

Example:
```
podman run -p 8080:80 -e OPNSENSE_API_KEY=<key> -e OPNSENSE_API_SECRET=<secret> -e OPNSENSE_API_HOSTNAME=<your router ip or hostname> hibby50/opnsense-unbound-dnsbl-toggle
```

Prebuild container is here https://hub.docker.com/repository/docker/hibby50/opnsense-unbound-dnsbl-toggle
