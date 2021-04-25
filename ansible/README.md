# Ansible setup

My cluster is made of a mix of arm64 and x86_64 nodes:
- [production](hosts-production)
- [test](hosts)

The test cluster is created with lxd

## Settings

See [groups_var](groups_var/all.yaml).

Secrets encrypted with [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html). Password stored at `~/.vault_pass.txt` as comfigured at [ansible.cfg](ansible.cfg). This is the only password that needs to be remembered. All other passwords are derived from this.

If a password needs to be changed use the command `ansible-vault encrypt_string` from this folder - it will ask to enter the content to string and end with ctrd-d.

## Install

0. Create nodes
   ```
   ansible-playbook -i hosts-production proxmox_install.yaml
   ```
1. Prepare nodes
   ```
   ansible-playbook -i hosts-production hw_setup.yaml
   ```
2. Install K3S cluster
   ```
   ansible-playbook -i hosts-production k3s_install.yaml
   ```
3. Install flux2
   ```
   ansible-playbook -i hosts-production flux_install.yaml

## Update Host OS
   ```
   ansible-playbook -i hosts-production hw_update.yaml
   ```

## Update Flux

This should not be needed since there is GitHub workflow to do this automatically via PR

1. Update
   ```
   flux install --export>clusters/staging/flux-system/gotk-components.yaml
   ```

## Uninstall

1. Uninstall flux2
   ```
   flux uninstall
   ```
2. Uninstall k3s (TBD)
   ```
   ansible-playbook -i hosts-production k3s_remove.yaml
   ```
   ```
2. Delete VMs
   ```
   ansible-playbook -i hosts-production proxmox_remove.yaml
   ```

## Deprecated
- lxd
- microk8s