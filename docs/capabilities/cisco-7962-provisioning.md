# Cisco 7962G SIP Phone — Full Provisioning Record

## ✅ FULLY RESOLVED — May 23, 2026
### Phone registered, calling OUT, and calling IN (ext 100 + ext 9000)
Firmware: SIP42.9-4-2SR3-1S (9.4.2SR3.1)

**Three root causes found and fixed:**

### Root Cause #1: disable_rport = yes in pjsip.conf [system]
- Asterisk showed Avail with RTT but phone showed cross icon
- Phone logs: `%REG auth failed: ack timer` repeating every ~32 seconds
- **Why**: `disable_rport=yes` strips rport from Via headers (RFC 3581).
  The Cisco 7962 SIP stack needs rport in the 200 OK Via to match it to the
  pending REGISTER transaction. Without it, the phone silently drops the 200 OK
  and times out.
- **Fix**: REMOVE `disable_rport = yes` from pjsip.conf [system] section.
  Default (no setting) = rport included.

### Root Cause #2: proxy MUST be USECALLMANAGER, NOT IP address
- Changing `<proxy>10.0.0.100</proxy>` in the SEP causes the phone to never
  send REGISTER at all (no contact appears on Asterisk)
- **Fix**: ALWAYS use `<proxy>USECALLMANAGER</proxy>` in the SEP line config.
  The actual server IP is set via the devicePool callManager block:
  `<processNodeName>10.0.0.100</processNodeName>`

### Additional working settings in pjsip.conf:
- `force_rport = no` on phone-template endpoint
- `rewrite_contact = yes` on phone-template endpoint
- [system] has NO disable_rport line

### Root Cause #3: UDP ephemeral socket — incoming calls blocked
- **Problem**: Phone registers from a random ephemeral UDP port (e.g., 50335) and closes the socket ~2ms after REGISTER. Asterisk stores that port as the contact address. When Asterisk sends an INVITE, the port is gone → `Connection refused`.
- **Evidence**: Asterisk error `Could not create dialog to invalid URI '9000'. Is endpoint registered and reachable?` Port scan confirms: registered port = `Connection refused`, UDP 5060 = no response, TCP 5060 = `Connection refused`.
- **Fix**: Change SEP `<transportLayerProtocol>` from `2` (UDP) to `4` (TCP). TCP is connection-oriented — the phone opens one TCP socket to Asterisk and keeps it open. Asterisk sends INVITEs over the same persistent connection.
- **Verification**: Contact shows `transport=TCP` and status `Avail` with RTT ~20ms. Incoming calls ring phone successfully.

### Current SEP line config:
```xml
<line button="1">
  <proxy>USECALLMANAGER</proxy>      <!-- MUST use USECALLMANAGER, not raw IP -->
  <name>100</name>
  <authName>100</authName>
  <authPassword>100pass</authPassword>
</line>
<line button="2">
  <proxy>USECALLMANAGER</proxy>
  <name>9000</name>
  <authName>9000</authName>
  <authPassword>9000pass</authPassword>
</line>
```

---

## ✅ FULLY RESOLVED — Historical record below documents the debug journey

---

## 1. PHONE IDENTITY
- **Model**: Cisco Unified IP Phone 7962G
- **MAC**: `00:27:0D:C0:1C:92` (sticker on back or Settings → Model Info)
- **SEP filename**: `SEP00270DC01C92.cnf.xml` (UPPERCASE MAC, no colons)
- **Current LAN IP**: 10.0.0.12 (from ONT DHCP)

## 2. NETWORK TOPOLOGY
```
ISP Fiber → Huawei ONT (10.0.0.1, DHCP + gateway)
                ↓ LAN Ethernet cable
            Switch (unmanaged TP-Link)
            ↙        ↓          ↘
      Dev PC     Server        Cisco 7962
    10.0.0.11  10.0.0.100     10.0.0.12
```

- **ONT is the DHCP server** — all devices get IPs from it
- **ONT owns 10.0.0.1** — causes IP conflict if server also claims it
- **Server 10.0.0.100** runs Asterisk + TFTP — this is the phone's TFTP target
- Phone configured with TFTP at **10.0.0.100** (NOT 10.0.0.1)

## 3. WHAT WE DID (CHRONOLOGICAL)

### 3.1 Firmware Download
Got firmware `cmterm-7942_7962-sip.9-4-2SR3-1` files from public mirror:
```
https://voip.omanski.pl/tftp/Firmware/cmterm-7942_7962-sip.9-4-2SR3-1/
```

### 3.2 Temporary DHCP + TFTP Setup (ONT Unplugged)
- Added `10.0.0.1` as secondary IP on server eno1
- Started dnsmasq container with DHCP + TFTP
- User unplugged ONT LAN cable
- Phone briefly had DHCP + TFTP from server
- User immediately asked to stop — stopped dnsmasq, removed IP
- Phone had already downloaded SOME files during that window

