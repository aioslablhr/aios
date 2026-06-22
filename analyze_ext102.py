"""Extract old prompt, build new travel agent prompt, and update DB."""
import json, os, glob

# 1. Extract old node-2 prompt
with open('/tmp/wf3.sqlout') as f:
    wf = json.load(f)

nodes = wf['nodes']
old_prompt = None
for n in nodes:
    if n['id'] == 'node-2':
        old_prompt = n['data']['prompt']
        break

if old_prompt:
    print(f"=== OLD PROMPT ({len(old_prompt)} chars) ===")
    print(old_prompt)
    print("=" * 60)
else:
    print("ERROR: node-2 not found")
    exit(1)

# 2. Load Shin Travels wiki
wiki_dir = '/aios/knowledge/companies/shin-travels/wiki'
wiki_content = ''
if os.path.isdir(wiki_dir):
    md_files = glob.glob(os.path.join(wiki_dir, '**/*.md'), recursive=True)
    md_files += glob.glob(os.path.join(wiki_dir, '*.md'))
    for fp in sorted(md_files):
        with open(fp) as f:
            content = f.read()
        # Strip YAML front matter
        if content.startswith('---'):
            _, _, content = content.partition('---')
            _, _, content = content.partition('---')
        # Get relative path for header
        rel = os.path.relpath(fp, wiki_dir)
        wiki_content += f"\n## Source: {rel}\n\n{content.strip()}\n"

print(f"\n=== WIKI CONTENT ({len(wiki_content)} chars) ===")
print(wiki_content[:1000])
print("..." if len(wiki_content) > 1000 else "")
