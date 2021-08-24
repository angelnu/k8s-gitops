# Changes done in the installed Proxmox

These changed have been done manually and not automated with Ansible yet.

## GPU passthrough

1. Edit `/etc/default/grub`
   `GRUB_CMDLINE_LINUX_DEFAULT="consoleblank=0 intel_iommu=on vfio-pci.ids=8086:3ea5 video=efifb:off video=vesafb:off"`
2. Edit `/etc/modprobe.d/blacklist.conf`
   ```
   blacklist snd_hda_intel
   blacklist snd_hda_codec_hdmi
   blacklist i915
   blacklist sof_pci_dev
   ```
3. Reboot
4. Add GPU to PCI passthrough in the proxmox UI (VM Hardware tab)

More info in [forum](https://forum.proxmox.com/threads/intel-nuc-igpu-passthrough-working-in-linux-guest-but-not-in-windows-10-guest.71861/)