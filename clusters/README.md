# Create config for new tenant

1. Copy an existing cluster folder
2. Adjust the `path` at `<new cluster>/config/cluster-config.yaml` to point to the `clusters/<new cluster>` folder
2. Adjust the `path` at `<new cluster>/config/cluster-apps.yaml` to point to the `clusters/<new cluster>` folder
3. Adjust the `path` at `<new cluster>/config/vars.yaml`  to point to the `clusters/<new cluster>` folder
4. Adjust the `path` at `<new cluster>/config/global-vars.yaml`  to point to the `clusters/<new cluster>` folder
5. Create a new Age secret for the cluster
   1. `age-keygen` and copy its output into `<cluster>/vars/sops-age.secret.sops.yaml`
   2. Adjust the `clusters/<cluster>/.sops.yaml`
      1. set `cluster_age_key` to use the age public key
      2. Adjust other authorized users that need to see/edit secrets
      3. Call `scripts/rewrap-secrets.sh` to rewrap the secrets with the new keys
5. Update the [cluster settings](flux/vars/cluster-settings.yaml)

## Bootstrap

1. `kubectl create ns flux-system`
2. Create the secret in the cluster:

       ```shell
       sops -d clusters/<cluster>/vars/sops-age.secret.sops.yaml|kubectl apply -f -
       ```
3. `kubectl -n flux-system apply -k bootstrap`
4. `kubectl -n flux-system apply -k clusters/<cluster>/config`
5. Install [nmstate](https://github.com/nmstate/kubernetes-nmstate/releases)
