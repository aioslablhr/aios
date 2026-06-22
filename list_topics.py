import ast, pathlib
topics = pathlib.Path('/app/api/services/voice_prompting_guide/topics')
for f in sorted(topics.glob('*.py')):
    mod = ast.parse(f.read_text())
    for node in ast.walk(mod):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'TOPIC':
            for kw in node.value.keywords:
                if kw.arg == 'title':
                    print(f"{f.stem}: {ast.literal_eval(kw.value)}")
