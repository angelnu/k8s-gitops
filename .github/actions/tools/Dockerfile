FROM stefanprodan/alpine-base:latest@sha256:be230171b01adc5e166899785e9419d90d1359d53a690bf72b8d34c05a1e3f6a

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
