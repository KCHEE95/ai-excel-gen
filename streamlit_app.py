import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🏭 Epicor 生产实时仪表盘")

# 1. 加载并清洗数据
uploaded_file = st.file_uploader("上传 Epicor 导出的 CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    today = pd.Timestamp("2026-07-07")
    
    # 定义 WIP 和 逾期
    wip_df = df[~df['Current Operation'].isin(['Shipped', 'Completed'])]
    overdue_df = wip_df[pd.to_datetime(wip_df['Exwork Date']) < today]

    # 2. KPI 区域
    col1, col2, col3 = st.columns(3)
    col1.metric("在制品总数 (WIP)", len(wip_df))
    col2.metric("逾期订单", len(overdue_df), delta_color="inverse")
    col3.metric("总处理中 Job", len(df))

    # 3. 可视化：工序瓶颈分布
    st.subheader("📊 当前工序瓶颈分布")
    op_counts = wip_df['Current Operation'].value_counts().reset_index()
    fig = px.bar(op_counts, x='index', y='Current Operation', title="各工序待处理 Job 数量")
    st.plotly_chart(fig, use_container_width=True)

    # 4. 可视化：步骤完成率 (示例逻辑)
    st.subheader("⚙️ 生产工艺流完成率")
    # 简化版：统计每个 Step 列的非空值
    steps = [f'Step {i}' for i in range(1, 21)]
    step_data = wip_df[steps].count().reset_index()
    fig2 = px.line(step_data, x='index', y=0, title="各步骤参与 Job 计数")
    st.plotly_chart(fig2, use_container_width=True)
