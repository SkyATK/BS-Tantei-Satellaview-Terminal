# BS Tantei Club Satellaview Terminal

<p align="center">
  <a href="README.md">简体中文</a> · <b>English</b>
</p>

A third-party companion tool built on top of [BS-Zelda-Satellaview-Terminal](https://github.com/kiriqaq/BS-Zelda-Satellaview-Terminal), made specifically for the **YinHeZhanShi Tieba community's Chinese translation of *BS Tantei Club: Yuki ni Kieta Kako***. It does the same job as the original project: through Python it drives the Mesen emulator and, at the instant the virtual clock reaches 18:00, drops the broadcast data into the emulator's `Satellaview/` folder while starting the matching `.wav` broadcast track — reproducing the real-time, synchronized Satellaview broadcast of the original game.

*BS Tantei Club: Yuki ni Kieta Kako* is a SoundLink-only title. Compared with *BS The Legend of Zelda* it no longer has a "video overlay" or a "results screen", but the chuuhen chapter does contain in-game music scenes, which still need an extra Lua script to catch.

## Requirements

* **Environment**
    * Windows 10 / 11.
    * Python 3.9 or newer.
    * [Mesen](https://www.mesen.ca/) (tested with MesenCE-2.2.1).
* **BIOS**: bring your own Japanese, DRM-free BS-X BIOS, e.g. `BS-X BIOS (Japan) [No DRM].sfc`.
* **Broadcast data**: the `bstantei/` folder (plaza `0/`, the three chapters `1/` `2/` `3/`, and `wav/`). Put it in the Mesen root folder (sitting next to this program is fine).

## Build & Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the emulator**
   * Install Mesen and **make sure to pick** `Store the data in same folder as the application`. **Keep the path free of non-ASCII characters** (Chinese characters will break it).
   * Close the emulator.

3. **Start the program**
   * Run `python main.py`.
   * `Mesen.exe` in the same folder is detected automatically. The resolved Mesen / BIOS paths are shown as two read-only fields (`Mesen` / `BIOS`) under "Monitor panel / Advanced settings".
   * Replacing the BIOS overwrites the local copy; if the file already exists, a confirmation dialog appears first.
   * Choose the chapter to broadcast: **Zenhen / Chuuhen / Kouhen**.
   * 简体中文 / English can be switched at the bottom-right of "Monitor panel / Advanced settings".
   * Press the step-3 button: the program launches Mesen itself (Chuuhen also loads the Lua script). When the clock reaches **18:00:00** the broadcast is pushed and the audio starts.

4. **Notes**
   
   * **Do not use paths containing Chinese characters.**
   * Do not close or modify the Lua script while it is running.
   * Save inheritance in *BS Tantei Club* is weak — only the investigation points are totalled up after the broadcast ends, and it affects nothing else. The "Delete save data" feature inherited from the BS Zelda terminal is still present; it wipes **all** BS-related saves, so use it at your own discretion.

## License

Released under the **MIT License** — free to use, modify and redistribute, but please keep the original author's notices.

This project bundles Source Han Sans, developed jointly by Adobe and Google and licensed under the [SIL Open Font License 1.1](https://openfontlicense.org). Copyright © 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.
