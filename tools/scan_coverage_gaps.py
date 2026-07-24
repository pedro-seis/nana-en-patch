"""
Full coverage sweep: walk the entire script region and report every
address that decodes to clean, plausible dialogue text but is NOT
already present in script_map.tsv.

Unlike find_missing_line.py (which hunts a specific phrase), this scans
everything and applies a text-quality heuristic to filter out noise,
so you get a comprehensive list of gaps in one pass.

Output: translation_data/coverage_gap_report.tsv
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from script_decoder import load_encoding, decode_bytes

ROM_PATH = Path("roms/YNAJA4_00.nds")
SCRIPT_MAP_PATH = Path("translation_data/script_map.tsv")
ENCODING_PATH = Path("docs/user_encoding.tsv")
REPORT_PATH = Path("translation_data/coverage_gap_report.tsv")

ARM9_RAM_BASE = 0x02000000
WINDOW = 300
MIN_TEXT_LEN = 4        # ignore trivially short decodes
MAX_BAD_RATIO = 0.15    # max fraction of chars that can be [?xx]/[oor:xx] markers


def load_arm9_from_nds(nds_path: Path):
    data = nds_path.read_bytes()
    arm9_rom_offset = int.from_bytes(data[0x20:0x24], "little")
    arm9_load = int.from_bytes(data[0x28:0x2C], "little")
    arm9_size = int.from_bytes(data[0x2C:0x30], "little")
    arm9 = data[arm9_rom_offset:arm9_rom_offset + arm9_size]
    return arm9, arm9_load, arm9_size


def looks_clean(text: str) -> bool:
    if len(text) < MIN_TEXT_LEN:
        return False
    bad = text.count("[?") + text.count("[oor:")
    if bad / max(len(text), 1) > MAX_BAD_RATIO:
        return False
    # require at least one real Japanese char (hiragana/katakana/kanji range)
    has_ja = any(
        ("\u3040" <= c <= "\u30ff") or ("\u4e00" <= c <= "\u9fff")
        for c in text
    )
    return has_ja


def main():
    print(f"Loading {ROM_PATH} ...")
    arm9, arm9_load, arm9_size = load_arm9_from_nds(ROM_PATH)
    print(f"ARM9: {arm9_size} bytes at RAM 0x{arm9_load:08x}")

    primary, alternates, states = load_encoding(ENCODING_PATH)

    known_vas: set[int] = set()
    known_ranges: list[tuple[int, int]] = []
    with open(SCRIPT_MAP_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                va = int(row["ram_va"], 16)
                nb = int(row["n_bytes"])
                known_vas.add(va)
                known_ranges.append((va, va + nb))
            except (KeyError, ValueError):
                pass
    known_ranges.sort()
    print(f"Known mapped entries: {len(known_vas):,}")

    if not known_ranges:
        print("ERROR: no known ranges loaded, aborting")
        sys.exit(1)
    region_start = min(r[0] for r in known_ranges)
    region_end = max(r[1] for r in known_ranges)
    print(f"Script region: 0x{region_start:08x}..0x{region_end:08x}")

    off_start = region_start - arm9_load
    off_end = region_end - arm9_load

    def in_known_range(va: int) -> bool:
        # cheap linear-ish check is fine given moderate list size; could
        # binarysearch but this is a one-off tool
        for s, e in known_ranges:
            if s <= va < e:
                return True
            if s > va:
                break
        return False

    print("Scanning full script region for unmapped clean text ...")
    candidates = []
    off = off_start
    total = off_end - off_start
    while off < off_end:
        if (off - off_start) % 50000 == 0:
            pct = 100 * (off - off_start) // max(total, 1)
            print(f"  ...{off - off_start:,}/{total:,} ({pct}%)  found={len(candidates)}")
        b = arm9[off]
        if b == 0x00:
            off += 1
            continue
        va = arm9_load + off
        if va in known_vas:
            off += 1
            continue
        end = min(off + WINDOW, len(arm9))
        try:
            result = decode_bytes(arm9, off, end, primary, alternates, states)
        except Exception:
            off += 1
            continue
        text = result.text
        if looks_clean(text) and not in_known_range(va):
            candidates.append((va, text))
            off += max(len(text), 1)
            continue
        off += 1

    print(f"\nDone scanning. {len(candidates)} unmapped candidate(s) found.")

    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
        f.write("ram_va\ttext\n")
        for va, text in candidates:
            safe_text = text.replace("\t", " ")
            f.write(f"0x{va:08x}\t{safe_text}\n")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
