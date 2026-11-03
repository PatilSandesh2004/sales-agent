# Sales Intelligence AI Tool 📊

A simple, beginner-friendly AI application that takes natural language sales questions, converts them into SQL using an AI tool, and queries data stored in multiple Excel spreadsheets.

---

## Project Structure

```text
├── backend/
│   ├── data/
│   │   ├── raw/                 # Excel files (.xlsx)
│   │   └── sales.db             # Local SQLite database
│   ├── src/
│   │   ├── agent/               # Sales agent workflow
│   │   ├── infrastructure/      # SQLite database & Excel loader
│   │   ├── prompts/             # System prompts for SQL generation
│   │   ├── routers/             # Query router
│   │   ├── schema/              # Pydantic data schemas
│   │   ├── scripts/             # Database reload script
│   │   ├── tools/               # SQL conversion and execution tools
│   │   ├── config.py            # App configurations
│   │   ├── main.py              # Backend CLI demo
│   │   └── models.py            # Database tables and column models
│   ├── requirements.txt
│   └── .env
├── frontend/
│   └── app.py                   # Streamlit web user interface
├── requirements.txt
└── .env
```

---

## How to Run the Application

### 1. Run the Web Application (Frontend + Backend)
```bash
streamlit run frontend/app.py
```
This launches the interactive dashboard in your browser (`http://localhost:8501`), where you can:
- Ask sales questions in plain English.
- See the generated SQL query created by the tool.
- View the fetched tabular data from your Excel sheets.

---

### 2. Run the Backend Terminal Demo
```bash
python backend/src/main.py
```
Executes sample sales questions directly in the terminal, printing:
- The user question
- Step 1: The generated SQL query
- Step 2: The table fetched from the Excel files
- Step 3: The final natural language answer

---

### 3. (Optional) Add your Groq API Key
If you want to use live LLM SQL generation, open `.env` and set:
```ini
GROQ_API_KEY=your_groq_api_key_here
```
*(If left empty, the application will automatically run using beginner demo rules.)*

# sales-agent
