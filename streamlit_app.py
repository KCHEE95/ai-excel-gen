import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import xlsxwriter

# 从 Secrets 获取 API Key
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("请先在 Streamlit Cloud 的 Secrets 中配置 GOOGLE_API_KEY")
    st.stop()

st.title("🤖 AI 仪表盘生成器")

user_prompt = st.text_area("描述你想要的数据（例如：生成一份过去5个月的销售数据，包含销售额和利润）：")

if st.button("开始生成"):
    with st.spinner('Gemini 正在思考数据...'):
        model = genai.GenerativeModel('gemini-pro')
        # 强制要求 Gemini 输出结构化的 CSV 格式
        prompt = f"请生成一份数据表格，以CSV格式输出，包含列名。需求是：{user_prompt}"
        response = model.generate_content(prompt)
        
        # 简单解析（实际应用中可能需要更严谨的字符串处理）
        csv_data = response.text.replace("```csv", "").replace("```", "").strip()
        df = pd.read_csv(io.StringIO(csv_data))
        
        st.write("预览数据：", df)
        
        # 生成 Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            # 这里可以添加简单的图表逻辑
            workbook = writer.book
            worksheet = writer.sheets['Data']
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({'values': ['Data', 1, 1, len(df), 1]})
            worksheet.insert_chart('D2', chart)
            
        st.download_button("📥 点击下载 Excel", data=output.getvalue(), file_name="report.xlsx")
