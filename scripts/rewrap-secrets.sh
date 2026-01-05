#!/bin/sh
FOLDER="$(dirname "$(dirname "$(readlink -f "$0")")")"
#find $FOLDER -type f -name ".+\.secret(\.sops)?\.ya?ml"
for f in $(find $FOLDER -type f -name "*secret.sops.yaml"); do
  cd $(dirname $f)
  sops updatekeys --yes $f
done
