import asyncio, json, os, urllib.request
from datetime import datetime, timezone
from loguru import logger

CW_URL = os.getenv("CW_URL", "http://10.70.0.50:3000/api/v1/accounts/1")
CW_TOKEN = os.getenv("CW_API_TOKEN", "S25Q5AkyFCGwUrXUzzn8SCYw")
INBOX_IDENTIFIER = os.getenv("CW_INBOX_ID", "8xXig1ed5a9Ps4hQVjuMsrSL")

def _cw_api(method, path, data=None):
    url = f"{CW_URL}{path}"
    headers = {"Content-Type": "application/json", "api_access_token": CW_TOKEN}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        if resp.status == 204:
            return resp.status, None
        return resp.status, json.loads(resp.read().decode())
    except urllib.request.HTTPError as e:
        body = e.read().decode()[:200]
        logger.warning(f"CW API {method} {path} failed: {e.code} {body}")
        return e.code, body
    except Exception as e:
        logger.error(f"CW API {method} {path} exception: {e}")
        return 0, str(e)

def _parse_turns(transcript_text: str):
    lines = transcript_text.strip().split("\n")
    turns = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("user:"):
            turns.append({"speaker": "Caller", "text": line[5:].strip()})
        elif line.lower().startswith("assistant:"):
            turns.append({"speaker": "Emma", "text": line[10:].strip()})
        elif line.lower().startswith("caller:"):
            turns.append({"speaker": "Caller", "text": line[7:].strip()})
        elif line.lower().startswith("emma:"):
            turns.append({"speaker": "Emma", "text": line[5:].strip()})
    return turns

async def sync_to_chatwoot(
    workflow_run_id: int,
    transcript_text: str,
    call_metadata: dict,
):
    try:
        if not transcript_text.strip():
            logger.info(f"Run {workflow_run_id}: empty transcript, skipping")
            return

        call_id = call_metadata.get("call_id", f"run-{workflow_run_id}")
        duration = call_metadata.get("call_duration_seconds", 0)
        disposition = call_metadata.get("call_disposition", "unknown")
        ext = call_metadata.get("ext_channel_id", "")
        caller_number = call_metadata.get("caller_number", "")

        contact_name = f"Caller {caller_number}" if caller_number else f"Call {workflow_run_id}"
        phone = caller_number if caller_number else f"+441234567{workflow_run_id % 100000:05d}"

        status, cw_resp = _cw_api("POST", "/contacts", {
            "inbox_id": 1,
            "name": contact_name,
            "phone_number": phone,
            "additional_attributes": {
                "call_id": call_id,
                "duration": duration,
                "disposition": disposition,
                "extension": ext,
                "run_id": workflow_run_id,
            },
        })
        if status != 200 or not cw_resp:
            logger.warning(f"Run {workflow_run_id}: contact creation failed ({status}), will retry via poller")
            return

        source_id = cw_resp.get("payload", {}).get("contact_inbox", {}).get("source_id", "")
        if not source_id:
            logger.warning(f"Run {workflow_run_id}: no source_id in contact response")
            return

        pub_url = f"http://10.70.0.50:3000/public/api/v1/inboxes/{INBOX_IDENTIFIER}/contacts/{source_id}/conversations"
        try:
            pub_req = urllib.request.Request(pub_url, data=b"{}",
                headers={"Content-Type": "application/json"}, method="POST")
            pub_resp = urllib.request.urlopen(pub_req, timeout=15)
            conv = json.loads(pub_resp.read())
            conv_id = conv.get("id")
        except urllib.request.HTTPError as e:
            logger.warning(f"Run {workflow_run_id}: conversation creation failed: {e.code}")
            return

        msg_parts = []
        header = f"📞 Call #{workflow_run_id} — {duration}s | {disposition}\n\n"
        header += "\n".join(f"{t['speaker']}: {t['text']}" for t in turns)
        msg_parts.append({
            "content": header,
            "message_type": "incoming",
        })

        for msg in msg_parts:
            try:
                msg_url = f"{CW_URL}/conversations/{conv_id}/messages"
                msg_req = urllib.request.Request(msg_url,
                    data=json.dumps(msg).encode(),
                    headers={"Content-Type": "application/json", "api_access_token": CW_TOKEN},
                    method="POST")
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: urllib.request.urlopen(msg_req, timeout=15))
            except Exception as e:
                logger.warning(f"Run {workflow_run_id}: message send error: {e}")

        logger.info(f"Run {workflow_run_id}: synced to Chatwoot conv {conv_id} (open)")

    except Exception as e:
        logger.error(f"Run {workflow_run_id}: chatwoot sync error: {e}")
