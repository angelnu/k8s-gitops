terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.2-rc07"
    }

    proxmox-bpg = {
      source = "bpg/proxmox"
      version = "0.93.0"
    }
  }
}

provider "proxmox" {
  pm_api_url  = format("%s/api2/json", var.api_url)
  pm_user     = var.user
  pm_password = var.passwd
  # pm_api_token_id     = var.token_id
  # pm_api_token_secret = var.token_secret
  # Leave to "true" for self-signed certificates
  pm_tls_insecure = "true"
  #pm_debug        = true
}

provider "proxmox-bpg" {
  endpoint  = var.api_url
  username     = var.user
  password = var.passwd
  # pm_api_token_id     = var.token_id
  # pm_api_token_secret = var.token_secret
  # Leave to "true" for self-signed certificates
  # insecure = "true"
  #pm_debug        = true
}
