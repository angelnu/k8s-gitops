# kube-system namespace

## Kubernetes dashboard settings

Configures the [Kubernetes dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/).

** NOTE **: this is not the dashboard but only the settings. The installation is done as part of installing the K8S cluster.

[Settings](dashboard.yaml)

## Kured

[Kured](https://github.com/weaveworks/kured) (KUbernetes REboot Daemon) is a Kubernetes daemonset that performs safe automatic node reboots when the need to do so is indicated by the package management system of the underlying OS.

[Settings](kured)

## Mail server

Mail server for application in K8S and LAN to send mail without having to store any Google settings.

[Settings](mail/release.yaml)

## NFS

Some [Persistant Volume Claims](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims) for the NAS.

[Settings](nfs)

## Others (to be moved)

  * [cert-manager](https://github.com/jetstack/cert-manager) - Automated letsencrypt broker