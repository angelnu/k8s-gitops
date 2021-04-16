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
## Install (test)

1. Prepare nodes
   ```
   ansible-playbook -i hosts-production lxd_install.yaml
   ANSIBLE_HOST_KEY_CHECKING=0 ansible-playbook -i hosts-test hw_setup.yaml
   ```
2. Install MicroK8S cluster
   ```
   ANSIBLE_HOST_KEY_CHECKING=0 ansible-playbook -i hosts-test microk8s_install.yaml
   ```
3. Install flux2
   ```
   ANSIBLE_HOST_KEY_CHECKING=0 ansible-playbook -i hosts-test flux_install.yaml
   ```

## Update Host OS (prod)
   ```
   ansible-playbook -i hosts-production hw_update.yaml
   ```
## Update Host OS (test)
   ```
   ANSIBLE_HOST_KEY_CHECKING=0 ansible-playbook -i hosts-test hw_update.yaml
   ```
## Update Flux (prod)

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
2. Uninstall microk8s
   ```
   ansible-playbook -i hosts-production microk8s_reset.yaml
   ```
## Uninstall (test)

1. Uninstall microk8s
   ```
   ANSIBLE_HOST_KEY_CHECKING=0 ansible-playbook -i hosts-test microk8s_reset.yaml
   ```
2. Uninstall LXD
   ```
   ansible-playbook -i hosts-production lxd_remove.yaml
   ```