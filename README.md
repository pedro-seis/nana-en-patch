# NANA: Live Staff Daiboshuu! Shoshinsha Kangei — English Fan Translation

An unofficial English fan translation patch for *NANA: Live Staff Daiboshuu! Shoshinsha Kangei!* (Nintendo DS, Konami, 2007), a Japan-only Caravan/promotional demo build based on the *NANA* manga/anime series.

**This is a fan project. It is not affiliated with, endorsed by, or sponsored by Konami, Yazawa Manga Seisakusho, VAP, Madhouse, NTV, or AVEX Entertainment.**

---

## What this is

- A patch that translates the game's dialogue, menus, UI buttons, and most on-screen graphics from Japanese to English.
- Built using [it-was-katsumata's nds-halfwidth-translation-engine](https://github.com/it-was-katsumata/nds-halfwidth-translation-engine) — an open-source, reverse-engineered toolkit for this specific title. All credit for cracking the game's custom script/graphics format goes to that project.
- Machine-translated (DeepL) as a first pass, not professionally localized. Grammar and tone are generally solid, but expect occasional awkward phrasing.

## What this is NOT

- This is **not a ROM**. No copyrighted game files are included. You must supply your own legally obtained copy of the game.
- Not a complete, polished, professional localization — see "Known limitations" below.

---

## Requirements

- Your own legally dumped copy of `NANA.nds`
- An xdelta3 patcher:
  - Command line: [xdelta3](https://github.com/jmacd/xdelta) (Windows/Mac/Linux builds available)
  - GUI alternative: **Delta Patcher** (easier for non-technical users)
- An NDS emulator (**DeSmuME**, **melonDS**) or a flashcart / TWiLight Menu++ setup for real hardware

---

## How to apply the patch

### Command line (xdelta3)
```
xdelta3 -d -s NANA.nds NANA_EN_patch.xdelta NANA_EN.nds
```
- `-d` = decode/apply
- `-s NANA.nds` = your original Japanese ROM
- `NANA_EN_patch.xdelta` = this patch file
- `NANA_EN.nds` = output filename for the patched, translated ROM

### GUI (Delta Patcher or similar)
1. Open the patcher tool
2. Select your original `NANA.nds` as the source file
3. Select `NANA_EN_patch.xdelta` as the patch
4. Apply — this produces a new, patched `.nds` file

---

## Known limitations

Coverage is broad but not exhaustive. The following remain untranslated or partially translated:

- **Sevens card minigame** — some text still in Japanese
- **Interview minigame** — some text still in Japanese
- **Calendar / clock HUD** (e.g. "1ヶ月目 01日(金) PM 08:00") — rendered by a runtime formatter, not static text, and can't be translated with current tooling
- **Flea-market money bar and month counter** — labels are translated, but one baked tile display remains Japanese
- **Character profile / stats panel** on the System menu
- A small number of other lines throughout the game that weren't captured by the current script mapping — this is an ongoing hobby project, not a finished commercial localization

If you find something and want to help, feel free to report it (see Credits/Contact below) or dig in yourself — the toolkit this patch is built on is open source.

---

## Credits

- **Reverse engineering & translation toolkit**: [it-was-katsumata](https://github.com/it-was-katsumata/nds-halfwidth-translation-engine) — cracked the game's custom script bytecode, text encoding, ARM9 hook architecture, and graphics compression from scratch
- **English translation (this patch)**: darkseis
- Original game: © Yazawa Manga Seisakusho / Shueisha / VAP / Madhouse / NTV, © 2007 Konami Digital Entertainment Co., Ltd.

---

## Legal

This patch is distributed as a binary diff (xdelta) and contains no copyrighted assets from the original game. You are responsible for obtaining your own legal copy of the ROM to apply this patch to. This project is non-commercial and made for preservation/accessibility purposes by fans, for fans.