### 3.3 TFTP-Only Restart (ONT Back Online)
- Restarted dnsmasq in TFTP-only mode (no DHCP)
- Phone got IP from ONT, requested SEP config via TFTP
- **tcpdump confirmed**: phone requested and received `SEP00270DC01C92.cnf.xml` (multi-packet transfer completed)
- But phone still shows "Unprovisioned"

### 3.4 Password Shortened
- Original password `b1n1lh2qzfol4hwb` (16 chars) — CISCO PHONES CAP AT ~12 CHARS
- Changed to `100pass` (8 chars)
- Updated `.env`: `EXT_100_SECRET=100pass`
- Restarted Asterisk container

### 3.5 SEP XML Format Changed
- **First version**: Used `<line lineIndex="1">` with full XML (devicePool, vendorConfig, sipProfile, etc.)
- **Current version**: Simplified to `<sipLines><line button="1">` format (per lparakhin GitHub guide)
- Password shortened to `100pass`

## 4. CURRENT SEP FILE (`/tftp/SEP00270DC01C92.cnf.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<device deviceType="Cisco Unified IP Phone 7962G">
  <versionStamp>1</versionStamp>
  <devicePool>
    <callManagerGroup>
      <members>
        <member priority="0">
          <callManager>
            <ports>
              <sipPort>5060</sipPort>
            </ports>
            <processNodeName>10.0.0.100</processNodeName>
          </callManager>
        </member>
      </members>
    </callManagerGroup>
  </devicePool>
  <loadInformation>SIP42.9-4-2SR3-1S</loadInformation>
  <sipProfile>
    <sipProxies>
      <sipProxy>
        <name>10.0.0.100</name>
        <port>5060</port>
      </sipProxy>
    </sipProxies>
  </sipProfile>
  <sipLines>
    <line button="1">
      <featureID>9</featureID>
      <featurePriority>0</featurePriority>
      <name>100</name>
      <displayName>Ext 100</displayName>
      <authName>100</authName>
      <authPassword>100pass</authPassword>
    </line>
  </sipLines>
