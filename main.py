import atexit
import configparser
import ctypes
import json
import os
import shutil

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except (AttributeError, OSError):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass
import subprocess
import sys
import threading
import time
import traceback
import wave
from datetime import datetime, timedelta
from tkinter import (Tk, Label, Frame, Button, Checkbutton, Entry, Spinbox, Canvas,
                     StringVar, BooleanVar, Text, filedialog, messagebox, TclError)
import tkinter.font as tkfont

LANG_DEFAULT = "zh"
LANG_CODES = ("zh", "en")
LANG_LABELS = {"zh": "简体中文", "en": "English"}
_TEXTS = {
    "app.title": {"zh": "Satellaview Terminal · BS 侦探俱乐部 1.01",
                  "en": "Satellaview Terminal · BS Tantei Club 1.01"},
    "ui.clock_title": {"zh": "虚拟广播时钟", "en": "Broadcast clock"},
    "ui.chapter_label": {"zh": "推送篇章：", "en": "Chapter:"},
    "ui.monitor_toggle": {"zh": "显示监视面板 / 高级设置", "en": "Monitor panel / Advanced settings"},
    "ui.lang_label": {"zh": "语言", "en": "Language"},
    "lbl.mesen": {"zh": "Mesen", "en": "Mesen"},
    "lbl.bios": {"zh": "BIOS", "en": "BIOS"},
    "lbl.audio": {"zh": "音频", "en": "Audio"},
    "lbl.offset": {"zh": "起点偏移(ms)", "en": "Offset(ms)"},
    "lbl.boot": {"zh": "开播等待", "en": "Boot delay"},
    "lbl.sec": {"zh": "秒", "en": "s"},
    "btn.browse": {"zh": "浏览", "en": "Browse"},
    "btn.default": {"zh": "默认", "en": "Default"},
    "chk.pin_top": {"zh": "窗口置顶", "en": "Always on top"},
    "chapter.zenhen": {"zh": "前篇", "en": "Zenhen"},
    "chapter.chuuhen": {"zh": "中篇", "en": "Chuuhen"},
    "chapter.kouhen": {"zh": "后篇", "en": "Kouhen"},
    "btn.step1": {"zh": "第 1 步：选择模拟器根目录的 Mesen.exe",
                  "en": "Step 1: Select Mesen.exe"},
    "btn.step2": {"zh": "第 2 步：选择 前篇 / 中篇 / 后篇",
                  "en": "Step 2: Choose Zenhen / Chuuhen / Kouhen"},
    "btn.step3": {"zh": "第 3 步：点击开始，将在 {boot} 秒后推送广播",
                  "en": "Step 3: Start — push in {boot} s"},
    "btn.delete_save": {"zh": "删除存档（需先关闭模拟器）",
                        "en": "Delete save data (close the emulator first)"},
    "stat.name_audio": {"zh": "音频", "en": "Audio"},
    "stat.name_lag": {"zh": "滞后", "en": "Lag"},
    "stat.name_rate": {"zh": "漂移率", "en": "Drift"},
    "stat.name_mute": {"zh": "静音", "en": "Mute"},
    "mute.off": {"zh": "未静音", "en": "not muted"},
    "mute.fading": {"zh": "静音（渐弱中）", "en": "muting (fade out)"},
    "mute.on": {"zh": "静音中 → {t} 恢复", "en": "muted → resumes {t}"},
    "mute.resuming": {"zh": "恢复（渐强中）", "en": "resuming (fade in)"},
    "status.pick_mesen": {"zh": "请定位模拟器的主程序 Mesen.exe",
                          "en": "Locate the emulator: Mesen.exe"},
    "status.pick_chapter": {"zh": "请选择要推送的篇章：前篇 / 中篇 / 后篇",
                            "en": "Choose the chapter to broadcast: Zenhen / Chuuhen / Kouhen"},
    "status.hint_chapter_click": {"zh": "请点击下方 前篇 / 中篇 / 后篇 选择要推送的篇章",
                                  "en": "Click Zenhen / Chuuhen / Kouhen below to pick a chapter"},
    "status.chapter_locked": {"zh": "已锁定：{name}{dur}{hint}\n点击第 3 步按钮，{boot} 秒后推送广播",
                              "en": "Locked: {name}{dur}{hint}\nClick Step 3 to push in {boot} s"},
    "status.dur_suffix": {"zh": "，音频 {dur}", "en": " · audio {dur}"},
    "status.id_collision": {"zh": "⚠️ 第 {n} 章与广场的广播 ID 完全相同\n固件会认为数据未更新 → 不会切章",
                            "en": "⚠️ Chapter {n} has the same broadcast ID as the plaza\n"
                                  "Firmware will treat it as no update → the chapter won't switch"},
    "status.booting": {"zh": "正在推送初始数据（广场）…", "en": "Pushing initial data (plaza)…"},
    "status.booting_toast": {"zh": "广场数据已推送，{boot} 秒后开播…",
                             "en": "Plaza data pushed · on air in {boot} s…"},
    "status.playing": {"zh": "广播中 · 正在播放音频", "en": "On air · playing audio"},
    "status.play_running": {"zh": "广播中 · 音频 {pos}{total}\n滞后 {lag}{muted}",
                            "en": "On air · audio {pos}{total}\nLag {lag}{muted}"},
    "status.total_suffix": {"zh": " / {t}", "en": " / {t}"},
    "status.muted_tag": {"zh": "　[静音中]", "en": "  [muted]"},
    "status.mesen_closed_stopped": {"zh": "Mesen 已关闭 · 已停止播放",
                                    "en": "Mesen closed · playback stopped"},
    "status.lua_stopped_closing": {"zh": "Lua 脚本已停止 · 正在关闭 Mesen",
                                   "en": "Lua script stopped · closing Mesen"},
    "status.mesen_closed_reset": {"zh": "Mesen 已关闭 · 已停止并回到初始状态\n请重新选择要推送的篇章",
                                  "en": "Mesen closed · stopped, back to start\n"
                                        "Choose the chapter again"},
    "status.lua_closed_reset": {"zh": "Lua 脚本窗口已关闭 · 已关闭 Mesen 并回到初始状态\n"
                                     "请重新选择要推送的篇章",
                                "en": "Lua script window closed · Mesen closed, back to start\n"
                                      "Choose the chapter again"},
    "status.finished_reset": {"zh": "播放结束 · 已关闭 Mesen 并回到初始状态\n请重新选择要推送的篇章",
                              "en": "Playback finished · Mesen closed, back to start\n"
                                    "Choose the chapter again"},
    "status.finished_in3": {"zh": "播放结束\n3 秒后回到初始状态…", "en": "Playback finished\nResetting in 3 s…"},
    "status.finished_k": {"zh": "播放结束 · 漂移率 k={k}（{pct}%）",
                          "en": "Finished · drift k={k} ({pct}%)"},
    "status.finished": {"zh": "播放结束", "en": "Playback finished"},
    "status.error": {"zh": "出错：{e}", "en": "Error: {e}"},
    "status.bios_missing": {"zh": "错误：BS-X BIOS 未配置", "en": "Error: BS-X BIOS not configured"},
    "status.bios_missing_entry": {"zh": "（缺失，点右侧「浏览」选择）",
                                  "en": "(missing — click Browse on the right)"},
    "hint.lua": {"zh": "，请勿修改或关闭Lua脚本",
                 "en": " — do not edit or close the Lua script"},
    "dlg.files_exe": {"zh": "可执行文件", "en": "Executables"},
    "dlg.files_bios": {"zh": "BS-X BIOS / SFC", "en": "BS-X BIOS / SFC"},
    "dlg.files_all": {"zh": "所有文件", "en": "All files"},
    "dlg.files_wav": {"zh": "WAV", "en": "WAV"},
    "dlg.pick_mesen": {"zh": "请选择模拟器根目录的 Mesen.exe",
                       "en": "Select Mesen.exe in the emulator folder"},
    "dlg.pick_bios": {"zh": "请选择 BS-X BIOS", "en": "Select the BS-X BIOS"},
    "dlg.replace_bios": {"zh": "更换 BIOS", "en": "Replace BIOS"},
    "dlg.replace_bios_msg": {"zh": "将用选中的文件覆盖：\n{name}\n\n继续吗？",
                             "en": "This will overwrite:\n{name}\n\nContinue?"},
    "dlg.error": {"zh": "错误", "en": "Error"},
    "dlg.bios_copy_fail": {"zh": "无法复制 BIOS：{e}", "en": "Cannot copy the BIOS: {e}"},
    "dlg.bios_check": {"zh": "BS-X BIOS 检查", "en": "BS-X BIOS check"},
    "dlg.bios_check_msg": {"zh": "未找到 BS-X BIOS，请手动选择日文 BIOS 文件。",
                           "en": "BS-X BIOS not found. Please pick the Japanese BIOS file."},
    "dlg.notice": {"zh": "提示", "en": "Notice"},
    "dlg.pick_chapter_first": {"zh": "请先选择篇章，再指定该篇章的音频。",
                               "en": "Choose a chapter first, then pick its audio."},
    "dlg.pick_wav": {"zh": "选择要播放的广播音频", "en": "Select the broadcast audio to play"},
    "dlg.cannot_start": {"zh": "无法开始", "en": "Cannot start"},
    "dlg.mesen_missing": {"zh": "未找到 Mesen.exe，请重新选择。",
                          "en": "Mesen.exe not found — please select it again."},
    "dlg.chapter_missing": {"zh": "请先选择篇章。", "en": "Choose a chapter first."},
    "dlg.files_missing": {"zh": "缺少文件", "en": "Missing files"},
    "dlg.file_missing_msg": {"zh": "{name} 不存在：\n{p}", "en": "{name} not found:\n{p}"},
    "dlg.bad_param": {"zh": "参数错误", "en": "Invalid value"},
    "dlg.offset_int": {"zh": "起点偏移必须是整数（毫秒）。",
                       "en": "Start offset must be an integer (ms)."},
    "dlg.del_save": {"zh": "删除存档确认", "en": "Confirm save deletion"},
    "dlg.del_save_msg": {"zh": "确定删除 BS-X BIOS 存档（Saves/BsxBios.srm）吗？\n"
                              "会清除游戏内注册的角色与全部广播游戏进度。",
                         "en": "Delete the BS-X BIOS save (Saves/BsxBios.srm)?\n"
                               "This clears the registered character and all broadcast progress."},
    "dlg.ok": {"zh": "成功", "en": "Done"},
    "dlg.save_deleted": {"zh": "存档已删除。", "en": "Save deleted."},
    "dlg.save_not_found": {"zh": "未找到存档文件，无需删除。",
                           "en": "No save file found — nothing to delete."},
    "dlg.save_del_fail": {"zh": "无法删除存档：{e}\n请先关闭 Mesen。",
                          "en": "Cannot delete the save: {e}\nClose Mesen first."},
    "dlg.save_del_running": {"zh": "检测到 Mesen 仍在运行，存档没有删除。\n"
                                   "请先关闭 Mesen 窗口，再点「删除存档」。",
                             "en": "Mesen is still running — the save was NOT deleted.\n"
                                   "Close Mesen first, then click Delete save data again."},
    "log.mesen_selected": {"zh": "[模拟器] {path}", "en": "[Emulator] {path}"},
    "log.mesen_auto": {"zh": "[模拟器] 自动识别 {path}", "en": "[Emulator] auto-detected {path}"},
    "log.ini_loaded": {"zh": "[配置] 已读取 {path}", "en": "[Config] loaded {path}"},
    "log.ini_absent": {"zh": "[配置] 未找到 {path}，全部按自动查找",
                       "en": "[Config] {path} not found — auto-detect only"},
    "log.ini_item": {"zh": "[配置] {name} = {path}{tag}", "en": "[Config] {name} = {path}{tag}"},
    "log.ini_item_bad": {"zh": "  🔴 路径不存在", "en": "  🔴 does not exist"},
    "log.ini_mesen_missing": {"zh": "[配置] mesen 指向的路径不存在：{path}（改回自动查找）",
                             "en": "[Config] mesen path not found: {path} (falling back to auto-detect)"},
    "log.data_auto": {"zh": "[配置] data 未设置，自动定位广播数据：{dir}",
                      "en": "[Config] data not set, broadcast data resolved to {dir}"},
    "log.ini_written": {"zh": "[配置] 已写回 config.ini：{name} = {path}",
                        "en": "[Config] written back to config.ini: {name} = {path}"},
    "log.ini_auto_saved": {"zh": "[配置] 自动记住到 config.ini：{name} = {path}",
                           "en": "[Config] remembered to config.ini: {name} = {path}"},
    "log.ini_cleared": {"zh": "[配置] 已清空 config.ini 的 {name}（改回自动查找）",
                        "en": "[Config] cleared {name} in config.ini (auto-detect again)"},
    "log.ini_write_fail": {"zh": "[配置] 写不回 config.ini：{e}",
                           "en": "[Config] cannot write config.ini: {e}"},
    "lbl.data": {"zh": "数据目录", "en": "Data dir"},
    "log.data_looks_wrong": {"zh": "[配置] 注意：{dir} 下没有 0/1/2/3 子目录",
                             "en": "[Config] note: no 0/1/2/3 subfolders under {dir}"},
    "dlg.pick_data": {"zh": "请选择 bstantei 目录（其下有 0 1 2 3 和 wav）",
                      "en": "Select the bstantei folder (it contains 0 1 2 3 and wav)"},
    "log.bios_selected": {"zh": "[BIOS] {name}", "en": "[BIOS] {name}"},
    "log.bios_replaced": {"zh": "[BIOS] 已替换为 {name}（源 {src}）",
                          "en": "[BIOS] replaced with {name} (from {src})"},
    "log.bios_placed": {"zh": "[BIOS] 已放入根目录: {name}", "en": "[BIOS] placed in root: {name}"},
    "log.chapter": {"zh": "[篇章] {name}（week {n}）{dur}{hint}",
                    "en": "[Chapter] {name} (week {n}){dur}{hint}"},
    "log.broadcast_id": {"zh": "[广播ID] 广场={a}  第{n}章={b}{tag}",
                         "en": "[Broadcast ID] plaza={a}  chapter{n}={b}{tag}"},
    "log.id_same": {"zh": "  🔴 撞车：换周不会触发！", "en": "  🔴 identical: the week won't trigger!"},
    "log.id_ok": {"zh": "  ✓ 不同，可触发", "en": "  ✓ different, will trigger"},
    "log.audio_custom": {"zh": "[音频] 指定 {name}{info}", "en": "[Audio] using {name}{info}"},
    "log.audio_default": {"zh": "[音频] 恢复默认音频", "en": "[Audio] back to the default audio"},
    "log.cfg_backup": {"zh": "[配置] 原始 settings.json 已备份 -> {path}",
                       "en": "[Config] original settings.json backed up -> {path}"},
    "log.patch": {"zh": "[配置] {k}: {v}", "en": "[Config] {k}: {v}"},
    "patch.fps": {"zh": "帧率", "en": "Frame rate"},
    "patch.lua": {"zh": "Lua", "en": "Lua"},
    "patch.shortcuts": {"zh": "快捷键", "en": "Shortcuts"},
    "patch.shortcuts_cleared": {"zh": "已清空 {n} 项时间轴快捷键",
                                "en": "{n} timeline shortcuts cleared"},
    "log.cfg_missing": {"zh": "[配置] ⚠️ settings.json 不存在，跳过补丁（BS-X 时间可能不对）",
                        "en": "[Config] ⚠️ settings.json not found, patch skipped (BS-X time may be wrong)"},
    "log.sat_cleared": {"zh": "[1/5] Satellaview/ 清空 {n} 项，拷入广场数据 {ok} 个{skipped}",
                        "en": "[1/5] Satellaview/ cleared {n} items, plaza data copied: {ok}{skipped}"},
    "log.skipped": {"zh": "（跳过 {n} 个非文件）", "en": " (skipped {n} non-files)"},
    "log.lua_missing": {"zh": "[脚本] ⚠️ 未找到 {name}，静音不可用",
                        "en": "[Script] ⚠️ {name} not found, muting unavailable"},
    "log.launch": {"zh": "[2/5] 启动 Mesen：{exe}{lua}", "en": "[2/5] Launching Mesen: {exe}{lua}"},
    "log.launch_lua": {"zh": " + {name}", "en": " + {name}"},
    "log.launch_nolua": {"zh": "（不加载 lua）", "en": " (no lua)"},
    "log.clock": {"zh": "[3/5] 虚拟时钟 {start} → 18:00:00（{boot}s）",
                  "en": "[3/5] Virtual clock {start} → 18:00:00 ({boot}s)"},
    "log.chapter_pushed": {"zh": "[4/5] 推送章节数据 {ok} 个 -> Satellaview/{skipped}",
                           "en": "[4/5] Chapter data pushed: {ok} -> Satellaview/{skipped}"},
    "log.audio_dev": {"zh": "[音频] 设备={dev} buffer={frames} 帧",
                      "en": "[Audio] device={dev} buffer={frames} frames"},
    "log.offset_late": {"zh": "[音频] 起点偏移 +{ms}ms：延后 {s:.3f}s 起播",
                        "en": "[Audio] start offset +{ms}ms: playback delayed by {s:.3f}s"},
    "log.offset_skip": {"zh": "[音频] 起点偏移 {ms}ms：跳过开头 {s:.3f}s",
                        "en": "[Audio] start offset {ms}ms: skipping first {s:.3f}s"},
    "log.play": {"zh": "[5/5] 播放 {name}", "en": "[5/5] Playing {name}"},
    "log.abort_wait": {"zh": "[中止] 用户在等待期停止。", "en": "[Abort] stopped by user while waiting."},
    "log.abort": {"zh": "[中止] 用户停止。", "en": "[Abort] stopped by user."},
    "log.mesen_closed_wait": {"zh": "[退出] 等待期检测到 Mesen 已关闭 → 停止推送，回到初始状态。",
                              "en": "[Exit] Mesen closed while waiting → push stopped, back to start."},
    "log.mesen_closed_play": {"zh": "[退出] 检测到 Mesen 已关闭 → 停止音频与推送，回到初始状态。",
                              "en": "[Exit] Mesen closed → audio and push stopped, back to start."},
    "log.no_closed_marker": {"zh": "[脚本] ⚠️ 未找到 script_closed.txt，已查目录: {dirs}",
                             "en": "[Script] ⚠️ script_closed.txt not found, looked in: {dirs}"},
    "log.no_script_window": {"zh": "[脚本] 没在 Mesen 里认出脚本窗口（标题可能是本地化的），当前窗口: {titles}",
                             "en": "[Script] no script window recognised in Mesen (title may be localized), "
                                   "windows: {titles}"},
    "log.flag_file": {"zh": "[静音] 标记文件 {path}", "en": "[Mute] flag file {path}"},
    "log.exits": {"zh": "[静音] 恢复时刻（音频内容）{a} → 真实时间 {b}（起点偏移 {ms} 已计入，整条时间轴一起平移）",
                  "en": "[Mute] resume points (audio content) {a} → real time {b} "
                        "(start offset {ms} included; the whole timeline shifts together)"},
    "log.flag_missing": {"zh": "[静音] ⚠️ 标记文件暂不存在 —— 需 Mesen 里加载 scene_mute.lua（AllowIoOsPermission）；"
                               "未加载则静音不触发。",
                         "en": "[Mute] ⚠️ flag file not there yet — load scene_mute.lua in Mesen "
                               "(AllowIoOsPermission); muting will not fire without it."},
    "log.marker_found": {"zh": "[静音] 已检测到标记文件", "en": "[Mute] flag file detected"},
    "log.marker_ready": {"zh": "[脚本] 关闭标记已就位：{path}",
                         "en": "[Script] close marker in place: {path}"},
    "log.enter_rejected": {"zh": "[静音] t={t} 收到进入 #{seq}，但 {why} → 不静音",
                           "en": "[Mute] t={t} got entry #{seq}, but {why} → not muting"},
    "log.enter_accept": {"zh": "[静音] t={t} 进入发声场景 #{seq} → 渐弱到 0（继续播放），固定于 {exit} 恢复",
                         "en": "[Mute] t={t} entered sound scene #{seq} → fading to 0 (keeps playing), "
                               "resumes at {exit}"},
    "log.rescan": {"zh": "[静音] 已定位标记文件 {path}", "en": "[Mute] flag file located: {path}"},
    "log.restore": {"zh": "[静音] 到恢复时刻（t={t}）→ 渐强 0.5s（本次静音 {held:.1f}s，音频全程未停）",
                    "en": "[Mute] resume point reached (t={t}) → fading in 0.5s "
                          "(muted {held:.1f}s, audio never stopped)"},
    "log.lag_line": {"zh": "  {w} | 音频 {pos} | 滞后 {lag}{tag}",
                     "en": "  {w} | audio {pos} | lag {lag}{tag}"},
    "log.stats": {"zh": "[统计] {n} 点：播放速率 k={k:.6f}（{pct}%） —— 1.000000=不漂",
                  "en": "[Stats] {n} samples: playback rate k={k:.6f} ({pct}%) — 1.000000 = no drift"},
    "log.done_closed": {"zh": "[完成] Mesen 已关闭 → 已停止播放，即将回到初始状态。",
                        "en": "[Done] Mesen closed → playback stopped, returning to start."},
    "log.done": {"zh": "[完成] 音频播放结束。", "en": "[Done] audio playback finished."},
    "log.reset": {"zh": "[系统] 重置状态", "en": "[System] state reset"},
    "log.mesen_closed_sys": {"zh": "[系统] Mesen 已关闭 → 停止推送并回到初始状态",
                             "en": "[System] Mesen closed → push stopped, back to start"},
    "log.lua_closed_sys": {"zh": "[系统] bs.lua 脚本窗口被关闭 → 已关闭 Mesen 并回到初始状态",
                           "en": "[System] bs.lua window closed → Mesen closed, back to start"},
    "log.auto_reset": {"zh": "[系统] 播放结束 → 回到初始状态", "en": "[System] playback finished → back to start"},
    "log.save_deleted": {"zh": "[存档] 已删除 {path}", "en": "[Save] deleted {path}"},
    "log.save_del_blocked": {"zh": "[存档] 检测到 Mesen 仍在运行 → 已拦截，未删除存档",
                             "en": "[Save] Mesen still running → blocked, save not deleted"},
    "log.error": {"zh": "[错误] {e}", "en": "[Error] {e}"},
    "log.close_fail": {"zh": "[关闭] 请求关闭 Mesen 失败：{e}", "en": "[Close] closing Mesen failed: {e}"},
    "log.closed": {"zh": "[关闭] 已关闭 Mesen。", "en": "[Close] Mesen closed."},
    "log.killed": {"zh": "[关闭] terminate 2 秒未退出 → 已强制关闭 Mesen。",
                   "en": "[Close] not exited in 2 s after terminate → force-closed Mesen."},
    "log.kill_fail": {"zh": "[关闭] 强制关闭 Mesen 失败：{e}", "en": "[Close] force-close failed: {e}"},
    "log.lua_stopped": {"zh": "[退出] 检测到 bs.lua 已停止（{why}）→ 关闭 Mesen。",
                        "en": "[Exit] bs.lua stopped ({why}) → closing Mesen."},
    "log.why_script": {"zh": "scriptEnded 标记", "en": "scriptEnded marker"},
    "log.why_window": {"zh": "脚本窗口消失", "en": "script window gone"},
    "why.all_passed": {"zh": "已过全部恢复时刻", "en": "all resume points have passed"},
    "why.too_early": {"zh": "距恢复时刻 {a} 还有 {b}（> {c}）",
                      "en": "still {b} to the resume point {a} (> {c})"},
    "why.cooldown": {"zh": "距上次恢复仅 {n:.0f}s（< {c:.0f}s）",
                     "en": "only {n:.0f}s since the last resume (< {c:.0f}s)"},
    "err.time_format": {"zh": "时间格式无法解析: {t}", "en": "cannot parse the time: {t}"},
    "err.time_positive": {"zh": "时刻必须大于 0: {t}", "en": "the time must be greater than 0: {t}"},
}
I18N = {c: {k: v[c] for k, v in _TEXTS.items()} for c in LANG_CODES}
_CUR_LANG = [LANG_DEFAULT]

