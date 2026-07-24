"""
Appends a fan-translation credit to the end of the credits/staff-roll
entry (va=0x02077581) in translated_script.tsv, without touching the
existing licensed content (voice actor names, song credits).
"""
from pathlib import Path

TSV_PATH = Path("translation_data/translated_script.tsv")
TARGET_VA = "0x02077581"

# Edit this to your name/handle
CREDIT_TEXT = "Fan Translation by dark_seis"

APPEND_BLOCK = f"␤␤Fan Translation␤{CREDIT_TEXT}␤(Unofficial, not affiliated with KONAMI or AVEX)␤"


def main():
    with open(TSV_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    hdr = lines[0].rstrip("\n").split("\t")
    i_va = hdr.index("ram_va")
    i_en = hdr.index("english")

    found = False
    for idx, line in enumerate(lines[1:], start=1):
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) <= max(i_va, i_en):
            continue
        if parts[i_va] == TARGET_VA:
            before = parts[i_en]
            parts[i_en] = before + APPEND_BLOCK
            lines[idx] = "\t".join(parts) + "\n"
            found = True
            print(f"Found row at line {idx}, va={TARGET_VA}")
            print(f"  Before: {before[-80:]!r}")
            print(f"  After:  {parts[i_en][-120:]!r}")
            break

    if not found:
        print(f"ERROR: va={TARGET_VA} not found in {TSV_PATH}")
        return

    with open(TSV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"\nWrote {TSV_PATH}")


if __name__ == "__main__":
    main()
