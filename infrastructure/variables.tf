variable "api_url" {
  description = "URL to the API of Proxmox"
  type        = string
  default     = "https://192.168.1.101:8006/api2/json"
}

variable "user" {
  description = "Name of the admin account to use"
  type        = string
  default     = "terraform@pve"
}

variable "passwd" {
  description = "Password for the user - defined elsewhere"
  type        = string
  sensitive   = true
}

# variable "token_id" {
#   description = "The token created for a user in Proxmox"
#   type        = string
#   sensitive   = true
# }

# variable "token_secret" {
#   description = "The secret created for a user's token in Proxmox"
#   type        = string
#   sensitive   = true
# }
variable "ansible_user" {
  description = "Name of the user used by Ansible. By default, I use ansible"
  type        = string
  default     = "ansible"
}
variable "ansible_pwd" {
  description = "Ansible password"
  type        = string
  sensitive   = true
}
variable "ansible_ssh_public_key" {
  description = "Ansible SSH public key"
  type        = string
}

variable "vmid_offset" {
  description = "Start of the first VM ID - they are fixed, but can be happily ignored"
  type        = number
  default     = 400
}
variable "vm_name_prefix" {
  description = "Don't ever create VMs with an existing name, it'll crash the existing one. Solution ? A cluster prefix"
  type        = string
  default     = "okd"
}
