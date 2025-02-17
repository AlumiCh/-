from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from werkzeug.utils import secure_filename
import secrets, os, threading, subprocess

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)

# 配置上传路径（指向共享文件夹）
UPLOAD_FOLDER = r'\\管理端IP\shared'  # 替换为实际共享路径
ALLOWED_EXTENSIONS = {'exe'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 存储任务和状态的全局变量
tasks = {}  # 格式：{ "Machine-001": {"command": "msiexec /i vscode.msi", "status": "pending"} }

class CommandForm(FlaskForm):
    exe_file = FileField('上传EXE文件')
    submit = SubmitField('上传')

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
    
def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_exe_list')
def get_exe_list():
    """获取共享文件夹中的EXE文件列表"""
    exe_files = []
    shared_folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(shared_folder):
        if filename.endswith('.exe'):
            exe_files.append(filename)
    return jsonify(exe_files)

@app.route('/deploy', methods=['POST'])
def handle_deploy():
    files = request.form.getlist('files')  # 前端传入的EXE文件名列表
    ips = request.form.get('ips').split(',')  # 目标机器IP列表

    for file in files:
        install_command = f"\\\\{MANAGER_IP}\\shared\\{file} /S"
        for ip in ips:
            agent_id = f"Machine-{ip}"
            tasks[agent_id] = {
                "command": install_command,
                "status": "pending"
            }
    return jsonify(success=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CommandForm()
    if form.validate_on_submit():
        # 文件上传
        uploaded_file = form.exe_file.data
        if uploaded_file:
            if allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(filepath)
                return "文件上传成功！"
            else:
                return "错误：仅支持上传EXE文件！"
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)