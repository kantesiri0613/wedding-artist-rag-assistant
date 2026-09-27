import os
import re

files = ['index.html', 'about.html', 'gallery.html', 'estimator.html', 'process.html', 'reviews.html', 'faq.html', 'contact.html']

all_valid = True
for f in files:
    if not os.path.exists(f):
        print(f"Missing file: {f}")
        all_valid = False
        continue
    content = open(f, encoding="utf-8").read()
    imgs = re.findall(r'src=["\'](assets/images/[^"\']+)["\']', content)
    for img in imgs:
        if not os.path.exists(img):
            print(f"BROKEN IMAGE in {f}: {img}")
            all_valid = False
        else:
            print(f"OK: {f} -> {img} ({os.path.getsize(img):,} bytes)")

if all_valid:
    print("\nSUCCESS: All files and image assets exist and are verified!")
