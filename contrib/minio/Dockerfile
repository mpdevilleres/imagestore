FROM minio/minio:RELEASE.2024-02-06T21-36-22Z

ENV MC_CONFIG_DIR=/root/.mc/

COPY local /local

COPY config.json /root/.mc/config.json
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]