</device>
```

### Also present in /tftp/:
- `XMLDefault.cnf.xml` — same XML structure minus `<sipLines>` sections
- `dialplan.xml` — basic pattern `[0-9*#]+`
- All firmware files (8 files, ~10MB total)
- NO `g3-tones.xml`, NO `SIPDefault.cnf`, NO `SIPConfiguration.cnf`

## 5. TFTP SERVER CONFIG (`/aios/configs/dnsmasq/dnsmasq-tftp.conf`)

```
port=0
bind-interfaces
interface=eno1
listen-address=10.0.0.1
enable-tftp
tftp-root=/tftp
log-queries
```
**NOTE**: `listen-address=10.0.0.1` but container binds to ALL IPs on eno1 because `interface=eno1`. 10.0.0.100:69 is also served.

## 6. ASTERISK CONFIG

### Transport (pjsip.conf)
```
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060

[transport-tcp]
type = transport
protocol = tcp
bind = 0.0.0.0:5060
```
Both UDP and TCP on 5060 are active (important: Cisco 9.x SIP firmware uses TCP by default).

### Endpoint 100
```
[100](phone-template)
  auth = auth100
  aors = 100
  callerid = "Admin" <100>

[auth100](auth-template)
  username = 100
  password = ${EXT_100_SECRET}   → 100pass

[100](aor-template)
  support_path = yes
```

## 7. CREDENTIALS (`.env` — gitignored)
```
EXT_100_SECRET=100pass
```
Container restarted after password change. Verify with:
```bash
docker exec aios-asterisk asterisk -rx "pjsip show auth auth100"
```

## 8. DOCKER INFRASTRUCTURE (TEMPORARY)

### Services running (docker ps):
| Name | Status | Role |
|------|--------|------|
| aios-asterisk | healthy | Asterisk PBX |
| aios-vault | healthy | HashiCorp Vault |
| aios-traefik | healthy | Reverse proxy |
| aios-keycloak | healthy | SSO/OAuth |
| aios-crowdsec | healthy | WAF |
| aios-qdrant | healthy | Vector DB |
| aios-postgres | healthy | Database |
| dnsmasq-tftp | Up | TFTP server (temporary — for provisioning) |
| aios-hermes | Up | Ops agent |
| aios-gitops | Up | Auto-deploy |

### TFTP container commands:
```bash
# Start
docker run -d --name dnsmasq-tftp --net=host --cap-add=NET_ADMIN \
  -v /tftp:/tftp \
  -v /aios/configs/dnsmasq/dnsmasq-tftp.conf:/etc/dnsmasq.conf \
  andyshinn/dnsmasq

# Stop + remove
docker stop dnsmasq-tftp && docker rm dnsmasq-tftp
```

## 9. TFTP TRAFFIC CAPTURE (PROOF SEP WAS DOWNLOADED)

```
IP 10.0.0.12.52488 > 10.0.0.100.69: RRQ "CTLSEP00270DC01C92.tlv"
IP 10.0.0.100.37052 > 10.0.0.12.52488: UDP, length 48 (error/not found)

IP 10.0.0.12.52749 > 10.0.0.100.69: RRQ "ITLSEP00270DC01C92.tlv"
IP 10.0.0.100.41956 > 10.0.0.12.52749: UDP, length 48 (error/not found)

IP 10.0.0.12.49770 > 10.0.0.100.69: RRQ "ITLFile.tlv"
IP 10.0.0.100.57455 > 10.0.0.12.49770: UDP, length 37 (error/not found)

IP 10.0.0.12.51584 > 10.0.0.100.69: RRQ "SEP00270DC01C92.cnf.xml" octet
IP 10.0.0.100.58351 > 10.0.0.12.51584: UDP, length 516 (DATA block 1)
IP 10.0.0.12.51584 > 10.0.0.100.58351: UDP, length 4 (ACK)
IP 10.0.0.100.58351 > 10.0.0.12.51584: UDP, length 516 (DATA block 2)
IP 10.0.0.12.51584 > 10.0.0.100.58351: UDP, length 4 (ACK)
IP 10.0.0.100.58351 > 10.0.0.12.51584: UDP, length 516 (DATA block 3)
IP 10.0.0.12.51584 > 10.0.0.100.58351: UDP, length 4 (ACK)
IP 10.0.0.100.58351 > 10.0.0.12.51584: UDP, length 422 (final block)
IP 10.0.0.12.51584 > 10.0.0.100.58351: UDP, length 4 (ACK)
```
**SEP file was fully transferred** — 3 full blocks (516 bytes) + 1 final block (422 bytes), all ACKed.

## 10. PHONE BOOT SEQUENCE (KNOWN)
1. Power on → POST
2. DHCP → gets 10.0.0.x from ONT
3. TFTP at 10.0.0.100:69 → requests files in order:
   a. `CTLSEP00270DC01C92.tlv` → not found (OK, optional)
   b. `ITLSEP00270DC01C92.tlv` → not found (OK, optional)
   c. `ITLFile.tlv` → not found (OK, optional)
   d. **`SEP00270DC01C92.cnf.xml`** → **SUCCESS** (confirmed)
   e. May also request `g3-tones.xml` (heard on separate tcpdump) → not found
4. Phone parses SEP config → if valid, registers to 10.0.0.100:5060
5. **Currently STUCK at step 4** — "Unprovisioned"

## 11. "UNPROVISIONED" — ROOT CAUSE HYPOTHESES (UNRESOLVED)

### Hypothesis A: SEP XML format wrong for 9.4(2) firmware
- Different firmware versions require different XML schemas
- The `<sipLines>` format might need additional tags (e.g., `<contact>`, `<lineIndex>`, `<messagesNumber>`)
- The `<deviceType>` must match exactly: `Cisco Unified IP Phone 7962G`
- `<loadInformation>` might need exact match with firmware version string

### Hypothesis B: Missing required files
- Phone might need `g3-tones.xml` (ringtones) before accepting config
- Phone might need `SIPDefault.cnf` (default SIP parameters)
- Phone might need `SIPConfiguration.cnf` (additional config)

### [RESOLVED] Hypothesis C: Transport mismatch — this was THE fix
- **Root cause confirmed**: Phone uses ephemeral UDP ports for REGISTER, closes socket immediately.
- **Fix**: Changed SEP `<transportLayerProtocol>` from `2` (UDP) to `4` (TCP).
- TCP maintains a persistent connection → Asterisk sends INVITEs over the same socket → phone rings.
- Without this tag, phone defaults to UDP. With `4`, phone uses TCP. This is not a 9.x default issue.
- **Verification**: After fix, contact shows `transport=TCP`, status `Avail`, incoming calls work.

### Hypothesis D: Password still wrong
- `100pass` is 8 chars, well under 12-char limit
- But Asterisk might not have picked up the new password
- **Verify**: `docker exec aios-asterisk asterisk -rx "pjsip show auth auth100"`
- Should show password = `100pass`

### Hypothesis E: `<name>` tag mismatch
- Per Cisco community forum: phone uses `<name>` as the SIP From user in REGISTER
- If `<name>` is "100" but phone sends something else, auth fails
- Current SEP has `<name>100</name>` which should match Asterisk's `username=100`

### Hypothesis F: Phone has old (failed) cached config
- Phone might have cached a failed provision from an earlier attempt
- May need factory reset before retrying (not just power cycle)
- Factory reset: hold `#` key while powering on, or Settings → Factory Reset

## 12. HISTORICAL DEBUG STEPS (all resolved — kept for reference)

The following debug steps were taken during the investigation. All issues are now resolved.

### Critical: TFTP container must be running for phone to pick up SEP changes
```bash
# Start TFTP container (if not running)
docker run -d --name aios-dnsmasq-tftp --net=host --cap-add=NET_ADMIN \
  -v /tftp:/tftp \
  -v /aios/configs/dnsmasq/dnsmasq-tftp.conf:/etc/dnsmasq.conf \
  andyshinn/dnsmasq

# Verify TFTP serving SEP
echo 'get SEP00270DC01C92.cnf.xml' | tftp 10.0.0.100

# Check Asterisk registration
docker exec aios-asterisk asterisk -rx "pjsip show contacts"
```

### Phone must be power-cycled after SEP change
Phone only reads SEP from TFTP on boot. Pulling the power cord is required.

### Check Asterisk PJSIP debug
```bash
docker exec aios-asterisk asterisk -rx "pjsip set logger on"
docker logs aios-asterisk --tail 50 -f
```
Look for REGISTER attempts from phone IP (10.0.0.12).

## 13. FILES REFERENCE

| Location | Content | Purpose |
|----------|---------|---------|
| **On Server** | | |
| `/tftp/` | Firmware + SEP + XMLDefault + dialplan | TFTP root |
| `/aios/configs/dnsmasq/dnsmasq-tftp.conf` | TFTP-only dnsmasq config | TFTP server |
| `/aios/configs/dnsmasq/dnsmasq.conf` | Full DHCP+TFTP config | Temp DHCP (ONT unplugged) |
| `/aios/configs/asterisk/pjsip.conf` | Asterisk SIP endpoints | PBX config |
| `/aios/.env` | ALL credentials (gitignored) | Env vars for containers |
| **On Dev PC (D:\AIOS)** | | |
| `configs\dnsmasq\SEP00270DC01C92.cnf.xml` | Phone SEP template | Source for phone config |
| `configs\dnsmasq\XMLDefault.cnf.xml` | Default phone config | Fallback config |
| `configs\dnsmasq\dialplan.xml` | Dial plan | Phone dial rules |
| `configs\dnsmasq\dnsmasq.conf` | DHCP+TFTP config | Temp DHCP template |
| `configs\dnsmasq\dnsmasq-tftp.conf` | TFTP-only config | TFTP template |
| `configs\asterisk\pjsip.conf` | Asterisk SIP config | PBX config template |
| `.env` | ALL credentials (gitignored) | Env vars local copy |
| `docs\capabilities\cisco-7962-provisioning.md` | THIS FILE | Full provisioning record |

## 14. USEFUL COMMANDS

```bash
# Asterisk
docker exec aios-asterisk asterisk -rx "pjsip show endpoints"     # All endpoints
docker exec aios-asterisk asterisk -rx "pjsip show auth auth100"  # Auth details
docker exec aios-asterisk asterisk -rx "pjsip show endpoint 100"  # Endpoint 100
docker exec aios-asterisk asterisk -rx "pjsip set logger on"      # Debug SIP
docker logs aios-asterisk -f                                       # Live logs

# TFTP
docker logs dnsmasq-tftp                                           # TFTP requests
echo 'get SEP00270DC01C92.cnf.xml' | tftp 10.0.0.100              # Test TFTP

# Network capture
sudo tcpdump -i eno1 -nn port 69 -c 30                             # TFTP traffic
sudo tcpdump -i eno1 -nn host 10.0.0.12 and port 5060 -c 30       # SIP traffic

# Temporary IP (if needed)
sudo ip addr add 10.0.0.1/24 dev eno1
sudo ip addr del 10.0.0.1/24 dev eno1
```

## 15. FIRMWARE DOWNLOAD SOURCE
```
https://voip.omanski.pl/tftp/Firmware/cmterm-7942_7962-sip.9-4-2SR3-1/
```
Alt: Cisco official requires login at `http://www.cisco.com/cgi-bin/tablebuild.pl/ip-7900ser`

## 16. REFERENCE LINKS
- lparakhin GitHub: https://github.com/lparakhin/-Cisco-7962G-SIP (example SEP + XMLDefault + dialplan)
- staskobzar GitHub: https://github.com/staskobzar/cisco_prov (templates at `sip/7942_7962_TEMPL.cnf.xml`)
- VoIP-Info: https://www.voip-info.org/cisco-7942-with-local-pbx/ (example SEP for Asterisk)
- Blog (reg issue): https://asmetanin.wordpress.com/2014/06/06/problem-while-registering-cisco-7962-voip-phone-with-asterisk-solved/
- w20.ir guide: https://w20.ir/index.php/2019/07/08/how-to-install-sip-firmware-on-cisco-7942-and-7962-ip-phone/
