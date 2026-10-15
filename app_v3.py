import math

import streamlit as st

st.set_page_config(page_title="계산기", page_icon="🧮", layout="centered")

# ---------------------------------------------------------------- 스타일
st.markdown(
    """
    <style>
    /* 바깥 배경과 계산기 본체 */
    .stApp {background: #cfd6de;}
    header[data-testid="stHeader"] {background: transparent;}
    #MainMenu, footer {visibility: hidden;}
    .block-container {
        max-width: 380px; margin-top: 1rem; margin-bottom: 1rem;
        padding: 1rem 0.8rem 1rem 0.8rem;
        background: #eef0f3; color: #1b1b1b;
        border-radius: 14px; box-shadow: 0 6px 24px rgba(0, 0, 0, 0.18);
    }

    /* 좁은 화면에서도 4열 유지, 열 너비 균등 */
    div[data-testid="stHorizontalBlock"] {flex-wrap: nowrap !important; gap: 0.4rem !important;}
    div[data-testid="stColumn"] {min-width: 0 !important; flex: 1 1 0 !important; width: auto !important;}
    div[data-testid="stElementContainer"] {width: 100% !important;}

    /* 공통 버튼: 칸을 가득 채운다 */
    div[data-testid="stButton"], .stButton {width: 100% !important;}
    div[data-testid="stPopover"] > button {
        width: 100% !important; min-width: 0; padding: 0; height: 2.6rem;
        background: #dfe3e8; border: 1px solid #c9ced6; border-radius: 8px; color: #1b1b1b;
    }
    .stButton > button {
        width: 100% !important; min-width: 0; height: 3.3rem; padding: 0;
        border-radius: 8px; border: 1px solid #c9ced6;
        background: #dfe3e8; color: #1b1b1b; box-shadow: none;
        font-size: 1.05rem; font-weight: 500; white-space: nowrap;
    }
    .stButton > button p {color: inherit; margin: 0; white-space: nowrap;}
    .stButton > button:hover {background: #d2d7de; border-color: #b9bfc8; color: #000;}
    .stButton > button:active {background: #c5cbd3;}

    /* 숫자 버튼은 흰색으로 구분 */
    div[class*="st-key-num_"] button {background: #ffffff; font-weight: 700; font-size: 1.15rem;}
    div[class*="st-key-num_"] button:hover {background: #f1f3f5;}

    /* 등호 버튼 */
    div[class*="st-key-eq"] button {background: #0f8f9b; border-color: #0f8f9b; color: #fff; font-size: 1.3rem;}
    div[class*="st-key-eq"] button:hover {background: #0c7a85; border-color: #0c7a85; color: #fff;}

    /* 메모리 버튼 */
    div[class*="st-key-mem_"] button {
        height: 2rem; background: transparent !important; border: none !important;
        font-size: 0.8rem; font-weight: 700;
    }
    div[class*="st-key-mem_"] button:hover {background: #dfe3e8;}
    div[class*="st-key-mem_"] button:disabled {color: #aab0b9; background: transparent;}

    /* 화면 */
    .calc-expr {text-align: right; color: #5f6670; font-size: 0.95rem; min-height: 1.4rem; padding: 0 0.25rem;}
    .calc-main {text-align: right; font-weight: 600; line-height: 1.2; padding: 0.2rem 0.25rem 0.8rem;
                white-space: nowrap; overflow: hidden; color: #1b1b1b;}
    .calc-title {font-size: 1.5rem; font-weight: 700; margin: 0; padding-top: 0.3rem; color: #1b1b1b;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- 상태
def init_state():
    st.session_state.setdefault("display", "0")   # 현재 입력 또는 결과
    st.session_state.setdefault("acc", None)      # 누적 값
    st.session_state.setdefault("op", None)       # 대기 중인 연산자
    st.session_state.setdefault("expr", "")       # 위쪽 작은 수식
    st.session_state.setdefault("fresh", True)    # 다음 숫자 입력 시 화면을 덮어쓸지 여부
    st.session_state.setdefault("after_op", False)  # 직전에 연산자를 눌렀는지 여부
    st.session_state.setdefault("error", False)
    st.session_state.setdefault("memory", None)
    st.session_state.setdefault("history", [])


def reset_all():
    st.session_state.display = "0"
    st.session_state.acc = None
    st.session_state.op = None
    st.session_state.expr = ""
    st.session_state.fresh = True
    st.session_state.after_op = False
    st.session_state.error = False


init_state()


# ---------------------------------------------------------------- 계산 도우미
def fmt(v):
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:.12g}"


def pretty(s):
    """화면 표시용으로 천 단위 쉼표를 넣는다."""
    if st.session_state.error or "e" in s or not (s[0].isdigit() or s[0] == "-"):
        return s
    sign = "-" if s.startswith("-") else ""
    body = s[1:] if sign else s
    int_part, dot, frac = body.partition(".")
    return f"{sign}{int(int_part or '0'):,}{dot}{frac}"


def compute(a, op, b):
    if op == "+":
        return a + b
    if op == "−":
        return a - b
    if op == "×":
        return a * b
    if op == "÷":
        if b == 0:
            raise ZeroDivisionError
        return a / b
    return b


def set_error(msg):
    st.session_state.display = msg
    st.session_state.error = True
    st.session_state.acc = None
    st.session_state.op = None
    st.session_state.expr = ""
    st.session_state.fresh = True
    st.session_state.after_op = False


def press(label):
    s = st.session_state

    if s.error:
        reset_all()
        if label == "C":
            return

    cur = float(s.display)

    # 숫자
    if label.isdigit():
        if s.fresh or s.display == "0":
            s.display = label
            if s.op is None:
                s.expr = ""
        elif len(s.display.replace("-", "").replace(".", "")) < 16:
            s.display += label
        s.fresh = False
        s.after_op = False

    # 소수점
    elif label == ".":
        if s.fresh:
            s.display = "0."
            if s.op is None:
                s.expr = ""
        elif "." not in s.display:
            s.display += "."
        s.fresh = False
        s.after_op = False

    # 부호 전환
    elif label == "+/−":
        if float(s.display) != 0:
            s.display = s.display[1:] if s.display.startswith("-") else "-" + s.display

    # 지우기
    elif label == "⌫":
        if not s.fresh:
            s.display = s.display[:-1]
            if s.display in ("", "-"):
                s.display = "0"
    elif label == "CE":
        s.display = "0"
        s.fresh = True
    elif label == "C":
        reset_all()

    # 사칙연산
    elif label in ("+", "−", "×", "÷"):
        if s.op is not None and not s.after_op:
            try:
                s.acc = compute(s.acc, s.op, cur)
            except ZeroDivisionError:
                set_error("0으로 나눌 수 없습니다")
                return
            s.display = fmt(s.acc)
        elif s.op is None:
            s.acc = cur
        s.op = label
        s.expr = f"{fmt(s.acc)} {label}"
        s.fresh = True
        s.after_op = True

    # 등호
    elif label == "=":
        if s.op is not None:
            b = cur
            try:
                result = compute(s.acc, s.op, b)
            except ZeroDivisionError:
                set_error("0으로 나눌 수 없습니다")
                return
            expr = f"{fmt(s.acc)} {s.op} {fmt(b)} ="
            s.history.append((expr, fmt(result)))
            s.expr = expr
            s.display = fmt(result)
            s.acc = None
            s.op = None
        else:
            s.expr = f"{fmt(cur)} ="
        s.fresh = True
        s.after_op = False

    # 단항 연산
    elif label in ("1/x", "x²", "√x"):
        try:
            if label == "1/x":
                if cur == 0:
                    raise ZeroDivisionError
                val, text = 1 / cur, f"1/({fmt(cur)})"
            elif label == "x²":
                val, text = cur * cur, f"sqr({fmt(cur)})"
            else:
                if cur < 0:
                    raise ValueError
                val, text = math.sqrt(cur), f"√({fmt(cur)})"
        except ZeroDivisionError:
            set_error("0으로 나눌 수 없습니다")
            return
        except ValueError:
            set_error("잘못된 입력입니다")
            return
        s.display = fmt(val)
        s.expr = text
        s.fresh = True
        s.after_op = False

    # 퍼센트
    elif label == "%":
        if s.acc is not None and s.op in ("+", "−"):
            val = s.acc * cur / 100
        elif s.acc is not None and s.op in ("×", "÷"):
            val = cur / 100
        else:
            val = 0.0
        s.display = fmt(val)
        s.fresh = True
        s.after_op = False

    # 메모리
    elif label == "MC":
        s.memory = None
    elif label == "MR":
        if s.memory is not None:
            s.display = fmt(s.memory)
            s.fresh = True
            s.after_op = False
    elif label == "M+":
        s.memory = (s.memory or 0.0) + cur
        s.fresh = True
    elif label == "M−":
        s.memory = (s.memory or 0.0) - cur
        s.fresh = True
    elif label == "MS":
        s.memory = cur
        s.fresh = True


def btn(container, label, key, **kwargs):
    container.button(label, key=key, on_click=press, args=(label,), **kwargs)


# ---------------------------------------------------------------- 화면
head_l, head_r = st.columns([5, 1])
head_l.markdown('<p class="calc-title">☰ &nbsp;표준</p>', unsafe_allow_html=True)
with head_r.popover("🕘"):
    if st.session_state.history:
        for expr, res in reversed(st.session_state.history):
            st.markdown(f"<div style='text-align:right;color:#6b6b6b'>{expr}</div>"
                        f"<div style='text-align:right;font-size:1.3rem;font-weight:600'>{res}</div>",
                        unsafe_allow_html=True)
        if st.button("기록 지우기", key="clear_history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("아직 기록이 없습니다.")

shown = pretty(st.session_state.display)
size = 3.0 if len(shown) <= 9 else max(1.4, 3.0 - 0.17 * (len(shown) - 9))
st.markdown(
    f'<div class="calc-expr">{st.session_state.expr}</div>'
    f'<div class="calc-main" style="font-size:{size:.2f}rem">{shown}</div>',
    unsafe_allow_html=True,
)

# 메모리 줄
mem_labels = ["MC", "MR", "M+", "M−", "MS"]
mem_cols = st.columns(6, gap="small")
has_mem = st.session_state.memory is not None
for col, label in zip(mem_cols, mem_labels):
    disabled = label in ("MC", "MR") and not has_mem
    btn(col, label, f"mem_{label}", disabled=disabled)
with mem_cols[5].container(key="mem_more"):
    with st.popover("M∨", disabled=not has_mem):
        if has_mem:
            st.write(f"메모리: {pretty(fmt(st.session_state.memory))}")

# 키패드
rows = [
    [("%", "fn_pct"), ("CE", "fn_ce"), ("C", "fn_c"), ("⌫", "fn_bs")],
    [("1/x", "fn_inv"), ("x²", "fn_sq"), ("√x", "fn_sqrt"), ("÷", "op_div")],
    [("7", "num_7"), ("8", "num_8"), ("9", "num_9"), ("×", "op_mul")],
    [("4", "num_4"), ("5", "num_5"), ("6", "num_6"), ("−", "op_sub")],
    [("1", "num_1"), ("2", "num_2"), ("3", "num_3"), ("+", "op_add")],
    [("+/−", "num_sign"), ("0", "num_0"), (".", "num_dot"), ("=", "eq")],
]
for row in rows:
    cols = st.columns(4, gap="small")
    for col, (label, key) in zip(cols, row):
        btn(col, label, key)
