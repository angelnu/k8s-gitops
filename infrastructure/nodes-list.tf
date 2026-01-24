########################################################
# This just builds the list of masters and workers nodes
########################################################
locals {
  clusters = yamldecode(file("vars/clusters.yaml")).clusters
  network  = yamldecode(file("vars/network.yaml"))
  main     = yamldecode(file("vars/main.yaml"))

  service = {
    name        = format("%s-service", var.vm_name_prefix)
    target_host = local.main.service.target_host
    cores       = local.main.service.cores
    ram         = local.main.service.ram
    diskSize    = local.main.service.diskSize
    ip          = local.main.service.ip
    macaddr     = local.main.service.macaddr
    vmid        = local.main.service.vmid
    os          = local.main.service.os
    boot        = "started"
  }

  masters = {
    for index, node in terraform.workspace == "default" ? [] : local.clusters[terraform.workspace].masters :
    "master${index}" => {
      target_host = node.target_host
      cores       = node.cores
      ram         = node.ram
      diskSize    = node.diskSize
      ip          = node.ip
      macaddr     = node.macaddr # Private MAC address. 
      vmid        = node.vmid
      boot        = "started"
    }
  }

  workers = {
    for index, node in terraform.workspace == "default" ? [] : local.clusters[terraform.workspace].workers :
    "worker${index}" => {
      target_host = node.target_host
      cores       = node.cores
      ram         = node.ram
      diskSize    = node.diskSize
      ip          = node.ip
      macaddr     = node.macaddr # Private MAC address. 
      vmid        = node.vmid
      boot        = "started"
    }
  }

  all_pxe_nodes = merge(local.masters, local.workers)
}
