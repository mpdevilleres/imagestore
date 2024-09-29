#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

DATA_MINIO=/data

if [ -z "$(ls -A ${DATA_MINIO})" ]; then
  echo "${DATA_MINIO} is empty, buckets will be created"

  minio server --address 0.0.0.0:9001 ${DATA_MINIO} &
  MINIO_PID=${!}

  for i in $(ls -rtd /local/*);
  do
    mc mb ${i:1}
    mc cp -r ${i}/ ${i:1}
  done

  kill ${MINIO_PID}

else
  echo "${DATA_MINIO} is not empty, skipping bucket creation"
fi

exec "$@"
