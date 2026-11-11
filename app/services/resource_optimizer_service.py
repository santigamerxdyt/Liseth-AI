"""
Resource Optimizer & Extreme Efficiency Service for Liseth AI / JARVIS.
Monitors and optimizes RAM and CPU consumption across backend services,
enforces bounded memory caches, triggers garbage collection, and provides
a Low-Power Mode ('Modo de Bajo Consumo') for resource-constrained devices.
"""

from __future__ import annotations

import gc
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger("jarvis.resource_optimizer")


class ResourceOptimizerService:
    """
    Monitors process and host telemetry, enforces memory boundaries,
    and coordinates low-power execution profiles for client and server.
    """

    def __init__(self):
        self._low_power_clients: Dict[str, float] = {}  # client_id -> last_active
        self._last_gc_time = time.time()
        self._gc_interval_seconds = 120  # Collect garbage every 2 minutes or on threshold
        self._start_time = time.time()

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Gathers live RAM, CPU, thread, and process telemetry.
        """
        metrics: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": int(time.time() - self._start_time),
            "python_gc_counts": gc.get_count(),
            "low_power_mode_active_sessions": len(self._low_power_clients),
        }

        if HAS_PSUTIL:
            try:
                proc = psutil.Process(os.getpid())
                mem_info = proc.memory_info()
                vmem = psutil.virtual_memory()

                metrics.update({
                    "process_rss_mb": round(mem_info.rss / (1024 * 1024), 2),
                    "process_vms_mb": round(mem_info.vms / (1024 * 1024), 2),
                    "process_cpu_percent": proc.cpu_percent(interval=None),
                    "process_threads": proc.num_threads(),
                    "host_ram_total_mb": round(vmem.total / (1024 * 1024), 2),
                    "host_ram_available_mb": round(vmem.available / (1024 * 1024), 2),
                    "host_ram_used_percent": vmem.percent,
                    "host_cpu_percent": psutil.cpu_percent(interval=None),
                    "host_cpu_count": psutil.cpu_count(logical=True),
                })
            except Exception as e:
                logger.warning(f"Error gathering psutil metrics: {e}")

        return metrics

    def trigger_memory_cleanup(self, force: bool = False) -> Dict[str, Any]:
        """
        Runs Python garbage collection and frees temporary buffers
        if interval elapsed or forced.
        """
        now = time.time()
        if force or (now - self._last_gc_time > self._gc_interval_seconds):
            unreachable = gc.collect()
            self._last_gc_time = now
            return {
                "ok": True,
                "cleaned": True,
                "unreachable_objects_collected": unreachable,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return {
            "ok": True,
            "cleaned": False,
            "reason": "Interval not yet elapsed; skipped.",
        }

    def register_client_low_power_mode(self, client_id: str, enabled: bool) -> Dict[str, Any]:
        """
        Toggles Low-Power Mode for a specific client session.
        When active, backend sends lean payloads and frontend reduces 3D/canvas effects.
        """
        if enabled:
            self._low_power_clients[client_id] = time.time()
        else:
            self._low_power_clients.pop(client_id, None)

        return {
            "ok": True,
            "client_id": client_id,
            "low_power_mode": enabled,
            "active_low_power_sessions": len(self._low_power_clients),
        }

    def is_client_low_power(self, client_id: Optional[str]) -> bool:
        """Checks if a client has low-power mode active."""
        if not client_id:
            return False
        # Prune expired (> 24 hours inactive)
        now = time.time()
        if client_id in self._low_power_clients:
            if now - self._low_power_clients[client_id] > 86400:
                self._low_power_clients.pop(client_id, None)
                return False
            return True
        return False

    def optimize_payload(self, data: Dict[str, Any], low_power: bool = False) -> Dict[str, Any]:
        """
        Trims verbose optional metadata when low_power mode is requested,
        conserving network bandwidth and device memory.
        """
        if not low_power:
            return data

        lean = dict(data)
        # Omit heavy debug/trace payloads if present
        for key in ("full_trace", "debug_info", "unpruned_context", "raw_embeddings"):
            lean.pop(key, None)
        return lean


# Global singleton
resource_optimizer_service = ResourceOptimizerService()
