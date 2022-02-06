# Changes done in the installed Proxmox

These changed have been done manually and not automated with Ansible yet.

## GPU passthrough

1. Edit `/etc/default/grub`
   `GRUB_CMDLINE_LINUX_DEFAULT="consoleblank=0 intel_iommu=on vfio-pci.ids=8086:3ea5 video=efifb:off video=vesafb:off"`
2. `update-grub`
3. Edit `/etc/modprobe.d/blacklist.conf`
   ```
   blacklist snd_hda_intel
   blacklist snd_hda_codec_hdmi
   blacklist i915
   blacklist sof_pci_dev
   blacklist radeon
   blacklist nouveau
   blacklist nvidia
   ```
4. Reboot
5. Add GPU to PCI passthrough in the proxmox UI (VM Hardware tab)
   - Note needed - implemented in Ansible

More info in [forum](https://forum.proxmox.com/threads/intel-nuc-igpu-passthrough-working-in-linux-guest-but-not-in-windows-10-guest.71861/)

## Mail server

1. In one node:
   1. Create file `/etc/pve/postfix_google_passwd`:
      ```sh
      #Not longer using gmail
      [smtp.gmail.com]:587    <user>:<password>
      ```
   1. Create file `/etc/pve/postfix_smtp_headers_checks`:
2. In all nodes:
   1. Add the block bellow to `/etc/postfix/main.cf`:
      ```sh
      # Instructions from https://forum.proxmox.com/threads/get-postfix-to-send-notifications-email-externally.59940/
      # also do:
      # - apt install postfix-pcre libsasl2-modules
      # - systemctl restart postfix.service
      # echo "Test mail from postfix" | mail -s "Test Postfix from $(hostname)" test@mydomain.com
      
      #Settings for google (not longer used)
      #relayhost = [smtp.gmail.com]:587
      #smtp_use_tls = yes
      #smtp_sasl_auth_enable = yes
      #smtp_sasl_security_options = noanonymous
      #smtp_sasl_password_maps = hash:/etc/pve/postfix_google_passwd
      
      relayhost = <my relay>:25
      smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
      smtp_header_checks = pcre:/etc/pve/postfix_smtp_headers_checks
      #mydestination = $myhostname, localhost.$mydomain, localhost
      ```
   2. `apt install postfix-pcre libsasl2-modules`
   3. `systemctl status postfix.service`
