import streamlit as st


def add(x, y):
    return x + y


def subtract(x, y):
    return x - y


def multiply(x, y):
    return x * y


def divide(x, y):
    if y == 0:
        return None
    return x / y


OPERATIONS = {
    "더하기 (+)": ("+", add),
    "빼기 (-)": ("-", subtract),
    "곱하기 (*)": ("*", multiply),
    "나누기 (/)": ("/", divide),
}

st.set_page_config(page_title="계산기", page_icon="🧮")
st.title("🧮 간단한 계산기")

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("calc_form"):
    op_name = st.radio("연산 선택", list(OPERATIONS.keys()), horizontal=True)
    col1, col2 = st.columns(2)
    num1 = col1.number_input("첫 번째 숫자", value=0.0, format="%f")
    num2 = col2.number_input("두 번째 숫자", value=0.0, format="%f")
    submitted = st.form_submit_button("계산하기")

if submitted:
    symbol, func = OPERATIONS[op_name]
    result = func(num1, num2)
    if result is None:
        st.error("오류: 0으로 나눌 수 없습니다.")
    else:
        expr = f"{num1} {symbol} {num2} = {result}"
        st.success(expr)
        st.session_state.history.append(expr)

if st.session_state.history:
    st.subheader("계산 기록")
    for item in reversed(st.session_state.history):
        st.write(item)
    if st.button("기록 지우기"):
        st.session_state.history = []
        st.rerun()
