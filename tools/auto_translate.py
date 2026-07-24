import re
import sys
import time
import deepl

API_KEY = "55f95817-55d0-428e-b29d-34f82a8392ca:fx"
TSV_PATH = "translation_data/translated_script.tsv"
SAVE_EVERY = 50

PLACEHOLDER_RE = re.compile(r"\[(NAME|MONEY|PRICE|TIME|DAYS|COST|VAL)\]")


def protect_placeholders(text):
    tokens = []

    def repl(m):
        tokens.append(m.group(0))
        return f"§{len(tokens)-1}§"

    protected = PLACEHOLDER_RE.sub(repl, text)
    return protected, tokens


def restore_placeholders(text, tokens):
    def repl(m):
        idx = int(m.group(1))
        return tokens[idx] if idx < len(tokens) else m.group(0)

    return re.sub(r"§(\d+)§", repl, text)


def sanitize_for_tsv(text):
    """Match the toolkit's own escaping: no raw newlines or tabs in a field."""
    return text.replace("\r\n", "␤").replace("\n", "␤").replace("\t", " ")


def unsanitize_from_tsv(text):
    return text.replace("␤", "\n")


def main():
    translator = deepl.Translator(API_KEY)

    with open(TSV_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    hdr = lines[0].rstrip("\n").split("\t")
    i_dec = hdr.index("decoded")
    i_en = hdr.index("english")

    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        while len(parts) < len(hdr):
            parts.append("")
        rows.append(parts)

    todo_idx = [
        idx for idx, parts in enumerate(rows)
        if parts[i_dec].strip() and not parts[i_en].strip()
    ]
    print(f"Total rows: {len(rows)}  |  Already translated: {len(rows) - len(todo_idx)}  |  To translate: {len(todo_idx)}")

    def save():
        out_lines = [lines[0]]
        for parts in rows:
            out_lines.append("\t".join(parts) + "\n")
        with open(TSV_PATH, "w", encoding="utf-8") as f:
            f.writelines(out_lines)

    done = 0
    try:
        for idx in todo_idx:
            parts = rows[idx]
            jp_text = unsanitize_from_tsv(parts[i_dec])
            protected, tokens = protect_placeholders(jp_text)

            try:
                result = translator.translate_text(protected, source_lang="JA", target_lang="EN-US")
                english = restore_placeholders(result.text, tokens)
                parts[i_en] = sanitize_for_tsv(english)
            except Exception as e:
                print(f"  [SKIP] error on row {idx}: {e}")
                continue

            done += 1
            if done % SAVE_EVERY == 0:
                save()
                print(f"  ...saved progress at {done}/{len(todo_idx)}")
                time.sleep(0.3)
    except KeyboardInterrupt:
        print("\nInterrupted — saving progress before exit...")
        save()
        print(f"Saved. Translated {done} rows this run.")
        sys.exit(0)

    save()
    print(f"Done. Translated {done} rows.")


if __name__ == "__main__":
    main()