def set_lang(code):
    _CUR_LANG[0] = code if code in LANG_CODES else LANG_DEFAULT

def current_lang():
    return _CUR_LANG[0]

def tr(key, **kw):
    table = I18N.get(_CUR_LANG[0]) or I18N[LANG_DEFAULT]
    s = table.get(key)
    if s is None:
        s = I18N[LANG_DEFAULT].get(key, key)
    if kw:
        try:
            s = s.format(**kw)
        except (KeyError, IndexError, ValueError):
            pass
    return s

def chapter_name(n):
    return tr(CHAPTER_KEY.get(n, "chapter.zenhen"))

def chapter_tpl(n):
    return _Tpl(CHAPTER_KEY.get(n, "chapter.zenhen"))

def lua_hint(n):
    return _Tpl("hint.lua") if n in MUTE_CHAPTERS else ""

class _Tpl:
    __slots__ = ("key", "kw")

    def __init__(self, key, **kw):
        self.key = key
        self.kw = kw

    def __str__(self):
        return tr(self.key, **self.kw)

    def __repr__(self):
        return str(self)

CHAPTERS = (1, 2, 3)
CHAPTER_KEY = {1: "chapter.zenhen", 2: "chapter.chuuhen", 3: "chapter.kouhen"}
DEFAULT_SCENE_EXITS = ["15:55", "46:20"]
MUTE_CHAPTERS = (2,)
BSX_DATE = "1995-02-19"
BSX_TIME = "16:59:00"
BOOT_SECONDS_DEFAULT = 60
BOOT_CHOICES = (15, 30, 45, 60)
TRIGGER_CLOCK = datetime(1995, 1, 1, 18, 0, 0)
BROADCAST_START_SEC = (TRIGGER_CLOCK.hour * 3600 + TRIGGER_CLOCK.minute * 60
                       + TRIGGER_CLOCK.second)
