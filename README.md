<img src="https://camo.githubusercontent.com/bd0df216af51c1525f14e62155608e448562cb4033554e001a0ac2009e545aec/68747470733a2f2f726173706265726e657465732e6769746875622e696f2f696d672f6c6f676f2e737667" align="left" width="144px" height="144px"/>

#### k8s-gitops - Home Cloud via Flux v2 | GitOps Toolkit
> GitOps state for my cluster using flux v2

[![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg?maxAge=60&style=flat-square)](https://discord.gg/DNCynrJ)

<br />

Microk8s multi-arch highly available cluster installed via [Ansible](ansible/README.md).

The cluster is designed to allow tearing it completely without any data lost.

** WIP ** - STILL MOVING FROM [PREVIOUS SETUP](https://github.com/angelnu/homecloud).

* Apps:
  * [gitea](https://gitea.io) - Internal git server (keep backups of my GitHub projects)
  * [drone](https://www.drone.io/) - CI with a native Kubernetes Runner
  * [home-assistant](https://github.com/home-assistant/core) - Home Automation
  * [RaspberryMatic](https://github.com/jens-maus/RaspberryMatic) - Homematic Home Automation platform
  * [code-server](https://github.com/cdr/code-server) - ~~Visual Studio~~ Code Server
* System:
  * [flux2](https://github.com/fluxcd/flux2) - Keep cluster in sync with this repo
  * [nginx-ingress](https://github.com/kubernetes/ingress-nginx) - Ingress controller
  * [cert-manager](https://github.com/jetstack/cert-manager) - Automated letsencrypt broker
  * [metallb](https://github.com/metallb/metallb) - Load-balancer for bare-metal
* Persistance:
  * Secrets stored in this git reposory wrapped - see [Secret Management](##-Secret-Management).
  * Files:
    * Fast but depending on Sinology NAS: nfs
    * Slower but replicated: custom glusterfs containers + Hekiti + custom chart to generate PVs, PVCs and backup cronjobs to the NAS.
  * Cluster postgres: 2 instances deployed via [Zalando´s Postgres Operator](https://github.com/zalando/postgres-operator)


## Installation

### Install

Installed via [Ansible](ansible/README.md).

The cluster is designed to allow tearing the cluster completly without any data lost. 

## Secret Management

Master secret is stored in [Ansible Vault](ansible/README.md).

Kubernetes passwords and secrets encrypted with [mozilla SOPS](https://github.com/mozilla/sops) which it is [supported out of the box in Flux2](https://toolkit.fluxcd.io/guides/mozilla-sops/).

GPG key is deployed via [Ansible](ansible/README.md). Its hash must be kept in sync with [.sops.yaml](.sops.yaml).

Based on [Vaskozl](https://github.com/Vaskozl/home-infra) I use a [pre-commit hook](scripts/find-unencrypted-secrets.sh) to ensure that secrets are never pushed unencrypted. The hook is deployed by running `cd scripts; ./install_git_hooks.sh`

To encrypt files with secrets use:

```
sops -e -i my-secret.yaml # Initial encrypt
sops my-secret.yaml # To edit it directly in you $EDITOR
```