import json
import re
import random

def split_long_sentences(pairs, max_len=110):
    """
    智能拆分长句：只有当中英文标点符号（逗号/分号）数量一致时才拆分。
    """
    new_pairs = []
    for pair in pairs:
        en, cn = pair.get('en', ''), pair.get('cn', '')
        if not en or not cn: continue
        
        if len(en) <= max_len:
            new_pairs.append(pair)
            continue
            
        en_parts = re.split(r';\s*|,\s*', en)
        cn_parts = re.split(r'；|，', cn)
        
        if len(en_parts) == len(cn_parts) and len(en_parts) > 1:
            for e_sub, c_sub in zip(en_parts, cn_parts):
                if e_sub.strip():
                    new_pairs.append({"en": e_sub.strip(), "cn": c_sub.strip(), "is_split": True})
        else:
            new_pairs.append(pair)
    return new_pairs

def generate_perfect_workbook(js_file_path, output_html):
    # 1. 强力读取并解析数据
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(js_file_path, 'r', encoding='gbk') as f:
            content = f.read()

    # 使用正则精确定位第一个 [ 的位置，跳过前面的变量声明
    match = re.search(r'\[\s*\{', content)
    if not match:
        print(f"错误：在文件 {js_file_path} 中找不到有效的数据数组！")
        return
    
    start_index = match.start()

    try:
        # raw_decode 能够自动识别 JSON 结构的结束位置，忽略后面的 JS 代码
        data, _ = json.JSONDecoder().raw_decode(content[start_index:])
    except Exception as e:
        print(f"解析 JSON 失败: {e}")
        # 最后的兜底方案：尝试截断到最后一个 ]
        try:
            end_index = content.rfind(']') + 1
            data = json.loads(content[start_index:end_index])
        except:
            print("所有解析尝试均失败，请检查 JS 文件格式。")
            return

    # 2. CSS 样式 (微软雅黑 + 打印优化)
    css_style = """
    <style>
        @media print { .page-break { page-break-after: always; } body { -webkit-print-color-adjust: exact; } }
        body { font-family: "Microsoft YaHei", "微软雅黑", sans-serif; line-height: 1.6; color: #2d3436; margin: 0; padding: 0; }
        .page { padding: 30px 50px; max-width: 850px; margin: auto; }
        .header { border-bottom: 2px solid #333; margin-bottom: 20px; padding-bottom: 10px; }
        h1 { margin: 0; font-size: 20px; color: #000; }
        .task-list { display: flex; justify-content: space-between; background: #f8f9fa; padding: 12px; border-radius: 6px; margin-bottom: 25px; border: 1px solid #eee; }
        .task-step { display: flex; align-items: center; font-size: 13px; font-weight: bold; }
        .step-n { background: #333; color: #fff; border-radius: 50%; width: 18px; height: 18px; display: inline-flex; justify-content: center; align-items: center; margin-right: 6px; font-size: 11px; }
        .section-title { font-size: 16px; font-weight: bold; margin: 30px 0 15px; padding-left: 10px; border-left: 5px solid #333; }
        .item { display: flex; margin-bottom: 15px; align-items: flex-end; }
        .idx { width: 35px; font-size: 13px; color: #999; font-weight: bold; }
        .line { flex: 1; border-bottom: 1px solid #ccc; min-height: 30px; }
        .split-mark { color: #2ecc71; margin-left: 4px; font-size: 12px; }
        .trans-card { border: 1px solid #f1f2f6; padding: 15px; margin-bottom: 12px; border-radius: 5px; page-break-inside: avoid; }
        .cn-text { font-size: 14px; color: #333; margin-bottom: 10px; }
        .ans-line { border-bottom: 1px dashed #ddd; height: 26px; width: 100%; }
        .tag { font-size: 10px; color: #bbb; margin-right: 8px; border: 1px solid #eee; padding: 0 4px; border-radius: 3px; }
    </style>
    """

    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css_style}</head><body>"

    for lesson in data:
        processed_pairs = split_long_sentences(lesson.get('pairs', []))
        total = len(processed_pairs)
        
        html_content += '<div class="page">'
        html_content += f'<div class="header"><h1>{lesson.get("title", "Lesson")}</h1>'
        html_content += '<div style="display:flex; justify-content:space-between; font-size:12px; color:#666; margin-top:8px;">'
        html_content += '<span>日期 : ________</span><span>用时 : ____ 分钟</span></div></div>'

        tasks = ["通听全文1-3遍", "听写", "朗读+生词", "回译", "复述/背诵(选做)"]
        html_content += '<div class="task-list">'
        for i, t in enumerate(tasks, 1):
            html_content += f'<div class="task-step"><span class="step-n">{i}</span>{t}</div>'
        html_content += '</div>'

        html_content += '<div class="section-title">Step 2: 听写</div>'
        for i, p in enumerate(processed_pairs, 1):
            mark = '<span class="split-mark">↳</span>' if p.get('is_split') else ''
            html_content += f'<div class="item"><div class="idx">{i}{mark}</div><div class="line"></div></div>'

        html_content += '<div class="section-title">Step 4: 回译</div>'
        display_pairs = list(enumerate(processed_pairs, 1))
        random.shuffle(display_pairs)

        for current_idx, (original_idx, pair) in enumerate(display_pairs, 1):
            html_content += f'<div class="trans-card"><div class="cn-text"><span class="tag">#{original_idx}</span>{pair["cn"]}</div><div class="ans-line"></div></div>'

        html_content += '</div><div class="page-break"></div>'

    html_content += "</body></html>"

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 处理完成！输出文件：{output_html}")

# 如果是处理 NCE4，直接改文件名即可
generate_perfect_workbook('data_nce4.js', 'NCE4_Worksheet.html')