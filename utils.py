import os
from ebooklib import epub

def extract_epub_cover(epub_path):
    book = epub.read_epub(epub_path)
    for item in book.get_items():
        if item.get_type() == epub.EpubCover:
            return item.get_content()
    return None

def save_cover(img_bytes, save_dir="covers"):
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"{os.urandom(4).hex()}.png")
    with open(filename, "wb") as f:
        f.write(img_bytes)
    return filename