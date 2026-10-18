"""
System Monitor — background metric checks with voice alert support.
Zero subprocess calls on all platforms — uses ctypes/pynvml/psutil/wmi only.
"""
import ctypes
import platform
import time

import psutil

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"

DEFAULT_THRESHOLDS = {
    "cpu":  90.0,
    "ram":  90.0,
    "temp": 85.0,
    "gpu":  95.0,
}

_COOLDOWN   = 300
_CPU_STREAK = 3

# ── NVML DLL cache (Windows: nvml.dll, Linux: libnvidia-ml.so.1) ─────────────
_nvml_lib: object = None
_nvml_ok:  object = None   # None=untested  True=works  False=unavailable


def _nvml_gpu() -> float:
    """GPU utilisation via NVML — zero subprocess on all platforms."""
    global _nvml_lib, _nvml_ok
    if _nvml_ok is False:
        return -1.0
    try:
        class _Util(ctypes.Structure):
            _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]

        if _nvml_lib is None:
            if _OS == "Windows":
                candidates = ("nvml", r"C:\Windows\System32\nvml.dll")
                _load = ctypes.WinDLL
            else:
                candidates = (
                    "libnvidia-ml.so.1",
                    "libnvidia-ml.so",
                    "libnvidia-ml.dylib",
                )
                _load = ctypes.CDLL
            for name in candidates:
                try:
                    lib = _load(name)
                    lib.nvmlInit_v2()
                    _nvml_lib = lib
                    break
                except Exception:
                    continue

        if _nvml_lib is None:
            _nvml_ok = False
            return -1.0

        dev = ctypes.c_void_p()
        _nvml_lib.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(dev))
        u = _Util()
        _nvml_lib.nvmlDeviceGetUtilizationRates(dev, ctypes.byref(u))
        _nvml_ok = True
        return float(u.gpu)
    except Exception:
        _nvml_ok = False
        return -1.0


def _get_gpu_usage() -> float:
    # pynvml — subprocess-free, works everywhere if installed
    try:
        import pynvml  # type: ignore
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        return float(pynvml.nvmlDeviceGetUtilizationRates(h).gpu)
    except Exception:
        pass

    return _nvml_gpu()


def _get_cpu_temp() -> float:
    # psutil — works on Linux; occasionally Windows with proper drivers
    try:
        temps = psutil.sensors_temperatures()
        for name in ["coretemp", "k10temp", "cpu_thermal", "acpitz",
                     "cpu-thermal", "zenpower", "it8688"]:
            if name in temps and temps[name]:
                return temps[name][0].current
        for entries in temps.values():
            if entries:
                return entries[0].current
    except Exception:
        pass

    # Windows: wmi module (pure Python COM, zero subprocess)
    if _OS == "Windows":
        try:
            import wmi  # type: ignore
            w = wmi.WMI(namespace="root/wmi")
            tz = w.MSAcpi_ThermalZoneTemperature()
            if tz:
                return (tz[0].CurrentTemperature / 10.0) - 273.15
        except Exception:
            pass

    return -1.0


