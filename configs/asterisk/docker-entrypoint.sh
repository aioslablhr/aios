#!/bin/bash
set -e

RUNTIME_CONF=/run/asterisk-configs
mkdir -p "$RUNTIME_CONF"

cp /etc/asterisk/*.conf "$RUNTIME_CONF/"

# Copy AGI scripts to AGI bin directory
cp /etc/asterisk/*.agi /var/lib/asterisk/agi-bin/ 2>/dev/null || true
chown asterisk:asterisk /var/lib/asterisk/agi-bin/*.agi 2>/dev/null || true
chmod +x /var/lib/asterisk/agi-bin/*.agi 2>/dev/null || true

for f in "$RUNTIME_CONF"/*.conf; do
  envsubst < "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
done

sed -i 's|astetcdir => /etc/asterisk|astetcdir => /run/asterisk-configs|' "$RUNTIME_CONF/asterisk.conf"

exec asterisk -f -U asterisk -p -C "$RUNTIME_CONF/asterisk.conf"
