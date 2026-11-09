
import streamlit as st
import pandas as pd
import sys
import io
import contextlib
import traceback

st.set_page_config(
    page_title="Python Code Tracer",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Python Code Tracer")
st.caption("Understand Python execution step by step.")

DEFAULT_CODE = """a = 10
b = 20
c = a + b
print(c)
"""

if "code" not in st.session_state:
    st.session_state.code = DEFAULT_CODE

if "steps" not in st.session_state:
    st.session_state.steps = []

if "output" not in st.session_state:
    st.session_state.output = ""

if "error" not in st.session_state:
    st.session_state.error = ""

if "current_step" not in st.session_state:
    st.session_state.current_step = 0


def get_variables(namespace):
    variables = {}

    for key, value in namespace.items():
        if key.startswith("__"):
            continue

        try:
            variables[key] = repr(value)[:300]
        except Exception:
            variables[key] = "<unavailable>"

    return variables


def execute_code(code):
    steps = []
    output = io.StringIO()
    error = ""

    namespace = {
        "__name__": "__main__"
    }

    filename = "<user_code>"
    last_line = None

    source_lines = code.splitlines()

    def save_step(line_number):
        if len(steps) >= 500:
            return

        steps.append({
            "line": line_number,
            "source": (
                source_lines[line_number - 1]
                if 0 < line_number <= len(source_lines)
                else ""
            ),
            "variables": get_variables(namespace)
        })

    def tracer(frame, event, arg):
        nonlocal last_line

        if frame.f_code.co_filename != filename:
            return None

        if event == "line":
            if last_line is not None:
                save_step(last_line)

            last_line = frame.f_lineno

            return tracer

        if event == "return":
            if last_line is not None:
                save_step(last_line)
                last_line = None

            return None

        if event == "exception":
            return tracer

        return tracer

    try:
        compiled_code = compile(code, filename, "exec")

        with contextlib.redirect_stdout(output):
            sys.settrace(tracer)

            try:
                exec(compiled_code, namespace, namespace)
            finally:
                sys.settrace(None)

    except Exception:
        error = traceback.format_exc()

    return steps, output.getvalue(), error


# Code editor
st.subheader("1. Python Code Editor")

st.session_state.code = st.text_area(
    "Enter your Python code",
    value=st.session_state.code,
    height=250,
    key="python_editor"
)

col1, col2 = st.columns([1, 5])

with col1:
    run_button = st.button(
        "▶ Run Code",
        type="primary",
        use_container_width=True
    )

with col2:
    st.caption("Maximum 500 execution snapshots per run.")

if run_button:
    steps, output, error = execute_code(st.session_state.code)

    st.session_state.steps = steps
    st.session_state.output = output
    st.session_state.error = error
    st.session_state.current_step = 0

# Execution results
if st.session_state.steps:
    st.divider()
    st.subheader("2. Execution Tracer")

    total_steps = len(st.session_state.steps)

    if total_steps > 1:
        selected_step = st.slider(
            "Navigate execution steps",
            min_value=0,
            max_value=total_steps - 1,
            value=min(
                st.session_state.current_step,
                total_steps - 1
            ),
            key="step_slider"
        )

        st.session_state.current_step = selected_step
    else:
        selected_step = 0

    current = st.session_state.steps[selected_step]

    st.write(
        f"**Step:** {selected_step + 1} / {total_steps}"
    )

    st.write(
        f"**Executing line:** {current['line']}"
    )

    st.write("**Current statement:**")

    st.code(
        current["source"] or "(No source statement)",
        language="python"
    )

    # Variables
    st.subheader("3. Variable Explorer")

    variables = current["variables"]

    if variables:
        df = pd.DataFrame(
            [
                {"Variable": key, "Value": value}
                for key, value in variables.items()
            ]
        )

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No variables created yet.")

    # Navigation
    previous_col, next_col = st.columns(2)

    with previous_col:
        if st.button(
            "⬅ Previous",
            disabled=selected_step == 0,
            use_container_width=True
        ):
            st.session_state.current_step = selected_step - 1
            st.rerun()

    with next_col:
        if st.button(
            "Next ➡",
            disabled=selected_step >= total_steps - 1,
            use_container_width=True
        ):
            st.session_state.current_step = selected_step + 1
            st.rerun()

elif st.session_state.output or st.session_state.error:
    st.info("Execution finished without recorded line snapshots.")

# Output console
st.divider()
st.subheader("4. Output Console")

if st.session_state.output:
    st.code(st.session_state.output)

else:
    st.caption("No output generated.")

# Error console
if st.session_state.error:
    st.subheader("5. Execution Error")
    st.error("An error occurred while executing the code.")
    st.code(st.session_state.error)

st.divider()
st.caption("Python Code Tracer | Learning and Debugging Tool")
