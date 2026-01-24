##############################
# Creating Service machine.
##############################
resource "proxmox_vm_qemu" "cloudinit-nodes" {
  count       = terraform.workspace == "default" ? 1 : 0
  name        = local.service.name
  vmid        = local.service.vmid
  target_node = local.service.target_host
  clone       = local.service.os
  full_clone  = true
  boot        = "order=scsi0;net0" # "c" by default, which renders the coreos35 clone non-bootable. "cdn" is HD, DVD and Network
  agent       = 1
  tags        = "okd,service"
  vm_state    = local.service.boot # start once created


  cpu {
    cores   = local.service.cores
    limit   = 0
    numa    = false
    sockets = 1
    type    = "host"
    units   = 0
    vcores  = 0
  }
  memory = local.service.ram
  scsihw = "virtio-scsi-pci"
  #bootdisk = "scsi0"
  hotplug = 0

  disks {
    scsi {
      scsi0 {
        disk {
          storage = "local-lvm"
          size    = "20G"
          format  = "raw"
        }
      }
    }
    ide {
      ide0 {
        cloudinit {
          storage = "local-lvm"
        }
      }
    }
  }
  network {
    id      = 0
    model   = "virtio"
    bridge  = local.network.bridge
    tag     = local.network.vlan
    macaddr = local.service.macaddr
  }

  # cloud-init config 
  cicustom   = "vendor=local:snippets/centos-qemu-agent.yml" # This installs the Qemu Guest Agent. Install the file in /var/lib/vz/snippets on proxmox host
  ciupgrade  = true
  nameserver = local.network.resolver
  ipconfig0  = "ip=${local.service.ip}/${local.network.lab_subnet},gw=${local.network.lab_gw}"
  skip_ipv6  = true
  ciuser     = var.ansible_user
  cipassword = var.ansible_pwd
  sshkeys    = var.ansible_ssh_public_key

  startup_shutdown {
    order            = -1
    shutdown_timeout = -1
    startup_delay    = -1
  }
}

###################################
# Creating all PXE/ISO booting devices.
###################################

resource "proxmox_virtual_environment_download_file" "okd_agent_iso" {
  count        = (terraform.workspace == "default" || local.main.ipxe.enabled) ? 0 : 1
  content_type = "iso"
  datastore_id = "cephfs"
  node_name    = "pve1"
  provider     = proxmox-bpg
  url          = format("http://%s:8080/%s/agent.x86_64.iso", local.main.service.ip, terraform.workspace)
  file_name    = format("okd-agent-%s.iso", terraform.workspace)
}

resource "proxmox_vm_qemu" "pxe-nodes" {
  for_each    = local.all_pxe_nodes
  name        = format("%s-%s-%s", var.vm_name_prefix, terraform.workspace, each.key)
  vmid        = each.value.vmid
  target_node = each.value.target_host

  dynamic "disk" {
    for_each = local.main.ipxe.enabled ? [] : [1]
    content {
      slot = "ide2"
      type = "cdrom"
      iso  = format("cephfs:iso/%s", proxmox_virtual_environment_download_file.okd_agent_iso[0].file_name)
    }
  }

  boot                   = format("order=scsi0;%s", local.main.ipxe.enabled ? "net0" : "ide2")
  agent                  = 0
  tags                   = format("okd,%s,%s", terraform.workspace, contains(keys(local.masters), each.key) ? "master" : "worker")
  vm_state               = each.value.boot # start once created
  define_connection_info = false

  cpu {
    cores   = each.value.cores
    limit   = 0
    numa    = false
    sockets = 1
    type    = "host"
    units   = 0
    vcores  = 0
  }
  memory = each.value.ram
  scsihw = "virtio-scsi-pci"
  #bootdisk = "scsi0"
  hotplug = 0

  disk {
    slot    = "scsi0"
    size    = each.value.diskSize
    type    = "disk"
    storage = "local-lvm"
    format  = "raw"
    #iothread = 1
  }
  network {
    id      = 0
    model   = "virtio"
    bridge  = local.network.bridge
    tag     = local.network.vlan
    macaddr = each.value.macaddr
  }

  startup_shutdown {
    order            = -1
    shutdown_timeout = -1
    startup_delay    = -1
  }
}

resource "local_file" "ansible_inventory" {
  count = terraform.workspace == "default" ? 1 : 0
  content = templatefile("templates/hosts.tmpl",
    {
      service_ip = local.service.ip
    }
  )
  filename = "inventory/hosts.ini"
}
