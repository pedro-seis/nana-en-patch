"""
Scan the ARM9 script region for occurrences of a target Japanese phrase
that are NOT already present in script_map.tsv (i.e. missing entries).

Usage:
    python src/find_missing_line.py "んじゃまたね"
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from script_decoder import load_encoding, decode_bytes

ROM_PATH = Path("roms/YNAJA4_00.nds")
SCRIPT_MAP_PATH = Path("translation_data/script_map.tsv")
ENCODING_PATH = Path("docs/user_encoding.tsv")

ARM9_RAM_BASE = 0x02000000


def load_arm9_from_nds(nds_path: Path) -> tuple[bytes, int, int]:
    """Minimal NDS header parse to pull out the ARM9 binary."""
    data = nds_path.read_bytes()
    arm9_rom_offset = int.from_bytes(data[0x20:0x24], "little")
    arm9_entry = int.from_bytes(data[0x24:0x28], "little")
    arm9_load = int.from_bytes(data[0x28:0x2C], "little")
    arm9_size = int.from_bytes(data[0x2C:0x30], "little")
    arm9 = data[arm9_rom_offset:arm9_rom_offset + arm9_size]
    return arm9, arm9_load, arm9_size


# Hardcoded here (not passed via command line) to avoid PowerShell mangling
# non-ASCII arguments. Add/edit candidates as needed.
TARGETS = [
    "またね",
    "んじゃ",
    "じゃまたね",
    "またね。",
]


def main():
    targets = TARGETS
    if len(sys.argv) >= 2:
        # allow override, but hardcoded list above is the reliable path
        targets = [sys.argv[1]]

    print(f"Loading {ROM_PATH} ...")
    arm9, arm9_load, arm9_size = load_arm9_from_nds(ROM_PATH)
    print(f"ARM9: {arm9_size} bytes at RAM 0x{arm9_load:08x}")

    primary, alternates, states = load_encoding(ENCODING_PATH)

    # Load known VAs from script_map so we can flag genuinely new hits
    known_vas: set[int] = set()
    if SCRIPT_MAP_PATH.is_file():
        with open(SCRIPT_MAP_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                try:
                    known_vas.add(int(row["ram_va"], 16))
                except (KeyError, ValueError):
                    pass
    print(f"Known mapped addresses: {len(known_vas):,}")

    region_start = arm9_load
    region_end = arm9_load + arm9_size

    print(f"Scanning byte-by-byte across {arm9_size:,} bytes ... (this may take a while)")
    hits = 0
    # Decode a fixed-size window at every offset; cheap heuristic scan.
    WINDOW = 200
    seen_texts = set()
    total = len(arm9) - 4
    off = 0
    while off < total:
        if off % 100000 == 0:
            print(f"  ...{off:,}/{total:,} ({100*off//total}%)")
        b = arm9[off]
        if b == 0x00:
            off += 1
            continue
        end = min(off + WINDOW, len(arm9))
        try:
            result = decode_bytes(arm9, off, end, primary, alternates, states)
        except Exception:
            off += 1
            continue
        text = result.text
        matched = next((t for t in targets if t in text), None)
        if matched:
            va = region_start + off
            status = "KNOWN" if va in known_vas else "*** NEW ***"
            if status == "*** NEW ***":
                print(f"  [{status}] match={matched!r} va=0x{va:08x}  text={text[:120]!r}")
                hits += 1
            # Skip past this whole decoded message before continuing the scan
            off += max(len(text), 1)
            if hits >= 100:
                print("  ...stopping after 100 NEW hits, narrow your targets")
                break
            continue
        off += 1

    print(f"Done. {hits} candidate location(s) found.")


if __name__ == "__main__":
    main()
