
# 🧠 Axon

**Axon** is a Python-based personal voice assistant inspired by J.A.R.V.I.S. from Iron Man. It understands spoken or typed natural language commands and can perform tasks like opening apps, searching online, describing your screen, and answering questions using AI.

---

## 🚀 Features

- 🎤 Voice and text input modes
- 🤖 Gemini AI-powered command interpretation
- ⚙️ Open traditional and UWP Windows apps
- 🔍 Search YouTube, Google, and Wikipedia
- 🖼️ Describe what's on your screen using image analysis
- 💬 Ask general questions (via OpenAI-compatible API)
- 🗣️ Text-to-Speech using `pyttsx3` (fallback: `gTTS`)
- 🔍 Fuzzy matching for commands (e.g., `whooo am i` → `who am i`)
- 📝 Logs all interactions to `log.txt`

---

## 🖥️ Requirements

- **OS:** Windows
- **Python:** 3.8+
- **Dependencies:** Install with:

```bash
pip install -r requirements.txt
```

---

## 🔐 API Setup

- **Gemini AI:** Add your API key to `command.py` (`GEMINI_API_KEY`)
- **OpenAI-compatible API:** Update `token` and `endpoint` in `ask_ai.py`

---

## ▶️ Usage

1. Run the assistant:

```bash
python app.py
```

2. Choose your preferred input mode:
   - Voice Input 🎤
   - Manual Text Input ⌨️

3. Example commands:

   - `Open Spotify`
   - `Search YouTube for Python tutorials`
   - `Tell me about black holes on Wikipedia`
   - `Ask AI: What's the capital of France?`
   - `What's on my screen?`
   - `Take a screenshot`
   - `Stop` (to exit)

---

## 📁 Project Structure

```
axon-voice-assistant/
│
├── app.py               # Main script
├── command.py           # Gemini AI command handler + screen description
├── ask_ai.py            # AI question answering and response formatting
├── open_app.py          # App launcher (UWP + traditional)
├── wikipedia.py         # Wikipedia article summarizer
├── requirements.txt     # Python dependencies
```

---

## 🙌 Credits

- Inspired by **J.A.R.V.I.S.** from *Iron Man*
- Powered by **Gemini AI** and **OpenAI-compatible APIs**
- Built with **Python** and ❤️ by Mann