BUFFER_FRAMES = 4096
SIGNAL_CHECK_INTERVAL = 0.1
LOG_INTERVAL = 60.0
MUTE_MAX_LEAD = 12 * 60.0
MUTE_COOLDOWN = 20.0

RISKY_SHORTCUTS = ["FastForward", "Rewind", "IncreaseSpeed", "DecreaseSpeed",
                   "MaxSpeed", "Pause", "RunSingleFrame"]

def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = _app_dir()
RES_DIR = getattr(sys, "_MEIPASS", APP_DIR)

def _res_file(*parts):
    for base in dict.fromkeys((RES_DIR, APP_DIR)):
        p = os.path.join(base, *parts)
        if os.path.exists(p):
            return p
    return os.path.join(RES_DIR, *parts)

def _find_root():
    start = d = APP_DIR
    while True:
        if os.path.exists(os.path.join(d, "Mesen.exe")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return start
        d = parent

ROOT = _find_root()
CONFIG_INI = os.path.join(APP_DIR, "config.ini")
BIOS_DEFAULT_NAME = "BS-X BIOS (Japan) [No DRM].sfc"

def _read_ini_text(path):
    for enc in ("utf-8-sig", "gbk"):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except OSError:
            return ""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""

def _parse_ini_text(text):
    cp = configparser.ConfigParser(interpolation=None,
                                   inline_comment_prefixes=(";", "#"))
    if (text or "").strip():
        try:
            cp.read_string(text)
        except configparser.Error:
            pass
    return cp

def _load_ini(path):
    return _parse_ini_text(_read_ini_text(path) if os.path.exists(path) else "")

INI = _load_ini(CONFIG_INI)

def ini_value(key, section="paths"):
    try:
        return (INI.get(section, key) or "").strip()
    except (configparser.NoSectionError, configparser.NoOptionError,
            configparser.InterpolationError):
        return ""

def _resolve_ini_path(value, base=None):
    v = (value or "").strip().strip('"').strip("'")
    if not v:
        return ""
    v = os.path.expandvars(os.path.expanduser(v))
    if not os.path.isabs(v):
        v = os.path.join(base or APP_DIR, v)
    return os.path.abspath(v)

def ini_path(key, section="paths"):
    return _resolve_ini_path(ini_value(key, section))

INI_KEYS = ("mesen", "bios", "data")

def _reload_ini():
    global INI, INI_MESEN, INI_BIOS, INI_DATA
    INI = _load_ini(CONFIG_INI)
    INI_MESEN = ini_path("mesen")
    INI_BIOS = ini_path("bios")
    INI_DATA = ini_path("data")

def ini_write(key, value, section="paths"):
    cp = _load_ini(CONFIG_INI)
    if not cp.has_section(section):
        cp.add_section(section)
    cp.set(section, key, value or "")
    tmp = CONFIG_INI + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            cp.write(f)
        with open(tmp, encoding="utf-8") as f:
            clean = "\n".join(ln.rstrip() for ln in f.read().splitlines()).rstrip() + "\n"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(clean)
        back = _load_ini(tmp).get(section, key, fallback=None)
        if back != (value or ""):
            raise OSError("verify failed")
        os.replace(tmp, CONFIG_INI)
    except (OSError, configparser.Error) as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False, str(e)
    _reload_ini()
    return True, ""

_reload_ini()
BACKUP_DIR = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
                          "BS-Tantei-Terminal")
CFG_PATH = os.path.join(APP_DIR, "data", "tantei_terminal.json")
CFG_PATH_LEGACY = os.path.join(ROOT, "_generated", "config", "tantei_terminal.json")
LUA_SCENE_MUTE = os.path.join(APP_DIR, "bs.lua")
LUA_SCENE_MUTE_LEGACY = os.path.join(ROOT, "_generated", "scripts", "lua", "scene_mute.lua")
LOGO_PNG = _res_file("ui", "icon.png")
ICON_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
FONT_CANDIDATES = [
    _res_file("fonts", "SourceHanSansHC-Normal.otf"),
]

def data_dir():
    if INI_DATA and os.path.isdir(INI_DATA):
        return INI_DATA
    return None

def data_path(*parts):
    base = data_dir()
    if base:
        if parts and parts[0] == "bstantei":
            parts = parts[1:]
        return os.path.join(base, *parts)
    first = os.path.join(ROOT, *parts)
    if os.path.exists(first):
        return first
    alt = os.path.join(APP_DIR, *parts)
    return alt if os.path.exists(alt) else first

def rp(*parts):
    return data_path(*parts)

def bios_file():
    if INI_BIOS and os.path.isfile(INI_BIOS):
        return INI_BIOS
    for d in (ROOT, APP_DIR):
        p = os.path.join(d, BIOS_DEFAULT_NAME)
        if os.path.isfile(p):
            return p
    return os.path.join(ROOT, BIOS_DEFAULT_NAME)

def wav_dir():
    return data_path("bstantei", "wav")

def lua_path():
    if os.path.exists(LUA_SCENE_MUTE):
        return LUA_SCENE_MUTE
    return LUA_SCENE_MUTE_LEGACY

def rel(p, root=None):
    try:
        return os.path.relpath(p, root or ROOT)
    except ValueError:
        return p

TH32CS_SNAPPROCESS = 0x00000002
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
INVALID_HANDLE = ctypes.c_void_p(-1).value

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_ulong),
                ("cntUsage", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", ctypes.c_ulong),
                ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_wchar * 260)]

def _kernel32():
    try:
        return ctypes.windll.kernel32
    except (AttributeError, OSError):
        return None

def proc_pids(name):
    """按进程名（如 Mesen.exe）列出 PID；枚举失败（非 Windows / 无权限）返回 None。"""
    k32 = _kernel32()
    if k32 is None:
        return None
    try:
        k32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        k32.CreateToolhelp32Snapshot.argtypes = (ctypes.c_ulong, ctypes.c_ulong)
    except AttributeError:
        return None
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not snap or snap == INVALID_HANDLE:
        return None
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(entry)
    pids = []
    try:
        ok = k32.Process32FirstW(ctypes.c_void_p(snap), ctypes.byref(entry))
        while ok:
            if (entry.szExeFile or "").lower() == str(name).lower():
                pids.append(int(entry.th32ProcessID))
            entry.dwSize = ctypes.sizeof(entry)
            ok = k32.Process32NextW(ctypes.c_void_p(snap), ctypes.byref(entry))
    finally:
        k32.CloseHandle(ctypes.c_void_p(snap))
    return pids

def proc_exe_path(pid):
    """取进程可执行文件的全路径；拿不到（权限 / 进程已退出）返回 ""。"""
    k32 = _kernel32()
    if k32 is None:
        return ""
    try:
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
    except AttributeError:
        return ""
    h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, int(pid))
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = ctypes.c_ulong(len(buf))
        if not k32.QueryFullProcessImageNameW(ctypes.c_void_p(h), 0, buf,
                                             ctypes.byref(size)):
            return ""
        return buf.value or ""
    finally:
        k32.CloseHandle(ctypes.c_void_p(h))

class LuaWindowWatcher:

    INTERVAL = 0.4

    def __init__(self, pid, names=("script window", "bs.lua")):
        self.pid = int(pid or 0)
        self.names = tuple(str(n).lower() for n in names if n)
        self.seen = False
        self._present = False
        self._last = 0.0

    @staticmethod
    def _enum_titles(pid):
        try:
            user32 = ctypes.windll.user32
        except (AttributeError, OSError):
            return None
        titles = []
        pid_ref = ctypes.c_ulong()

        @ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
        def _cb(hwnd, _lparam):
            user32.GetWindowThreadProcessId(ctypes.c_void_p(hwnd), ctypes.byref(pid_ref))
            if pid_ref.value == pid:
                n = user32.GetWindowTextLengthW(ctypes.c_void_p(hwnd))
                if n > 0:
                    buf = ctypes.create_unicode_buffer(n + 1)
                    user32.GetWindowTextW(ctypes.c_void_p(hwnd), buf, n + 1)
                    if buf.value:
                        titles.append(buf.value)
            return 1

        try:
            user32.EnumWindows(_cb, 0)
        except OSError:
            return None
        return titles

    def _match(self, titles):
        for t in titles or ():
            low = str(t).lower()
            for n in self.names:
                if n and n in low:
                    return True
        return False

    def poll(self):
        now = time.time()
        if now - self._last < self.INTERVAL:
            return True if self._present else (False if self.seen else None)
        self._last = now
        titles = self._enum_titles(self.pid)
        if titles is None:
            return True if self._present else (False if self.seen else None)
        hit = self._match(titles)
        self._present = hit
        if hit:
            self.seen = True
            return True
        return False if self.seen else None

class LuaStopSignal:

    HITS = 3
    GRACE = 2.0
    MARKER = "script_closed.txt"

    def __init__(self, mesen_dir, since=None, script_stem=None, extra_dirs=(), log=None):
        self.mesen_dir = mesen_dir
        self.since = time.time() if since is None else float(since)
        self.script_stem = (script_stem or "").strip()
        self.extra_dirs = list(extra_dirs or ())
        self.log = log
        self.dir = None
        self.armed = False
        self.hits = 0
        self._logged = False

    def _base_dirs(self):
        out = [os.path.join(self.mesen_dir, "LuaScriptData")]
        out += [os.path.join(d, "LuaScriptData") for d in self.extra_dirs]
        return [d for i, d in enumerate(out) if d not in out[:i]]

    def _candidates(self):
        out = []
        for base in self._base_dirs():
            if not os.path.isdir(base):
                continue
            if self.script_stem:
                d = os.path.join(base, self.script_stem)
                if os.path.isdir(d):
                    return [d]
            try:
                names = sorted(os.listdir(base))
            except OSError:
                names = []
            for n in names:
                d = os.path.join(base, n)
                if os.path.isdir(d) and d not in out:
                    out.append(d)
        return out

    def _file(self):
        if self.dir is not None:
            p = os.path.join(self.dir, self.MARKER)
            if os.path.isfile(p):
                return p
            self.dir = None
        for d in self._candidates():
            p = os.path.join(d, self.MARKER)
            if not os.path.isfile(p):
                continue
            if os.path.basename(d) != self.script_stem:
                try:
                    if os.path.getmtime(p) < self.since:
                        continue
                except OSError:
                    continue
            self.dir = d
            if self.log and not self._logged:
                self._logged = True
                self.log(tr("log.marker_ready", path=p))
            return p
        return None

    def poll(self):
        path = self._file()
        if path is None:
            self.hits = 0
            return False
        v = read_flag(path)
        if v == "0":
            self.armed, self.hits = True, 0
            return False
        if v != "1":
            self.hits = 0
            return False
        try:
            mt = os.path.getmtime(path)
        except OSError:
            self.hits = 0
            return False
        if mt < self.since:
            self.hits = 0
            return False
        if not self.armed and mt < self.since + self.GRACE:
            self.hits = 0
            return False
        self.hits += 1
        return self.hits >= self.HITS

