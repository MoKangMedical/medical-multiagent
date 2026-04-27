# 多Agent系统简化实施方案
# 针对当前Gateway配置问题的替代方案

# 问题分析
# 根据之前的错误信息：
# gateway closed (1008): unauthorized: gateway token mismatch

# 解决方案

# 方案A：修复Gateway配置
# 1. 检查配置文件一致性
#    # 检查gateway配置
#    grep -A 10 "gateway" ~/.openclaw/openclaw.json
#    
#    # 检查auth.token配置
#    grep -A 5 "auth" ~/.openclaw/openclaw.json | grep -A 5 "token"
#
# 2. 重新配置Gateway
#    # 停止现有Gateway
#    openclaw gateway stop
#    
#    # 重新生成配置
#    openclaw configure --section gateway
#    
#    # 启动Gateway
#    openclaw gateway start

# 方案B：使用简化多Agent架构
# 如果Gateway配置问题难以解决，可以采用以下简化架构：

# 1. 基于文件的Agent协作系统
# agents/file_based_orchestrator.py
"""
基于文件系统的多Agent协作系统
每个Agent有自己的工作目录，通过文件交换信息
"""

import os
import json
import time
from datetime import datetime

class FileBasedAgentSystem:
    def __init__(self, base_dir="~/Desktop/multiagent_system"):
        self.base_dir = os.path.expanduser(base_dir)
        self.agents = {}
        self.setup_directories()
    
    def setup_directories(self):
        """创建系统目录结构"""
        directories = [
            "agents",
            "tasks",
            "results",
            "logs",
            "communication"
        ]
        
        for dir_name in directories:
            dir_path = os.path.join(self.base_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
    
    def register_agent(self, agent_id, agent_type, capabilities):
        """注册一个Agent"""
        agent_dir = os.path.join(self.base_dir, "agents", agent_id)
        os.makedirs(agent_dir, exist_ok=True)
        
        agent_info = {
            "id": agent_id,
            "type": agent_type,
            "capabilities": capabilities,
            "status": "idle",
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat()
        }
        
        # 保存Agent信息
        with open(os.path.join(agent_dir, "agent_info.json"), "w") as f:
            json.dump(agent_info, f, indent=2)
        
        self.agents[agent_id] = agent_info
        return agent_info
    
    def create_task(self, task_id, description, requirements, priority="medium"):
        """创建一个新任务"""
        task_dir = os.path.join(self.base_dir, "tasks", task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        task_info = {
            "id": task_id,
            "description": description,
            "requirements": requirements,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assigned_agent": None,
            "result": None
        }
        
        # 保存任务信息
        with open(os.path.join(task_dir, "task_info.json"), "w") as f:
            json.dump(task_info, f, indent=2)
        
        # 添加到任务队列
        self.add_to_task_queue(task_id)
        return task_info
    
    def add_to_task_queue(self, task_id):
        """将任务添加到队列"""
        queue_file = os.path.join(self.base_dir, "tasks", "task_queue.json")
        
        if os.path.exists(queue_file):
            with open(queue_file, "r") as f:
                queue = json.load(f)
        else:
            queue = []
        
        if task_id not in queue:
            queue.append(task_id)
        
        with open(queue_file, "w") as f:
            json.dump(queue, f, indent=2)
    
    def assign_task(self, task_id, agent_id):
        """将任务分配给Agent"""
        task_dir = os.path.join(self.base_dir, "tasks", task_id)
        task_file = os.path.join(task_dir, "task_info.json")
        
        if os.path.exists(task_file):
            with open(task_file, "r") as f:
                task_info = json.load(f)
            
            task_info["assigned_agent"] = agent_id
            task_info["status"] = "assigned"
            task_info["assigned_at"] = datetime.now().isoformat()
            
            with open(task_file, "w") as f:
                json.dump(task_info, f, indent=2)
            
            # 创建Agent任务文件
            agent_task_file = os.path.join(self.base_dir, "agents", agent_id, f"task_{task_id}.json")
            with open(agent_task_file, "w") as f:
                json.dump(task_info, f, indent=2)
            
            return True
        return False
    
    def submit_result(self, task_id, agent_id, result):
        """提交任务结果"""
        task_dir = os.path.join(self.base_dir, "tasks", task_id)
        result_file = os.path.join(task_dir, "result.json")
        
        result_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "result": result,
            "submitted_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        with open(result_file, "w") as f:
            json.dump(result_data, f, indent=2)
        
        # 更新任务状态
        task_file = os.path.join(task_dir, "task_info.json")
        if os.path.exists(task_file):
            with open(task_file, "r") as f:
                task_info = json.load(f)
            
            task_info["status"] = "completed"
            task_info["completed_at"] = datetime.now().isoformat()
            task_info["result"] = result_data
            
            with open(task_file, "w") as f:
                json.dump(task_info, f, indent=2)
        
        return result_data
    
    def get_system_status(self):
        """获取系统状态"""
        status = {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for agent in self.agents.values() if agent["status"] == "active"),
            "pending_tasks": self.count_pending_tasks(),
            "completed_tasks": self.count_completed_tasks(),
            "system_uptime": self.get_system_uptime(),
            "timestamp": datetime.now().isoformat()
        }
        return status
    
    def count_pending_tasks(self):
        """计算待处理任务数"""
        tasks_dir = os.path.join(self.base_dir, "tasks")
        count = 0
        
        if os.path.exists(tasks_dir):
            for task_id in os.listdir(tasks_dir):
                if task_id == "task_queue.json":
                    continue
                    
                task_file = os.path.join(tasks_dir, task_id, "task_info.json")
                if os.path.exists(task_file):
                    with open(task_file, "r") as f:
                        task_info = json.load(f)
                    
                    if task_info["status"] in ["pending", "assigned"]:
                        count += 1
        
        return count
    
    def count_completed_tasks(self):
        """计算已完成任务数"""
        tasks_dir = os.path.join(self.base_dir, "tasks")
        count = 0
        
        if os.path.exists(tasks_dir):
            for task_id in os.listdir(tasks_dir):
                if task_id == "task_queue.json":
                    continue
                    
                task_file = os.path.join(tasks_dir, task_id, "task_info.json")
                if os.path.exists(task_file):
                    with open(task_file, "r") as f:
                        task_info = json.load(f)
                    
                    if task_info["status"] == "completed":
                        count += 1
        
        return count
    
    def get_system_uptime(self):
        """获取系统运行时间（简化版）"""
        # 这里可以记录系统启动时间
        uptime_file = os.path.join(self.base_dir, "system_uptime.txt")
        
        if os.path.exists(uptime_file):
            with open(uptime_file, "r") as f:
                start_time = datetime.fromisoformat(f.read().strip())
        else:
            start_time = datetime.now()
            with open(uptime_file, "w") as f:
                f.write(start_time.isoformat())
        
        uptime = datetime.now() - start_time
        return str(uptime)

# 预定义的医疗研究Agent类型
MEDICAL_AGENTS = {
    "clinical_analyst": {
        "name": "临床分析师",
        "capabilities": ["数据分析", "统计检验", "结果解释", "图表生成"],
        "description": "负责临床数据的统计分析和结果解释"
    },
    "medical_writer": {
        "name": "医学写作者",
        "capabilities": ["论文撰写", "文献综述", "方法描述", "结果报告"],
        "description": "负责研究论文和报告的撰写"
    },
    "protocol_designer": {
        "name": "研究方案设计师",
        "capabilities": ["研究设计", "样本量计算", "伦理考量", "方案撰写"],
        "description": "负责研究方案的设计和撰写"
    },
    "data_manager": {
        "name": "数据管理员",
        "capabilities": ["数据清洗", "质量控制", "数据安全", "文档管理"],
        "description": "负责研究数据的管理和质量控制"
    },
    "project_coordinator": {
        "name": "项目协调员",
        "capabilities": ["任务分配", "进度跟踪", "团队协调", "报告生成"],
        "description": "负责多Agent项目的协调和管理"
    }
}

# 示例使用
def setup_medical_research_system():
    """设置医疗研究多Agent系统"""
    system = FileBasedAgentSystem(base_dir="~/Desktop/medical_multiagent")
    
    # 注册医疗研究Agent
    for agent_id, agent_info in MEDICAL_AGENTS.items():
        system.register_agent(
            agent_id=agent_id,
            agent_type=agent_info["name"],
            capabilities=agent_info["capabilities"]
        )
    
    print("✅ 医疗研究多Agent系统已设置")
    print(f"系统目录: {system.base_dir}")
    print(f"注册Agent数: {len(system.agents)}")
    
    return system

def create_medical_research_tasks(system):
    """创建医疗研究任务示例"""
    tasks = [
        {
            "id": "task_001",
            "description": "分析糖尿病患者的运动习惯与脑卒中风险关系",
            "requirements": ["临床数据分析", "生存分析", "风险比计算"],
            "priority": "high"
        },
        {
            "id": "task_002",
            "description": "撰写冠心病运动研究论文的统计方法部分",
            "requirements": ["统计方法描述", "R代码文档", "图表说明"],
            "priority": "medium"
        },
        {
            "id": "task_003",
            "description": "设计新的糖尿病预防研究方案",
            "requirements": ["研究设计", "样本量计算", "伦理考量"],
            "priority": "medium"
        }
    ]
    
    for task in tasks:
        system.create_task(
            task_id=task["id"],
            description=task["description"],
            requirements=task["requirements"],
            priority=task["priority"]
        )
    
    print(f"✅ 已创建 {len(tasks)} 个医疗研究任务")

if __name__ == "__main__":
    # 设置系统
    system = setup_medical_research_system()
    
    # 创建示例任务
    create_medical_research_tasks(system)
    
    # 显示系统状态
    status = system.get_system_status()
    print("\n📊 系统状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")