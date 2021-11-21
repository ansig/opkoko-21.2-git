#!/usr/bin/env python3

import zlib
import os
from hashlib import sha1

content = 'Lorem ipsum dolor\n'
content_bytes = content.encode('utf-8')

header = f'blob {len(content_bytes)}\0'

obj = header + content
sha = sha1(obj.encode('utf-8')).hexdigest()

compressed_obj = zlib.compress(obj.encode('utf-8'))

path = f'.git/objects/{sha[0:2]}/{sha[2:]}'

os.makedirs(os.path.dirname(path))

with open(path, 'wb') as f:
    f.write(compressed_obj)
