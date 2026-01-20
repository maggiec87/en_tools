import docx
import re
import pandas as pd
import json

def is_title(text):
    # 匹配类似 "1. Title (中文)" 或 "Week 1" 的标题行
    return re.match(r'^(Week \d+|第?\d+[\.、].*（.*）)', text)

def clean_text(text):
    # 移除多余空格和特殊符号
    return text.strip()

def process_docx(file_path):
    doc = docx.Document(file_path)
    all_data = []
    current_topic = "未分类"
    sentence_count = 0
    
    # 英文句子匹配正则（考虑了缩写和标点）
    en_sent_pattern = re.compile(r'([A-Z][^.!?]*[.!?])')

    for para in doc.paragraphs:
        text = clean_text(para.text)
        if not text: continue
        
        # 1. 识别并更新标题（不作为句子提取）
        if is_title(text):
            current_topic = text
            sentence_count = 0 # 换新文章，序号重置
            continue
        
        # 2. 提取段落中的英文句子
        sentences = en_sent_pattern.findall(text)
        
        for sent in sentences:
            sentence_count += 1
            # 这里默认中文翻译为空，您可以手动在Excel中补充或接入API
            all_data.append({
                "ID": sentence_count,
                "Topic": current_topic,
                "English": sent.strip(),
                "Chinese": "" # 预留位置
            })
            
    return all_data

# 执行处理
file_name = "SSP 全文.docx"
data_list = process_docx(file_name)
df = pd.DataFrame(data_list)

# --- 导出 1: Excel (按Topic分组显示更清晰) ---
df.to_excel("ssp_output.xlsx", index=False)

# --- 导出 2: HTML (标题不重复，逐句带序号) ---
html_str = """
<html><head><meta charset="utf-8"><style>
    body { font-family: 'Segoe UI', Tahoma, sans-serif; padding: 40px; background: #f4f7f6; }
    .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; }
    h2 { color: #2c3e50; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 40px; }
    .row { display: flex; margin-bottom: 10px; border-bottom: 1px solid #eee; padding: 8px 0; }
    .num { width: 40px; color: #999; font-size: 0.9em; }
    .content { flex: 1; }
    .en { font-weight: 500; color: #333; margin-bottom: 4px; }
    .zh { color: #666; font-size: 0.95em; }
</style></head><body><div class="container">
"""

last_topic = ""
for _, row in df.iterrows():
    if row['Topic'] != last_topic:
        html_str += f"<h2>{row['Topic']}</h2>"
        last_topic = row['Topic']
    
    html_str += f"""
    <div class="row">
        <div class="num">{row['ID']}.</div>
        <div class="content">
            <div class="en">{row['English']}</div>
            <div class="zh">{row['Chinese']}</div>
        </div>
    </div>
    """
html_str += "</div></body></html>"
with open("ssp_output.html", "w", encoding="utf-8") as f:
    f.write(html_str)

# --- 导出 3: data.js ---
json_data = df.to_dict(orient='records')
with open("data.js", "w", encoding="utf-8") as f:
    f.write(f"const sspData = {json.dumps(json_data, ensure_ascii=False, indent=2)};")

print("处理完成！已生成：ssp_output.xlsx, ssp_output.html, data.js")