def get_system_status() -> dict:
    """Snapshot of current system metrics for the system_status tool."""
    cpu  = psutil.cpu_percent(interval=0.2)
    ram  = psutil.virtual_memory()
    temp = _get_cpu_temp()
    gpu  = _get_gpu_usage()

    boot_time   = psutil.boot_time()
    uptime_secs = time.time() - boot_time
    uptime_h    = int(uptime_secs // 3600)
    uptime_m    = int((uptime_secs % 3600) // 60)

    return {
        "cpu_percent":   round(cpu, 1),
        "ram_percent":   round(ram.percent, 1),
        "ram_used_gb":   round(ram.used   / 1024 ** 3, 1),
        "ram_total_gb":  round(ram.total  / 1024 ** 3, 1),
        "cpu_temp_c":    round(temp, 1) if temp > 0 else None,
        "gpu_percent":   round(gpu,  1) if gpu  >= 0 else None,
        "uptime":        f"{uptime_h}h {uptime_m}m",
        "process_count": len(psutil.pids()),
    }


class SystemMonitor:
    """
    Stateful monitor — cooldown state persists across session reconnections.
    Call check() periodically; returns a [SYSTEM_ALERT] string or None.
    """

    def __init__(self, thresholds: dict | None = None):
        self.thresholds   = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self._last_alert: dict[str, float] = {}
        self._cpu_streak  = 0

    def _can_alert(self, key: str) -> bool:
        return (time.monotonic() - self._last_alert.get(key, 0)) > _COOLDOWN

    def _record(self, key: str):
        self._last_alert[key] = time.monotonic()

    def check(self) -> str | None:
        try:
            cpu  = psutil.cpu_percent(interval=None)
            ram  = psutil.virtual_memory().percent
            temp = _get_cpu_temp()
            gpu  = _get_gpu_usage()
        except Exception:
            return None

        alerts: list[str] = []

        if cpu >= self.thresholds["cpu"]:
            self._cpu_streak += 1
            if self._cpu_streak >= _CPU_STREAK and self._can_alert("cpu"):
                alerts.append(
                    f"[SYSTEM_ALERT] CPU usage has been critically high ({cpu:.0f}%) "
                    "for several seconds. Warn the user in their language and suggest "
                    "closing heavy applications."
                )
                self._record("cpu")
                self._cpu_streak = 0
        else:
            self._cpu_streak = 0

        if ram >= self.thresholds["ram"] and self._can_alert("ram"):
            alerts.append(
                f"[SYSTEM_ALERT] RAM is at {ram:.0f}% — nearly exhausted. "
                "Warn the user in their language and suggest freeing memory."
            )
            self._record("ram")

        if temp > 0 and temp >= self.thresholds["temp"] and self._can_alert("temp"):
            alerts.append(
                f"[SYSTEM_ALERT] CPU temperature is {temp:.0f}°C — above the safe limit. "
                "Warn the user in their language and advise reducing system load "
                "or checking cooling."
            )
            self._record("temp")

        if gpu >= 0 and gpu >= self.thresholds["gpu"] and self._can_alert("gpu"):
            alerts.append(
                f"[SYSTEM_ALERT] GPU load is at {gpu:.0f}%. "
                "Briefly inform the user in their language."
            )
            self._record("gpu")

        return " ".join(alerts) if alerts else None


PROTECTED_PROCESSES = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe",
    "wininit.exe", "services.exe", "lsass.exe", "svchost.exe", "fontdrvhost.exe",
    "winlogon.exe", "explorer.exe", "dwm.exe"
}


def optimize_memory(target_process: str | None = None) -> str:
    """
    Frees system memory and optimizes RAM consumption.
    Can terminate a specific runaway process or flush process working sets via Win32.
    """
    import gc
    import os
    gc.collect()

    initial_ram = psutil.virtual_memory()
    initial_used_gb = initial_ram.used / (1024 ** 3)
    initial_pct = initial_ram.percent

    terminated = []
    # If specific target process is requested to close
    if target_process and target_process.strip():
        name_lower = target_process.strip().lower()
        for p in psutil.process_iter(['pid', 'name']):
            try:
                pname = (p.info.get('name') or '').lower()
                if name_lower in pname and pname not in PROTECTED_PROCESSES:
                    # Do not kill current Python process running Liseth
                    if p.info.get('pid') == os.getpid():
                        continue
                    p.terminate()
                    terminated.append(p.info.get('name'))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # Flush Windows working sets
    flushed_count = 0
    if _OS == "Windows":
        try:
            psapi = ctypes.windll.psapi
            kernel32 = ctypes.windll.kernel32
            PROCESS_SET_QUOTA = 0x0100
            PROCESS_QUERY_INFORMATION = 0x0400

            for p in psutil.process_iter(['pid', 'name']):
                try:
                    pname = (p.info.get('name') or '').lower()
                    if pname in PROTECTED_PROCESSES:
                        continue
                    pid = p.info.get('pid')
                    if pid and pid > 4:
                        h_proc = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                        if h_proc:
                            psapi.EmptyWorkingSet(h_proc)
                            kernel32.CloseHandle(h_proc)
                            flushed_count += 1
                except Exception:
                    continue
        except Exception:
            pass

    time.sleep(0.3)
    final_ram = psutil.virtual_memory()
    final_used_gb = final_ram.used / (1024 ** 3)
    final_pct = final_ram.percent
    freed_gb = max(0.0, initial_used_gb - final_used_gb)

    if terminated:
        return (
            f"Se cerró el proceso '{', '.join(set(terminated))}'. "
            f"La memoria RAM pasó del {initial_pct:.0f}% al {final_pct:.0f}%, liberando {freed_gb:.1f} GB de memoria."
        )
    elif freed_gb >= 0.1:
        return (
            f"Memoria optimizada con éxito. Se redujo el uso de RAM del {initial_pct:.0f}% al {final_pct:.0f}%, "
            f"liberando aproximadamente {freed_gb:.1f} GB ({flushed_count} procesos optimizados)."
        )
    else:
        return (
            f"Optimización completada. La memoria RAM se encuentra actualmente al {final_pct:.0f}% ({final_used_gb:.1f} GB en uso)."
        )

