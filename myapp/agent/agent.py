# agent/agent.py
import os
import requests
import time

# 代理配置
MANAGER_URL = "http://管理端IP:5000"  # 替换为你的管理端IP
AGENT_ID = "Machine-001"            # 每台机器的唯一标识

def report_status(status):
    """向管理端报告状态"""
    data = {
        "agent_id": AGENT_ID,
        "status": status
    }
    requests.post(f"{MANAGER_URL}/report", json=data)

def main():
    # 首次启动时注册
    report_status("Agent已启动")

    while True:
        # 每隔10秒向管理端请求任务
        response = requests.get(f"{MANAGER_URL}/get_task?agent_id={AGENT_ID}")
        task = response.json()

        if task["action"] == "install":
            # 执行安装命令（示例：安装Chocolatey）
            os.system(task["command"])
            report_status("安装完成")
        time.sleep(10)

if __name__ == "__main__":
    main()