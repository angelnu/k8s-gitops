#!/bin/sh

# Installs git hooks.

ln -sf ../../scripts/find-unencrypted-secrets.sh ../.git/hooks/pre-commit