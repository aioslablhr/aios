PGPASSWORD=aios_secret_2026
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -c "INSERT INTO telephony_phone_numbers (organization_id, telephony_configuration_id, address, address_normalized, address_type, label, inbound_workflow_id, is_active, extra_metadata) VALUES (1, 1, '500', '500', 'sip_extension', 'Ext 500 - Quick Urdu Test', 5, true, '{\"type\": \"ari_extension\"}') ON CONFLICT DO NOTHING;"
echo "Done"
