"""
Bulk-append candidates from coverage_gap_report_filtered.tsv to
translation_data/script_map.tsv, so they flow through the normal
populate -> translate -> wrap -> relocate -> build pipeline.

Same n_bytes logic as add_missing_lines.py: scan forward to the first
single 0x00 byte (the real message terminator).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from script_decoder import load_encoding, decode_bytes

ROM_PATH = Path("roms/YNAJA4_00.nds")
SCRIPT_MAP_PATH = Path("translation_data/script_map.tsv")
ENCODING_PATH = Path("docs/user_encoding.tsv")
FILTERED_REPORT_PATH = Path("translation_data/coverage_gap_report_filtered.tsv")
ARM9_RAM_BASE = 0x02000000


def load_arm9_from_nds(nds_path: Path):
    data = nds_path.read_bytes()
    arm9_rom_offset = int.from_bytes(data[0x20:0x24], "little")
    arm9_load = int.from_bytes(data[0x28:0x2C], "little")
    arm9_size = int.from_bytes(data[0x2C:0x30], "little")
    arm9 = data[arm9_rom_offset:arm9_rom_offset + arm9_size]
    return arm9, arm9_load, arm9_size, arm9_rom_offset


def main():
    print(f"Loading {ROM_PATH} ...")
    arm9, arm9_load, arm9_size, arm9_rom_offset = load_arm9_from_nds(ROM_PATH)
    primary, alternates, states = load_encoding(ENCODING_PATH)

    with open(FILTERED_REPORT_PATH, encoding="utf-8") as f:
        report_lines = f.readlines()[1:]  # skip header
    candidate_vas = []
    for line in report_lines:
        if not line.strip():
            continue
        va_str = line.split("\t", 1)[0]
        try:
            candidate_vas.append(int(va_str, 16))
        except ValueError:
            pass
    print(f"Loaded {len(candidate_vas):,} candidate addresses from {FILTERED_REPORT_PATH}")

    with open(SCRIPT_MAP_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    hdr = lines[0].rstrip("\n").split("\t")
    i_va = hdr.index("ram_va")

    existing_vas = set()
    existing_ranges = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) > i_va:
            try:
                va = int(parts[i_va], 16)
                nb = int(parts[hdr.index("n_bytes")])
                existing_vas.add(va)
                existing_ranges.append((va, va + nb))
            except ValueError:
                pass
    existing_ranges.sort()

    def overlaps_existing(va: int) -> bool:
        for s, e in existing_ranges:
            if s <= va < e:
                return True
            if s > va:
                break
        return False

    new_rows = []
    skipped_existing = 0
    skipped_no_term = 0
    skipped_overlap = 0
    n_progress = 0

    for va in candidate_vas:
        n_progress += 1
        if n_progress % 500 == 0:
            print(f"  ...{n_progress:,}/{len(candidate_vas):,} processed, {len(new_rows):,} added so far")

        if va in existing_vas or overlaps_existing(va):
            skipped_overlap += 1
            continue

        off = va - arm9_load
        term_off = None
        for p in range(off, min(off + 500, len(arm9))):
            if arm9[p] == 0x00:
                term_off = p
                break
        if term_off is None:
            skipped_no_term += 1
            continue
        n_bytes = term_off - off + 1

        raw = bytes(arm9[off:off + n_bytes])
        result = decode_bytes(raw, 0, len(raw), primary, alternates, states)

        rom_off = arm9_rom_offset + off
        row = [
            f"0x{va:08x}",
            f"0x{rom_off:08x}",
            str(n_bytes),
            "",
            "",
            str(result.n_resolved),
            str(result.n_missing),
            str(result.n_out_of_range),
            "",
            "",
        ]
        new_rows.append(row)
        # Extend the "existing" range coverage so later candidates in this
        # same run don't get double-added if they overlap this one.
        existing_ranges.append((va, va + n_bytes))
        existing_ranges.sort()

    if new_rows:
        with open(SCRIPT_MAP_PATH, "a", encoding="utf-8") as f:
            for row in new_rows:
                f.write("\t".join(row) + "\n")

    print(f"\nAdded {len(new_rows):,} new rows.")
    print(f"Skipped (already present / overlaps existing): {skipped_overlap:,}")
    print(f"Skipped (no terminator found): {skipped_no_term:,}")


if __name__ == "__main__":
    main()
