# AI Content Studio Agent 🎬🧠

Welcome to the **AI Content Studio Agent**, your all-in-one AI companion for social media strategy and content generation. Powered by Google's Gemini API, this tool helps you brainstorm viral ideas in **Talk Mode** and instantly crafts full content packages (scripts, captions, hashtags, and thumbnail ideas).

---

## 🚀 Speed Run (Spin-up Instructions)

Follow these steps to get the app running on your machine in under 2 minutes.

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Google Gemini API Key**: Get one for free at [aistudio.google.com](https://aistudio.google.com/).

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```
**Configure Environment**: Create a `.env` file in the `backend/` folder:
```env
GEMINI_API_KEY=your_actual_key_here
PORT=8080
```
**Start the Server**:
```bash
python main.py
```

### 3. Frontend Setup
Open a **new terminal**:
```bash
cd frontend
npm install
npm run dev
```
**Access the app**: Usually at `http://localhost:5173`.

---

## ✨ Key Features

- **🗣️ Talk Mode (AI Strategist)**: Brainstorm with a high-energy AI agent. It remembers your context and suggests viral hooks.
- **🎬 One-Click Generation**: Once you have an idea, click 'Generate' to get:
  - 🎥 **YouTube Shorts Script** (30s structure)
  - 📝 **Instagram/TikTok Caption**
  - 🏷️ **Trending Hashtags**
  - 🖼️ **Thumbnail Concept Description**
- **📜 Conversation History**: All your brainstorms are saved to a local SQLite database. Reuse and switch between sessions with the history panel.
- **🎙️ Voice Input**: Hands-free brainstorming using integrated speech-to-text.
- **💎 Glassmorphism UI**: A premium, futuristic design built for a seamless user experience.

---

## 🛠️ Tech Stack

- **Frontend**: React (Vite), CSS3 (Vanilla), React Markdown.
- **Backend**: FastAPI (Python), Google GenAI SDK.
- **Database**: SQLite (local persistence).
- **Styles**: Glassmorphism design system.

---

## 📂 Project Structure

- `/backend`: FastAPI server, agent logic (`agents/`), and database tools.
- `/frontend`: React application, premium components, and design assets.

---

## 📝 License
This project was built for a hackathon. Feel free to use and improve it!

> "If a judge can't figure out how to run your code, they can't appreciate your genius." — *Spin-up instructions included!* 🚀
