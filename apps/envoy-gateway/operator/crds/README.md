# Envoy Gateway CRDs (vendored)

Source: `gateway-crds-helm` chart v1.9.2 (`templates/generated/`), oci://docker.io/envoyproxy/gateway-crds-helm
Why vendored: Helm releases fail here (>1Mi helm secret limit) and OKD's Ingress Operator
manages the Gateway API CRDs itself (admission policy) — so only the
`gateway.envoyproxy.io` CRDs are installed, applied directly by Flux.
To update: download the new chart version and replace these files.
