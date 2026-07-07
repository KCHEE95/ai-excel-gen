import streamlit as st
import pandas as pd
import io
import xlsxwriter

st.title("📊 Epicor 订单报表生成器")

uploaded_file = st.file_uploader("上传 Epicor CSV 文件", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # 定义 WIP
    wip_df = df[~df['Current Operation'].isin(['Shipped', 'Completed'])]
    
    if st.button("生成带 Dashboard 的 Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # 1. 保存明细表
            wip_df.to_excel(writer, index=False, sheet_name='WIP_Data')
            
            # 2. 创建 Dashboard 工作表
            dashboard = writer.book.add_worksheet('Dashboard')
            
            # 3. 统计数据准备
            op_counts = wip_df['Current Operation'].value_counts()
            
            # 4. 在 Excel 里画图
            chart = writer.book.add_chart({'type': 'column'})
            chart.add_series({
                'name':       '在制品数量',
                'categories': ['WIP_Data', 1, 23, len(wip_df), 23], # 假设 Column X 是第 24 列
                'values':     ['Dashboard', 1, 1, len(op_counts), 1],
            })
            dashboard.insert_chart('B2', chart)
            
        st.download_button("📥 下载带 Dashboard 的 Excel", data=output.getvalue(), file_name="Report_Dashboard.xlsx")
