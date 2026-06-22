import sys
with open('/aios/docker-compose-aios.yml', 'r') as f:
    lines = f.readlines()
if 'EXT_2000_SECRET' in lines[1059]:
    print(f'Removing line 1060: {lines[1059].strip()}')
    del lines[1059]
    with open('/aios/docker-compose-aios.yml', 'w') as f:
        f.writelines(lines)
    print('Done')
else:
    print('Unexpected content at line 1060')
    sys.exit(1)
