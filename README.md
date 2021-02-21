<img src="https://camo.githubusercontent.com/bd0df216af51c1525f14e62155608e448562cb4033554e001a0ac2009e545aec/68747470733a2f2f726173706265726e657465732e6769746875622e696f2f696d672f6c6f676f2e737667" align="left" width="144px" height="144px"/>

#### k8s-gitops - Home Cloud via Flux v2 | GitOps Toolkit
> GitOps state for my cluster using flux v2

[![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg?maxAge=60&style=flat-square)](https://discord.gg/DNCynrJ)
[![test](https://github.com/angelnu/k8s-gitops/workflows/test/badge.svg)](https://github.com/angelnu/k8s-gitop/workflows/actions)
[![e2e](https://github.com/angelnu/k8s-gitops/workflows/e2e/badge.svg)](https://github.com/angelnu/k8s-gitop/actions)
[![renovate](https://github.com/angelnu/k8s-gitops/workflows/renovate/badge.svg)](https://github.com/angelnu/k8s-gitop/workflows/renovate/actions)
[![update-flux](https://github.com/angelnu/k8s-gitops/workflows/update-flux/badge.svg)](https://github.com/angelnu/k8s-gitop/workflows/update-flux/actions)
<br />

Microk8s multi-arch highly available cluster installed via [Ansible](ansible/README.md).

The cluster is designed to allow tearing it completely without any data lost.

* Applications
  * [base/default](apps/base/default)
  * [base/kube-system](apps/base/kube-system)
  * [production global settings](clusters/production/apps.yaml)
  * [production overlay](apps/production)
  * [staging global settings](clusters/staging/apps.yaml)
  * [staging overlay](apps/staging)
* Substitutions
  * [global settings](clusters/settings.yaml)
  * [production global settings](clusters/production/settings.yaml)
  * [staging global settings](clusters/staging/settings.yaml)
* Operators
  * [sources](operators/sources)
  * [cert-manager](operators/cert-manager)
  * [postgres](operators/postgres)
* Infrastructure
  * [base/cert-manager](infrastructure/base/cert-manager)
  * [base/flux-system](infrastructure/base/flux-system)
  * [base/nginx](infrastructure/base/nginx)
  * [base/postgres](infrastructure/base/postgres)
  * [production overlay](infrastructure/production)
  * [staging overlay](infrastructure/staging)
* Clusters:
  * [production](clusters/production)
  * [staging](clusters/staging)
* Persistance:
  * Cluster configuration:
    * [flux2](https://github.com/fluxcd/flux2) - Keep cluster in sync with this repo
  * Secrets - see [Secret Management](##-Secret-Management)::
    - [Ansible Vault](ansible) - Ansible, Deployment
    - [SOPS](##-Secret-Management) - Flux, K8S GitOps
  * Files:
    * Fast but depending on Sinology NAS: nfs
    * Slower but replicated: custom glusterfs containers + Hekiti + custom chart to generate PVs, PVCs and backup cronjobs to the NAS.
  * Databases:
    * postgres: 2 instances deployed via [Zalando´s Postgres Operator](https://github.com/zalando/postgres-operator)


## Installation

### Install / Update / Uninstall

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

## Useful commands

- Delete stuck objects (NSs, PVs, PVCs)
  ```
  kubectl patch <object type> <object name> -p '{"metadata":{"finalizers": []}}' --type=merge
  ```


## :handshake:&nbsp; Community

This cluster in inspired by the work of others shared at [awesome-home-kubernetes](https://github.com/k8s-at-home/awesome-home-kubernetes), specially [billimek´s setup](https://github.com/billimek/k8s-gitops/).

There is also an active [k8s@home Discord](https://discord.gg/7PbmHRK) for this community.