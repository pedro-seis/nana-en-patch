"""
Filter translation_data/coverage_gap_report.tsv down to high-confidence
genuine new messages, by keeping only entries whose address is NOT
within MIN_GAP bytes of a lower-address entry already kept.

This removes the "sliding window" duplicate noise (same message caught
at 1-3 byte offset variations) while preserving genuinely distinct
sequential messages (which are naturally spaced by real message length).
"""
from pathlib import Path

REPORT_PATH = Path("translation_data/coverage_gap_report.tsv")
FILTERED_PATH = Path("translation_data/coverage_gap_report_filtered.tsv")
MIN_GAP = 20          # bytes; entries closer than this to a kept entry are dropped
MIN_TEXT_LEN = 12     # ignore short fragments entirely


def main():
    with open(REPORT_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    hdr = lines[0]

    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        va_str, text = line.rstrip("\n").split("\t", 1)
        va = int(va_str, 16)
        rows.append((va, text))
    rows.sort(key=lambda r: r[0])

    kept = []
    last_kept_end = -1
    for va, text in rows:
        if len(text) < MIN_TEXT_LEN:
            continue
        if va < last_kept_end + MIN_GAP:
            continue
        kept.append((va, text))
        last_kept_end = va + len(text)

    print(f"Input rows: {len(rows):,}")
    print(f"Kept after filtering (gap>={MIN_GAP}, len>={MIN_TEXT_LEN}): {len(kept):,}")

    with open(FILTERED_PATH, "w", encoding="utf-8") as f:
        f.write(hdr)
        for va, text in kept:
            f.write(f"0x{va:08x}\t{text}\n")
    print(f"Wrote {FILTERED_PATH}")


if __name__ == "__main__":
    main()
