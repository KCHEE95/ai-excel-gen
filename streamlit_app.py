import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# 配置 API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("📊 Epicor Kinetic 订单智能仪表盘")

# 1. 上传文件功能
uploaded_file = st.file_uploader("请上传从 Epicor 导出的 Excel 文件", type=["xlsx", "xls"])

if uploaded_file is not None:
    # 读取 Excel
    df = pd.read_excel(uploaded_file)
    st.write("### 数据预览", df.head())
    
    if st.button("开始分析并生成 Dashboard"):
        with st.spinner('Gemini 正在深度分析订单数据...'):
            # 将数据转为文本摘要（为了节省 Token，只发送前 20 行或特定列）
            data_summary = df.head(50).to_string()
            
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"你是一个数据分析专家。这是从 Epicor Kinetic 导出的订单数据摘要：\n{data_summary}\n\n请为我生成一份详细的总结报告，包含：1. 销售趋势分析；2. 关键瓶颈提示；3. 改进建议。并给出可以直接用 Python/Streamlit 绘图的建议。"
            
            response = model.generate_content(prompt)
            st.markdown("### 🤖 AI 分析报告")
            st.write(response.text)
            
            # 2. 自动生成可视化仪表盘
            st.subheader("📈 快速可视化图表")
            # 假设你的 Excel 有 'OrderDate' 和 'OrderAmount' 列
            try:
                st.line_chart(df.set_index('OrderDate')['OrderAmount'])
            except:
                st.warning("未能自动绘图，请确保 Excel 中包含日期和金额列，或检查列名是否正确。")
