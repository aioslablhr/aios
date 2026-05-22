#!/bin/bash
set -e

RUNTIME_CONF=/run/asterisk-configs
mkdir -p "$RUNTIME_CONF"

cp /etc/asterisk/*.conf "$RUNTIME_CONF/"

for f in "$RUNTIME_CONF"/*.conf; do
  envsubst < "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
done

sed -i 's|astetcdir => /etc/asterisk|astetcdir => /run/asterisk-configs|' "$RUNTIME_CONF/asterisk.conf"

exec asterisk -f -U asterisk -p -C "$RUNTIME_CONF/asterisk.conf"
