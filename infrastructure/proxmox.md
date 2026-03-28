# Proxmox notes

## Recovering ceph cluser after a cluster shut down

systemctl list-units "ceph-*" --all
ceph daemon mon.$(hostname) mon_status

systemctl restart mnt-pve-cephfs.mount

systemctl reset-failed ceph-mon@pve*.service
systemctl reset-failed ceph-mds@pve*.service
systemctl reset-failed ceph-mgr@pve*.service
systemctl reset-failed ceph-osd@*.service
