"""
self_improver.py — Jarvis Self-Improvement Module
Allows Jarvis to analyze, optimize, and extend its own codebase.
Uses Gemini (primary) with full safety controls and backups.
"""

import os
import sys
import json
import shutil
import hashlib
import datetime
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
BACKUP_DIR      = BASE_DIR / "backups" / "self_improver"
LOG_PATH        = BASE_DIR / "logs" / "self_improver.log"
ACTIONS_DIR     = BASE_DIR / "actions"
AGENT_DIR       = BASE_DIR / "agent"

SAFE_FILES = {
    "actions": [f.name for f in ACTIONS_DIR.glob("*.py")] if ACTIONS_DIR.exists() else [],
    "agent":   ["planner.py", "executor.py", "error_handler.py"],
}

FORBIDDEN_FILES = {"main.py", "config", "__init__.py"}


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _log(message: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[SelfImprover] {message}")


def _backup_file(file_path: Path) -> Path:
    """Creates a timestamped backup before any modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    _log(f"Backup created: {backup_path.name}")
    return backup_path


def _checksum(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def _resolve_file(filename: str) -> Path | None:
    """Safely resolves a filename to an absolute path within the project."""
    candidates = [
        ACTIONS_DIR / filename,
        AGENT_DIR   / filename,
        BASE_DIR    / filename,
    ]
    for path in candidates:
        if path.exists() and path.name not in FORBIDDEN_FILES:
            return path
    return None


# ── Core AI Calls ─────────────────────────────────────────────────────────────

def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    import google.generativeai as genai
    from app.config import settings
    genai.configure(api_key=_get_api_key())
    target_model = getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash") or "gemini-3.8-flash"
    model = genai.GenerativeModel(
        model_name=target_model,
        system_instruction=system_prompt,
    )
    response = model.generate_content(user_prompt)
    return response.text.strip()


# ── Actions ───────────────────────────────────────────────────────────────────

def _optimize_file(filename: str, speak=None) -> str:
    """Analyzes a file and rewrites it with improvements."""
    file_path = _resolve_file(filename)
    if not file_path:
        return f"File '{filename}' not found or is protected."

    if speak:
        speak(f"Analyzing {filename} for optimization, sir.")

    original_code = file_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are an expert Python engineer specialized in clean, efficient code. "
        "Your job is to optimize existing Python code. "
        "Rules:\n"
        "- Keep ALL existing functionality intact\n"
        "- Improve readability, performance, and error handling\n"
        "- Add or improve docstrings and comments\n"
        "- Remove redundant code\n"
        "- Do NOT change function signatures or public APIs\n"
        "- Return ONLY the complete optimized Python code, no explanation, no markdown"
    )

    user_prompt = (
        f"Optimize this Python file ({filename}):\n\n"
        f"```python\n{original_code}\n```"
    )

    _log(f"Requesting optimization for: {filename}")
    optimized_code = _call_gemini(system_prompt, user_prompt)
    optimized_code = optimized_code.replace("```python", "").replace("```", "").strip()

    if _checksum(original_code) == _checksum(optimized_code):
        return f"{filename} is already optimal. No changes needed."

    backup_path = _backup_file(file_path)
    file_path.write_text(optimized_code, encoding="utf-8")
    _log(f"Optimized: {filename} (backup: {backup_path.name})")

    return f"Successfully optimized {filename}. Backup saved as {backup_path.name}."


def _add_feature(filename: str, feature_description: str, speak=None) -> str:
    """Adds a new feature to an existing action file."""
    file_path = _resolve_file(filename)
    if not file_path:
        return f"File '{filename}' not found or is protected."

    if speak:
        speak(f"Adding new feature to {filename}, sir.")

    original_code = file_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are an expert Python engineer. "
        "Your job is to add new functionality to existing Python code. "
        "Rules:\n"
        "- Keep ALL existing code intact\n"
        "- Add the new feature cleanly, following the existing code style\n"
        "- Add proper error handling and docstrings to new code\n"
        "- Do NOT break existing functions\n"
        "- Return ONLY the complete updated Python code, no explanation, no markdown"
    )

    user_prompt = (
        f"Add this feature to the file ({filename}):\n"
        f"Feature: {feature_description}\n\n"
        f"Existing code:\n```python\n{original_code}\n```"
    )

    _log(f"Adding feature to {filename}: {feature_description[:80]}")
    updated_code = _call_gemini(system_prompt, user_prompt)
    updated_code = updated_code.replace("```python", "").replace("```", "").strip()

    backup_path = _backup_file(file_path)
    file_path.write_text(updated_code, encoding="utf-8")
    _log(f"Feature added to {filename} (backup: {backup_path.name})")

    return f"Feature added to {filename} successfully. Backup saved as {backup_path.name}."


def _create_new_action(action_name: str, description: str, speak=None) -> str:
    """Creates a brand new action file from a description."""
    safe_name = action_name.lower().replace(" ", "_").replace("-", "_")
    if not safe_name.endswith(".py"):
        safe_name += ".py"

    output_path = ACTIONS_DIR / safe_name

    if output_path.exists():
        return f"Action '{safe_name}' already exists. Use 'add_feature' to modify it."

    if speak:
        speak(f"Creating new action: {safe_name}, sir.")

    # Read an existing action as style reference
    reference_code = ""
    ref_file = ACTIONS_DIR / "weather_report.py"
    if ref_file.exists():
        reference_code = ref_file.read_text(encoding="utf-8")

    system_prompt = (
        "You are an expert Python engineer building a modular AI assistant action. "
        "Rules:\n"
        "- Create a single clean Python file\n"
        "- The main function must accept (parameters: dict, player=None, speak=None) as arguments\n"
        "- Add full error handling\n"
        "- Add docstrings\n"
        "- Follow the style of the reference code provided\n"
        "- Return ONLY the complete Python code, no explanation, no markdown"
    )

    user_prompt = (
        f"Create a new action file named '{safe_name}' that does the following:\n"
        f"{description}\n\n"
        f"Follow the style of this existing action:\n```python\n{reference_code}\n```"
    )

    _log(f"Creating new action: {safe_name}")
    new_code = _call_gemini(system_prompt, user_prompt)
    new_code = new_code.replace("```python", "").replace("```", "").strip()

    output_path.write_text(new_code, encoding="utf-8")
    _log(f"New action created: {safe_name}")

    return (
        f"New action '{safe_name}' created successfully.\n"
        f"Remember to register it in agent/executor.py and agent/planner.py, sir."
    )


def _analyze_codebase(speak=None) -> str:
    """Analyzes the full codebase and returns improvement suggestions."""
    if speak:
        speak("Analyzing the codebase for improvements, sir.")

    action_files = list(ACTIONS_DIR.glob("*.py"))
    summaries = []

    for f in action_files[:8]:  # Limit to avoid token overload
        try:
            code = f.read_text(encoding="utf-8")
            summaries.append(f"### {f.name}\n{code[:600]}")
        except Exception:
            pass

    combined = "\n\n".join(summaries)

    system_prompt = (
        "You are a senior Python code reviewer. "
        "Analyze the provided code files and return a concise improvement report. "
        "Focus on: performance issues, missing error handling, code duplication, "
        "and potential new features that would make the assistant more powerful."
    )

    user_prompt = (
        f"Analyze these action files from a personal AI assistant:\n\n{combined}\n\n"
        "Provide a numbered list of the top 5 improvements or new features recommended."
    )

    _log("Codebase analysis requested")
    analysis = _call_gemini(system_prompt, user_prompt)
    return analysis


def _restore_backup(filename: str, speak=None) -> str:
    """Restores the most recent backup of a file."""
    stem = Path(filename).stem
    backups = sorted(BACKUP_DIR.glob(f"{stem}_*.py"), reverse=True)

    if not backups:
        return f"No backup found for '{filename}'."

    latest = backups[0]
    target = _resolve_file(filename)

    if not target:
        # Try to reconstruct path
        target = ACTIONS_DIR / filename if not filename.endswith(".py") else ACTIONS_DIR / filename

    shutil.copy2(latest, target)
    _log(f"Restored {filename} from backup: {latest.name}")

    if speak:
        speak(f"Restored {filename} from backup, sir.")

    return f"Restored '{filename}' from backup '{latest.name}'."


# ── Entry Point ───────────────────────────────────────────────────────────────

def self_improver(parameters: dict, player=None, speak=None) -> str:
    """
    Main entry point for the self-improvement module.

    Parameters:
        action       : "optimize" | "add_feature" | "create_action" | "analyze" | "restore"
        filename     : target file (for optimize / add_feature / restore)
        description  : feature or action description (for add_feature / create_action)
        action_name  : name of new action file (for create_action)
    """
    action      = parameters.get("action", "analyze").lower()
    filename    = parameters.get("filename", "")
    description = parameters.get("description", "")
    action_name = parameters.get("action_name", "")

    try:
        if action == "optimize":
            if not filename:
                return "Please provide a 'filename' to optimize."
            return _optimize_file(filename, speak=speak)

        elif action == "add_feature":
            if not filename or not description:
                return "Please provide 'filename' and 'description' for the new feature."
            return _add_feature(filename, description, speak=speak)

        elif action == "create_action":
            name = action_name or description.split()[0]
            if not description:
                return "Please provide a 'description' for the new action."
            return _create_new_action(name, description, speak=speak)

        elif action == "analyze":
            return _analyze_codebase(speak=speak)

        elif action == "restore":
            if not filename:
                return "Please provide a 'filename' to restore."
            return _restore_backup(filename, speak=speak)

        else:
            return f"Unknown action '{action}'. Use: optimize, add_feature, create_action, analyze, restore."

    except Exception as e:
        _log(f"ERROR in action '{action}': {e}")
        return f"Self-improvement failed: {e}"
