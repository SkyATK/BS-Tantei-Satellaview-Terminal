# BS Tantei Club Satellaview Terminal

<p align="center">
  <a href="README.md">简体中文</a> · <b>English</b>
</p>

**Current version: 1.02**

This project is based on [BS-Zelda-Satellaview-Terminal](https://github.com/kiriqaq/BS-Zelda-Satellaview-Terminal) and is a third-party companion tool made specifically for the **Chinese fan translation of *BS Tantei Club: Yuki ni Kieta Kako*** by the **YinHeZhanShi Tieba community**. It works essentially the same as the original project: driven by Python, it hooks up with the Mesen emulator and, at the instant the virtual clock reaches 18:00, drops the broadcast data into the emulator's `Satellaview/` folder while starting the matching `.wav` broadcast track, reproducing the real-time, synchronized Satellaview broadcast of the original game.

*BS Tantei Club: Yuki ni Kieta Kako* is a SoundLink-only title. Compared with *BS The Legend of Zelda* it no longer provides a "video overlay" or a "results screen", but the Chuuhen chapter does contain in-game sound scenes, which still need an extra Lua script to catch.

## Requirements

* **Environment**:
    * Windows 10 / 11.
    * Python 3.9 or newer.
    * [Mesen](https://www.mesen.ca/) (tested with MesenCE-2.2.1).
* **Core BIOS**: bring your own Japanese, DRM-free BS-X BIOS firmware, e.g. `BS-X BIOS (Japan) [No DRM].sfc`.
* **Broadcast data**: the `bstantei/` folder (the plaza `0/`, the three chapters `1/` `2/` `3/`, and `wav/`). Bring your own and put it in the Mesen root folder (sitting next to this program is fine).

## Build & Run

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the emulator**:
   * Download and install Mesen; you **must** pick `Store the data in same folder as the application`, and **keep the path free of Chinese characters**.
   * Close the emulator.

3. **Start the program**:
   * Run `python main.py`.
   * `Mesen.exe` in the same folder is detected automatically. The detected result and the BIOS path are shown as one read-only field each (`Mesen` / `BIOS`) under "Monitor panel / Advanced settings".
   * On first use a character must be created first: follow the flow to create the character, and close the Mesen window only after you have entered the town. After that you can push broadcast data.
   * Choose the chapter to push: **Zenhen / Chuuhen / Kouhen**.
   * 简体中文 / English can be switched at the bottom-right of "Monitor panel / Advanced settings".
   * Press the Step 3 button and the program launches Mesen itself; for Chuuhen it also loads the Lua script. When the clock reaches **18:00:00** the push fires, the audio starts, and the game goes on air.

4. **Notes**:
   * **Do not use directories containing Chinese characters.**
   * Do not close or modify the Lua script while it is running.

## License

Released under the **MIT License**: free to use, modify and redistribute, but please keep the original author's notices.

This project bundles Source Han Sans, developed jointly by Adobe and Google and licensed under the [SIL Open Font License 1.1](https://openfontlicense.org). Copyright © 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.
