"""
Adds a translation credit to the ROM's banner title (shown in DS
flashcart menus and most emulator ROM browsers/info panels).

This only touches banner text, completely separate from the dialogue
engine we just fixed -- zero risk to gameplay.
"""
from pathlib import Path

ROM_PATH = Path("roms/YNAJA4_00_patched.nds")

# English title slot in the NDS banner: offset 0x340, 256 bytes (128 UTF-16LE
# code units), up to 3 lines separated by \n, null-terminated.
ENGLISH_TITLE_OFFSET = 0x340
TITLE_MAX_CHARS = 128

# Edit this to your name/handle
CREDIT_LINE = "Fan Translation by dark_seis"

NEW_TITLE = f"NANA LIVE\n{CREDIT_LINE}\nEnglish Patch"


def main():
    data = bytearray(ROM_PATH.read_bytes())

    encoded = NEW_TITLE.encode("utf-16-le")
    if len(encoded) > (TITLE_MAX_CHARS - 1) * 2:
        raise ValueError("Title text too long for the 128-char UTF-16 slot")

    # Zero out the whole 256-byte slot first, then write the new text
    data[ENGLISH_TITLE_OFFSET:ENGLISH_TITLE_OFFSET + 256] = b"\x00" * 256
    data[ENGLISH_TITLE_OFFSET:ENGLISH_TITLE_OFFSET + len(encoded)] = encoded

    ROM_PATH.write_bytes(data)
    print(f"Wrote credit into {ROM_PATH}")
    print(f"New English banner title:\n{NEW_TITLE}")
    print("\nNote: banner CRC was not recomputed. Emulators typically don't")
    print("validate it when loading a ROM directly, so this should display")
    print("fine in DeSmuME/melonDS. Real-hardware flashcarts may be pickier.")


if __name__ == "__main__":
    main()
