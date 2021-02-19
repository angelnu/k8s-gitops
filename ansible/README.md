# Ansible setup

My cluster is made of a mix of arm64 and x86_64 nodes:
- [production](hosts-production)
- [test](hosts)

## Settings

See [groups_var](groups_var/all.yaml).

Secrets encrypted with [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html). Password stored at `~/.vault_pass.txt` as comfigured at [ansible.cfg](ansible.cfg). This is the only password that needs to be remembered. All other passwords are derived from this.

## Install

0. Reset Host OS UUID (needed in some devices once after Host OS install)
   ```
   ansible-playbook -i hosts-production hw_reset.yaml
   ```
1. Prepare nodes
   ```
   ansible-playbook -i hosts-production hw_setup.yaml
   ```
2. Install MicroK8S cluster
   ```
   ansible-playbook -i hosts-production microk8s_install.yaml
   ```
3. Install flux2
   ```
   ansible-playbook -i hosts-production flux_install.yaml
   ```

## Update Host OS
   ```
   ansible-playbook -i hosts-production hw_update.yaml
   ```
## Update Flux

1. Update staging
   ```
   flux install --export>clusters/staging/flux-system/gotk-components.yaml
   ```
2. Update production
   ```
   flux install --export>clusters/production/flux-system/gotk-components.yaml
   ```

## Uninstall

1. Uninstall flux2
   ```
   flux uinstall
   ```
2. Uninstall flux2
   ```
   ansible-playbook -i hosts-production microk8s_reset.yaml
   ```