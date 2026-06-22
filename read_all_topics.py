import pathlib, ast

topics_dir = pathlib.Path('/app/api/services/voice_prompting_guide/topics')
for f in sorted(topics_dir.glob('*.py')):
    source = f.read_text()
    lines = source.split('\n')
    title = ""
    content_lines = []
    in_content = False
    for line in lines:
        if 'title=' in line and '"""' not in line:
            try:
                title = line.split('title=')[1].split(',')[0].strip().strip('"\'')
            except:
                pass
        if 'content="""' in line:
            in_content = True
            content_lines.append(line.split('content="""')[1])
            continue
        if in_content:
            if '"""' in line:
                content_lines.append(line.split('"""')[0])
                break
            content_lines.append(line)
    
    content = '\n'.join(content_lines)
    print(f"\n{'='*60}")
    print(f"TOPIC: {f.stem}")
    print(f"Title: {title}")
    print(f"{'='*60}")
    print(content)
