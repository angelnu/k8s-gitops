# Unifi

## manual adopting

1. `ssh -oHostKeyAlgorithms=+ssh-dss ubnt@<new device IP>`
   - password: `ubnt`
2. `set-inform http://unifi.home.prod.angelnu.com:8080/inform`

## Already addopted device

1. `ssh angel@<new device IP>`
   - password (only if missing ssh key): check in devices -> settings