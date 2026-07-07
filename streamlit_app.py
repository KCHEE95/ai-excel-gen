import streamlit as st
import pandas as pd
import io
import xlsxwriter

def calculate_progress(row):
    # 获取 Step 1 到 Step 20 的列名
    steps = [row[f'Step {i}'] for i in range(1, 21)]
    current_op = str(row['Current Operation'])
    
    if current_op in ['Shipped', 'Completed', 'nan']: 
        return 100
    
    # 查找当前工序在步骤中的位置
    try:
        # 在 step 列表中查找当前工序出现的位置
        idx = steps.index(current_op)
        return round(((idx + 1) / 20) * 100, 1)
    except ValueError:
        return 0

st.title("📊 Epicor 生产实时仪表盘")

# 使用 file_uploader 支持 .xlsx
uploaded_file = st.file_uploader("请上传从 Epicor 导出的 Excel (.xlsx) 文件", type=["xlsx"])

if uploaded_file:
    try:
        # 直接读取 Excel
        df = pd.read_excel(uploaded_file)
        
        # 数据过滤：WIP 定义
        wip_df = df[~df['Current Operation'].isin(['Shipped', 'Completed'])].copy()
        wip_df['Progress'] = wip_df.apply(calculate_progress, axis=1)
        
        st.success("数据读取成功！")
        st.write("WIP 订单预览：", wip_df.head())
        
        if st.button("生成带 Dashboard 的 Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # 写入数据
                wip_df.to_excel(writer, index=False, sheet_name='WIP_Data')
                
                # 创建 Dashboard 工作表
                workbook = writer.book
                dashboard = workbook.add_worksheet('Dashboard')
                
                # 写入 KPI
                bold = workbook.add_format({'bold': True, 'font_size': 12})
                dashboard.write('A1', '生产概览', bold)
                dashboard.write('A2', 'WIP 总数:')
                dashboard.write('B2', len(wip_df))
                
                # 插入图表
                chart = workbook.add_chart({'type': 'column'})
                # 注意：此处列索引 45 是假设 'Progress' 在第 46 列
                chart.add_series({
                    'name': '订单完成进度',
                    'values': ['WIP_Data', 1, wip_df.columns.get_loc('Progress'), len(wip_df), wip_df.columns.get_loc('Progress')],
                })
                dashboard.insert_chart('D2', chart)
            
            st.download_button("📥 点击下载生成的 Excel", data=output.getvalue(), file_name="Epicor_Report.xlsx")
            
    except Exception as e:
        st.error(f"发生错误: {e}")
