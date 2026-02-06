# Resize OKD disk

1. Grow in proxmox
2. chroot /host sh -c "growpart /dev/sda 4 && xfs_growfs /var"