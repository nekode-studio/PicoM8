import os
import re
import struct
from PIL import Image

def decode_byte(byte_val):
    """Decodifica um byte (0-255) em ARGB (2 bits por canal)"""
    return (
        (byte_val >> 6) & 0x03,  # A
        (byte_val >> 4) & 0x03,  # R
        (byte_val >> 2) & 0x03,  # G
        byte_val & 0x03          # B
    )

def get_bytes_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if filepath.endswith(".js"):
        match = re.search(r"var\s+_cartdat\s*=\s*(.*?)", content, re.S)
        if not match:
            raise ValueError("Não foi possível encontrar _cartdat em arquivo .js")
        data = match.group(1)
    else:
        data = content

    numbers = list(map(int, re.findall(r'\d+', data)))
    return numbers

def embed_pico8_signature(pixels):
    sig = [34, 0, 2, 5, 0x77, 0x02]
    for i, val in enumerate(sig):
        pixels[0x8000 + i] = decode_byte(val)
    return pixels

def create_image(pixels, outname):
    # 160x205 pixels, formato ARGB (8 bits por canal)
    img = Image.new("RGBA", (160, 205))
    raw_data = []

    for p in pixels:
        if isinstance(p, tuple) and len(p) == 4:
            a, r, g, b = [x * 85 for x in p]  # 2 bits => 0-255 scale
            raw_data.append((r, g, b, a))
        else:
            raw_data.append((0, 0, 0, 0))

    img.putdata(raw_data)
    img.save(outname)
    print(f"Imagem salva como {outname}")

def main():
    print("=== PICO-8 Data to PNG Converter ===")
    path = input("Digite o caminho para um arquivo .txt ou .js: ").strip()

    if not os.path.exists(path):
        print("Arquivo não encontrado.")
        return

    ext = os.path.splitext(path)[1].lower()
    if ext not in [".txt", ".js"]:
        print("Arquivo precisa ser .txt ou .js")
        return

    numbers = get_bytes_from_file(path)

    # Inicializa pixels
    pixels = [decode_byte(n) for n in numbers[:160 * 205]]
    pixels += [(0, 0, 0, 0)] * (160 * 205 - len(pixels))  # padding
    pixels = embed_pico8_signature(pixels)

    base = os.path.splitext(path)[0]
    outname = base + ".p8.png"

    create_image(pixels, outname)

if __name__ == "__main__":
    main()