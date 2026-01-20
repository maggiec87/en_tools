from bs4 import BeautifulSoup
import json
import os
import re

def is_contains_chinese(text):
    """判断字符串是否包含中文字符"""
    return len(re.findall(r'[\u4e00-\u9fa5]', text)) > 0

def extract_ssp_data(html_path, js_path):
    if not os.path.exists(html_path):
        print(f"❌ 找不到文件: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    structured_data = {}
    # 查找所有内容行
    rows = soup.find_all(class_='row')
    
    print(f"🚀 正在分析 HTML 结构并提取数据...")

    for row in rows:
        # 1. 寻找所属 Topic (向上寻找最近的 h2)
        h2_tag = row.find_previous('h2')
        topic = h2_tag.get_text().strip() if h2_tag else "Default Topic"
        
        if topic not in structured_data:
            structured_data[topic] = []

        # 2. 提取 content 区域内的所有文本碎片
        content_div = row.find(class_='content')
        if not content_div:
            continue
            
        # 使用自定义分隔符提取所有层级的文本，防止单词粘连
        all_text_parts = content_div.get_text(separator="|||", strip=True).split("|||")
        
        en_fragments = []
        zh_fragments = []

        for part in all_text_parts:
            # 清理沉浸式翻译可能引入的特殊字符
            clean_part = part.replace('\n', ' ').strip()
            if not clean_part: continue
            
            # 核心判定：含中文则归入中文组，否则归入英文组
            if is_contains_chinese(clean_part):
                zh_fragments.append(clean_part)
            else:
                # 排除单纯的数字序号（如 "1."）
                if not re.match(r'^\d+\.$', clean_part):
                    en_fragments.append(clean_part)

        # 3. 合并碎片
        full_en = " ".join(en_fragments).replace("  ", " ").strip()
        full_zh = "".join(zh_fragments).strip()

        if full_en:
            structured_data[topic].append({
                "english": full_en,
                "chinese": full_zh
            })

    # 4. 写入 data.js 供练习册使用
    with open(js_path, 'w', encoding='utf-8') as f:
        json_content = json.dumps(structured_data, ensure_ascii=False, indent=2)
        f.write(f"const sspData = {json_content};")
    
    print(f"✅ 处理完成！")
    print(f"📊 统计：共提取 {len(structured_data)} 个主题，数据已保存至 {js_path}")

# 执行转换（请确保文件名与你上传的一致）
extract_ssp_data("3. ssp_translated.html", "data.js")