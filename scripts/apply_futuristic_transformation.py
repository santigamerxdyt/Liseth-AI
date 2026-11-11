# -*- coding: utf-8 -*-
"""
Master Transformation Script for Liseth AI / JARVIS Futuristic AI Core Interface.
Implements:
1. AI FUTURISTIC DESIGN SYSTEM (Deep space palette #05070B, #00E5FF, #00F5D4, #278BFF, #8B5CF6).
2. AI CORE ORB (Interactive Three.js WebGL 3D particle sphere with neural network synapses,
   concentric gimbal rings, pulsating plasma core, and 7 reactive AI states).
3. THREE-PANEL HUD OS (Left collapsible navigation sidebar, Top HUD command bar,
   Adaptive Hero/Compact Orb stage, Futuristic glass chat stream, Right contextual inspector).
4. AI AGENT HUB (Futuristic showcase of 7 specialized AI agents with capability badges).
5. 100% byte-identical synchronization for index.html, jarvis.html, and app/static/index.html.
"""
import os
import re
import shutil
import hashlib

def main():
    print("Reading index.html...")
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # =========================================================================
    # 1. INJECT AI FUTURISTIC DESIGN SYSTEM CSS
    # =========================================================================
    futuristic_css = '''
    /* =========================================================================
       AI FUTURISTIC DESIGN SYSTEM — JARVIS AI CORE OS (OFFICIAL PALETTE & HUD)
       ========================================================================= */
    :root {
      --bg-void: #05070b;
      --bg-tech: #080d14;
      --bg-darkblue: #0b1220;
      --bg-graphite: #101a29;
      --neon-cyan: #00e5ff;
      --neon-cyan-glow: rgba(0, 229, 255, 0.45);
      --neon-turquoise: #00f5d4;
      --neon-turquoise-glow: rgba(0, 245, 212, 0.4);
      --neon-blue: #278bff;
      --neon-blue-glow: rgba(39, 139, 255, 0.4);
      --neon-violet: #8b5cf6;
      --neon-violet-glow: rgba(139, 92, 246, 0.4);
      --tech-white: #eaf4ff;
      --tech-slate: #8b9bad;
      --tech-muted: #5a6e85;
      --status-green: #38ef7d;
      --status-yellow: #ffd166;
      --status-red: #ff5c77;
      --font-hud: 'Orbitron', 'Cinzel', sans-serif;
      --font-tech: 'Rajdhani', sans-serif;
      --font-body: 'Plus Jakarta Sans', system-ui, sans-serif;
      --font-code: 'JetBrains Mono', monospace;
    }

    /* Ambient Tech Grid Overlay */
    .ambient-tech-grid {
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image: 
        linear-gradient(to right, rgba(0, 229, 255, 0.035) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 229, 255, 0.035) 1px, transparent 1px);
      background-size: 32px 32px;
      z-index: 1;
      opacity: 0.85;
    }

    .ambient-vignette {
      position: fixed;
      inset: 0;
      pointer-events: none;
      background: radial-gradient(circle at 50% 35%, transparent 30%, rgba(5, 7, 11, 0.85) 90%);
      z-index: 2;
    }

    /* Holographic Corner Brackets */
    .hud-bracket {
      position: absolute;
      width: 14px;
      height: 14px;
      pointer-events: none;
      border-color: var(--neon-cyan);
      opacity: 0.75;
      transition: all 0.25s ease;
    }
    .hud-bracket-tl { top: -1px; left: -1px; border-top: 2px solid var(--neon-cyan); border-left: 2px solid var(--neon-cyan); }
    .hud-bracket-tr { top: -1px; right: -1px; border-top: 2px solid var(--neon-cyan); border-right: 2px solid var(--neon-cyan); }
    .hud-bracket-bl { bottom: -1px; left: -1px; border-bottom: 2px solid var(--neon-cyan); border-left: 2px solid var(--neon-cyan); }
    .hud-bracket-br { bottom: -1px; right: -1px; border-bottom: 2px solid var(--neon-cyan); border-right: 2px solid var(--neon-cyan); }

    /* Layout Tri-Panel Container */
    .hud-app-layout {
      display: flex;
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      overflow: hidden;
      position: relative;
      background: var(--bg-void);
    }

    /* ─── 1. LEFT HUD NAVIGATION SIDEBAR ─── */
    .hud-sidebar {
      width: 275px;
      flex-shrink: 0;
      height: 100%;
      background: rgba(8, 13, 20, 0.94);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border-right: 1px solid rgba(0, 229, 255, 0.22);
      box-shadow: 4px 0 25px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      z-index: 100;
      transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), width 0.35s ease;
      position: relative;
    }

    .hud-sidebar.collapsed {
      transform: translateX(-100%);
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
    }

    @media (min-width: 1024px) {
      .hud-sidebar.collapsed {
        transform: translateX(0);
        width: 68px;
      }
      .hud-sidebar.collapsed .hud-brand-text,
      .hud-sidebar.collapsed .hud-user-info,
      .hud-sidebar.collapsed .hud-new-chat-btn span,
      .hud-sidebar.collapsed .hud-nav-label,
      .hud-sidebar.collapsed .hud-nav-badge,
      .hud-sidebar.collapsed .hud-nav-group-title,
      .hud-sidebar.collapsed .hud-sidebar-footer {
        display: none !important;
      }
      .hud-sidebar.collapsed .hud-nav-item {
        justify-content: center;
        padding: 10px 0;
      }
      .hud-sidebar.collapsed .hud-user-card {
        padding: 8px 0;
        justify-content: center;
      }
      .hud-sidebar.collapsed .hud-sidebar-brand {
        justify-content: center;
        padding: 14px 0;
      }
    }

    .hud-sidebar-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      z-index: 99;
    }
    .hud-sidebar-backdrop.active {
      display: block;
    }

    .hud-sidebar-brand {
      padding: 14px 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid rgba(0, 229, 255, 0.16);
      position: relative;
    }

    .hud-brand-orb-icon {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: radial-gradient(circle, #00f5d4 0%, #00e5ff 40%, rgba(39, 139, 255, 0.2) 80%);
      box-shadow: 0 0 16px var(--neon-cyan);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .hud-orb-mini-core {
      width: 10px;
      height: 10px;
      background: #ffffff;
      border-radius: 50%;
      box-shadow: 0 0 8px #ffffff;
      animation: miniCorePulse 2s infinite ease-in-out;
    }

    @keyframes miniCorePulse {
      0%, 100% { transform: scale(1.0); opacity: 0.9; }
      50% { transform: scale(1.3); opacity: 1; }
    }

    .hud-brand-text {
      flex: 1;
      overflow: hidden;
    }

    .hud-brand-name {
      font-family: var(--font-hud);
      font-size: 0.92rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      color: #ffffff;
      text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .hud-brand-version {
      font-size: 0.62rem;
      color: var(--neon-cyan);
      background: rgba(0, 229, 255, 0.12);
      border: 1px solid rgba(0, 229, 255, 0.35);
      padding: 1px 5px;
      border-radius: 4px;
      font-family: var(--font-code);
    }

    .hud-brand-sub {
      font-size: 0.65rem;
      font-family: var(--font-tech);
      letter-spacing: 0.12em;
      color: var(--tech-slate);
      text-transform: uppercase;
    }

    .hud-sidebar-close-btn {
      background: none;
      border: none;
      color: var(--tech-slate);
      font-size: 1.1rem;
      cursor: pointer;
      padding: 4px;
      display: none;
    }
    @media (max-width: 1023px) {
      .hud-sidebar-close-btn { display: block; }
    }

    /* Creator Profile Card in Sidebar */
    .hud-user-card {
      margin: 10px 14px;
      padding: 10px 12px;
      background: rgba(11, 18, 32, 0.7);
      border: 1px solid rgba(0, 229, 255, 0.25);
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      transition: all 0.25s ease;
      position: relative;
    }
    .hud-user-card:hover {
      border-color: var(--neon-cyan);
      box-shadow: 0 0 15px rgba(0, 229, 255, 0.25);
      background: rgba(16, 26, 41, 0.85);
    }
    .hud-user-avatar {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: linear-gradient(135deg, #a855f7, #ec4899);
      color: #ffffff;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      box-shadow: 0 0 10px rgba(168, 85, 247, 0.4);
      flex-shrink: 0;
    }
    .hud-user-info {
      flex: 1;
      overflow: hidden;
    }
    .hud-user-name {
      font-size: 0.76rem;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .hud-user-role {
      font-size: 0.65rem;
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 2px;
    }
    .hud-role-pill {
      background: rgba(245, 158, 11, 0.2);
      color: #ffd166;
      border: 1px solid rgba(245, 158, 11, 0.4);
      border-radius: 3px;
      padding: 0 4px;
      font-weight: 800;
      font-size: 0.6rem;
    }
    .hud-breb-key {
      color: var(--neon-cyan);
      font-family: var(--font-code);
      font-size: 0.62rem;
    }

    /* New Chat Button */
    .hud-new-chat-btn {
      margin: 4px 14px 12px;
      padding: 9px 14px;
      background: linear-gradient(135deg, rgba(0, 229, 255, 0.18), rgba(39, 139, 255, 0.22));
      border: 1px solid var(--neon-cyan);
      border-radius: 8px;
      color: #ffffff;
      font-family: var(--font-hud);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 0 14px rgba(0, 229, 255, 0.25);
      transition: all 0.25s ease;
    }
    .hud-new-chat-btn:hover {
      background: linear-gradient(135deg, rgba(0, 229, 255, 0.35), rgba(39, 139, 255, 0.4));
      box-shadow: 0 0 22px rgba(0, 229, 255, 0.5);
      transform: translateY(-1px);
    }
    .hud-btn-plus {
      font-size: 1.1rem;
      color: var(--neon-turquoise);
      line-height: 1;
    }

    /* Navigation Menu */
    .hud-nav-menu {
      flex: 1;
      overflow-y: auto;
      padding: 0 10px;
      scrollbar-width: thin;
      scrollbar-color: rgba(0, 229, 255, 0.3) transparent;
    }
    .hud-nav-group-title {
      font-size: 0.62rem;
      font-family: var(--font-tech);
      font-weight: 700;
      letter-spacing: 0.14em;
      color: var(--tech-muted);
      padding: 10px 8px 4px;
      text-transform: uppercase;
    }
    .hud-nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      color: var(--tech-slate);
      text-decoration: none;
      border-radius: 6px;
      font-size: 0.76rem;
      font-weight: 500;
      margin-bottom: 2px;
      transition: all 0.2s ease;
      position: relative;
    }
    .hud-nav-item:hover {
      color: var(--neon-cyan);
      background: rgba(0, 229, 255, 0.08);
      border-left: 2px solid var(--neon-cyan);
    }
    .hud-nav-item.active {
      color: #ffffff;
      background: rgba(0, 229, 255, 0.14);
      border-left: 2px solid var(--neon-cyan);
      font-weight: 700;
    }
    .hud-nav-icon {
      font-size: 0.95rem;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 20px;
    }
    .hud-nav-label {
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .hud-nav-badge {
      font-size: 0.6rem;
      padding: 1px 6px;
      border-radius: 10px;
      font-family: var(--font-code);
      font-weight: 700;
      background: rgba(0, 229, 255, 0.15);
      color: var(--neon-cyan);
    }

    /* Sidebar Footer Telemetry */
    .hud-sidebar-footer {
      padding: 10px 14px;
      border-top: 1px solid rgba(0, 229, 255, 0.16);
      background: rgba(5, 7, 11, 0.6);
    }
    .hud-telemetry-pill {
      display: flex;
      justify-content: space-between;
      font-size: 0.65rem;
      font-family: var(--font-code);
      color: var(--tech-slate);
      margin-bottom: 6px;
    }
    .hud-low-power-label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.68rem;
      color: var(--tech-slate);
      cursor: pointer;
    }

    /* ─── 2. CENTRAL INTERACTION AREA ─── */
    .hud-center-stage {
      flex: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
      background: radial-gradient(circle at 50% 15%, rgba(11, 18, 32, 0.8) 0%, rgba(5, 7, 11, 0.98) 75%);
    }

    /* Top HUD Header Bar */
    .hud-top-bar {
      height: 52px;
      flex-shrink: 0;
      background: rgba(8, 13, 20, 0.85);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(0, 229, 255, 0.2);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 50;
      gap: 10px;
    }

    .hud-top-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .hud-toggle-btn {
      background: rgba(11, 18, 32, 0.8);
      border: 1px solid rgba(0, 229, 255, 0.3);
      color: var(--neon-cyan);
      border-radius: 6px;
      padding: 6px 10px;
      cursor: pointer;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    .hud-toggle-btn:hover {
      background: rgba(0, 229, 255, 0.2);
      box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    }

    .hud-orb-state-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.7rem;
      font-family: var(--font-tech);
      font-weight: 700;
      letter-spacing: 0.1em;
      color: var(--neon-cyan);
      background: rgba(0, 229, 255, 0.08);
      border: 1px solid rgba(0, 229, 255, 0.3);
      padding: 4px 10px;
      border-radius: 20px;
      text-transform: uppercase;
    }

    .hud-state-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--neon-cyan);
      box-shadow: 0 0 8px var(--neon-cyan);
      animation: stateDotPulse 1.6s infinite ease-in-out;
    }

    @keyframes stateDotPulse {
      0%, 100% { transform: scale(1); opacity: 0.8; }
      50% { transform: scale(1.4); opacity: 1; }
    }

    .hud-top-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .hud-model-select {
      background: rgba(11, 18, 32, 0.9);
      border: 1px solid rgba(0, 229, 255, 0.35);
      color: #ffffff;
      font-size: 0.72rem;
      font-family: var(--font-body);
      font-weight: 600;
      padding: 5px 8px;
      border-radius: 6px;
      cursor: pointer;
      outline: none;
    }

    /* ─── 3. AI CORE ORB HERO & ADAPTIVE STAGE ─── */
    .ai-core-orb-stage {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 16px 20px 8px;
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      z-index: 10;
    }

    .ai-core-orb-stage.compact {
      padding: 6px 16px;
      flex-direction: row;
      justify-content: space-between;
      border-bottom: 1px solid rgba(0, 229, 255, 0.15);
      background: rgba(8, 13, 20, 0.45);
    }

    .ai-core-orb-stage.compact .orb-hero-extras {
      display: none !important;
    }

    .ai-core-orb-wrapper {
      position: relative;
      width: 250px;
      height: 250px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: width 0.4s ease, height 0.4s ease;
    }

    .ai-core-orb-stage.compact .ai-core-orb-wrapper {
      width: 76px;
      height: 76px;
    }

    .ai-core-orb-canvas {
      width: 100%;
      height: 100%;
      display: block;
      border-radius: 50%;
    }

    /* Volumetric Aura Backdrop behind Orb */
    .ai-core-orb-aura {
      position: absolute;
      inset: -15%;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0, 245, 212, 0.28) 0%, rgba(0, 229, 255, 0.14) 45%, transparent 70%);
      pointer-events: none;
      filter: blur(18px);
      animation: orbAuraBreathe 4s infinite alternate ease-in-out;
      transition: all 0.4s ease;
    }

    @keyframes orbAuraBreathe {
      0% { transform: scale(0.92); opacity: 0.6; }
      100% { transform: scale(1.08); opacity: 0.95; }
    }

    .ai-core-orb-stage.compact .ai-core-orb-aura {
      filter: blur(8px);
    }

    .orb-dock-toggle-btn {
      background: rgba(0, 229, 255, 0.12);
      border: 1px solid rgba(0, 229, 255, 0.35);
      color: var(--neon-cyan);
      font-size: 0.68rem;
      font-family: var(--font-tech);
      font-weight: 700;
      letter-spacing: 0.08em;
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      margin-top: 6px;
      transition: all 0.2s ease;
    }
    .orb-dock-toggle-btn:hover {
      background: rgba(0, 229, 255, 0.24);
      box-shadow: 0 0 12px rgba(0, 229, 255, 0.4);
    }

    .ai-core-title {
      font-family: var(--font-hud);
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      color: #ffffff;
      text-shadow: 0 0 15px rgba(0, 229, 255, 0.6);
      margin-top: 8px;
    }

    .ai-core-status-text {
      font-size: 0.74rem;
      color: var(--tech-slate);
      font-family: var(--font-tech);
      letter-spacing: 0.06em;
      margin-top: 2px;
      text-align: center;
    }

    /* ─── 4. UNIFIED CONVERSATION STREAM ─── */
    .hud-chat-scroll-area {
      flex: 1;
      overflow-y: auto;
      padding: 16px 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scrollbar-width: thin;
      scrollbar-color: rgba(0, 229, 255, 0.35) transparent;
      z-index: 5;
    }

    /* Message Rows & Bubbles */
    .message-row {
      display: flex;
      gap: 12px;
      max-width: 88%;
      animation: msgFuturisticIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    @keyframes msgFuturisticIn {
      from { opacity: 0; transform: translateY(12px) scale(0.98); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .message-row.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }

    .message-row.assistant {
      align-self: flex-start;
    }

    .message-row .avatar {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.85rem;
      flex-shrink: 0;
      position: relative;
    }

    .message-row.assistant .avatar {
      background: radial-gradient(circle, #00f5d4, #00e5ff);
      color: #04070d;
      box-shadow: 0 0 15px rgba(0, 229, 255, 0.6);
      border: 1px solid #ffffff;
    }

    .message-row.user .avatar {
      background: linear-gradient(135deg, #278bff, #8b5cf6);
      color: #ffffff;
      box-shadow: 0 0 12px rgba(39, 139, 255, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.4);
    }

    .bubble {
      background: rgba(11, 18, 32, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-radius: 10px;
      padding: 12px 16px;
      color: var(--tech-white);
      font-size: 0.82rem;
      line-height: 1.6;
      border: 1px solid rgba(0, 229, 255, 0.25);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      position: relative;
    }

    .message-row.user .bubble {
      background: linear-gradient(135deg, rgba(16, 26, 41, 0.95), rgba(39, 139, 255, 0.2));
      border-color: rgba(39, 139, 255, 0.5);
      box-shadow: 0 4px 20px rgba(39, 139, 255, 0.15);
      border-bottom-right-radius: 2px;
    }

    .message-row.assistant .bubble {
      background: linear-gradient(135deg, rgba(8, 13, 20, 0.95), rgba(0, 229, 255, 0.08));
      border-color: rgba(0, 229, 255, 0.35);
      box-shadow: 0 4px 25px rgba(0, 229, 255, 0.12);
      border-bottom-left-radius: 2px;
    }

    .bubble-sender {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      font-family: var(--font-tech);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--neon-cyan);
      text-transform: uppercase;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      padding-bottom: 4px;
    }

    .bubble-tag {
      font-size: 0.58rem;
      background: rgba(0, 229, 255, 0.15);
      color: var(--neon-cyan);
      border: 1px solid rgba(0, 229, 255, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      font-family: var(--font-code);
      font-weight: 700;
      letter-spacing: 0.05em;
    }

    .bubble-content pre {
      background: rgba(4, 7, 13, 0.95);
      border: 1px solid rgba(0, 229, 255, 0.3);
      border-radius: 6px;
      padding: 12px;
      margin: 8px 0;
      overflow-x: auto;
      font-family: var(--font-code);
      font-size: 0.74rem;
      color: #e2e8f0;
    }

    .bubble-content code {
      font-family: var(--font-code);
      color: var(--neon-turquoise);
      background: rgba(0, 245, 212, 0.1);
      padding: 2px 5px;
      border-radius: 4px;
      font-size: 0.78rem;
    }

    /* ─── 5. FUTURISTIC COMMAND BAR (INPUT DOCK) ─── */
    .hud-command-dock {
      padding: 10px 20px 14px;
      background: rgba(8, 13, 20, 0.92);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-top: 1px solid rgba(0, 229, 255, 0.25);
      position: relative;
      z-index: 50;
    }

    .hud-input-box {
      background: rgba(11, 18, 32, 0.85);
      border: 1.5px solid rgba(0, 229, 255, 0.4);
      border-radius: 12px;
      padding: 6px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
      transition: all 0.25s ease;
    }
    .hud-input-box:focus-within {
      border-color: var(--neon-cyan);
      box-shadow: 0 0 28px rgba(0, 229, 255, 0.35);
      background: rgba(16, 26, 41, 0.95);
    }

    .hud-input-textarea {
      flex: 1;
      background: none;
      border: none;
      outline: none;
      color: #ffffff;
      font-family: var(--font-body);
      font-size: 0.84rem;
      resize: none;
      max-height: 120px;
      line-height: 1.45;
    }
    .hud-input-textarea::placeholder {
      color: var(--tech-muted);
    }

    .hud-send-btn {
      background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
      border: none;
      border-radius: 8px;
      color: #04070d;
      font-weight: 900;
      padding: 8px 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      font-family: var(--font-hud);
      font-size: 0.74rem;
      letter-spacing: 0.08em;
      box-shadow: 0 0 16px rgba(0, 229, 255, 0.4);
      transition: all 0.2s ease;
    }
    .hud-send-btn:hover {
      box-shadow: 0 0 24px rgba(0, 229, 255, 0.7);
      transform: scale(1.02);
    }

    /* ─── 6. RIGHT CONTEXTUAL HUD INSPECTOR DRAWER ─── */
    .hud-inspector {
      width: 310px;
      flex-shrink: 0;
      height: 100%;
      background: rgba(8, 13, 20, 0.94);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border-left: 1px solid rgba(0, 229, 255, 0.22);
      box-shadow: -4px 0 25px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      z-index: 90;
      transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hud-inspector.collapsed {
      display: none;
    }

    .hud-inspector-header {
      padding: 14px 16px;
      border-bottom: 1px solid rgba(0, 229, 255, 0.16);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .hud-inspector-title {
      font-family: var(--font-hud);
      font-size: 0.82rem;
      font-weight: 800;
      color: var(--neon-cyan);
      letter-spacing: 0.08em;
    }
    .hud-inspector-body {
      flex: 1;
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .hud-inspector-card {
      background: rgba(11, 18, 32, 0.75);
      border: 1px solid rgba(0, 229, 255, 0.2);
      border-radius: 8px;
      padding: 12px;
      font-size: 0.74rem;
    }
    .hud-inspector-card-title {
      font-family: var(--font-tech);
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      color: var(--neon-cyan);
      margin-bottom: 6px;
      text-transform: uppercase;
    }

    /* ─── 7. AI AGENT HUB MODAL & CARDS ─── */
    .agent-hub-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
      max-height: 480px;
      overflow-y: auto;
      padding: 6px 2px;
    }
    .agent-card {
      background: rgba(11, 18, 32, 0.85);
      border: 1px solid rgba(0, 229, 255, 0.3);
      border-radius: 10px;
      padding: 14px;
      transition: all 0.25s ease;
      position: relative;
      cursor: pointer;
    }
    .agent-card:hover {
      border-color: var(--neon-cyan);
      box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
      transform: translateY(-2px);
      background: rgba(16, 26, 41, 0.95);
    }
    .agent-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .agent-card-name {
      font-weight: 800;
      font-size: 0.86rem;
      color: #ffffff;
      font-family: var(--font-hud);
    }
    .agent-card-desc {
      font-size: 0.72rem;
      color: var(--tech-slate);
      line-height: 1.45;
      margin-bottom: 10px;
    }
    .agent-chips-row {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-bottom: 12px;
    }
    .agent-chip {
      background: rgba(0, 229, 255, 0.1);
      border: 1px solid rgba(0, 229, 255, 0.25);
      color: var(--neon-cyan);
      font-size: 0.62rem;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: var(--font-code);
    }
    '''

    # Inject futuristic CSS into <style> right after :root or at the start of <style>
    if "/* =========================================================================\n       AI FUTURISTIC DESIGN SYSTEM" not in html:
        style_open = "<style>"
        if style_open in html:
            html = html.replace(style_open, style_open + "\n" + futuristic_css, 1)
            print("✔ AI Futuristic Design System CSS injected.")

    # =========================================================================
    # 2. INJECT AI CORE ORB CANVAS & TOP HUD BAR INTO MAIN BODY
    # =========================================================================
    # Check if AI Core Orb markup is already injected
    if 'id="ai-core-orb-stage"' not in html:
        # We will wrap the existing main interface into our cohesive HUD Tri-Panel layout
        hud_top_bar_html = '''
  <!-- TOP HUD COMMAND & TELEMETRY BAR -->
  <div class="hud-top-bar" id="hud-top-bar">
    <div class="hud-top-left">
      <button type="button" class="hud-toggle-btn" id="btn-hud-sidebar-toggle" onclick="toggleHudSidebar()" title="Alternar panel de navegación (Alt+S)">
        <span>☰</span>
      </button>
      <div class="hud-orb-state-indicator" id="hud-orb-state-indicator">
        <span class="hud-state-dot"></span>
        <span id="hud-orb-state-text">IDLE // EN REPOSO</span>
      </div>
      <div class="server-badge" id="server-badge" style="padding:4px 8px;font-size:0.68rem;" title="Estado del servidor">
        <span class="badge-dot"></span>
        <span id="server-status-text">SYS.JARVIS // NOMINAL</span>
      </div>
    </div>

    <div class="hud-top-right">
      <select class="hud-model-select" id="hud-model-select" onchange="switchModelProfileUI(this.value)" title="Modelo de IA Inteligente">
        <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash-Lite (Rápido)</option>
        <option value="gemini-2.5-flash" selected>Gemini 2.5 Flash (Equilibrado)</option>
        <option value="gemini-2.5-pro">Gemini 2.5 Pro (Razonamiento / Código)</option>
      </select>

      <button class="hud-toggle-btn" id="btn-quick-agenthub" onclick="openAgentHubModal()" title="AI Agent Hub (Cerebros y Agentes)">
        <span>🤖</span>
      </button>
      <button class="hud-toggle-btn" id="btn-quick-hudmodules" onclick="openHudModulesModal()" title="48 Módulos HUD">
        <span>◈</span>
      </button>
      <button class="hud-toggle-btn" id="btn-quick-nfc" onclick="openNfcModal()" title="Terminal NFC & Pagos">
        <span>📶</span>
      </button>
      <button class="hud-toggle-btn" id="btn-quick-saas" onclick="openSaasModal()" title="Plataforma SaaS & Panel Creator">
        <span>💎</span>
      </button>
      <button class="hud-toggle-btn" id="btn-toggle-inspector" onclick="toggleHudInspector()" title="Inspector Contextual (Alt+I)">
        <span>⚡</span>
      </button>
      <button class="hud-toggle-btn" id="btn-session-lock-top" onclick="triggerSessionLockUI()" title="Bloquear Sesión (PIN)">
        <span>🔒</span>
      </button>
    </div>
  </div>
'''

        # The new AI CORE ORB STAGE
        ai_core_orb_stage_html = '''
    <!-- AI CORE ORB HERO & ADAPTIVE STAGE -->
    <div class="ai-core-orb-stage" id="ai-core-orb-stage">
      <div class="ai-core-orb-wrapper" id="ai-core-orb-wrapper" onclick="handleOrbInteraction()" title="AI CORE ORB (Clic para hablar con Liseth o alternar tamaño)">
        <div class="ai-core-orb-aura" id="ai-core-orb-aura"></div>
        <canvas id="ai-core-orb-canvas" width="250" height="250" class="ai-core-orb-canvas"></canvas>
      </div>

      <div class="orb-hero-extras" id="orb-hero-extras" style="display: flex; flex-direction: column; align-items: center;">
        <h1 class="ai-core-title" id="assistant-display-name">LISETH // JARVIS AI CORE</h1>
        <div class="ai-core-status-text" id="status-label">A sus órdenes, Señor Santiago. Red neuronal cuántica en línea.</div>

        <div style="display:flex;gap:6px;margin-top:8px;">
          <button type="button" class="orb-dock-toggle-btn" onclick="toggleOrbDockMode()" title="Alternar tamaño del núcleo visual">
            <span id="orb-dock-icon">↕</span> <span id="orb-dock-label">Acoplar Núcleo</span>
          </button>
          <button type="button" class="orb-dock-toggle-btn" onclick="openAgentHubModal()" style="border-color:#a855f7;color:#c084fc;" title="Ver AI Agent Hub">
            <span>🤖 Agentes IA</span>
          </button>
          <button type="button" class="orb-dock-toggle-btn" onclick="openNfcModal()" style="border-color:#38ef7d;color:#38ef7d;" title="Terminal NFC">
            <span>📶 NFC Pay</span>
          </button>
        </div>
      </div>
    </div>
'''

        # Left Sidebar Navigation HTML
        left_sidebar_html = '''
  <!-- 1. LEFT HUD NAVIGATION SIDEBAR -->
  <aside class="hud-sidebar" id="hud-sidebar-nav" aria-label="Navegación del Sistema">
    <div class="hud-sidebar-brand">
      <div class="hud-brand-orb-icon">
        <span class="hud-orb-mini-core"></span>
      </div>
      <div class="hud-brand-text">
        <div class="hud-brand-name">LISETH <span class="hud-brand-version">OS 3.8</span></div>
        <div class="hud-brand-sub">AI CORE // JARVIS PROTOCOL</div>
      </div>
      <button type="button" class="hud-sidebar-close-btn" onclick="toggleHudSidebar(false)" title="Cerrar panel lateral">✕</button>
    </div>

    <!-- Creator Profile Card (Señor Santiago) -->
    <div class="hud-user-card" onclick="openSaasModal(); switchSaasTab('account');" title="Perfil de Usuario • Señor Santiago">
      <div class="hud-user-avatar">S</div>
      <div class="hud-user-info">
        <div class="hud-user-name">Santiago Huérfano López</div>
        <div class="hud-user-role"><span class="hud-role-pill">CREATOR</span> <span class="hud-breb-key">@NEQUISAN243100</span></div>
      </div>
    </div>

    <!-- Nueva Conversación -->
    <button type="button" class="hud-new-chat-btn" onclick="startNewConversationUI()" title="Iniciar nueva conversación limpia">
      <span class="hud-btn-plus">+</span>
      <span>NUEVA CONVERSACIÓN</span>
    </button>

    <!-- Menú de Navegación -->
    <nav class="hud-nav-menu">
      <div class="hud-nav-group-title">SISTEMA & COMUNICACIÓN</div>
      <a href="javascript:void(0)" class="hud-nav-item active" id="nav-item-chat" onclick="switchMainStageView('chat')">
        <span class="hud-nav-icon">💬</span>
        <span class="hud-nav-label">Consola de Chat</span>
        <span class="hud-nav-badge">ACTIVO</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-workspace" onclick="openSaasModal(); switchSaasTab('workspace');">
        <span class="hud-nav-icon">📁</span>
        <span class="hud-nav-label">Espacios & Conversaciones</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-memory" onclick="openSaasModal(); switchSaasTab('workspace');">
        <span class="hud-nav-icon">🧠</span>
        <span class="hud-nav-label">Cerebro de Memoria</span>
      </a>

      <div class="hud-nav-group-title">INTELIGENCIA & HERRAMIENTAS</div>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-agenthub" onclick="openAgentHubModal()">
        <span class="hud-nav-icon">🤖</span>
        <span class="hud-nav-label">AI Agent Hub</span>
        <span class="hud-nav-badge" style="background:rgba(0,229,255,0.2);color:#00e5ff;">7 AGENTES</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-modules" onclick="openHudModulesModal()">
        <span class="hud-nav-icon">◈</span>
        <span class="hud-nav-label">48 Módulos HUD</span>
        <span class="hud-nav-badge" style="background:rgba(168,85,247,0.2);color:#c084fc;">48</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-nfc" onclick="openNfcModal()">
        <span class="hud-nav-icon">📶</span>
        <span class="hud-nav-label">Terminal NFC & Pagos</span>
        <span class="hud-nav-badge" style="background:rgba(56,239,125,0.2);color:#38ef7d;">NFC</span>
      </a>

      <div class="hud-nav-group-title">SAAS & PROPIEDAD</div>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-plans" onclick="openSaasModal(); switchSaasTab('plans');">
        <span class="hud-nav-icon">💎</span>
        <span class="hud-nav-label">Planes & Bre-B</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-referrals" onclick="openSaasModal(); switchSaasTab('referrals');">
        <span class="hud-nav-icon">🎁</span>
        <span class="hud-nav-label">Referidos & Recompensas</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-legal" onclick="openSaasModal(); switchSaasTab('legal');">
        <span class="hud-nav-icon">⚖️</span>
        <span class="hud-nav-label">Legal & Propiedad</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-creator" onclick="openSaasModal(); switchSaasTab('creator');">
        <span class="hud-nav-icon">👑</span>
        <span class="hud-nav-label">Panel Superadmin CREATOR</span>
        <span class="hud-nav-badge" style="background:linear-gradient(135deg,#f59e0b,#ef4444);color:#fff;">OWNER</span>
      </a>
      <a href="javascript:void(0)" class="hud-nav-item" id="nav-item-aiperf" onclick="openSaasModal(); switchSaasTab('ai-perf');">
        <span class="hud-nav-icon">⚡</span>
        <span class="hud-nav-label">Telemetría IA & RAM</span>
      </a>
    </nav>

    <!-- Footer de Sidebar con Telemetría Rápida -->
    <div class="hud-sidebar-footer">
      <div class="hud-telemetry-pill">
        <span>⚡ LATENCIA: <b style="color:#00e5ff;">12 ms</b></span>
        <span>TOKENS: <b style="color:#38ef7d;">-34%</b></span>
      </div>
      <label class="hud-low-power-label">
        <input type="checkbox" id="sidebar-low-power-toggle" onchange="toggleClientLowPowerModeUI(this)" />
        <span>Modo Bajo Consumo</span>
      </label>
    </div>
  </aside>
  <div class="hud-sidebar-backdrop" id="hud-sidebar-backdrop" onclick="toggleHudSidebar(false)"></div>
'''

        # Right Contextual HUD Inspector HTML
        right_inspector_html = '''
  <!-- 3. RIGHT CONTEXTUAL HUD INSPECTOR DRAWER -->
  <aside class="hud-inspector collapsed" id="hud-context-inspector" aria-label="Inspector Contextual">
    <div class="hud-inspector-header">
      <span class="hud-inspector-title">⚡ CONTEXT INSPECTOR</span>
      <button type="button" class="hud-toggle-btn" onclick="toggleHudInspector(false)" style="padding:2px 6px;">✕</button>
    </div>
    <div class="hud-inspector-body">
      <!-- Active Agent Card -->
      <div class="hud-inspector-card">
        <div class="hud-inspector-card-title">🤖 AGENTE ACTIVO</div>
        <div style="font-weight:800;color:#ffffff;font-size:0.84rem;" id="insp-agent-name">Liseth / JARVIS Core</div>
        <div style="color:var(--tech-slate);font-size:0.68rem;margin-top:2px;" id="insp-agent-role">Coordinación Ejecutiva & Alta Dirección</div>
        <div style="margin-top:6px;display:flex;gap:4px;">
          <span class="bubble-tag" id="insp-agent-model">GEMINI 2.5 FLASH</span>
          <span class="bubble-tag" style="background:rgba(56,239,125,0.15);color:#38ef7d;border-color:#38ef7d;">ONLINE</span>
        </div>
      </div>

      <!-- Active Skills & Tools -->
      <div class="hud-inspector-card">
        <div class="hud-inspector-card-title">🛠️ SKILLS EN EJECUCIÓN</div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;" id="insp-active-skills">
          <span class="agent-chip">workspace-automation</span>
          <span class="agent-chip">business-strategist</span>
          <span class="agent-chip">nfc-core</span>
          <span class="agent-chip">academic-researcher</span>
        </div>
      </div>

      <!-- Token Optimizer KPIs -->
      <div class="hud-inspector-card">
        <div class="hud-inspector-card-title">🧠 TOKEN OPTIMIZER & AHORRO</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;text-align:center;">
          <div style="background:rgba(0,0,0,0.3);padding:6px;border-radius:4px;">
            <div style="font-size:0.6rem;color:var(--tech-slate);">Ahorro Tokens</div>
            <div style="font-size:0.95rem;font-weight:800;color:var(--neon-cyan);">34.2%</div>
          </div>
          <div style="background:rgba(0,0,0,0.3);padding:6px;border-radius:4px;">
            <div style="font-size:0.6rem;color:var(--tech-slate);">Caché Hits</div>
            <div style="font-size:0.95rem;font-weight:800;color:#38ef7d;">100%</div>
          </div>
        </div>
      </div>

      <!-- System Resources -->
      <div class="hud-inspector-card">
        <div class="hud-inspector-card-title">💻 RECURSOS DE HARDWARE</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;color:var(--tech-slate);">
          <span>RAM RSS:</span> <b style="color:#ffffff;" id="insp-ram-val">42.5 MB</b>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;color:var(--tech-slate);">
          <span>CPU Host:</span> <b style="color:#ffd166;" id="insp-cpu-val">2.8%</b>
        </div>
        <div style="display:flex;justify-content:space-between;color:var(--tech-slate);">
          <span>Estado GC:</span> <b style="color:#38ef7d;">Óptimo // Normal</b>
        </div>
      </div>
    </div>
  </aside>
'''

        # AI Agent Hub Modal HTML
        agent_hub_modal_html = '''
  <!-- MODAL: AI AGENT HUB (CATÁLOGO HOLOGRÁFICO DE AGENTES) -->
  <div class="modal-overlay" id="agent-hub-modal" style="display:none;z-index:10006;">
    <div class="modal-window" style="max-width:960px;width:92%;background:rgba(8,13,20,0.96);border:1px solid var(--neon-cyan);box-shadow:0 0 35px rgba(0,229,255,0.35);">
      <div class="hud-bracket hud-bracket-tl"></div>
      <div class="hud-bracket hud-bracket-tr"></div>
      <div class="hud-bracket hud-bracket-bl"></div>
      <div class="hud-bracket hud-bracket-br"></div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid rgba(0,229,255,0.25);padding-bottom:10px;">
        <div>
          <div style="font-family:var(--font-hud);font-size:1.1rem;font-weight:900;color:var(--neon-cyan);letter-spacing:0.08em;">🤖 AI AGENT HUB — SISTEMA MULTIAGENTE</div>
          <div style="font-size:0.72rem;color:var(--tech-slate);">Especialistas cognitivos con herramientas, modelos avanzados y flujos autónomos</div>
        </div>
        <button class="modal-close" onclick="closeAgentHubModal()">&times;</button>
      </div>

      <div class="agent-hub-grid">
        <!-- Agente 1: JARVIS Core Executive -->
        <div class="agent-card" onclick="activateAgentPersona('jarvis_core')">
          <div class="agent-card-header">
            <div class="agent-card-name">💎 Liseth / JARVIS Core</div>
            <span class="bubble-tag" style="background:rgba(0,229,255,0.2);color:#00e5ff;">TODOS LOS PLANES</span>
          </div>
          <div class="agent-card-desc">Asistente ejecutiva de alta dirección, coordinación proactiva, agenda Google, correos y síntesis ejecutiva.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">workspace-automation</span>
            <span class="agent-chip">gcalendar</span>
            <span class="agent-chip">gdrive</span>
            <span class="agent-chip">gemini-2.5-flash</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>

        <!-- Agente 2: Senior Full Stack -->
        <div class="agent-card" onclick="activateAgentPersona('fullstack_dev')">
          <div class="agent-card-header">
            <div class="agent-card-name">💻 Senior Full Stack</div>
            <span class="bubble-tag" style="background:rgba(39,139,255,0.2);color:#38bdf8;">STARTER+</span>
          </div>
          <div class="agent-card-desc">Arquitectura de software, depuración profunda, auditoría de código, Flutter/Dart, Python, FastAPI y Node.js.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">code-auditor</span>
            <span class="agent-chip">fastapi</span>
            <span class="agent-chip">python</span>
            <span class="agent-chip">gemini-2.5-pro</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>

        <!-- Agente 3: Cybersecurity Specialist -->
        <div class="agent-card" onclick="activateAgentPersona('cybersecurity')">
          <div class="agent-card-header">
            <div class="agent-card-name">🛡️ Cybersecurity Auditor</div>
            <span class="bubble-tag" style="background:rgba(239,68,68,0.2);color:#ff5c77;">PRO+</span>
          </div>
          <div class="agent-card-desc">Revisión de vulnerabilidades, reglas de seguridad Firestore, criptografía HMAC-SHA256 y hardening de APIs.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">security-audit</span>
            <span class="agent-chip">owasp-top-10</span>
            <span class="agent-chip">crypto-hmac</span>
            <span class="agent-chip">gemini-2.5-pro</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>

        <!-- Agente 4: Business Strategist -->
        <div class="agent-card" onclick="activateAgentPersona('business_strategist')">
          <div class="agent-card-header">
            <div class="agent-card-name">📊 Business Strategist</div>
            <span class="bubble-tag" style="background:rgba(245,158,11,0.2);color:#ffd166;">PRO+</span>
          </div>
          <div class="agent-card-desc">Modelación financiera pro-forma, flujo de caja, matrices FODA / Cinco Fuerzas, amortizaciones y WACC.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">business-strategist</span>
            <span class="agent-chip">financial-model</span>
            <span class="agent-chip">gemini-2.5-flash</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>

        <!-- Agente 5: Academic Researcher -->
        <div class="agent-card" onclick="activateAgentPersona('academic_researcher')">
          <div class="agent-card-header">
            <div class="agent-card-name">🎓 Academic Researcher</div>
            <span class="bubble-tag" style="background:rgba(168,85,247,0.2);color:#c084fc;">STARTER+</span>
          </div>
          <div class="agent-card-desc">Búsqueda científica en OpenAlex y arXiv, síntesis de papers, extracción de DOIs y citación estricta APA 7ma Ed.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">academic-researcher</span>
            <span class="agent-chip">openalex</span>
            <span class="agent-chip">apa-7th</span>
            <span class="agent-chip">gemini-2.5-flash</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>

        <!-- Agente 6: Data Science & ML -->
        <div class="agent-card" onclick="activateAgentPersona('data_science')">
          <div class="agent-card-header">
            <div class="agent-card-name">🔬 Data Science & ML</div>
            <span class="bubble-tag" style="background:rgba(56,239,125,0.2);color:#38ef7d;">PRO+</span>
          </div>
          <div class="agent-card-desc">Limpieza automática de datasets, EDA, modelado estadístico, regresiones, clustering y pipelines BigQuery.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">data-ml-toolkit</span>
            <span class="agent-chip">pandas</span>
            <span class="agent-chip">scikit-learn</span>
            <span class="agent-chip">gemini-2.5-flash</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>

        <!-- Agente 7: NFC Core Specialist -->
        <div class="agent-card" onclick="activateAgentPersona('nfc_engineer')">
          <div class="agent-card-header">
            <div class="agent-card-name">📶 NFC Core Specialist</div>
            <span class="bubble-tag" style="background:rgba(0,229,255,0.2);color:#00e5ff;">TODOS LOS PLANES</span>
          </div>
          <div class="agent-card-desc">Lectura y escritura NDEF, Smart Business Cards vCard 4.0, enlaces dinámicos y pagos contactless tokenizados.</div>
          <div class="agent-chips-row">
            <span class="agent-chip">nfc-core</span>
            <span class="agent-chip">ndef-validation</span>
            <span class="agent-chip">vcard-generator</span>
            <span class="agent-chip">gemini-3.1-flash-lite</span>
          </div>
          <button type="button" class="btn-primary" style="width:100%;padding:6px;font-size:0.72rem;">Activar Agente ↳</button>
        </div>
      </div>
    </div>
  </div>
'''

        # Insert ambient grid, sidebar, top bar, and right inspector into HTML
        body_target = '<body>'
        body_replacement = f'''<body>
  <div class="ambient-tech-grid"></div>
  <div class="ambient-vignette"></div>
  <div class="hud-app-layout" id="hud-app-layout">
{left_sidebar_html}
    <div class="hud-center-stage" id="hud-center-stage">
{hud_top_bar_html}
{ai_core_orb_stage_html}'''

        if body_target in html:
            html = html.replace(body_target, body_replacement, 1)
            print("✔ HUD App Layout, Sidebar & Top bar injected into <body>.")

        # Close the center stage and app layout before the modals / script
        modal_anchor = '<div class="liseth-toast" id="liseth-toast"></div>'
        if modal_anchor in html:
            closing_divs = f'''    </div><!-- /.hud-center-stage -->
{right_inspector_html}
  </div><!-- /.hud-app-layout -->
{agent_hub_modal_html}
'''
            html = html.replace(modal_anchor, closing_divs + modal_anchor, 1)
            print("✔ Closing divs and Agent Hub Modal injected.")

    # =========================================================================
    # 3. INJECT JAVASCRIPT ENGINE FOR AI CORE ORB & HUD OS
    # =========================================================================
    orb_js = '''
      // =========================================================================
      // MOTOR DE AI CORE ORB (ESFERA DE ENERGÍA DE PARTÍCULAS THREE.JS / WEBGL)
      // =========================================================================
      let aiCoreOrb = {
        isInitialized: false,
        scene: null,
        camera: null,
        renderer: null,
        canvas: null,
        container: null,
        particles: null,
        particlePositions: null,
        particleBasePositions: null,
        particleColors: null,
        particleCount: 1200,
        synapseLines: null,
        synapseGeometry: null,
        synapsePositions: null,
        maxConnections: 1200,
        innerCore: null,
        innerCoreWire: null,
        gimbalRings: [],
        audioRing: null,
        clock: null,
        state: 'idle',
        targetSpeed: 0.5,
        currentSpeed: 0.5,
        targetScale: 1.0,
        currentScale: 1.0,
        targetGlow: 1.0,
        currentGlow: 1.0,
        mouse: { x: 0, y: 0, targetX: 0, targetY: 0 },
        dockMode: 'hero',
        rafId: null
      };

      function initAICoreOrbEngine() {
        if (aiCoreOrb.isInitialized) return;
        const canvas = document.getElementById("ai-core-orb-canvas");
        const container = document.getElementById("ai-core-orb-wrapper");
        if (!canvas || !container || typeof THREE === "undefined") return;

        const w = container.clientWidth || 250;
        const h = container.clientHeight || 250;

        // 1. Scene, Camera, WebGLRenderer
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
        camera.position.set(0, 0, 4.2);

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(w, h);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        // 2. High-Tech Particle Core Texture
        const offCanvas = document.createElement("canvas");
        offCanvas.width = 64;
        offCanvas.height = 64;
        const offCtx = offCanvas.getContext("2d");
        const radGrad = offCtx.createRadialGradient(32, 32, 0, 32, 32, 32);
        radGrad.addColorStop(0, "rgba(255, 255, 255, 1)");
        radGrad.addColorStop(0.25, "rgba(0, 245, 212, 0.95)");
        radGrad.addColorStop(0.55, "rgba(0, 229, 255, 0.55)");
        radGrad.addColorStop(1, "rgba(0, 229, 255, 0)");
        offCtx.fillStyle = radGrad;
        offCtx.fillRect(0, 0, 64, 64);
        const particleTex = new THREE.CanvasTexture(offCanvas);

        // 3. Fibonacci Spherical Harmonic Particles
        const count = aiCoreOrb.particleCount;
        const geo = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const basePositions = new Float32Array(count * 3);
        const colors = new Float32Array(count * 3);

        const cyanColor = new THREE.Color(0x00e5ff);
        const turqColor = new THREE.Color(0x00f5d4);

        for (let i = 0; i < count; i++) {
          const phi = Math.acos(1 - 2 * (i + 0.5) / count);
          const theta = Math.PI * (1 + Math.sqrt(5)) * i;
          const radius = 1.35 + (Math.random() - 0.5) * 0.22;

          const x = radius * Math.sin(phi) * Math.cos(theta);
          const y = radius * Math.sin(phi) * Math.sin(theta);
          const z = radius * Math.cos(phi);

          positions[i * 3] = x;
          positions[i * 3 + 1] = y;
          positions[i * 3 + 2] = z;

          basePositions[i * 3] = x;
          basePositions[i * 3 + 1] = y;
          basePositions[i * 3 + 2] = z;

          const c = (Math.random() > 0.4) ? cyanColor : turqColor;
          colors[i * 3] = c.r;
          colors[i * 3 + 1] = c.g;
          colors[i * 3 + 2] = c.b;
        }

        geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));

        const mat = new THREE.PointsMaterial({
          size: 0.11,
          map: particleTex,
          vertexColors: true,
          transparent: true,
          opacity: 0.95,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        });

        const particles = new THREE.Points(geo, mat);
        scene.add(particles);

        // 4. Dynamic Neural Synapses (Connecting Lines)
        const maxLines = aiCoreOrb.maxConnections;
        const synapseGeo = new THREE.BufferGeometry();
        const synapsePositions = new Float32Array(maxLines * 6);
        synapseGeo.setAttribute("position", new THREE.BufferAttribute(synapsePositions, 3));
        synapseGeo.setDrawRange(0, 0);

        const synapseMat = new THREE.LineBasicMaterial({
          color: 0x00e5ff,
          transparent: true,
          opacity: 0.28,
          blending: THREE.AdditiveBlending
        });

        const synapseLines = new THREE.LineSegments(synapseGeo, synapseMat);
        scene.add(synapseLines);

        // 5. Pulsating Plasma Core (Inner Geodesic Sphere)
        const coreGeo = new THREE.IcosahedronGeometry(0.55, 3);
        const coreMat = new THREE.MeshBasicMaterial({
          color: 0x00f5d4,
          wireframe: true,
          transparent: true,
          opacity: 0.45,
          blending: THREE.AdditiveBlending
        });
        const innerCoreWire = new THREE.Mesh(coreGeo, coreMat);
        scene.add(innerCoreWire);

        const solidCoreGeo = new THREE.SphereGeometry(0.38, 24, 24);
        const solidCoreMat = new THREE.MeshBasicMaterial({
          color: 0x00e5ff,
          transparent: true,
          opacity: 0.65,
          blending: THREE.AdditiveBlending
        });
        const innerCore = new THREE.Mesh(solidCoreGeo, solidCoreMat);
        scene.add(innerCore);

        // 6. Holographic Gimbal Rings
        const gimbalRings = [];
        const ringConfigs = [
          { r: 1.82, tube: 0.015, color: 0x00e5ff, rotX: 0.55, rotY: 0.2, speed: 0.35 },
          { r: 2.05, tube: 0.012, color: 0x00f5d4, rotX: -0.75, rotY: 0.45, speed: -0.28 },
          { r: 2.25, tube: 0.014, color: 0x278bff, rotX: 1.15, rotY: -0.5, speed: 0.22 }
        ];

        ringConfigs.forEach(cfg => {
          const rGeo = new THREE.TorusGeometry(cfg.r, cfg.tube, 8, 48);
          const rMat = new THREE.MeshBasicMaterial({
            color: cfg.color,
            transparent: true,
            opacity: 0.55,
            blending: THREE.AdditiveBlending
          });
          const rMesh = new THREE.Mesh(rGeo, rMat);
          rMesh.rotation.set(cfg.rotX, cfg.rotY, 0);
          scene.add(rMesh);
          gimbalRings.push({ mesh: rMesh, speed: cfg.speed });
        });

        aiCoreOrb.scene = scene;
        aiCoreOrb.camera = camera;
        aiCoreOrb.renderer = renderer;
        aiCoreOrb.canvas = canvas;
        aiCoreOrb.container = container;
        aiCoreOrb.particles = particles;
        aiCoreOrb.particlePositions = positions;
        aiCoreOrb.particleBasePositions = basePositions;
        aiCoreOrb.particleColors = colors;
        aiCoreOrb.synapseLines = synapseLines;
        aiCoreOrb.synapseGeometry = synapseGeo;
        aiCoreOrb.synapsePositions = synapsePositions;
        aiCoreOrb.innerCore = innerCore;
        aiCoreOrb.innerCoreWire = innerCoreWire;
        aiCoreOrb.gimbalRings = gimbalRings;
        aiCoreOrb.clock = new THREE.Clock();
        aiCoreOrb.isInitialized = true;

        // Mouse Parallax Listener
        window.addEventListener("mousemove", (e) => {
          aiCoreOrb.mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
          aiCoreOrb.mouse.targetY = -(e.clientY / window.innerHeight) * 2 + 1;
        }, { passive: true });

        // Responsive Resize
        window.addEventListener("resize", onAICoreOrbResize, { passive: true });

        // Start Animation Loop
        renderAICoreOrbFrame();
        console.log("✔ AI Core Orb Engine initialized successfully!");
      }

      function onAICoreOrbResize() {
        if (!aiCoreOrb.container || !aiCoreOrb.renderer || !aiCoreOrb.camera) return;
        const nw = aiCoreOrb.container.clientWidth || 250;
        const nh = aiCoreOrb.container.clientHeight || 250;
        aiCoreOrb.camera.aspect = nw / nh;
        aiCoreOrb.camera.updateProjectionMatrix();
        aiCoreOrb.renderer.setSize(nw, nh);
      }

      function renderAICoreOrbFrame() {
        aiCoreOrb.rafId = requestAnimationFrame(renderAICoreOrbFrame);
        if (!aiCoreOrb.isInitialized || document.hidden) return;

        const time = aiCoreOrb.clock.getElapsedTime();

        // Smooth state lerp
        aiCoreOrb.currentSpeed += (aiCoreOrb.targetSpeed - aiCoreOrb.currentSpeed) * 0.08;
        aiCoreOrb.currentScale += (aiCoreOrb.targetScale - aiCoreOrb.currentScale) * 0.08;
        aiCoreOrb.currentGlow += (aiCoreOrb.targetGlow - aiCoreOrb.currentGlow) * 0.08;

        aiCoreOrb.mouse.x += (aiCoreOrb.mouse.targetX - aiCoreOrb.mouse.x) * 0.05;
        aiCoreOrb.mouse.y += (aiCoreOrb.mouse.targetY - aiCoreOrb.mouse.y) * 0.05;

        // Particle Harmonic Noise Oscillation
        const count = aiCoreOrb.particleCount;
        const pos = aiCoreOrb.particlePositions;
        const base = aiCoreOrb.particleBasePositions;
        const spd = aiCoreOrb.currentSpeed;
        const scl = aiCoreOrb.currentScale;

        for (let i = 0; i < count; i++) {
          const i3 = i * 3;
          const bx = base[i3];
          const by = base[i3 + 1];
          const bz = base[i3 + 2];

          const wave = Math.sin(time * 1.8 * spd + i * 0.12) * 0.07 * scl;
          pos[i3] = bx * (1 + wave) + (aiCoreOrb.mouse.x * 0.12);
          pos[i3 + 1] = by * (1 + wave) + (aiCoreOrb.mouse.y * 0.12);
          pos[i3 + 2] = bz * (1 + wave);
        }
        aiCoreOrb.particles.geometry.attributes.position.needsUpdate = true;

        // Rotate Global Particle Sphere
        aiCoreOrb.particles.rotation.y = time * 0.22 * spd;
        aiCoreOrb.particles.rotation.x = Math.sin(time * 0.1 * spd) * 0.12;

        // Dynamic Neural Synapses Calculation (Lightweight Neighborhood)
        if (!document.body.classList.contains("low-power-mode")) {
          let lineIdx = 0;
          const threshold = 0.40;
          const maxLines = aiCoreOrb.maxConnections;
          const sPos = aiCoreOrb.synapsePositions;

          for (let i = 0; i < count && lineIdx < maxLines * 6; i += 3) {
            for (let j = i + 3; j < Math.min(count, i + 36) && lineIdx < maxLines * 6; j += 3) {
              const dx = pos[i] - pos[j];
              const dy = pos[i+1] - pos[j+1];
              const dz = pos[i+2] - pos[j+2];
              const distSq = dx*dx + dy*dy + dz*dz;
              if (distSq < threshold * threshold) {
                sPos[lineIdx++] = pos[i];
                sPos[lineIdx++] = pos[i+1];
                sPos[lineIdx++] = pos[i+2];
                sPos[lineIdx++] = pos[j];
                sPos[lineIdx++] = pos[j+1];
                sPos[lineIdx++] = pos[j+2];
              }
            }
          }
          aiCoreOrb.synapseGeometry.setDrawRange(0, lineIdx / 3);
          aiCoreOrb.synapseGeometry.attributes.position.needsUpdate = true;
          aiCoreOrb.synapseLines.rotation.y = aiCoreOrb.particles.rotation.y;
          aiCoreOrb.synapseLines.rotation.x = aiCoreOrb.particles.rotation.x;
        }

        // Inner Plasma Core Pulse
        const corePulse = 1.0 + Math.sin(time * 2.4 * spd) * 0.08 * scl;
        if (aiCoreOrb.innerCoreWire) {
          aiCoreOrb.innerCoreWire.scale.set(corePulse, corePulse, corePulse);
          aiCoreOrb.innerCoreWire.rotation.y = -time * 0.4 * spd;
          aiCoreOrb.innerCoreWire.rotation.z = time * 0.2 * spd;
        }
        if (aiCoreOrb.innerCore) {
          aiCoreOrb.innerCore.scale.set(corePulse * 0.9, corePulse * 0.9, corePulse * 0.9);
        }

        // Rotating Gimbal Rings
        aiCoreOrb.gimbalRings.forEach((r, idx) => {
          r.mesh.rotation.z += 0.008 * r.speed * spd;
          r.mesh.rotation.y += 0.005 * r.speed * spd;
        });

        aiCoreOrb.renderer.render(aiCoreOrb.scene, aiCoreOrb.camera);
      }

      // Reactive Orb State Machine
      window.setOrbState = function(state, info) {
        if (!aiCoreOrb.isInitialized) initAICoreOrbEngine();
        aiCoreOrb.state = state;
        const textEl = document.getElementById("hud-orb-state-text");
        const auraEl = document.getElementById("ai-core-orb-aura");

        switch(state) {
          case 'idle':
            aiCoreOrb.targetSpeed = 0.5;
            aiCoreOrb.targetScale = 1.0;
            aiCoreOrb.targetGlow = 1.0;
            if (textEl) textEl.textContent = "IDLE // EN REPOSO";
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(0,245,212,0.28) 0%, rgba(0,229,255,0.14) 45%, transparent 70%)";
            break;
          case 'listening':
            aiCoreOrb.targetSpeed = 1.4;
            aiCoreOrb.targetScale = 1.25;
            aiCoreOrb.targetGlow = 1.6;
            if (textEl) textEl.textContent = "LISTENING // ESCUCHANDO";
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(0,245,212,0.55) 0%, rgba(0,229,255,0.35) 50%, transparent 75%)";
            break;
          case 'thinking':
            aiCoreOrb.targetSpeed = 3.2;
            aiCoreOrb.targetScale = 1.15;
            aiCoreOrb.targetGlow = 1.8;
            if (textEl) textEl.textContent = "THINKING // PROCESANDO";
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(139,92,246,0.55) 0%, rgba(0,229,255,0.3) 50%, transparent 75%)";
            break;
          case 'speaking':
            aiCoreOrb.targetSpeed = 1.6;
            aiCoreOrb.targetScale = 1.35;
            aiCoreOrb.targetGlow = 1.7;
            if (textEl) textEl.textContent = "SPEAKING // ASISTIENDO";
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(0,229,255,0.5) 0%, rgba(39,139,255,0.35) 50%, transparent 75%)";
            break;
          case 'executing':
            aiCoreOrb.targetSpeed = 2.4;
            aiCoreOrb.targetScale = 1.2;
            aiCoreOrb.targetGlow = 1.5;
            if (textEl) textEl.textContent = `EXECUTING // ${info || 'TOOL_RUN'}`;
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(56,239,125,0.5) 0%, rgba(0,229,255,0.3) 50%, transparent 75%)";
            break;
          case 'error':
            aiCoreOrb.targetSpeed = 0.8;
            aiCoreOrb.targetScale = 0.95;
            aiCoreOrb.targetGlow = 1.3;
            if (textEl) textEl.textContent = "ERROR // ALERTA";
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(255,92,119,0.5) 0%, rgba(255,209,102,0.3) 50%, transparent 75%)";
            break;
          case 'offline':
            aiCoreOrb.targetSpeed = 0.15;
            aiCoreOrb.targetScale = 0.85;
            aiCoreOrb.targetGlow = 0.4;
            if (textEl) textEl.textContent = "OFFLINE // DESCONECTADO";
            if (auraEl) auraEl.style.background = "radial-gradient(circle, rgba(90,110,133,0.3) 0%, transparent 60%)";
            break;
        }
      };

      // Handle Orb Interaction (Click to Speak / Listen)
      window.handleOrbInteraction = function() {
        if (typeof playHudSound === "function") playHudSound("click");
        const micBtn = document.getElementById("mic-btn");
        if (micBtn) {
          micBtn.click();
        } else {
          toggleOrbDockMode();
        }
      };

      // Docking Mode Toggle (Hero vs Compact)
      window.toggleOrbDockMode = function() {
        const stage = document.getElementById("ai-core-orb-stage");
        const icon = document.getElementById("orb-dock-icon");
        const lbl = document.getElementById("orb-dock-label");
        if (!stage) return;
        stage.classList.toggle("compact");
        const isCompact = stage.classList.contains("compact");
        aiCoreOrb.dockMode = isCompact ? "compact" : "hero";
        if (icon) icon.textContent = isCompact ? "▲" : "↕";
        if (lbl) lbl.textContent = isCompact ? "Expandir Núcleo" : "Acoplar Núcleo";
        setTimeout(onAICoreOrbResize, 200);
      };

      // HUD Sidebar & Inspector Controls
      window.toggleHudSidebar = function(force) {
        const sidebar = document.getElementById("hud-sidebar-nav");
        const backdrop = document.getElementById("hud-sidebar-backdrop");
        if (!sidebar) return;
        if (typeof force === "boolean") {
          if (force) {
            sidebar.classList.remove("collapsed");
            if (backdrop) backdrop.classList.add("active");
          } else {
            sidebar.classList.add("collapsed");
            if (backdrop) backdrop.classList.remove("active");
          }
        } else {
          sidebar.classList.toggle("collapsed");
          if (backdrop) backdrop.classList.toggle("active");
        }
        if (typeof playHudSound === "function") playHudSound("click");
      };

      window.toggleHudInspector = function(force) {
        const insp = document.getElementById("hud-context-inspector");
        if (!insp) return;
        if (typeof force === "boolean") {
          if (force) insp.classList.remove("collapsed");
          else insp.classList.add("collapsed");
        } else {
          insp.classList.toggle("collapsed");
        }
        if (typeof playHudSound === "function") playHudSound("click");
      };

      // Agent Hub Modal Controls
      window.openAgentHubModal = function() {
        const modal = document.getElementById("agent-hub-modal");
        if (modal) modal.style.display = "flex";
        if (typeof playHudSound === "function") playHudSound("open");
      };

      window.closeAgentHubModal = function() {
        const modal = document.getElementById("agent-hub-modal");
        if (modal) modal.style.display = "none";
        if (typeof playHudSound === "function") playHudSound("close");
      };

      window.activateAgentPersona = function(agentKey) {
        closeAgentHubModal();
        const personas = {
          jarvis_core: { name: "Liseth / JARVIS Core", role: "Coordinación Ejecutiva", model: "GEMINI 2.5 FLASH", prompt: "Hola Liseth, coordina mis prioridades ejecutivas y actividades de hoy." },
          fullstack_dev: { name: "Senior Full Stack Dev", role: "Arquitectura & Código", model: "GEMINI 2.5 PRO", prompt: "Actúa como Senior Full Stack Developer y Software Architect. Revisa y audita este código." },
          cybersecurity: { name: "Cybersecurity Auditor", role: "Ciberseguridad & Pentesting", model: "GEMINI 2.5 PRO", prompt: "Actúa como Cybersecurity Specialist. Evalúa las reglas de seguridad y vulnerabilidades." },
          business_strategist: { name: "Business Strategist", role: "Estrategia & Finanzas", model: "GEMINI 2.5 FLASH", prompt: "Actúa como Senior Business Strategist. Ayúdame con una modelación financiera y flujo de caja." },
          academic_researcher: { name: "Academic Researcher", role: "Investigación & APA 7ma", model: "GEMINI 2.5 FLASH", prompt: "Actúa como Academic Researcher. Busca literatura científica y redacta con citas en normas APA 7ma Edición." },
          data_science: { name: "Data Science & ML", role: "Ciencia de Datos & Modelado", model: "GEMINI 2.5 FLASH", prompt: "Actúa como Data Scientist. Analiza los datos de mi dataset con estadísticas y modelos predictivos." },
          nfc_engineer: { name: "NFC Core Specialist", role: "Transmisión Inalámbrica", model: "GEMINI 3.1 FLASH-LITE", prompt: "Actúa como NFC Core Specialist. Ayúdame a configurar un enlace dinámico y tarjeta inteligente vCard." }
        };

        const p = personas[agentKey] || personas.jarvis_core;
        const nameEl = document.getElementById("insp-agent-name");
        const roleEl = document.getElementById("insp-agent-role");
        const modelEl = document.getElementById("insp-agent-model");
        if (nameEl) nameEl.textContent = p.name;
        if (roleEl) roleEl.textContent = p.role;
        if (modelEl) modelEl.textContent = p.model;

        const input = document.getElementById("user-input");
        if (input) {
          input.value = p.prompt;
          input.focus();
        }
        showToast(`🤖 Agente activado: ${p.name}`);
        setOrbState("executing", p.name);
        setTimeout(() => setOrbState("idle"), 2500);
      };

      window.switchMainStageView = function(view) {
        if (view === "chat") {
          const sphereWs = document.getElementById("sphere-workspace");
          const consoleWs = document.getElementById("console-workspace");
          if (sphereWs) sphereWs.classList.remove("hidden");
          if (consoleWs) consoleWs.classList.remove("hidden");
        }
      };

      window.startNewConversationUI = function() {
        if (typeof window.clearChat === "function") {
          window.clearChat();
        } else {
          const btnClear = document.getElementById("btn-clear-chat");
          if (btnClear) btnClear.click();
        }
        showToast("💬 Nueva conversación iniciada");
      };

      window.switchModelProfileUI = function(modelCode) {
        localStorage.setItem("liseth_selected_model", modelCode);
        showToast(`⚡ Modelo activo: ${modelCode}`);
        const inspModel = document.getElementById("insp-agent-model");
        if (inspModel) inspModel.textContent = modelCode.toUpperCase();
      };

      window.triggerSessionLockUI = function() {
        const btnLock = document.getElementById("btn-session-lock");
        if (btnLock) btnLock.click();
      };

      // Auto-initialize AI Core Orb upon load
      window.addEventListener("DOMContentLoaded", () => {
        setTimeout(initAICoreOrbEngine, 200);
      });
'''

    # Inject Orb JS right before </script> at the end of the file
    script_close = "</script>\n</body>"
    if "let aiCoreOrb = {" not in html:
        if script_close in html:
            html = html.replace(script_close, orb_js + "\n    " + script_close, 1)
            print("✔ AI Core Orb Engine JavaScript injected.")
        else:
            # Fallback search for last </script>
            idx = html.rfind("</script>")
            if idx != -1:
                html = html[:idx] + orb_js + "\n    " + html[idx:]
                print("✔ AI Core Orb Engine JavaScript injected at last </script>.")

    # Write modified content to index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✔ index.html updated successfully!")

    # Synchronize jarvis.html and app/static/index.html
    shutil.copyfile("index.html", "jarvis.html")
    shutil.copyfile("index.html", "app/static/index.html")
    print("✔ Synchronized jarvis.html and app/static/index.html.")

    # Verify SHA256 checksums
    files = ["index.html", "jarvis.html", "app/static/index.html"]
    hashes = {}
    for fn in files:
        with open(fn, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
            hashes[fn] = h
            print(f"  {fn}: {h}")
    assert len(set(hashes.values())) == 1, "Files are not identical!"
    print("✔ VERIFICATION PASS: All 3 files are 100% byte-identical!")

if __name__ == "__main__":
    main()
