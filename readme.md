# Dynamic AI Agent with LangChain & Gemini

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A sophisticated, multimodal AI assistant built with Python, LangChain, and Google's Gemini Pro. This project showcases a dynamic, agentic architecture with a web-based UI, real-time Text-to-Speech (TTS), and modular, extensible tools.

---

## 🌟 Core Features

- **Conversational AI:** Powered by Google's Gemini Pro for natural and intelligent dialogue.
- **Interactive Web UI:** A fluid and responsive chat interface built with Streamlit.
- **Real-time Text-to-Speech:** Brings the agent to life using the `RealtimeTTS` library with the Coqui engine.
- **Modular Tool-Using Agent:** Uses LangGraph to decide which tool to use based on the user’s query.
- **Persistent Memory:** Saves conversations to MongoDB Atlas and displays them via an admin panel.
- **Specialized Knowledge:** Custom API tools for domain-specific tasks (e.g., The Land of Legends events).
- **General Knowledge:** Web search via Tavily for up-to-date, real-world information.
- **Expert Persona:** Guided by a system prompt to stay within its domain of expertise.

---

## 🛠️ Tech Stack & Architecture

- **Frameworks:** LangChain, LangGraph, Streamlit  
- **AI/LLM:** Google Gemini Pro  
- **TTS Engine:** `RealtimeTTS` with Coqui  
- **Database:** MongoDB Atlas  
- **Integrated Tools:**
  - Tavily Search (Web)
  - Custom API tools (`requests`)
  - Internal tools (e.g., Time, Weather)

---

## 🚀 Future Roadmap

- [ ] Integrate more specialized APIs (weather, finance, calendar, etc.)
- [ ] Add real-time Speech-to-Text (STT) with Whisper
- [ ] More advanced agent workflows with LangGraph
- [ ] Deploy to Streamlit Community Cloud or Hugging Face Spaces
- [ ] Enhance the admin panel with analytics & metrics

---

## 📄 License

This project is licensed under the MIT License.  
See the [LICENSE](./LICENSE) file for details.

