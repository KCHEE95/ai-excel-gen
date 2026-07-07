import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 假设 wip_df 已经处理好
def show_interactive_dashboard(wip_df):
    # --- KPI 区域 ---
    col1, col2, col3 = st.columns(3)
    col1.metric("WIP 总数", len(wip_df))
    col2.metric("逾期订单", len(wip_df[wip_df['Exwork Date'] < '2026-07-07']))
    col3.metric("平均进度", f"{wip_df['Progress'].mean():.1f}%")
    
    # --- 瓶颈分析图表 ---
    st.subheader("⚠️ 当前工序积压热度")
    fig = px.bar(wip_df.groupby('Current Operation').size().reset_index(name='count'), 
                 x='Current Operation', y='count', color='count', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)
    
    # --- 进度明细表 (支持点击行) ---
    st.subheader("📋 WIP 订单详情")
    st.dataframe(wip_df[['JobNum/Asm', 'Subpart Part Num', 'Current Operation', 'Exwork Date', 'Progress']])

show_interactive_dashboard(wip_df)
