import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="Spin Coating Simulator", layout="wide")
st.title("Spin Coating Simulator: Thin-Film Uniformity")
st.markdown("---")

# 1. 왼쪽 컨트롤 패널 (입력 변수)
st.sidebar.header("Process Parameters")
rpm = st.sidebar.slider("Rotation Speed (RPM)", 500, 6000, 3000, 100)
viscosity = st.sidebar.slider("Initial Viscosity (Pa·s)", 0.01, 0.20, 0.05, 0.01)
evap_rate = st.sidebar.slider("Evaporation Rate (µm/s)", 0.0, 2.0, 0.5, 0.1)
h0 = st.sidebar.slider("Initial Thickness (µm)", 10, 200, 50, 10)

# 2. 물리 엔진 및 수치 해석 (Euler Method)
rho = 1000  # 밀도
omega = rpm * 2 * np.pi / 60  # 각속도 변환
E = evap_rate * 1e-6  # 증발률 (m/s)
h0_m = h0 * 1e-6  # 초기 두께 (m)
K = (2 * rho * omega**2) / (3 * viscosity)

dt = 0.1
t_max = 20.0
t_arr = np.arange(0, t_max + dt, dt)

# 해석적 해 (Analytical, E=0)
h_ana = h0_m / np.sqrt(1 + 2 * K * h0_m**2 * t_arr)

# 수치 해석 (Numerical, with Evaporation)
h_num = np.zeros_like(t_arr)
h_num[0] = h0_m
t_gel = "> 20.0"
gel_found = False

for i in range(1, len(t_arr)):
    if h_num[i-1] > 0:
        dhdt = -K * h_num[i-1]**3 - E
        h_num[i] = h_num[i-1] + dhdt * dt
    else:
        h_num[i] = 0

    if h_num[i] <= 0 and not gel_found:
        t_gel = f"{t_arr[i]:.1f}"
        gel_found = True
        
    if h_num[i] < 0:
        h_num[i] = 0

# 3. 겔화 시간 결과 출력
st.sidebar.markdown("---")
st.sidebar.markdown(f"### ⏱️ Estimated Gelation Time ($t_{{gel}}$)")
st.sidebar.error(f"**{t_gel} seconds**")

# 4. 데이터 시각화 (Validation View)
df = pd.DataFrame({
    "Time (s)": t_arr,
    "Analytical (E=0)": h_ana * 1e6,
    "Numerical (With Evaporation)": h_num * 1e6
})

fig = px.line(df, x="Time (s)", y=["Analytical (E=0)", "Numerical (With Evaporation)"],
              labels={"value": "Thickness (µm)", "variable": "Model Types"},
              title="Film Thickness Over Time")
fig.update_traces(line=dict(width=3))

st.plotly_chart(fig, use_container_width=True)
