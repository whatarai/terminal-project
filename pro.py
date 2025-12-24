import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import google.generativeai as genai


st.set_page_config(page_title="化學反應模擬器", layout="wide")
st.title("ChemSim AI: 動力學模擬引擎")


with st.sidebar:
    st.header("模擬參數設定")
    reaction_type = st.selectbox(
        "選擇反應類型",
        ["零級反應 (Zero-order)", "一級反應 (First-order)", "二級反應 (Second-order)", 
         "連串反應 (Consecutive)", "平行反應 (Parallel)"]
    )
    k1 = st.slider("速率常數 k1", 0.01, 2.0, 0.5)
    k2 = st.slider("速率常數 k2 (複合反應專用)", 0.01, 2.0, 0.2)
    ca0 = st.number_input("初始濃度 Ca0 (mol/L)", value=1.0, min_value=0.1)
    t_end = st.number_input("模擬總時間 (s)", value=10.0, min_value=1.0)
    dt = st.slider("運算步長 (dt)", 0.01, 0.1, 0.05)


def get_derivatives(C, k1, k2, r_type):
    Ca = C[0]
   
    Ca_safe = max(0, Ca)
    
    if r_type == "零級反應 (Zero-order)":
        # d[A]/dt = -k (當 [A] > 0)
        return np.array([-k1 if Ca_safe > 0 else 0])
    
    elif r_type == "一級反應 (First-order)":
        # d[A]/dt = -k1 * [A]
        return np.array([-k1 * Ca_safe])
    
    elif r_type == "二級反應 (Second-order)":
        # d[A]/dt = -k1 * [A]^2
        return np.array([-k1 * (Ca_safe**2)])
    
    elif r_type == "連串反應 (Consecutive)":
        # A -> B -> C
        Cb = C[1]
        dAdt = -k1 * Ca_safe
        dBdt = k1 * Ca_safe - k2 * max(0, Cb)
        dCdt = k2 * max(0, Cb)
        return np.array([dAdt, dBdt, dCdt])
    
    elif r_type == "平行反應 (Parallel)":
        # A -> B, A -> C
        dAdt = -(k1 + k2) * Ca_safe
        dBdt = k1 * Ca_safe
        dCdt = k2 * Ca_safe
        return np.array([dAdt, dBdt, dCdt])

def solve_rk4(k1, k2, ca0, t_end, dt, r_type):
    t_steps = int(t_end / dt)
    time = np.linspace(0, t_end, t_steps)
    
    
    num_species = 3 if "連串" in r_type or "平行" in r_type else 1
    C_results = np.zeros((t_steps, num_species))
    C_results[0, 0] = ca0
    
    for i in range(1, t_steps):
        curr_C = C_results[i-1]
        k_1 = get_derivatives(curr_C, k1, k2, r_type)
        k_2 = get_derivatives(curr_C + k_1 * dt / 2, k1, k2, r_type)
        k_3 = get_derivatives(curr_C + k_2 * dt / 2, k1, k2, r_type)
        k_4 = get_derivatives(curr_C + k_3 * dt, k1, k2, r_type)
        C_results[i] = curr_C + (dt / 6) * (k_1 + 2*k_2 + 2*k_3 + k_4)
        
    return time, C_results

t_plot, sol_plot = solve_rk4(k1, k2, ca0, t_end, dt, reaction_type)

fig, ax = plt.subplots(figsize=(10, 5))
labels = ["[A] Reactant", "[B] Intermediate/Product", "[C] Product"] if sol_plot.shape[1] > 1 else ["[A] Reactant"]
for i in range(sol_plot.shape[1]):
    ax.plot(t_plot, sol_plot[:, i], label=labels[i], linewidth=2.5)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Concentration (mol/L)")
ax.set_title(f"Numerical Simulation (RK4): {reaction_type}")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)


st.divider()
st.subheader("AI 數據智能診斷")
api_key = st.text_input("輸入 Gemini API Key ", type="password")

if st.button("生成分析報告"):
   
    local_report = f"""
    ###  本地動力學診斷報告
    * **模型**：手寫 NumPy RK4 數值求解器。
    * **反應級數**：{reaction_type}。
    * **參數狀態**：k1={k1}, Ca0={ca0}。
    * **物理意義**：
        - 若為**零級**，反應速率與濃度無關，呈現線性下降。
        - 若為**一級**，濃度呈指數衰減，具備固定半衰期。
        - 若為**二級**，反應隨濃度降低顯著變慢。
    ---

    """
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"分析此化學模擬結果：{reaction_type}, k1={k1}, k2={k2}。")
            st.info(res.text)
        except:
            st.markdown(local_report)
    else:
        st.markdown(local_report)
