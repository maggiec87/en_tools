import json
import random

def generate_perfect_workbook(js_file_path, output_html, shuffle_translation=True):
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    start_index = content.find('[')
    data, _ = json.JSONDecoder().raw_decode(content[start_index:])

    css_style = """
    <style>
        @media print {
            .page-break { page-break-after: always; }
            body { -webkit-print-color-adjust: exact; }
            @page { margin: 1.5cm; }
        }

        body { 
            /* 强制优先使用微软雅黑 */
            font-family: "Microsoft YaHei", "Standard Webview Font", "PingFang SC", sans-serif; 
            line-height: 1.6; color: #2d3436; margin: 0; padding: 0;
        }
        
        .page { padding: 20px 40px; max-width: 900px; margin: auto; position: relative; }

        /* 标题部分 */
        .header-section { border-bottom: 2px solid #2d3436; margin-bottom: 25px; padding-bottom: 10px; }
        h1 { margin: 0; color: #000; font-size: 24px; font-weight: 900; }
        .meta-info { display: flex; justify-content: space-between; font-size: 13px; color: #636e72; margin-top: 10px; }

        /* 任务清单优化：重构为 1-5 步 */
        .task-container { 
            display: flex; justify-content: space-between;
            background: #f1f2f6; padding: 15px; border-radius: 4px; margin-bottom: 30px;
        }
        .task-step { display: flex; align-items: center; font-size: 13px; font-weight: bold; }
        .step-num { 
            width: 18px; height: 18px; background: #2d3436; color: #fff; 
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 11px; margin-right: 6px; flex-shrink: 0;
        }
        .step-text { color: #2d3436; }

        /* 练习区域标题 */
        .section-header { 
            font-size: 16px; font-weight: 900; margin: 30px 0 15px; 
            padding-left: 10px; border-left: 4px solid #2d3436;
        }
        .dictation-title { color: #2d3436; }
        .translation-title { color: #2d3436; }

        /* 听写区域 */
        .dictation-item { margin-bottom: 18px; display: flex; align-items: flex-end; }
        .num { font-weight: bold; width: 25px; color: #b2bec3; font-size: 14px; }
        .line-box { 
            flex: 1; border-bottom: 1px solid #b2bec3; min-height: 28px; 
        }

        /* 回译区域卡片 */
        .translation-item { 
            border: 1px solid #dfe6e9; padding: 15px; margin-bottom: 15px; 
            page-break-inside: avoid; border-radius: 4px;
        }
        .cn-text { font-size: 15px; color: #2d3436; margin-bottom: 12px; font-weight: 500; }
        .original-tag { font-size: 11px; color: #b2bec3; margin-right: 8px; font-family: "Arial"; }
        .ans-area { border-bottom: 1px dashed #b2bec3; min-height: 25px; color: #b2bec3; font-size: 12px; padding-top: 5px;}

    </style>
    """

    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css_style}</head><body>"

    for lesson in data:
        pairs = lesson.get('pairs', [])
        total_sentences = len(pairs)
        title_text = lesson.get('title', 'Unknown Lesson')

        html_content += '<div class="page">'
        
        # 顶部标题栏
        html_content += f'''
        <div class="header-section">
            <h1>{title_text}</h1>
            <div class="meta-info">
                <span> 日期：202__  /  __  /  __ </span>
                <span> 用时：________ 分钟 </span>
            </div>
        </div>'''

        # 优化后的 5 步任务清单
        html_content += f'''
        <div class="task-container">
            <div class="task-step"><span class="step-num">1</span><span class="step-text">通听全文1-3遍</span></div>
            <div class="task-step"><span class="step-num">2</span><span class="step-text">听写 ({total_sentences}句)</span></div>
            <div class="task-step"><span class="step-num">3</span><span class="step-text">朗读+生词</span></div>
            <div class="task-step"><span class="step-num">4</span><span class="step-text">回译</span></div>
            <div class="task-step"><span class="step-num">5</span><span class="step-text">复述/背诵(选做)</span></div>
        </div>'''

        # 听写
        html_content += '<div class="section-header dictation-title">Step 2: 听写</div>'
        for i in range(1, total_sentences + 1):
            html_content += f'<div class="dictation-item"><div class="num">{i}</div><div class="line-box"></div></div>'

        # 回译
        html_content += '<div class="section-header translation-title">Step 4: 回译</div>'
        indexed_pairs = list(enumerate(pairs, 1))
        if shuffle_translation:
            random.shuffle(indexed_pairs)

        for current_idx, (original_idx, pair) in enumerate(indexed_pairs, 1):
            html_content += f'''
            <div class="translation-item">
                <div class="cn-text"><span class="original-tag">#{original_idx}</span>{pair.get('cn', '')}</div>
                <div class="ans-area">英文：</div>
            </div>'''

        html_content += '</div><div class="page-break"></div>'

    html_content += "</body></html>"

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 生成成功：{output_html}")

# 执行生成
generate_perfect_workbook('data_nce3.js', 'NCE3_Modern_Workbook.html')