#!/bin/bash
set -e
PGPASSWORD=aios_secret_2026

# 1. Add phone mapping for 500
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh << 'SQL'
INSERT INTO telephony_phone_numbers (organization_id, telephony_configuration_id, address, address_normalized, address_type, label, inbound_workflow_id, is_active, extra_metadata)
VALUES (1, 1, '500', '500', 'sip_extension', 'Ext 500 - Quick Urdu Test', 5, true, '{"type": "ari_extension"}')
ON CONFLICT (organization_id, address_normalized) DO UPDATE SET inbound_workflow_id=5, is_active=true;
SQL

echo "Phone mapping added"

# 2. Verify
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -c "select address, inbound_workflow_id, label, is_active from telephony_phone_numbers order by address;"
