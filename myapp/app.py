from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import threading
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# 存储任务和状态的全局变量
tasks = {}  # 格式：{ "Machine-001": {"command": "msiexec /i vscode.msi", "status": "pending"} }

class CommandForm(FlaskForm):
    ip_list = StringField('目标机器IP（多个用逗号分隔）')
    software_name = StringField('要安装的软件名称（需提前上传EXE）')
    submit = SubmitField('执行安装')

@app.route('/report', methods=['POST'])
def handle_report():
    """接收代理的状态报告"""
    data = request.json
    agent_id = data["agent_id"]
    tasks[agent_id]["status"] = data["status"]
    return jsonify(success=True)

@app.route('/get_task')
def get_task():
    """代理请求任务"""
    agent_id = request.args.get("agent_id")
    if agent_id in tasks:
        return jsonify({"action": "install", "command": tasks[agent_id]["command"]})
    else:
        return jsonify({"action": "wait"})

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CommandForm()
    if form.validate_on_submit():
        ips = form.ip_list.data.split(',')
        software = form.software_name.data

        # 生成安装命令（假设EXE已上传到共享路径）
        install_command = f"\\\\{MANAGER_IP}\\shared\\{software}.exe /S"  # 静默安装

        # 分配任务
        for ip in ips:
            agent_id = f"Machine-{ip}"
            tasks[agent_id] = {"command": install_command, "status": "pending"}

        return "任务已下发！"
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)