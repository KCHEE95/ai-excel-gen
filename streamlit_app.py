import streamlit as st
import pandas as pd
import io
import xlsxwriter

def calculate_progress(row):
    steps = [row[f'Step {i}'] for i in range(1, 21)]
    current_op = row['Current Operation']
    if current_op in ['Shipped', 'Completed']: return 100
    try:
        # 找到当前工序在步骤序列中的位置
        idx = steps.index(current_op)
        return (idx / 20) * 100
    except ValueError:
        return 0

st.title("🏭 Epicor 智能报表生成器")

uploaded_file = st.file_uploader("上传 Epicor CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # 数据清洗
    wip_df = df[~df['Current Operation'].isin(['Shipped', 'Completed'])].copy()
    wip_df['Progress'] = wip_df.apply(calculate_progress, axis=1)
    
    if st.button("生成带 Dashboard 的 Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wip_df.to_excel(writer, index=False, sheet_name='WIP_Data')
            workbook = writer.book
            dashboard = workbook.add_worksheet('Dashboard')
            
            # 设置 Dashboard 样式
            header_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#D3D3D3'})
            dashboard.write('A1', '生产仪表盘', header_fmt)
            dashboard.write('A3', 'WIP 在制品总数:')
            dashboard.write('B3', len(wip_df))
            
            # 创建完成率图表
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': '进度百分比',
                'categories': ['WIP_Data', 1, 19, len(wip_df), 19], # 假设 JobNum 在第20列
                'values':     ['WIP_Data', 1, 45, len(wip_df), 45], # 假设 Progress 是新加的列
            })
            chart.set_title({'name': '各订单生产完成进度'})
            dashboard.insert_chart('D2', chart)
            
        st.download_button("📥 下载完整报表 (含进度 Dashboard)", data=output.getvalue(), file_name="Epicor_Dashboard.xlsx")
