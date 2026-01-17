from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import difflib

app = Flask(__name__)

# 配置你的 API Key
# 实际开发中建议放在环境变量里
genai.configure(api_key="你的_GOOGLE_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 1. 获取上传的文件
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        # 读取内容
        text1 = file1.read().decode('utf-8')
        text2 = file2.read().decode('utf-8')

        # 2. 生成传统的 Diff (用于高亮显示)
        # 这里为了演示方便，我们只返回简单的文本差异，实际可用 diff2html 库在前端渲染
        diff = difflib.unified_diff(
            text1.splitlines(), 
            text2.splitlines(), 
            lineterm=''
        )
        diff_text = '\n'.join(list(diff))

        # 3. 调用 Gemini 进行智能分析
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
        请对比以下两个文件的内容变更，并用Markdown格式输出一份简短的分析报告。
        重点关注：代码/文本的意图改变、潜在风险。
        
        ---变更内容 (Diff)---
        {diff_text[:8000]} 
        """
        
        response = model.generate_content(prompt)
        ai_analysis = response.text

        # 4. 返回 JSON 数据给前端
        return jsonify({
            "status": "success",
            "diff_raw": diff_text,
            "ai_analysis": ai_analysis
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)