def build_logo_canvases(sizes=ICON_SIZES):
    from PIL import Image
    src = Image.open(LOGO_PNG).convert("RGBA")
    w, h = src.size
    out = []
    for s in sizes:
        canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        box = max(1, int(round(s * 0.94)))
        scale = min(box / float(w), box / float(h))
        nw = max(1, int(round(w * scale)))
        nh = max(1, int(round(h * scale)))
        resample = Image.NEAREST if scale >= 1 else Image.LANCZOS
        piece = src.resize((nw, nh), resample)
        canvas.paste(piece, ((s - nw) // 2, (s - nh) // 2), piece)
        out.append((s, canvas))
    return out

def load_logo_images(master):
    if not os.path.exists(LOGO_PNG):
        return [], "缺少 icon.png"
    try:
        from PIL import ImageTk
    except ImportError:
        try:
            import tkinter as _tk
            raw = _tk.PhotoImage(master=master, file=LOGO_PNG)
            return [raw], "无 PIL，用原图"
        except Exception:
            return [], "PNG 读不了"
    try:
        canvases = build_logo_canvases()
        imgs = [ImageTk.PhotoImage(im, master=master) for _, im in canvases]
        return imgs, f"icon.png -> {len(imgs)} 档"
    except Exception as exc:
        return [], f"PIL 处理失败: {exc}"

def fmt_mmss(sec):
    if sec is None:
        return "--:--"
    sec = int(round(sec))
    if sec < 0:
        sec = 0
    if sec >= 3600:
        return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"
    return f"{sec // 60}:{sec % 60:02d}"

def fmt_hms(sec):
    sec = int(max(0, sec))
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"

def parse_time_token(tok):
    tok = str(tok).strip()
    if ":" in tok:
        parts = tok.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        raise ValueError(tr("err.time_format", t=tok))
    return float(tok)

def parse_scene_exit(spec):
    last = str(spec).split("-")[-1].strip()
    sec = parse_time_token(last)
    if sec <= 0:
        raise ValueError(tr("err.time_positive", t=spec))
    return sec

def next_exit(exits, now):
    future = [e for e in exits if e[0] > now]
    return min(future, key=lambda e: e[0]) if future else None

def mute_lead_ok(content, nx, max_lead=MUTE_MAX_LEAD):
    return nx is None or (nx[0] - content) <= max_lead

def mute_enter_ok(content, nx, last_unmute=None,
                  max_lead=MUTE_MAX_LEAD, cooldown=MUTE_COOLDOWN):
    if nx is None:
        return False, tr("why.all_passed")
    if not mute_lead_ok(content, nx, max_lead):
        return False, tr("why.too_early", a=fmt_mmss(nx[0]), b=fmt_mmss(nx[0] - content),
                         c=fmt_mmss(max_lead))
    if last_unmute is not None and (content - last_unmute) < cooldown:
        return False, tr("why.cooldown", n=content - last_unmute, c=cooldown)
    return True, ""

def read_flag(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            v = f.read().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None
    if v in ("0", "1"):
        return v
    if v == "":
        return None
    return "1" if v.startswith("1") else "0"

def read_seq(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            v = f.read().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return 1 if v.startswith("1") else 0

def resolve_flag_file(explicit, root):
    if explicit:
        return os.path.abspath(explicit)
    base = os.path.join(root, "LuaScriptData")
    found = []
    if os.path.isdir(base):
        for dirpath, _dirnames, filenames in os.walk(base):
            if "scene_flag.txt" in filenames:
                found.append(os.path.join(dirpath, "scene_flag.txt"))
    if found:
        found.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return found[0]
    return os.path.join(base, "scene_mute", "scene_flag.txt")

def wav_info(path):
    try:
        with wave.open(path, "rb") as w:
            rate = w.getframerate()
            frames = w.getnframes()
            return (w.getnchannels(), rate, w.getsampwidth() * 8,
                    (frames / rate) if rate else 0.0)
    except (wave.Error, EOFError, FileNotFoundError, OSError):
        return None

def read_broadcast_ids(folder):
    f120 = os.path.join(folder, "BSX0120-0.bin")
    f125 = os.path.join(folder, "BSX0125-0.bin")
    try:
        with open(f120, "rb") as f:
            a = f.read(16)
        with open(f125, "rb") as f:
            b = f.read(16)
        return (a[11], a[12], b[10])
    except (FileNotFoundError, IndexError, OSError):
        return None

def clear_dir(dst):
    n = 0
    if os.path.isdir(dst):
        for item in os.listdir(dst):
            p = os.path.join(dst, item)
            try:
                if os.path.isfile(p) or os.path.islink(p):
                    os.remove(p)
                elif os.path.isdir(p):
                    shutil.rmtree(p)
                n += 1
            except OSError:
                pass
    return n

def copy_dir(src, dst):
    os.makedirs(dst, exist_ok=True)
    ok = skipped = 0
    for item in os.listdir(src):
        s = os.path.join(src, item)
        if not os.path.isfile(s):
            skipped += 1
            continue
        try:
            shutil.copy2(s, os.path.join(dst, item))
            ok += 1
        except (shutil.Error, OSError):
            skipped += 1
    return ok, skipped

def patch_settings(settings_path, date=BSX_DATE, time_s=BSX_TIME,
                   integer_fps=True, clear_shortcuts=True, log=None):
    with open(settings_path, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    changes = {}

    cfg.setdefault("Snes", {})
    cfg["Snes"]["BsxUseCustomTime"] = True
    cfg["Snes"]["BsxCustomDate"] = date + "T00:00:00+00:00"
    cfg["Snes"]["BsxCustomTime"] = time_s
    changes["BSX"] = f"{date} {time_s} (JST {int(time_s[:2]) + 1:02d}:{time_s[3:5]})"

    if integer_fps:
        cfg.setdefault("Video", {})
        cfg["Video"]["IntegerFpsMode"] = True
        cfg["Video"]["VerticalSync"] = True
        changes[tr("patch.fps")] = "IntegerFpsMode + VerticalSync"

    cfg.setdefault("Debug", {}).setdefault("ScriptWindow", {})
    cfg["Debug"]["ScriptWindow"]["AllowIoOsAccess"] = True
    cfg["Debug"]["ScriptWindow"]["AutoStartScriptOnLoad"] = True
    changes[tr("patch.lua")] = "AllowIoOsAccess + AutoStartScriptOnLoad"

    if clear_shortcuts:
        keys = cfg.get("Preferences", {}).get("ShortcutKeys")
        n = 0
        if isinstance(keys, list):
            for item in keys:
                if not isinstance(item, dict) or item.get("Shortcut") not in RISKY_SHORTCUTS:
                    continue
                for comb in ("KeyCombination", "KeyCombination2"):
                    if comb in item and isinstance(item[comb], dict):
                        item[comb]["Key1"] = 0
                        n += 1
        changes[tr("patch.shortcuts")] = tr("patch.shortcuts_cleared", n=n)

    tmp = settings_path + ".tmp_terminal"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    with open(tmp, "r", encoding="utf-8") as f:
        json.load(f)
    os.replace(tmp, settings_path)

    if log:
        for k, v in changes.items():
            log(tr("log.patch", k=k, v=v))
    return changes

def ramp_volume(target, duration=0.5, steps=20, stop_evt=None):
    try:
        import pygame
        start = pygame.mixer.music.get_volume()
    except Exception:
        return 0.0
    import pygame
    delta = (target - start) / steps
    t0 = time.time()
    for i in range(steps):
        if stop_evt is not None and stop_evt.is_set():
            break
        v = start + delta * (i + 1)
        try:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, v)))
        except Exception:
            break
        time.sleep(duration / steps)
    try:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, target)))
    except Exception:
        pass
    return time.time() - t0

def unregister_font(path):
    try:
        ctypes.windll.gdi32.RemoveFontResourceExW(path, 0x10, 0)
    except Exception:
        pass

def get_dpi_scale():
    try:
        if hasattr(ctypes.windll.user32, "GetDpiForSystem"):
            return ctypes.windll.user32.GetDpiForSystem() / 96.0
    except Exception:
        pass
    try:
        hdc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except Exception:
        return 1.0

def register_font():
    for p in FONT_CANDIDATES:
        if not os.path.exists(p):
            continue
        try:
            if ctypes.windll.gdi32.AddFontResourceExW(p, 0x10, 0):
                atexit.register(unregister_font, p)
                return "思源黑體 香港 Normal"
        except Exception:
            pass
    return "Microsoft YaHei UI"

def load_config():
    for path in (CFG_PATH, CFG_PATH_LEGACY):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
        if isinstance(cfg, dict):
            return cfg
    return {}

def backup_dir():
    return BACKUP_DIR

def backup_enabled():
    return os.environ.get("TANTEI_NO_BACKUP", "") not in ("1", "true", "yes")

