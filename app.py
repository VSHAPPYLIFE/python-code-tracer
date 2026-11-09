import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import contextlib
import traceback

st.set_page_config(
    page_title="Python Code Tracer",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Python Code Tracer")
st.write("Online Python Coding and Execution Platform")

default_code = '''import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    marks INTEGER
)
""")

cursor.execute(
    "INSERT INTO students VALUES (1, 'Arun', 95)"
)

cursor.execute("SELECT * FROM students")

print(cursor.fetchall())

conn.close()
'''

code = st.text_area(
    "Enter Python Code",
    value=default_code,
    height=300
)

if st.button("▶ Run Python Code"):

    output = io.StringIO()

    try:
        namespace = {
            "__name__": "__main__"
        }

        with contextlib.redirect_stdout(output):
            exec(compile(code, "<user_code>", "exec"), namespace)

        st.success("Code executed successfully!")

    except Exception:
        output.write(traceback.format_exc())
        st.error("Execution error!")

    st.subheader("Program Output")
    st.code(output.getvalue())

st.divider()

st.subheader("Supported Libraries")

st.write(
    "SQLite, Pandas, NumPy, Matplotlib "
    "and standard Python libraries."
)
