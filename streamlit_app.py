import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 把 Dashboard 展示逻辑定义在最前面
def show_interactive_dashboard(wip_df):
    col1, col2, col3 = st.columns(3)
    col1.metric("WIP 总数", len(wip_df))
    # 假设 Exwork Date 列名准确
    overdue_count = len(wip_df[pd.to_datetime(wip_df['Exwork Date']) < pd.Timestamp("2026-07-07")])
    col2.metric("逾期订单", overdue_count)
    col3.metric("平均进度", f"{wip_df['Progress'].mean():.1f}%")
    
    st.subheader("⚠️ 当前工序积压热度")
    fig = px.bar(wip_df.groupby('Current Operation').size().reset_index(name='count'), 
                 x='Current Operation', y='count')
    st.plotly_chart(fig, use_container_width=True)

# 2. 读取逻辑
st.title("🏭 Epicor 智能报表")
uploaded_file = st.file_uploader("上传 Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    wip_df = df[~df['Current Operation'].isin(['Shipped', 'Completed'])].copy()
    wip_df['Progress'] = wip_df.apply(calculate_progress, axis=1) # 确保 calculate_progress 函数已定义
    
    # 3. 只有在这里调用，才不会报错，因为此时 wip_df 已经定义了
    show_interactive_dashboard(wip_df)
    
    # 4. 下载按钮逻辑也放在这里
    if st.button("生成 Excel"):
        # ... 你的下载逻辑 ...
