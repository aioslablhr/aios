import subprocess, sys

r = subprocess.run(['docker','exec','aios-dograh-api','cat','/app/api/services/workflow/text_chat_runner.py'],
    capture_output=True, text=True, timeout=10)
original = r.stdout

old = '    base_checkpoint = _resolve_checkpoint_for_pending_turn(session_data, checkpoint)\n\n    response_window'
new = '''    base_checkpoint = _resolve_checkpoint_for_pending_turn(session_data, checkpoint)

    # Inject start node prompt as system message (same as voice pipeline)
    _start_node = workflow_graph.get_node(workflow_graph.start_node_id)
    _start_prompt = ''
    _start_node_data = _start_node.get('data', {}) if isinstance(_start_node, dict) else {}
    _start_prompt = _start_node_data.get('prompt', '') or ''
    if _start_prompt:
        base_checkpoint['messages'] = [{'role': 'system', 'content': _start_prompt}] + list(base_checkpoint.get('messages', []))

    response_window'''

if old in original:
    patched = original.replace(old, new, 1)
    with open('/tmp/_patched_runner.py', 'w') as f:
        f.write(patched)
    subprocess.run(['docker','cp','/tmp/_patched_runner.py','aios-dograh-api:/app/api/services/workflow/text_chat_runner.py'],
        capture_output=True, text=True, timeout=10)
    # Verify
    r2 = subprocess.run(['docker','exec','aios-dograh-api','grep','-c','_start_prompt','/app/api/services/workflow/text_chat_runner.py'],
        capture_output=True, text=True, timeout=10)
    print('Patched:', r2.stdout.strip(), 'occurrences found')
else:
    print('Pattern not found. First 600 chars:')
    print(original[:600])
