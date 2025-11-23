# 🤖 Gemini Multi-Agent Research System

A Python-based AI agent that acts as an autonomous researcher. It utilizes the **Google Gemini API** for reasoning and **Function Calling (Tools)** to perform real-time web searches via DuckDuckGo.

## 🌟 Key Features
* **Automatic Function Calling:** The AI decides when to browse the internet without manual prompts.
* **Stateful Agent Workflow:** Maintains context between the "Research Phase" and the "Writing Phase."
* **Robust Error Handling:** Includes a dynamic model selector that automatically finds the correct API model version available in the environment to prevent configuration crashes.
* **No API Costs:** Uses the free tier of Gemini and the open DuckDuckGo search library.

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ai-research-agent
