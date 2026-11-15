# BS 侦探俱乐部 广播推送终端

<p align="center">
  <b>简体中文</b> · <a href="README.en.md">English</a>
</p>

本项目基于 [BS-Zelda-Satellaview-Terminal](https://github.com/kiriqaq/BS-Zelda-Satellaview-Terminal) ，是特定为<strong>《BS侦探俱乐部 \~雪中消失的过去\~》银河战士贴吧社区版本汉化</strong>所制作的第三方辅助工具。功能与原项目基本相同，通过 Python 与 Mesen 模拟器联动，在虚拟时钟走到 18:00 的瞬间把广播数据推进模拟器的 `Satellaview/` 目录，同时开始播放对应的 `.wav` 广播音轨，以此模拟 Satellaview 游戏的实时同步广播功能。

《BS侦探俱乐部 \~雪中消失的过去\~》为纯 SoundLink 游戏，相较于《BS塞尔达传说》不再提供“视频遮罩"与"结算单"等内容，但由于游戏中篇存在游戏内发音场景，仍需要额外的Lua脚本进行捕获。

## 使用要求

* **软件环境**：
    * Windows 10 / 11 系统。
    * Python 3.9 或更高版本。
    * [Mesen 模拟器](https://www.mesen.ca/)（本项目的测试版本为 MesenCE-2.2.1 ）。
* **核心 BIOS**：自备日文无DRM版本的 BS-X BIOS 固件，例如 `BS-X BIOS (Japan) [No DRM].sfc`。
* **广播数据**：`bstantei/` 目录（广场 `0/`、三篇 `1/` `2/` `3/` 与 `wav/`），请自备并放在 Mesen 模拟器根目录（与本程序同级即可）。

## 构建流程

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置模拟器**：
   * 下载并安装 Mesen，**必须**选择 `Store the data in same folder as the application`，且**路径不要带中文**。
   * 关闭模拟器。

3. **启动程序**：
   * 运行 `python main.py`。
   * 程序会自动识别同目录下的 `Mesen.exe`，识别结果与 BIOS 路径在“显示监视面板 / 高级设置”里各有一行只读输入框（`Mesen` / `BIOS`）。
   * 换 BIOS 会覆盖本地那份；已有文件时会先弹确认框。
   * 选择要推送的篇章：**前篇 / 中篇 / 后篇**。
   * 可在“显示监视面板 / 高级设置”右下角切换中文 / English 语言。
   * 点击第 3 步按钮，程序将自行启动 Mesen 模拟器，中篇还会额外启动Lua脚本。时钟走到 **18:00:00** 触发推送并起播音频，正式放送游戏。
   
4. **注意事项**：
   * **请勿使用含中文的目录**。
   * 请勿在运行中关闭或修改 Lua 脚本。
   * 《BS侦探俱乐部 \~雪中消失的过去\~》的存档继承属性不强，只有调查指数的数值会在放送结束后进行总结，不影响任何游戏体验。本软件仍保留了 BS 塞尔达传说 广播推送终端的“删除存档”功能，使用后会清空全部 BS 相关存档，请酌情使用。

## 许可证

本项目采用 **MIT License** 开源，可以自由使用、修改和分发，但请保留原作者信息。

本项目使用的思源黑体（Source Han Sans）由 Adobe 与 Google 共同开发，采用 [SIL Open Font License 1.1](https://openfontlicense.org) 授权。Copyright © 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.
