-- ⚠️ 不要关闭本窗口 / Do not close this window —— 
-- 关闭 = 终端立刻关 Mesen 并中止本次推送 / closing it makes the terminal quit Mesen and abort this push.

local read = emu.read
local log = emu.log
local snesMem = emu.memType.snesMemory
local dspMem = emu.memType.spcDspRegisters

local SCENES = {
    { name = "发声场景", addr = 0x7E0000 + 0x1A885, inValue = 0x14 },
}

local FLAG_FILE = "scene_flag.txt"
local CLOSED_FILE = "script_closed.txt"
local CHECK_INTERVAL = 4
local USE_APU = true
local MIN_VOICES = 1
local MIN_ENVX = 0x08
local SRCN_ALLOW = { [0x10] = true, [0x17] = true }
local DEBUG_UNKNOWN = false
local ENTER_WINDOW = 20
local ENTER_HITS = 6
local QUIET_TICKS = 90
local LOG_GAP_TICKS = 7200
local DSP_ENDX = 0x7C
local DSP_ENVX = 0x08
local DSP_SRCN = 0x04

local function dsp(reg)
    return read(reg, dspMem, true) or 0
end

local function s8(v)
    if v >= 0x80 then return v - 0x100 end
    return v
end

local function bitOf(byte, i)
    return math.floor(byte / (2 ^ i)) % 2
end

local function voiceEnv(v)
    return dsp(v * 0x10 + DSP_ENVX)
end

local function apuActiveVoices(onlyAllow)
    local endx = dsp(DSP_ENDX)
    local n = 0
    for v = 0, 7 do
        local b = v * 0x10
        local vl = s8(dsp(b + 0))
        local vr = s8(dsp(b + 1))
        local pitch = dsp(b + 2) + dsp(b + 3) * 256
        if pitch ~= 0 and (vl ~= 0 or vr ~= 0) and bitOf(endx, v) == 0
            and voiceEnv(v) >= MIN_ENVX then
            if (not onlyAllow) or SRCN_ALLOW[dsp(b + DSP_SRCN)] then
                n = n + 1
            end
        end
    end
    return n
end

local function voiceList()
    local endx = dsp(DSP_ENDX)
    local t = {}
    for v = 0, 7 do
        local b = v * 0x10
        local pitch = dsp(b + 2) + dsp(b + 3) * 256
        if pitch ~= 0 and (s8(dsp(b)) ~= 0 or s8(dsp(b + 1)) ~= 0) and bitOf(endx, v) == 0 then
            t[#t + 1] = string.format("%d:s%02X e%02X p%04X",
                v, dsp(b + DSP_SRCN), voiceEnv(v), pitch)
        end
    end
    if #t == 0 then return "-" end
    return table.concat(t, " ")
end

local frameCounter = 0
local ticks = 0
local lastLogTick = 0
local inScene = false
local seq = 0
local win = {}
local winPos = 0
local winHits = 0
local lastLoudTick = -1e9
local lastUnknownLog = 0

local cachedDataFolder = nil
local function writeFlag(name, v)
    if not cachedDataFolder then
        cachedDataFolder = emu.getScriptDataFolder()
        if not cachedDataFolder or cachedDataFolder == "" then
            log("错误：无法获取脚本数据文件夹路径，请检查 Mesen 设置中是否允许 I/O 访问")
            return
        end
    end
    local path = cachedDataFolder .. "/" .. name
    local f, err = io.open(path, "w")
    if f then
        f:write(v)
        f:close()
    else
        log(string.format("写入 %s 失败: %s", name, tostring(err)))
    end
end

local function monitor()
    ticks = ticks + 1
    frameCounter = frameCounter + 1
    if frameCounter < CHECK_INTERVAL then return end
    frameCounter = 0

    local s = SCENES[1]
    local val = read(s.addr, snesMem, false)
    local nv, nvAllow = nil, nil
    if USE_APU then
        nv = apuActiveVoices(false)
        nvAllow = apuActiveVoices(true)
    end

    local flagIn = (val == s.inValue)
    local cond
    if USE_APU then
        cond = flagIn and (nvAllow >= MIN_VOICES)
        if DEBUG_UNKNOWN and flagIn and nvAllow < MIN_VOICES and nv >= MIN_VOICES then
            if lastUnknownLog == 0 or ticks - lastUnknownLog >= LOG_GAP_TICKS then
                lastUnknownLog = ticks
                log(string.format("[静音] 标志内有一未知音源的 BGM（不静音）：%s", voiceList()))
            end
        end
    else
        cond = flagIn
    end

    winPos = winPos % ENTER_WINDOW + 1
    local old = win[winPos] or 0
    local cur = cond and 1 or 0
    win[winPos] = cur
    winHits = winHits - old + cur
    if cur == 1 then lastLoudTick = ticks end

    if not inScene then
        if winHits < ENTER_HITS then return end
        inScene = true
        seq = seq + 1
        writeFlag(FLAG_FILE, tostring(seq))
        if lastLogTick == 0 or ticks - lastLogTick >= LOG_GAP_TICKS then
            lastLogTick = ticks
            log(string.format("[静音] 进入发声场景 #%d（标志=%02X 声部=%d %s）",
                seq, val or 0, nv or -1, voiceList()))
        end
        return
    end

    if ticks - lastLoudTick >= QUIET_TICKS then inScene = false end
end

local function onReset()
    inScene = false
    seq = 0
    ticks, lastLogTick = 0, 0
    win, winPos, winHits = {}, 0, 0
    lastLoudTick = -1e9
    lastUnknownLog = 0
    writeFlag(FLAG_FILE, "0")
    writeFlag(CLOSED_FILE, "0")
    log("bs.lua 已就绪：监听发声场景（请勿关闭本窗口）")
end

local function onScriptEnded()
    writeFlag(CLOSED_FILE, "1")
end

emu.addEventCallback(monitor, emu.eventType.endFrame)
emu.addEventCallback(onReset, emu.eventType.reset)
emu.addEventCallback(onScriptEnded, emu.eventType.scriptEnded)

onReset()
