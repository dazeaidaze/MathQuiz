from flask import Flask, render_template, jsonify, request  # 导入必要的Flask模块
import random  # 用于生成随机数

app = Flask(__name__)


# 生成单个数学问题
def generate_question():
    num1 = random.randint(1, 10)  # 随机生成第一个数字
    operation = random.choice(['+', '-', '*', '/'])  # 随机选择运算符
    if operation == '/':  # 如果是除法，确保结果为整数且除数不为0
        num2 = random.randint(1, 10)
        while num1 % num2 != 0:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
    else:
        num2 = random.randint(1, 10)  # 对于其他运算符，随机生成第二个数字
    answer = eval(f'{num1} {operation} {num2}')  # 计算答案
    question = f'{num1} {operation} {num2} = '  # 构建问题字符串
    return {'question': question, 'answer': answer}


@app.route('/')
def index():
    return render_template('index.html')  # 渲染主页模板


@app.route('/get_questions')
def get_questions():
    questions = [generate_question() for _ in range(5)]  # 生成3个问题
    return jsonify(questions)  # 返回JSON格式的问题集


@app.route('/check_answers', methods=['POST'])
def check_answers():
    data = request.json  # 获取提交的答案数据
    results = []
    score = 0
    for idx, qa_pair in enumerate(data):
        correct = int(qa_pair['answer']) == eval(qa_pair['question'].replace("= ", ""))  # 判断用户答案是否正确
        if correct:
            score += 1
        results.append(
            {'index': idx + 1, 'correct': correct, 'expected': eval(qa_pair['question'].replace("= ", ""))})  # 保存每题的结果

    response_message = {"score": score, "results": results}

    if score == len(data):  # 如果全部回答正确
        response_message["message"] = "恭喜你，全答对！"
    else:  # 如果有错有对
        response_message["message"] = "有对有错，请查看详细结果："
        correct_msg = "; ".join([f"第{item['index']}题正确" for item in results if item['correct']])
        incorrect_msg = "; ".join(
            [f"第{item['index']}题错误，正确的答案是{item['expected']}" for item in results if not item['correct']])
        response_message["details"] = correct_msg + ("" if not incorrect_msg else ("; " + incorrect_msg))

    return jsonify(response_message)


if __name__ == '__main__':
    app.run(port="9000",debug=True)  # 启动应用，启用调试模式