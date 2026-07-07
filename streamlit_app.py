import streamlit as st
import pandas as pd
import io
import xlsxwriter
import plotly.express as px

# 1. 定义计算进度的函数
def calculate_progress(row):
    steps = [row[f'Step {i}'] for i in range(1, 21)]
    current_op = str(row['Current Operation'])
    if current_op in ['Shipped', 'Completed', 'nan', 'nan']: return 100
    try:
        idx = steps.index(current_op)
        return round(((idx + 1) / 20) * 100, 1)
    except ValueError:
        return 0

st.title("🏭 Epicor 生产实时仪表盘")

uploaded_file = st.file_uploader("请上传 Epicor Excel 文件", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    wip_df = df[~df['Current Operation'].isin(['Shipped', 'Completed'])].copy()
    wip_df['Progress'] = wip_df.apply(calculate_progress, axis=1)
    
    # 2. 预览仪表盘
    col1, col2, col3 = st.columns(3)
    col1.metric("WIP 总数", len(wip_df))
    overdue_count = len(wip_df[pd.to_datetime(wip_df['Exwork Date'], errors='coerce') < pd.Timestamp("2026-07-07")])
    col2.metric("逾期订单", overdue_count)
    col3.metric("平均进度", f"{wip_df['Progress'].mean():.1f}%")
    
    st.subheader("⚠️ 当前工序积压热度")
    fig = px.bar(wip_df.groupby('Current Operation').size().reset_index(name='count'), x='Current Operation', y='count')
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. 生成 Excel 下载逻辑 (确保缩进正确)
    if st.button("生成并下载带 Dashboard 的 Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wip_df.to_excel(writer, index=False, sheet_name='WIP_Data')
            workbook = writer.book
            dashboard = workbook.add_worksheet('Dashboard')
            # 添加一些简单的汇总
            dashboard.write('A1', 'WIP 总数')
            dashboard.write('B1', len(wip_df))
            
        st.download_button(
            label="📥 点击下载 Excel",
            data=output.getvalue(),
            file_name="Epicor_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
