import json
import os
import random

def generate_pro_workbook_final(js_path, output_html):
    if not os.path.exists(js_path):
        print(f"❌ 错误：找不到 {js_path}")
        return

    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read().replace("const sspData = ", "").strip().rstrip(";")
        ssp_data = json.loads(content)

    html_start = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <style>
            @page { size: A4; margin: 0; }
            body { background: #eee; margin: 0; padding: 0; font-family: 'PingFang SC', sans-serif; line-height: 1.3; }
            .page { 
                background: white; width: 210mm; min-height: 296mm; 
                margin: 5mm auto; padding: 10mm 15mm; box-sizing: border-box; 
                page-break-after: always; position: relative;
            }
            .header { text-align: center; border-bottom: 1.5px solid #1a2a3a; margin-bottom: 5px; }
            .header h1 { margin: 0; font-size: 18px; color: #1a2a3a; }
            .info-bar { display: flex; justify-content: space-between; font-size: 10px; margin: 5px 0; font-weight: bold; }
            .section-title { background: #1a2a3a; color: white; padding: 3px 10px; margin: 10px 0 5px; border-radius: 2px; font-size: 12px; }
            
            .tasks { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; list-style: none; padding: 0; font-size: 9px; }
            .tasks li { border: 1px solid #ddd; padding: 3px; text-align: left; background: #fff; }

            /* 听写区：单行高行距 */
            .dict-item { 
                border-bottom: 1px solid #eee; min-height: 40px; 
                display: flex; align-items: flex-end; padding-bottom: 2px;
            }
            .dict-num { width: 25px; font-size: 10px; color: #bbb; }

            /* 20词汇表：紧凑并列 */
            .vocab-container { display: grid; grid-template-columns: 1fr 1fr; gap: 0 10px; }
            .vocab-table { width: 100%; border-collapse: collapse; }
            .vocab-table th, .vocab-table td { border: 1px solid #ddd; padding: 4px 6px; font-size: 10px; text-align: left; }
            .vocab-table th { background: #f8f9fa; }
            .col-num { width: 20px; text-align: center; }

            /* 回译区 */
            .bt-item { margin-bottom: 6px; }
            .bt-zh { background: #f9f9f9; padding: 4px 8px; font-size: 11px; color: #333; border-left: 3px solid #1a2a3a; line-height: 1.3; }
            .bt-en-blank { border-bottom: 1px solid #000; height: 22px; width: 100%; }

            @media print {
                body { background: white; }
                .page { margin: 0; box-shadow: none; }
                .no-print { display: none; }
            }
        </style>
    </head>
    <body>
    """

    full_body = ""

    for topic, sentences in ssp_data.items():
        total = len(sentences)
        dict_content = "".join([f'<div class="dict-item"><div class="dict-num">{i+1}.</div></div>' for i in range(total)])
        
        def get_vocab_rows(start, end):
            return "".join([f'<tr><td class="col-num">{i}</td><td></td><td></td><td></td></tr>' for i in range(start, end + 1)])

        shuffled = list(sentences)
        random.shuffle(shuffled)
        bt_content = "".join([f'<div class="bt-item"><div class="bt-zh">{i+1}. {item["chinese"]}</div><div class="bt-en-blank"></div></div>' for i, item in enumerate(shuffled)])

        page_html = f"""
        <div class="page">
            <div class="header"><h1>SSP-Worksheet</h1></div>
            <div class="info-bar"><span>课程：{topic}</span><span>日期：____/____/____</span><span>时长：____ min</span></div>

            <div class="section-title">任务清单</div>
            <ul class="tasks">
                <li>☐ 1. 通听全文</li><li>☐ 2. 听写</li><li>☐ 3. 朗读&录音</li><li>☐ 4.完成理解题</li>
                <li>☐ 5. 词汇积累</li><li>☐ 6. 回译</li><li>☐ 7. 复述(选)</li><li>☐ 8. Essay(选)</li>
            </ul>

            <div class="section-title">Step 2: 听写</div>
            <div>{dict_content}</div>

            <div class="section-title">Step 5: 词汇积累</div>
            <div class="vocab-container">
                <table class="vocab-table">
                    <thead><tr><th class="col-num">#</th><th>英文</th><th>中文</th><th>复习</th></tr></thead>
                    <tbody>{get_vocab_rows(1, 10)}</tbody>
                </table>
                <table class="vocab-table">
                    <thead><tr><th class="col-num">#</th><th>英文</th><th>中文</th><th>复习</th></tr></thead>
                    <tbody>{get_vocab_rows(11, 20)}</tbody>
                </table>
            </div>

            <div class="section-title">Step 6: 回译 </div>
            {bt_content}
        </div>
        """
        full_body += page_html

    html_end = """<div class="no-print" style="position:fixed; bottom:30px; right:30px;"><button onclick="window.print()" style="padding:15px 30px; background:#1a2a3a; color:white; border:none; border-radius:5px; cursor:pointer;">预览并打印</button></div></body></html>"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_start + full_body + html_end)
    
    print(f"✅ 生成成功！已优化行高并压缩排版。")

generate_pro_workbook_final("data.js", "SSP_Workbook_Compact.html")