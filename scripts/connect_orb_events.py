# -*- coding: utf-8 -*-
"""
Helper script to connect AI Core Orb state transitions to:
1. speakText audio playback (speaking / idle)
2. fallbackLocalSpeech (speaking / idle)
3. setThinkingState (thinking / idle)
4. recognition onstart / onend (listening / idle)
5. appendMessage rich badges and auto-docking
"""
import shutil
import hashlib

def main():
    with open("index.html", "r", encoding="utf-8") as f:
        text = f.read()

    # 1. audio.onplay in speakText
    t1 = '''            audio.onplay = () => {
              isSpeaking = true;
              orb.classList.add("speaking");'''
    r1 = '''            audio.onplay = () => {
              isSpeaking = true;
              if (typeof window.setOrbState === "function") window.setOrbState("speaking");
              orb.classList.add("speaking");'''
    if t1 in text:
        text = text.replace(t1, r1, 1)
        print("✔ audio.onplay connected to setOrbState('speaking')")

    # 2. handleSpeechOutputFinished
    t2 = '''      function handleSpeechOutputFinished() {
        isSpeaking = false;
        orb.classList.remove("speaking");'''
    r2 = '''      function handleSpeechOutputFinished() {
        isSpeaking = false;
        if (typeof window.setOrbState === "function") window.setOrbState("idle");
        orb.classList.remove("speaking");'''
    if t2 in text:
        text = text.replace(t2, r2, 1)
        print("✔ handleSpeechOutputFinished connected to setOrbState('idle')")

    # 3. fallbackLocalSpeech onstart
    t3 = '''          utterance.onstart = () => {
            isSpeaking = true;
            orb.classList.add("speaking");'''
    r3 = '''          utterance.onstart = () => {
            isSpeaking = true;
            if (typeof window.setOrbState === "function") window.setOrbState("speaking");
            orb.classList.add("speaking");'''
    if t3 in text:
        text = text.replace(t3, r3, 1)
        print("✔ utterance.onstart connected to setOrbState('speaking')")

    # 4. fallbackLocalSpeech onend
    t4 = '''          utterance.onend = () => {
            handleSpeechOutputFinished();
          };'''
    r4 = '''          utterance.onend = () => {
            if (typeof window.setOrbState === "function") window.setOrbState("idle");
            handleSpeechOutputFinished();
          };'''
    if t4 in text:
        text = text.replace(t4, r4, 1)
        print("✔ utterance.onend connected to setOrbState('idle')")

    # 5. setThinkingState
    t5 = '''        if (thinking) {
          orb.classList.add("thinking");
          orb.setAttribute("title", "Liseth • Procesando su requerimiento...");
          statusLabel.textContent = "Analizando y procesando con agudeza...";
        } else {
          orb.classList.remove("thinking");
          orb.setAttribute("title", "Liseth • En reposo");
          statusLabel.textContent = "A su entera disposición, Santiago";
          userInput.focus();
        }'''
    r5 = '''        if (thinking) {
          if (typeof window.setOrbState === "function") window.setOrbState("thinking");
          orb.classList.add("thinking");
          orb.setAttribute("title", "Liseth • Procesando su requerimiento...");
          statusLabel.textContent = "Analizando y procesando con agudeza...";
        } else {
          if (typeof window.setOrbState === "function") window.setOrbState("idle");
          orb.classList.remove("thinking");
          orb.setAttribute("title", "Liseth • En reposo");
          statusLabel.textContent = "A su entera disposición, Santiago";
          userInput.focus();
        }'''
    if t5 in text:
        text = text.replace(t5, r5, 1)
        print("✔ setThinkingState connected to setOrbState")

    # 6. recognition onstart & onend
    t6 = '''          recognition.onstart = () => {
            isListening = true;'''
    r6 = '''          recognition.onstart = () => {
            isListening = true;
            if (typeof window.setOrbState === "function") window.setOrbState("listening");'''
    if t6 in text:
        text = text.replace(t6, r6, 1)
        print("✔ recognition.onstart connected to setOrbState('listening')")

    t6_end = '''          recognition.onend = () => {
            isListening = false;'''
    r6_end = '''          recognition.onend = () => {
            isListening = false;
            if (typeof window.setOrbState === "function") window.setOrbState("idle");'''
    if t6_end in text:
        text = text.replace(t6_end, r6_end, 1)
        print("✔ recognition.onend connected to setOrbState('idle')")

    # 7. appendMessage rich tag badge & auto-docking
    t7 = '''        const nameSpan = document.createElement("span");
        nameSpan.textContent = isAssistant ? ASSISTANT_NAME : "Santiago";
        senderLabel.appendChild(nameSpan);'''
    r7 = '''        const nameSpan = document.createElement("span");
        nameSpan.textContent = isAssistant ? ASSISTANT_NAME : "Santiago";
        senderLabel.appendChild(nameSpan);

        if (isAssistant) {
          let tagText = "AI CORE // INTELLIGENCE";
          if (content.includes("```")) tagText = "CODE ENGINE // ARTIFACT";
          else if (content.includes("DOI") || content.includes("arXiv") || content.includes("APA 7")) tagText = "DEEP RESEARCH // SYNTHESIS";
          else if (content.includes("NFC") || content.includes("vCard") || content.includes("NDEF") || content.includes("Bre-B")) tagText = "NFC CORE // HARDWARE";
          else if (content.includes("WACC") || content.includes("TIR") || content.includes("VPN") || content.includes("FODA")) tagText = "BUSINESS STRATEGY";
          else if (content.includes("Agente") || content.includes("Agent Hub")) tagText = "MULTI-AGENT COORDINATION";

          const tagSpan = document.createElement("span");
          tagSpan.className = "bubble-tag";
          tagSpan.textContent = tagText;
          senderLabel.appendChild(tagSpan);
        }'''
    if t7 in text:
        text = text.replace(t7, r7, 1)
        print("✔ appendMessage rich response badges added.")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(text)

    # Synchronize all 3 files
    shutil.copyfile("index.html", "jarvis.html")
    shutil.copyfile("index.html", "app/static/index.html")

    files = ["index.html", "jarvis.html", "app/static/index.html"]
    hashes = {}
    for fn in files:
        with open(fn, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
            hashes[fn] = h
            print(f"  {fn}: {h}")
    assert len(set(hashes.values())) == 1, "Files are not identical!"
    print("✔ All 3 frontend files synchronized perfectly!")

if __name__ == "__main__":
    main()