class TanteiTerminal:

    def __init__(self, selftest=False):
        self.selftest = selftest
        self.s = max(1.0, get_dpi_scale())
        self.fam = register_font()
        self.cfg = load_config()
        for _legacy in ("buffer", "scene_exits", "mute_enabled", "boot_seconds"):
            self.cfg.pop(_legacy, None)
        set_lang(self.cfg.get("lang") or LANG_DEFAULT)

        self.mesen_path = ""
        self.mesen_dir = ""
        self.bios_path = bios_file()
        self.chapter = None

        self.running = False
        self.stop_evt = threading.Event()
        self.engine = None
        self.proc = None
        self.lua_watch = None
        self.lua_stop = None
        self._lua_gone_why = None
        self._stop_reason = None
        self.lock = threading.Lock()

        self.state = {
            "phase": "idle",
            "clock": "17:59:00",
            "status": tr("status.pick_mesen"),
            "audio_pos": 0.0,
            "audio_total": 0.0,
            "lag": None,
            "k": None,
            "mute": tr("mute.off"),
            "mute_key": "mute.off",
            "mute_fmt": {},
            "exit_target": None,
        }
        self._status_key, self._status_fmt = "status.pick_mesen", {}
        self._step = 1
        self._lua_killed = False
        self._i18n_widgets = []
        self.samples = []
        self.fit = [0, 0.0, 0.0, 0.0, 0.0]
        self._last_drawn = (0.0, None)
        self._last_chart_draw = 0.0

        self._logbuf = []

        self.root = Tk()
        self.root.title(tr("app.title"))
        self.root.resizable(False, False)
        if selftest:
            self.root.withdraw()
        self.base_w, self.base_h = 460, 402
        self._icon_images, self._icon_note = [], "未加载"
        self._apply_icon()
        self.show_monitor = BooleanVar(master=self.root, value=bool(self.cfg.get("show_monitor", False)))
        self.pin_top = BooleanVar(master=self.root, value=bool(self.cfg.get("pin_top", False)))
        self.lang_var = StringVar(master=self.root, value=current_lang())
        self._setup_ui()
        self._apply_pin()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(120, self._tick)
        self._log_config()
        self._auto_detect()
        self._remember_paths()
        self._apply_language()

    def _apply_icon(self):
        imgs, note = load_logo_images(self.root)
        self._icon_images = imgs
        self._icon_note = note
        if imgs:
            try:
                self.root.iconphoto(True, *imgs)
            except TclError:
                pass
        return note

    def _px(self, v):
        return int(round(v * self.s))

    def _apply_geometry(self, h):
        w = self.base_w
        h = min(h, int(self.root.winfo_screenheight() / self.s * 0.95))
        self.root.geometry(f"{self._px(w)}x{self._px(h)}")

    def _fit_height(self):
        self.root.update_idletasks()
        need = self.root.winfo_reqheight() + self._px(3)
        max_h = int(self.root.winfo_screenheight() * 0.95)
        self.root.geometry(f"{self._px(self.base_w)}x{min(need, max_h)}")

    @staticmethod
    def _clamp_boot(raw):
        try:
            v = int(str(raw).strip())
        except (TypeError, ValueError):
            return BOOT_SECONDS_DEFAULT
        return min(BOOT_CHOICES, key=lambda c: (abs(c - v), c))

    def _boot_start_clock(self, boot=None):
        if boot is None:
            boot = self._clamp_boot(self.boot_var.get())
        return (TRIGGER_CLOCK - timedelta(seconds=boot)).strftime("%H:%M:%S")

    def _normalize_boot(self):
        boot = self._clamp_boot(self.boot_var.get())
        if self.boot_var.get().strip() != str(boot):
            self.boot_var.set(str(boot))
        self._on_boot_changed()

    def _on_boot_changed(self):
        boot = self._clamp_boot(self.boot_var.get())
        if not self.running:
            self._set_state(clock=self._boot_start_clock(boot))
            if self.chapter:
                self._refresh_main_label()
                st = self._get_state()
                if st.get("phase") == "idle":
                    self._status("status.chapter_locked",
                                 name=chapter_tpl(self.chapter),
                                 dur=self._dur_tpl(self.chapter),
                                 hint=lua_hint(self.chapter), boot=boot)

    def _dur_suffix(self, n):
        info = wav_info(self._effective_wav())
        return tr("status.dur_suffix", dur=fmt_mmss(info[3])) if info else ""

    def _dur_tpl(self, n):
        info = wav_info(self._effective_wav())
        return _Tpl("status.dur_suffix", dur=fmt_mmss(info[3])) if info else ""

    def _log(self, msg):
        line = f"[{datetime.now():%H:%M:%S}] {msg}"
        try:
            print(line, flush=True)
        except Exception:
            pass
        with self.lock:
            self._logbuf.append(line)

    def _set_state(self, **kw):
        with self.lock:
            self.state.update(kw)

    def _get_state(self):
        with self.lock:
            return dict(self.state)

    def _persist(self):
        pass

    def _status(self, key, **kw):
        self._status_key, self._status_fmt = key, kw
        self._set_state(status=tr(key, **kw))

    def _mute(self, key, **kw):
        self._set_state(mute=tr(key, **kw), mute_key=key, mute_fmt=kw)

    def _reg(self, widget, key, **fmt):
        self._i18n_widgets.append((widget, key, fmt))
        try:
            widget.configure(text=tr(key, **fmt))
        except TclError:
            pass
        return widget

    def _btn_w(self):
        return {"zh": 38, "en": 44}.get(current_lang(), 38)

    def _text_width(self, text, font=None, pad=2):
        try:
            f = tkfont.Font(font=font or self.f_small)
            unit = max(1, f.measure("0"))
            return max(3, int(round(f.measure(text) / float(unit))) + pad)
        except (TclError, ValueError):
            return 4

    def _set_step(self, step, command=None):
        self._step = step
        if command is not None:
            self.btn_main.config(command=command)
        self._refresh_main_label()

    def _refresh_main_label(self):
        step = getattr(self, "_step", 1)
        if step == 3:
            text = tr("btn.step3", boot=self._clamp_boot(self.boot_var.get()))
        elif step == 2:
            text = tr("btn.step2")
        else:
            text = tr("btn.step1")
        try:
            self.btn_main.config(text=text, width=self._btn_w())
            self.btn_delete_save.config(width=self._btn_w())
        except TclError:
            pass

    def _refresh_stats(self):
        st = self._get_state()
        total = st.get("audio_total") or 0.0
        self.stat_audio.set(fmt_mmss(st.get("audio_pos") or 0)
                            + " / " + (fmt_mmss(total) if total else "--:--"))
        lag = st.get("lag")
        self.stat_lag.set(f"{lag:+.3f}s" if lag is not None else "--")
        k = st.get("k")
        self.stat_rate.set(f"k={k:.6f} ({((k - 1) * 100):+.4f}%)" if k is not None else "--")
        self.stat_mute.set(tr(st.get("mute_key", "mute.off"), **(st.get("mute_fmt") or {})))

    def _apply_language(self, code=None):
        code = code or (self.lang_var.get() if hasattr(self, "lang_var") else current_lang())
        set_lang(code)
        self.cfg["lang"] = current_lang()
        try:
            self.root.title(tr("app.title"))
        except TclError:
            pass
        for w, key, fmt in list(self._i18n_widgets):
            try:
                w.configure(text=tr(key, **fmt))
            except TclError:
                pass
        for w, key, _f in self._i18n_widgets:
            if key in ("btn.browse", "btn.default"):
                try:
                    w.configure(width=self._text_width(tr(key)))
                except TclError:
                    pass
        for n, b in getattr(self, "chapter_buttons", ()):
            try:
                b.configure(text=chapter_name(n))
            except TclError:
                pass
        if hasattr(self, "btn_main"):
            self._refresh_main_label()
        num_font = self.f_num
        names = getattr(self, "stat_names", {})
        for key, nv in names.items():
            try:
                nv.set(tr(key))
            except TclError:
                pass
        if names:
            wcol = max(self._text_width(tr(k), font=num_font, pad=0) for k in names)
            for lb in getattr(self, "stat_nlabels", ()):
                try:
                    lb.configure(width=wcol, anchor="w")
                except TclError:
                    pass
        if self._status_key:
            self._set_state(status=tr(self._status_key, **self._status_fmt))
        self._refresh_stats()
        try:
            self.status_var.set(self._get_state()["status"])
        except (TclError, KeyError, AttributeError):
            pass

    def _pick_lang(self, code):
        if self.running:
            return
        self.lang_var.set(code)
        for c, b in getattr(self, "lang_buttons", ()):
            try:
                b.config(relief="sunken" if c == code else "raised")
            except TclError:
                pass
        self._apply_language(code)

    def _setup_ui(self):
        fam = self.fam
        self.f_clock = (fam, -self._px(26), "bold")
        self.f_title = (fam, -self._px(15), "bold")
        self.f_body = (fam, -self._px(13))
        self.f_small = (fam, -self._px(11))
        self.f_num = ("Consolas", -self._px(12))
        p4, p8, p12 = self._px(4), self._px(8), self._px(12)

        tf = Frame(self.root, pady=p8)
        tf.pack()
        self._reg(Label(tf, font=self.f_title), "ui.clock_title").pack(side="left")
        self.clock_var = StringVar(master=self.root, value="17:59:00")
        self.time_label = Label(tf, textvariable=self.clock_var,
                                font=self.f_clock, fg="#c0392b", padx=p12)
        self.time_label.pack(side="left")

        self.status_var = StringVar(value=tr("status.pick_mesen"))
        self.status_label = Label(self.root, textvariable=self.status_var, font=self.f_body,
                                  fg="#c0392b", wraplength=self._px(430), height=2,
                                  justify="center")
        self.status_label.pack(pady=(0, p8))

        ch = Frame(self.root, pady=p4)
        ch.pack()
        self._reg(Label(ch, font=self.f_body), "ui.chapter_label").pack(side="left")
        self.chapter_buttons = []
        for n in CHAPTERS:
            b = Button(ch, text=chapter_name(n), width=7, height=1, state="disabled",
                       font=self.f_body, command=lambda k=n: self.select_chapter(k))
            b.pack(side="left", padx=p4)
            self.chapter_buttons.append((n, b))

        self.btn_main = Button(self.root, text=tr("btn.step1"), width=self._btn_w(), height=2,
                               font=self.f_body, command=self.select_mesen)
        self.btn_main.pack(pady=p8)

        self.btn_delete_save = self._reg(Button(self.root, width=self._btn_w(), height=1,
                                                state="disabled", fg="#c0392b",
                                                font=self.f_body, command=self.delete_save),
                                         "btn.delete_save")
        self.btn_delete_save.pack(pady=(0, p4))

        self.chk_monitor = self._reg(Checkbutton(self.root, variable=self.show_monitor,
                                                 font=self.f_small,
                                                 activebackground=self.root.cget("bg"),
                                                 command=self._toggle_monitor),
                                     "ui.monitor_toggle")
        self.chk_monitor.pack(pady=p4)

        self._build_monitor()
        self._refresh_env_line()

        self.log_box = Text(self.root, height=5, width=1, font=self.f_small, state="disabled",
                            wrap="char", bg="#111418", fg="#cfd8dc", insertbackground="#cfd8dc")
        self.log_box.pack(fill="x", padx=p12, pady=(0, p8))
        self.log_box.tag_config("err", foreground="#ff8a80")
        self.log_box.tag_config("ok", foreground="#a5d6a7")

        self.root.update_idletasks()
        self.base_h = int(self.root.winfo_reqheight() / self.s) + 2
        self._apply_geometry(self.base_h)

        if self.show_monitor.get():
            self._toggle_monitor()

    def _build_monitor(self):
        p4, p8 = self._px(4), self._px(8)
        self.monitor = Frame(self.root, relief="groove", borderwidth=1, padx=p8, pady=p4)

        row0 = Frame(self.monitor)
        row0.pack(fill="x", pady=2)
        self._reg(Label(row0, font=self.f_small, width=10, anchor="w"), "lbl.mesen").pack(side="left")
        self.mesen_var = StringVar(master=self.root, value="")
        self.mesen_entry = Entry(row0, textvariable=self.mesen_var, font=self.f_small,
                                 state="readonly", readonlybackground="#f7f9fa")
        self.mesen_entry.pack(side="left", fill="x", expand=True)
        self.btn_mesen_browse = self._reg(Button(row0, font=self.f_small, width=4,
                                                 command=self.select_mesen), "btn.browse")
        self.btn_mesen_browse.pack(side="left", padx=2)

        row0b = Frame(self.monitor)
        row0b.pack(fill="x", pady=2)
        self._reg(Label(row0b, font=self.f_small, width=10, anchor="w"), "lbl.bios").pack(side="left")
        self.bios_var = StringVar(master=self.root, value="")
        self.bios_entry = Entry(row0b, textvariable=self.bios_var, font=self.f_small,
                                state="readonly", readonlybackground="#f7f9fa")
        self.bios_entry.pack(side="left", fill="x", expand=True)
        self.btn_bios_browse = self._reg(Button(row0b, font=self.f_small, width=4,
                                                command=self.browse_bios), "btn.browse")
        self.btn_bios_browse.pack(side="left", padx=2)

        row0c = Frame(self.monitor)
        row0c.pack(fill="x", pady=2)
        self._reg(Label(row0c, font=self.f_small, width=10, anchor="w"), "lbl.data").pack(side="left")
        self.data_var = StringVar(master=self.root, value="")
        self.data_entry = Entry(row0c, textvariable=self.data_var, font=self.f_small,
                                state="readonly", readonlybackground="#f7f9fa")
        self.data_entry.pack(side="left", fill="x", expand=True)
        self.btn_data_browse = self._reg(Button(row0c, font=self.f_small, width=4,
                                                command=self.browse_data), "btn.browse")
        self.btn_data_browse.pack(side="left", padx=2)
        self.btn_data_default = self._reg(Button(row0c, font=self.f_small, width=4,
                                                 command=self.default_data), "btn.default")
        self.btn_data_default.pack(side="left")

        row = Frame(self.monitor)
        row.pack(fill="x", pady=2)
        self._reg(Label(row, font=self.f_small, width=10, anchor="w"), "lbl.audio").pack(side="left")
        self.wav_var = StringVar()
        self.wav_entry = Entry(row, textvariable=self.wav_var, font=self.f_small,
                               state="readonly", readonlybackground="#f7f9fa")
        self.wav_entry.pack(side="left", fill="x", expand=True)
        self._reg(Button(row, font=self.f_small, width=4, command=self.browse_wav),
                  "btn.browse").pack(side="left", padx=2)
        self._reg(Button(row, font=self.f_small, width=4, command=self.reset_wav),
                  "btn.default").pack(side="left")

        row2 = Frame(self.monitor)
        row2.pack(fill="x", pady=2)
        self._reg(Label(row2, font=self.f_small, width=10, anchor="w"),
                  "lbl.offset").pack(side="left", padx=(0, 3))
        self.offset_var = StringVar(master=self.root, value=str(self.cfg.get("offset_ms", 0)))
        Entry(row2, textvariable=self.offset_var, font=self.f_small, width=7).pack(side="left", padx=2)

        row2b = Frame(self.monitor)
        row2b.pack(fill="x", pady=2)
        self._reg(Label(row2b, font=self.f_small, width=10, anchor="w"),
                  "lbl.boot").pack(side="left", padx=(0, 3))
        self.boot_var = StringVar(master=self.root)
        self.boot_spin = Spinbox(row2b, from_=BOOT_CHOICES[0], to=BOOT_CHOICES[-1],
                                 values=BOOT_CHOICES, increment=15, width=4, justify="center",
                                 textvariable=self.boot_var, font=self.f_small,
                                 command=self._on_boot_changed)
        self.boot_spin.pack(side="left", padx=2)
        self.boot_spin.bind("<FocusOut>", lambda _e: self._normalize_boot())
        self.boot_var.set(str(BOOT_SECONDS_DEFAULT))
        self._reg(Label(row2b, font=self.f_small), "lbl.sec").pack(side="left", padx=(1, 0))

        self.stat_names = {}
        self.stat_nlabels = []
        self.stat_audio = StringVar(value="--:-- / --:--")
        self.stat_lag = StringVar(value="--")
        self.stat_rate = StringVar(value="--")
        self.stat_mute = StringVar(value=tr("mute.off"))
        rows = (("stat.name_audio", self.stat_audio, "#2c3e50"),
                ("stat.name_lag", self.stat_lag, "#2c3e50"),
                ("stat.name_rate", self.stat_rate, "#2c3e50"),
                ("stat.name_mute", self.stat_mute, "#8e44ad"))
        for name_key, var, color in rows:
            rowf = Frame(self.monitor)
            rowf.pack(fill="x")
            nv = StringVar(value=tr(name_key))
            self.stat_names[name_key] = nv
            nlb = Label(rowf, textvariable=nv, font=self.f_num, fg=color, anchor="w")
            nlb.pack(side="left")
            vlb = Label(rowf, textvariable=var, font=self.f_num, fg=color, anchor="w")
            vlb.pack(side="left", padx=(self._px(8), 0))
            self.stat_nlabels.append(nlb)

        self.chart = Canvas(self.monitor, height=self._px(104), bg="#fbfcfd",
                            highlightthickness=1, highlightbackground="#d0d7de")
        self.chart.pack(fill="x", pady=(p4, 2))
        self.chart.bind("<Configure>", lambda _e: setattr(self, "_last_chart_draw", 0.0))

        rowx = Frame(self.monitor)
        rowx.pack(fill="x")
        self.pin_check = self._reg(Checkbutton(rowx, variable=self.pin_top, font=self.f_small,
                                               activebackground=self.root.cget("bg"),
                                               command=self._apply_pin), "chk.pin_top")
        self.pin_check.pack(side="left")

        self.lang_box = Frame(rowx)
        self.lang_box.pack(side="right")
        self._reg(Label(self.lang_box, font=self.f_small), "ui.lang_label").pack(side="left", padx=(0, 2))
        self.lang_buttons = []
        for code in LANG_CODES:
            rb = Button(self.lang_box, text=LANG_LABELS[code], font=self.f_small,
                        width=self._text_width(LANG_LABELS[code]),
                        relief="sunken" if code == current_lang() else "raised",
                        command=lambda c=code: self._pick_lang(c))
            rb.pack(side="left", padx=1)
            self.lang_buttons.append((code, rb))

    def _toggle_monitor(self):
        if self.show_monitor.get():
            self.monitor.pack(fill="x", padx=self._px(12), pady=(0, self._px(4)))
            try:
                self.monitor.pack_configure(before=self.log_box)
            except TclError:
                pass
            self._fit_height()
        else:
            self.monitor.pack_forget()
            self._apply_geometry(self.base_h)
        self.cfg["show_monitor"] = bool(self.show_monitor.get())
        self._persist()

    def _apply_pin(self):
        try:
            self.root.attributes("-topmost", bool(self.pin_top.get()))
        except TclError:
            pass
        self.cfg["pin_top"] = bool(self.pin_top.get())
        self._persist()

    def _log_config(self):
        if os.path.exists(CONFIG_INI):
            self._log(tr("log.ini_loaded", path=CONFIG_INI))
        else:
            self._log(tr("log.ini_absent", path=CONFIG_INI))
        for key, val, kind in (("mesen", INI_MESEN, "file"), ("bios", INI_BIOS, "file"),
                               ("data", INI_DATA, "dir")):
            if not val:
                continue
            ok = os.path.isdir(val) if kind == "dir" else os.path.isfile(val)
            self._log(tr("log.ini_item", name=key, path=val,
                         tag="" if ok else tr("log.ini_item_bad")))
        if not data_dir():
            self._log(tr("log.data_auto", dir=data_path("bstantei")))

    def _auto_detect(self):
        if INI_MESEN and os.path.isfile(INI_MESEN):
            self._use_mesen(INI_MESEN, silent=True)
            return
        if INI_MESEN:
            self._log(tr("log.ini_mesen_missing", path=INI_MESEN))
        p = rp("Mesen.exe")
        if os.path.exists(p):
            self._use_mesen(p, silent=True)

    def _remember_paths(self):
        if self.selftest:
            return
        wrote = False
        for key, val, ok in (("mesen", self.mesen_path, os.path.isfile),
                             ("bios", self.bios_path, os.path.isfile),
                             ("data", data_path("bstantei"), os.path.isdir)):
            if not val:
                continue
            val = os.path.abspath(val)
            if not ok(val):
                continue
            cur = ini_value(key)
            if cur and ok(cur):
                continue
            if ini_write(key, val)[0]:
                self._log(tr("log.ini_auto_saved", name=key, path=val))
                wrote = True
        if wrote:
            self._refresh_env_line()

    def select_mesen(self):
        if self.running:
            return
        p = filedialog.askopenfilename(title=tr("dlg.pick_mesen"),
                                       filetypes=[("Mesen", "Mesen.exe"),
                                                  (tr("dlg.files_exe"), "*.exe")])
        if not p:
            return
        self._use_mesen(p)
        if self.mesen_path and os.path.abspath(self.mesen_path) == os.path.abspath(p):
            self._save_ini("mesen", os.path.abspath(p))

    def _use_mesen(self, path, silent=False):
        self.mesen_path = path
        self.mesen_dir = os.path.dirname(os.path.abspath(path))
        self.btn_delete_save.config(state="normal")
        self._refresh_env_line()
        if not os.path.exists(self.bios_path) and not self._handle_missing_bios():
            self._refresh_env_line()
            return
        self._refresh_env_line()
        self._set_step(2, command=self._hint_chapter)
        self.btn_main.config(state="normal")
        for _n, b in self.chapter_buttons:
            b.config(state="normal")
        self._status("status.pick_chapter")
        if not silent:
            self._log(tr("log.mesen_selected", path=path))
            self._log(tr("log.bios_selected", name=os.path.basename(self.bios_path)))
        else:
            self._log(tr("log.mesen_auto", path=path))

    def _refresh_env_line(self):
        mesen = self.mesen_path or ""
        bios = self.bios_path if os.path.exists(self.bios_path) else tr("status.bios_missing_entry")
        data = data_path("bstantei")
        try:
            self.mesen_var.set(mesen)
            self.bios_var.set(bios)
            if hasattr(self, "data_var"):
                self.data_var.set(data)
            self.root.update_idletasks()
            for ent, txt in ((self.mesen_entry, mesen), (self.bios_entry, bios),
                             (getattr(self, "data_entry", None), data)):
                if ent is not None:
                    ent.xview_moveto(1.0 if txt else 0.0)
            st = "disabled" if self.running else "normal"
            self.btn_mesen_browse.config(state=st)
            self.btn_bios_browse.config(state=st)
            for b in (getattr(self, "btn_data_browse", None),
                      getattr(self, "btn_data_default", None)):
                if b is not None:
                    b.config(state=st)
        except TclError:
            pass

    def _save_ini(self, key, value):
        ok, err = ini_write(key, value)
        if ok:
            if value:
                self._log(tr("log.ini_written", name=key, path=value))
            else:
                self._log(tr("log.ini_cleared", name=key))
            self._refresh_env_line()
        else:
            self._log(tr("log.ini_write_fail", e=err))
        return ok

    def browse_data(self):
        if self.running:
            return
        cur = data_path("bstantei")
        p = filedialog.askdirectory(title=tr("dlg.pick_data"),
                                    initialdir=cur if os.path.isdir(cur) else APP_DIR)
        if not p:
            return
        p = os.path.abspath(p)
        if self._save_ini("data", p):
            self._refresh_wav_var()
            if not any(os.path.isdir(os.path.join(p, str(n))) for n in CHAPTERS):
                self._log(tr("log.data_looks_wrong", dir=p))

    def default_data(self):
        if self.running or not ini_value("data"):
            return
        if self._save_ini("data", ""):
            self._refresh_wav_var()

    def browse_bios(self):
        if self.running:
            return
        if not os.path.exists(self.bios_path):
            self._handle_missing_bios()
            self._refresh_env_line()
            return
        p = filedialog.askopenfilename(title=tr("dlg.pick_bios"),
                                       filetypes=[(tr("dlg.files_bios"), "*.sfc *.smc *.bin"),
                                                  (tr("dlg.files_all"), "*.*")])
        if not p:
            return
        if os.path.abspath(p) == os.path.abspath(self.bios_path):
            return
        if not messagebox.askyesno(tr("dlg.replace_bios"),
                                   tr("dlg.replace_bios_msg", name=os.path.basename(self.bios_path))):
            return
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.bios_path)), exist_ok=True)
            shutil.copy2(p, self.bios_path)
        except (shutil.Error, OSError) as e:
            messagebox.showerror(tr("dlg.error"), tr("dlg.bios_copy_fail", e=e))
            return
        self._log(tr("log.bios_replaced", name=os.path.basename(self.bios_path), src=p))
        self._save_ini("bios", os.path.abspath(self.bios_path))

    def _handle_missing_bios(self):
        messagebox.showinfo(tr("dlg.bios_check"), tr("dlg.bios_check_msg"))
        p = filedialog.askopenfilename(title=tr("dlg.pick_bios"),
                                       filetypes=[(tr("dlg.files_bios"), "*.sfc *.smc *.bin"),
                                                  (tr("dlg.files_all"), "*.*")])
        if not p:
            self._status("status.bios_missing")
            return False
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.bios_path)), exist_ok=True)
            shutil.copy2(p, self.bios_path)
            self._log(tr("log.bios_placed", name=os.path.basename(self.bios_path)))
            return True
        except (shutil.Error, OSError) as e:
            messagebox.showerror(tr("dlg.error"), tr("dlg.bios_copy_fail", e=e))
            return False

    def _hint_chapter(self):
        self._status("status.hint_chapter_click")

    def select_chapter(self, n):
        if self.running:
            return
        self.chapter = n
        boot = self._clamp_boot(self.boot_var.get())
        self._refresh_wav_var()
        self._set_step(3, command=self.start_broadcast)
        self.btn_main.config(state="normal")
        for k, b in self.chapter_buttons:
            b.config(state="disabled" if k == n else "normal", relief="sunken" if k == n else "raised")
        self.cfg["chapter"] = n
        self._persist()

        dur = self._dur_suffix(n)
        hint = lua_hint(n)
        self._status("status.chapter_locked", name=chapter_tpl(n), dur=self._dur_tpl(n),
                     hint=hint, boot=boot)
        self._log(tr("log.chapter", name=chapter_name(n), n=n, dur=dur,
                     hint=hint if n == 2 else ""))
        self._check_broadcast_id(n)

    def _check_broadcast_id(self, n):
        base = read_broadcast_ids(rp("bstantei", "0"))
        chap = read_broadcast_ids(rp("bstantei", str(n)))
        if not base or not chap:
            return
        same = (base == chap)
        self._log(tr("log.broadcast_id", a=f"{base[0]}/{base[1]}/{base[2]}", n=n,
                     b=f"{chap[0]}/{chap[1]}/{chap[2]}",
                     tag=tr("log.id_same") if same else tr("log.id_ok")))
        if same:
            self._status("status.id_collision", n=n)

    def _default_wav(self, n=None):
        n = n or self.chapter or 1
        return os.path.join(wav_dir(), f"{n}.wav")

    def _effective_wav(self):
        n = self.chapter or 1
        custom = (self.cfg.get("wav_map") or {}).get(str(n))
        return custom if custom and os.path.exists(custom) else self._default_wav(n)

    def _refresh_wav_var(self):
        self.wav_var.set(self._effective_wav())

    def browse_wav(self):
        if not self.chapter:
            messagebox.showinfo(tr("dlg.notice"), tr("dlg.pick_chapter_first"))
            return
        p = filedialog.askopenfilename(title=tr("dlg.pick_wav"),
                                       filetypes=[(tr("dlg.files_wav"), "*.wav"),
                                                  (tr("dlg.files_all"), "*.*")])
        if not p:
            return
        self.cfg.setdefault("wav_map", {})[str(self.chapter)] = os.path.abspath(p)
        self._persist()
        self.wav_var.set(os.path.abspath(p))
        info = wav_info(p)
        self._log(tr("log.audio_custom", name=os.path.basename(p),
                     info=(f" · {info[1]}Hz/{info[0]}ch/{info[2]}bit · {fmt_mmss(info[3])}"
                           if info else "")))

    def reset_wav(self):
        if self.chapter:
            (self.cfg.get("wav_map") or {}).pop(str(self.chapter), None)
            self._persist()
            self._refresh_wav_var()
            self._log(tr("log.audio_default"))

    def _scene_exits(self):
        exits = [(parse_scene_exit(s), s) for s in DEFAULT_SCENE_EXITS]
        exits.sort(key=lambda e: e[0])
        return exits

    def _mute_active(self):
        return self.chapter in MUTE_CHAPTERS

    def start_broadcast(self):
        if self.running:
            return
        if not self.mesen_path or not os.path.exists(self.mesen_path):
            messagebox.showerror(tr("dlg.cannot_start"), tr("dlg.mesen_missing"))
            return
        if not self.chapter:
            messagebox.showerror(tr("dlg.cannot_start"), tr("dlg.chapter_missing"))
            return
        base = rp("bstantei", "0")
        chap = rp("bstantei", str(self.chapter)) if self.chapter else None
        wav = self._effective_wav()

        need = [(self.bios_path, "BS-X BIOS"), (base, "bstantei/0")]
        need.append((chap, f"bstantei/{self.chapter}"))
        need.append((wav, tr("lbl.audio")))
        for p, name in need:
            if not p or not os.path.exists(p):
                messagebox.showerror(tr("dlg.files_missing"),
                                     tr("dlg.file_missing_msg", name=name, p=p))
                return

        try:
            offset_ms = int(self.offset_var.get() or 0)
        except ValueError:
            messagebox.showerror(tr("dlg.bad_param"), tr("dlg.offset_int"))
            return
        boot_seconds = self._clamp_boot(self.boot_var.get())
        if self.boot_var.get().strip() != str(boot_seconds):
            self.boot_var.set(str(boot_seconds))
        buffer_frames = BUFFER_FRAMES
        exits = self._scene_exits()

        self.cfg["offset_ms"] = offset_ms
        self._persist()

        mute_on = self._mute_active()

        info = wav_info(wav)
        total = info[3] if info else 0.0
        self.samples = []
        self.fit = [0, 0.0, 0.0, 0.0, 0.0]
        self._last_drawn = (0.0, None)

        self.running = True
        self.stop_evt.clear()
        self._lock_ui(True)
        self._set_state(phase="boot", clock=self._boot_start_clock(boot_seconds),
                        audio_pos=0.0, audio_total=total,
                        lag=None, k=None, exit_target=None)
        self._mute("mute.off")
        self._status("status.booting")

        self.engine = threading.Thread(target=self._sequence, name="TanteiEngine", daemon=True,
                                       args=(chap, wav, offset_ms, buffer_frames, exits,
                                             mute_on, boot_seconds))
        self.engine.start()

    def _lock_ui(self, locked):
        self.btn_main.config(state="disabled" if locked else "normal")
        for _n, b in self.chapter_buttons:
            b.config(state="disabled")
        self.chk_monitor.config(state="disabled" if locked else "normal")
        self.boot_spin.config(state="disabled" if locked else "normal")
        self.btn_mesen_browse.config(state="disabled" if locked else "normal")
        self.btn_bios_browse.config(state="disabled" if locked else "normal")
        for _b in (getattr(self, "btn_data_browse", None),
                   getattr(self, "btn_data_default", None)):
            if _b is not None:
                _b.config(state="disabled" if locked else "normal")
        for _c, b in getattr(self, "lang_buttons", ()):
            b.config(state="disabled" if locked else "normal")

    def _on_engine_finished(self):
        reason, self._stop_reason = self._stop_reason, None

        if reason == "mesen_closed":
            self._log(tr("log.mesen_closed_sys"))
            self.reset_system()
            self._status("status.mesen_closed_reset")
            return

        if reason == "lua_closed":
            self._log(tr("log.lua_closed_sys"))
            self.reset_system()
            self._status("status.lua_closed_reset")
            return

        if reason == "finished":
            self._status("status.finished_in3")
            self.root.after(3000, self._auto_reset_after_finish)
            return

        if self.stop_evt.is_set():
            return
        self.btn_main.config(state="disabled")

    def _auto_reset_after_finish(self):
        self._log(tr("log.auto_reset"))
        self.reset_system()
        self._status("status.finished_reset")

    def _lua_gone(self):
        if self._lua_killed:
            return False
        proc = getattr(self, "proc", None)
        if proc is None or proc.poll() is not None:
            return False
        sig = getattr(self, "lua_stop", None)
        if sig is not None and sig.poll():
            self._lua_gone_why = "script_ended"
            return True
        w = getattr(self, "lua_watch", None)
        if w is not None and w.poll() is False:
            self._lua_gone_why = "window"
            return True
        return False

    def _kill_for_lua(self, proc):
        if self._lua_killed:
            return False
        self._lua_killed = True
        self._stop_reason = "lua_closed"
        self._log(tr("log.lua_stopped",
                     why=tr("log.why_script") if self._lua_gone_why == "script_ended"
                     else (tr("log.why_window") if self._lua_gone_why == "window" else "?")))
        self._close_mesen(proc)
        return True

    def _start_lua_watchdog(self, proc):
        if getattr(self, "lua_stop", None) is None and getattr(self, "lua_watch", None) is None:
            return

        def _run():
            while proc.poll() is None:
                time.sleep(0.3)
                if proc.poll() is not None:
                    return
                if self.running or self._lua_killed:
                    continue
                if self._lua_gone() and self._kill_for_lua(proc):
                    try:
                        self.root.after(0, self._on_engine_finished)
                    except (TclError, RuntimeError):
                        pass
                    return

        threading.Thread(target=_run, name="LuaWatchdog", daemon=True).start()

    def _close_mesen(self, proc):
        try:
            proc.terminate()
        except Exception as e:
            self._log(tr("log.close_fail", e=repr(e)))
            return False
        for _ in range(20):
            if proc.poll() is not None:
                self._log(tr("log.closed"))
                return True
            time.sleep(0.1)
        try:
            proc.kill()
            self._log(tr("log.killed"))
            return True
        except Exception as e:
            self._log(tr("log.kill_fail", e=repr(e)))
            return False

    def _sequence(self, chap_dir, wav, offset_ms, buffer_frames, exits, mute_on, boot_seconds):
        try:
            settings_path = os.path.join(self.mesen_dir, "settings.json")
            if os.path.exists(settings_path):
                if backup_enabled():
                    try:
                        os.makedirs(backup_dir(), exist_ok=True)
                        backup = os.path.join(backup_dir(), "settings.first_run_backup.json")
                        if not os.path.exists(backup):
                            shutil.copy2(settings_path, backup)
                            self._log(tr("log.cfg_backup", path=backup))
                    except OSError:
                        pass
                patch_settings(settings_path, log=self._log)
            else:
                self._log(tr("log.cfg_missing"))

            sat = os.path.join(self.mesen_dir, "Satellaview")
            n_del = clear_dir(sat)
            ok, skipped = copy_dir(rp("bstantei", "0"), sat)
            self._log(tr("log.sat_cleared", n=n_del, ok=ok,
                         skipped=tr("log.skipped", n=skipped) if skipped else ""))

            cmd = [self.mesen_path, self.bios_path]
            lua = None
            if mute_on:
                cand = lua_path()
                if os.path.exists(cand):
                    lua = cand
                    cmd.append(lua)
                else:
                    self._log(tr("log.lua_missing", name=os.path.basename(cand)))
            self._log(tr("log.launch", exe=os.path.basename(self.mesen_path),
                         lua=tr("log.launch_lua", name=os.path.basename(lua)) if lua
                         else tr("log.launch_nolua")))
            proc = subprocess.Popen(cmd, cwd=self.mesen_dir)
            launch_t = time.time()
            self.proc = proc
            self.lua_watch = (LuaWindowWatcher(proc.pid, (os.path.basename(lua),))
                              if lua else None)
            self.lua_stop = (LuaStopSignal(
                self.mesen_dir, since=launch_t,
                script_stem=os.path.splitext(os.path.basename(lua))[0],
                extra_dirs=[ROOT], log=self._log) if lua else None)
            self._lua_killed = False
            self._start_lua_watchdog(proc)

            boot = boot_seconds
            self._set_state(phase="boot")
            self._status("status.booting_toast", boot=boot)
            self._log(tr("log.clock", start=self._boot_start_clock(boot), boot=boot))
            t0 = time.time()
            start_sim = TRIGGER_CLOCK - timedelta(seconds=boot)
            while True:
                if self.stop_evt.is_set():
                    self._log(tr("log.abort_wait"))
                    return
                if proc.poll() is not None:
                    self._stop_reason = "mesen_closed"
                    self._log(tr("log.mesen_closed_wait"))
                    return
                if self._lua_gone():
                    self._kill_for_lua(proc)
                    return
                el = time.time() - t0
                if el >= boot:
                    break
                self._set_state(clock=(start_sim + timedelta(seconds=el)).strftime("%H:%M:%S"))
                time.sleep(0.1)
            self._set_state(clock="18:00:00")
            if self.lua_stop is not None and self.lua_stop.dir is None:
                self._log(tr("log.no_closed_marker",
                             dirs=repr(self.lua_stop._candidates()[:5])))
            if self.lua_watch is not None and not self.lua_watch.seen:
                self._log(tr("log.no_script_window",
                             titles=repr(LuaWindowWatcher._enum_titles(proc.pid) or [])))

            ok, skipped = copy_dir(chap_dir, sat)
            self._log(tr("log.chapter_pushed", ok=ok,
                         skipped=tr("log.skipped", n=skipped) if skipped else ""))

            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=buffer_frames)
            dev = pygame.mixer.get_init()
            self._log(tr("log.audio_dev", dev=dev, frames=buffer_frames))

            offset = offset_ms / 1000.0
            if offset > 0:
                self._log(tr("log.offset_late", ms=offset_ms, s=offset))
                time.sleep(offset)
            pygame.mixer.music.load(wav)
            pygame.mixer.music.set_volume(1.0)
            if offset < 0:
                self._log(tr("log.offset_skip", ms=offset_ms, s=abs(offset)))
                pygame.mixer.music.play(start=abs(offset))
            else:
                pygame.mixer.music.play()
            self._set_state(phase="play")
            self._status("status.playing")
            self._log(tr("log.play", name=os.path.basename(wav)))
            self._monitor_loop(pygame, offset, exits, mute_on, proc)

            if proc is not None and proc.poll() is None and not self.stop_evt.is_set():
                self._stop_reason = "finished"
                self._close_mesen(proc)

        except Exception as e:
            self._log(tr("log.error", e=repr(e)))
            self._log(traceback.format_exc().rstrip())
            self._set_state(phase="error")
            self._status("status.error", e=e)
        finally:
            was_running = self.running
            self.running = False
            if was_running and self._get_state().get("phase") != "error":
                self._set_state(phase="done")
            try:
                self.root.after(0, self._on_engine_finished)
            except (TclError, RuntimeError):
                pass

    def _monitor_loop(self, pygame, offset, exits, mute_on, proc=None):
        flag_file = resolve_flag_file(None, self.mesen_dir)
        mute_state, mute_target, mute_start = "IDLE", None, 0.0
        last_unmute = None
        last_seq = None
        warned_missing = False
        rescan_tick = 0
        if mute_on:
            self._log(tr("log.flag_file", path=rel(flag_file, ROOT)))
            self._log(tr("log.exits",
                         a=" / ".join(fmt_mmss(e[0]) for e in exits),
                         b=" / ".join(fmt_mmss(e[0] + offset) for e in exits),
                         ms=f"{offset * 1000:+.0f}"))
            if not os.path.exists(flag_file):
                self._log(tr("log.flag_missing"))
                warned_missing = True

        t_play = time.time()
        last_sample = 0.0
        next_log = LOG_INTERVAL
        next_status = 2.0
        hard_mute = max(0.0, -offset)
        exited = False
        try:
            while True:
                if self.stop_evt.is_set():
                    self._log(tr("log.abort"))
                    break
                if proc is not None and proc.poll() is not None:
                    exited = True
                    self._stop_reason = "mesen_closed"
                    self._log(tr("log.mesen_closed_play"))
                    self._set_state(phase="done")
                    self._status("status.mesen_closed_stopped")
                    break
                if self._lua_gone():
                    exited = True
                    self._set_state(phase="done")
                    self._status("status.lua_stopped_closing")
                    self._kill_for_lua(proc)
                    break
                w = time.time() - t_play
                busy = pygame.mixer.music.get_busy()
                pos_ms = pygame.mixer.music.get_pos() / 1000.0
                if pos_ms < 0:
                    pos_ms = 0.0
                content = hard_mute + pos_ms
                lag = w - pos_ms

                if w - last_sample >= 0.1:
                    last_sample = w
                    f = self.fit
                    f[0] += 1; f[1] += w; f[2] += pos_ms
                    f[3] += w * w; f[4] += w * pos_ms
                    n = f[0]
                    den = n * f[3] - f[1] * f[1]
                    k = ((n * f[4] - f[1] * f[2]) / den) if den else 1.0
                    self._set_state(audio_pos=content, lag=lag, k=k)

                if mute_on:
                    seq = read_seq(flag_file)
                    if seq is not None:
                        if warned_missing:
                            warned_missing = False
                            self._log(tr("log.marker_found"))
                        if last_seq is None:
                            last_seq = seq
                        elif seq != last_seq:
                            fresh = seq > last_seq
                            last_seq = seq
                            if fresh and mute_state == "IDLE":
                                nx = next_exit(exits, content)
                                ok, why = mute_enter_ok(content, nx, last_unmute)
                                if not ok:
                                    self._log(tr("log.enter_rejected", t=fmt_mmss(content),
                                                 seq=seq, why=why))
                                else:
                                    self._log(tr("log.enter_accept", t=fmt_mmss(content),
                                                 seq=seq, exit=fmt_mmss(nx[0])))
                                    self._mute("mute.fading")
                                    self._set_state(exit_target=nx[0])
                                    mute_start = time.time()
                                    ramp_volume(0.0, 0.5, 20, self.stop_evt)
                                    mute_state = "MUTED"
                                    mute_target = nx[0]
                                    self._mute("mute.on", t=fmt_mmss(mute_target))
                    elif not os.path.exists(flag_file):
                        rescan_tick += 1
                        if rescan_tick >= 30:
                            rescan_tick = 0
                            nf = resolve_flag_file(None, self.mesen_dir)
                            if nf != flag_file and os.path.exists(nf):
                                flag_file = nf
                                self._log(tr("log.rescan", path=rel(nf, ROOT)))

                    if mute_state == "MUTED" and mute_target is not None and content >= mute_target:
                        held = time.time() - mute_start
                        self._log(tr("log.restore", t=fmt_mmss(content), held=held))
                        self._mute("mute.resuming")
                        self._set_state(exit_target=None)
                        ramp_volume(1.0, 0.5, 20, self.stop_evt)
                        mute_state, mute_target = "IDLE", None
                        last_unmute = content
                        self._mute("mute.off")

                if w - self._last_drawn[0] >= 0.5:
                    self._last_drawn = (w, lag)
                    self.samples.append((w, lag))

                if w >= next_status:
                    total = self._get_state().get("audio_total") or 0.0
                    self._status("status.play_running",
                                 pos=fmt_mmss(content),
                                 total=tr("status.total_suffix", t=fmt_mmss(total)) if total else "",
                                 lag=f"{lag:+.2f}s",
                                 muted=_Tpl("status.muted_tag") if mute_state == "MUTED" else "")
                    next_status += 2.0

                if w >= next_log:
                    self._log(tr("log.lag_line", w=fmt_mmss(w), pos=fmt_mmss(content),
                                 lag=f"{lag:+.2f}s",
                                 tag="  [mute]" if mute_state == "MUTED" else ""))
                    next_log += LOG_INTERVAL

                if not busy and w > 1.0:
                    break
                time.sleep(SIGNAL_CHECK_INTERVAL)

        finally:
            try:
                pygame.mixer.music.set_volume(1.0)
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
            f = self.fit
            if f[0] >= 2:
                n = f[0]
                den = n * f[3] - f[1] * f[1]
                k = ((n * f[4] - f[1] * f[2]) / den) if den else 1.0
                self._log(tr("log.stats", n=n, k=k, pct=f"{(k - 1) * 100:+.4f}"))
                self._set_state(k=k)
                self._mute("mute.off")
                if exited:
                    self._status("status.mesen_closed_stopped")
                else:
                    self._status("status.finished_k", k=f"{k:.6f}", pct=f"{(k - 1) * 100:+.4f}")
            else:
                self._mute("mute.off")
                if exited:
                    self._status("status.mesen_closed_stopped")
                else:
                    self._status("status.finished")
            if exited:
                self._set_state(phase="done")
                self._log(tr("log.done_closed"))
            else:
                self._log(tr("log.done"))

    def reset_system(self):
        self._log(tr("log.reset"))
        self.running = False
        self.stop_evt.set()
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.music.set_volume(1.0)
                pygame.mixer.music.unload()
        except Exception:
            pass

        self.chapter = None
        self.samples = []
        self.fit = [0, 0.0, 0.0, 0.0, 0.0]
        self._last_drawn = (0.0, None)
        self.chart.delete("all")
        self._set_state(phase="idle", clock=self._boot_start_clock(), audio_pos=0.0,
                        audio_total=0.0, lag=None, k=None, exit_target=None)
        self._mute("mute.off")
        for _n, b in self.chapter_buttons:
            b.config(state="normal", relief="raised")
        self.chk_monitor.config(state="normal")
        self.boot_spin.config(state="normal")
        for _c, b in getattr(self, "lang_buttons", ()):
            b.config(state="normal")
        if self.mesen_path:
            self._set_step(2, command=self._hint_chapter)
            self.btn_main.config(state="normal")
            self._status("status.pick_chapter")
        else:
            self._set_step(1, command=self.select_mesen)
            self.btn_main.config(state="normal")
            self._status("status.pick_mesen")
        self._refresh_env_line()
        self.root.after(400, lambda: self.btn_main.config(state="normal"))

    def _mesen_running(self):
        """Mesen 是否还开着：先看本终端启动的进程，再枚举同名进程核对目录。"""
        proc = getattr(self, "proc", None)
        if proc is not None and proc.poll() is None:
            return True
        pids = proc_pids("Mesen.exe")
        if not pids:
            return False
        want = ""
        if self.mesen_dir:
            want = os.path.normcase(os.path.abspath(self.mesen_dir))
        for pid in pids:
            exe = proc_exe_path(pid)
            if not exe or not want:
                return True
            if os.path.normcase(os.path.dirname(os.path.abspath(exe))) == want:
                return True
        return False

    def delete_save(self):
        srm = os.path.join(self.mesen_dir or ROOT, "Saves", "BsxBios.srm")
        if self._mesen_running():
            self._log(tr("log.save_del_blocked"))
            messagebox.showwarning(tr("dlg.notice"), tr("dlg.save_del_running"))
            return
        if not messagebox.askyesno(tr("dlg.del_save"), tr("dlg.del_save_msg")):
            return
        if not os.path.exists(srm):
            messagebox.showinfo(tr("dlg.notice"), tr("dlg.save_not_found"))
            return
        try:
            os.remove(srm)
            self._log(tr("log.save_deleted", path=rel(srm, ROOT)))
            messagebox.showinfo(tr("dlg.ok"), tr("dlg.save_deleted"))
        except OSError as e:
            messagebox.showerror(tr("dlg.error"), tr("dlg.save_del_fail", e=e))

    def _tick(self):
        try:
            st = self._get_state()
            phase = st["phase"]
            clock = st["clock"]
            if phase == "idle":
                clock = self._boot_start_clock()
            elif phase in ("play", "done"):
                if phase == "play" or (st.get("audio_total") or 0) > 0:
                    clock = fmt_hms(BROADCAST_START_SEC + (st.get("audio_pos") or 0.0))
            self.clock_var.set(clock)
            self.time_label.config(fg="#c0392b" if phase in ("idle", "boot") else "#27ae60")
            self.status_var.set(st["status"])

            self._refresh_stats()

            if self.show_monitor.get() and self.samples and (time.time() - self._last_chart_draw) >= 1.0:
                self._last_chart_draw = time.time()
                self._draw_chart()

            if self._logbuf:
                with self.lock:
                    lines, self._logbuf = self._logbuf, []
                self.log_box.config(state="normal")
                for ln in lines:
                    tag = None
                    if any(w in ln for w in ("错误", "⚠️", "🔴", "[Error]", "[エラー]")):
                        tag = "err"
                    elif any(w in ln for w in ("✓", "完成", "[Done]", "[完了]")):
                        tag = "ok"
                    self.log_box.insert("end", ln + "\n", tag)
                self.log_box.see("end")
                self.log_box.config(state="disabled")
        except TclError:
            return
        self.root.after(120, self._tick)

    def _draw_chart(self):
        c = self.chart
        w, h = c.winfo_width(), c.winfo_height()
        if w < self._px(160) or h < self._px(40):
            return
        c.delete("all")
        pad_l, pad_r, pad_t, pad_b = self._px(40), self._px(6), self._px(6), self._px(20)
        xs = [p[0] for p in self.samples]
        ys = [p[1] for p in self.samples]
        x_max = max(60.0, xs[-1] if xs else 60.0)
        y_abs = max(0.15, max(abs(v) for v in ys) * 1.25 if ys else 0.15)

        def X(t):
            return pad_l + (w - pad_l - pad_r) * (t / x_max)

        def Y(v):
            mid = (pad_t + h - pad_b) / 2
            half = (h - pad_t - pad_b) / 2
            return mid - half * (v / y_abs)

        for frac in (0, 0.5, 1.0):
            v = -y_abs + 2 * y_abs * frac
            y = Y(v)
            c.create_line(pad_l, y, w - pad_r, y,
                          fill="#c8d0d8" if frac == 0.5 else "#e8edf1", dash=(3, 4) if frac == 0.5 else ())
            c.create_text(pad_l - 3, y, text=f"{v:+.2f}", anchor="e",
                          font=("Consolas", -max(8, self._px(9))), fill="#7f8c8d")
        fracs = (0, 0.5, 1.0) if w < self._px(380) else (0, 0.25, 0.5, 0.75, 1.0)
        for frac in fracs:
            t = x_max * frac
            x = X(t)
            c.create_line(x, pad_t, x, h - pad_b, fill="#f0f3f6")
            anchor = "nw" if frac == 0 else ("ne" if frac >= 1.0 else "n")
            c.create_text(x, h - pad_b + self._px(3), text=fmt_mmss(t), anchor=anchor,
                          font=("Consolas", -max(8, self._px(9))), fill="#95a5a6")
        pts = []
        step = max(1, len(self.samples) // 600)
        for t, v in self.samples[::step]:
            pts.extend((X(t), Y(v)))
        if len(pts) >= 4:
            c.create_line(*pts, fill="#2980b9", width=max(1, self._px(1.4)))
        k = self._get_state().get("k")
        if k is not None:
            c.create_text(w - pad_r - 2, pad_t + 2,
                          text=f"k={k:.6f} ({(k - 1) * 100:+.4f}%)", anchor="ne",
                          font=("Consolas", -max(8, self._px(10))), fill="#c0392b")

    def _on_close(self):
        self.stop_evt.set()
        self.running = False
        try:
            self.cfg["show_monitor"] = bool(self.show_monitor.get())
            self.cfg["pin_top"] = bool(self.pin_top.get())
            self.cfg["offset_ms"] = int(self.offset_var.get() or 0)
            if self.chapter:
                self.cfg["chapter"] = self.chapter
        except Exception:
            pass
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except TclError:
            pass

    def run(self):
        self.root.mainloop()

def main():
    TanteiTerminal().run()


if __name__ == "__main__":
    main()
