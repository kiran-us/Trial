# Custom WebSearch Agent with LangGraph

1.python -m venv my-env
2. source my-env/Scripts/activate
3.pip install -r requirements.txt

streamlit run app.py
streamlit run app.py --server.runOnSave true

uvicorn main:app --host 0.0.0.0 --port 3000 --reload
