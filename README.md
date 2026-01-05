# k8s-gitops - Home Cloud via Flux v2 | GitOps Toolkit

NOTE: I am moving my setup to OKD (OpenSource OpenShift) and as result the infrastructure deployment (and this readme) is still WIP.

Old setup is now archived in the [legacy k3s branch](https://github.com/angelnu/k8s-gitops/tree/legacy-k3s)

## Preparation

1. Create `centos10-cloudinit` VM
   1. create empty VM without any disk
   2. into Proxmox with the VM: wget qcow2 from https://cloud.centos.org/centos/10-stream/x86_64/images/
   3. detach and delete disk in existing template (if you are updating the template)
   4. `qm importdisk <VM id> centos.qcow2 local-lvm`
   5. `qm set <VM id> --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-<VM id>-disk-0 
   6. make the VM a template
2. Create secrets.auto.tfvars

   ```ini
   api_url                = "https://pve1.angelnu.com:8006/api2/json"
   user                   = "root@pam"
   passwd                 = "Proxmox password"
   ansible_pwd            = "password for ansible user at service VM"
   ansible_ssh_public_key = "public key to ssh into service VM"
   ```

3. Adjust other settings into the [vars folder](vars)
4. Create following DNS records:

   ```yaml
   - type: A
     name: okd-service.homelab # okd-service.<domain>
     value: 192.168.5.250
   - type: A # For each cluster
     name: api.prod.homelab  # api.<cluster name>.<domain>
     value: 192.168.5.1      # apiVip in vars/clusters.yaml 
   - type: A # For each cluster
     name: '*.apps.prod.homelab'  # *.apps.<cluster name>.<domain>
     value: 192.168.5.2           # ingressVip in vars/clusters.yaml 
   ```

## How to install

1. Create service virtual machine

   ```shell
   terraform init  # Only first time
   terraform workspace select default
   terraform apply
   ssh ansible@192.168.251.196 # To accept ssh key
   ansible-playbook setup-linux.yaml
   ```

2. Create virtual machines for cluster prod - they will automatically install

   ```shell
   terraform workspace create prod # Only first time
   terraform workspace select prod
   terraform apply
   ```

3. Wait for cluster to install - this takes 30-60 minutes for my cluster. The following command logs install status and prints credentials

   ```shell
   ssh ansible@192.168.251.196 openshift-install agent wait-for install-complete --dir=clusters/prod/install_dir
   ```

4. Next steps:
   - OKD console is available at https://console-openshift-console.apps.prod.homelab
     - you can connect with user `kubeadmin` and the password from the previous step
     - credentials (user and password) stored in the service VM at `/home/ansible/clusters/prod/install-dir/auth`
   - Service node has a webb interface at https://192.168.251.196:9090/ (or https://okd-service.homelab - replace homelab with your domain)

## ToDos

- [x] Automate further:
- [ ] Install flux
- [x] Open to outside (install cloudflare operator)
- [x] Check I can install 2 clusters in parallel (one for test)
- [ ] Check how to recover cluster