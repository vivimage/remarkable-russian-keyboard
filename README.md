# Russian keyboard for reMarkable

Adds a Russian (ЙЦУКЕН) layout to the reMarkable on-screen keyboard.

- Three rows of 11 keys, the same width as the built-in German and Nordic layouts.
- Long-press `е` for `ё` and `ь` for `ъ`.
- On the symbols page, long-press `$` for `₽`, `"` for `« » „ “`, and `#` for `№`.

Tested on a reMarkable Paper Pure with OS 3.28.0.172. Other devices and versions are untested.

## Install

Requires [xovi](https://github.com/asivery/xovi) with qt-resource-rebuilder.

Copy `russian-keyboard.rcc` to `/home/root/xovi/exthome/qt-resource-rebuilder/` and restart xovi.
Then open the keyboard, tap the globe key and choose Russian.

To remove it, delete that file and restart xovi.

## How it works

The stock keyboard lists every layout it finds under `:/misc/keyboards/<locale>/keyboard_layout.json`
in its Qt resources. The `.rcc` file adds one more entry, `ru_RU`. No stock file is replaced or patched.

## Quick language switch (separate, optional)

`keyboardQuickSwitch.qmd` changes the globe key on the on-screen keyboard. It works with any pair of languages and does not need the Russian layout.

- Tap the globe key to switch to the language you used before the current one.
- Hold the globe key to open the full language list.
- Until two languages have been used, a tap opens the list as before.

Copy `keyboardQuickSwitch.qmd` to `/home/root/xovi/exthome/qt-resource-rebuilder/` and restart xovi. Delete the file and restart to remove it.

The previous language is remembered in `/home/root/.config/remarkable/keyboard-previous-language`.
The file is a hashed qmldiff patch for `KeyboardPanel.qml`, written for OS 3.28 and tested on a Paper Pure with OS 3.28.0.172.

## Build

```sh
python3 make_layout.py ru_RU_keyboard_layout.json
python3 make_rcc.py build russian-keyboard.rcc misc/keyboards/ru_RU/keyboard_layout.json=ru_RU_keyboard_layout.json
```

`make_rcc.py` writes an uncompressed Qt resource file (format version 1) and needs only Python 3.
