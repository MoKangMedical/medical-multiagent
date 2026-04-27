#!/usr/bin/env python3
# 简化版多Agent系统实现
# 基于文件系统的Agent协作

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
        "name": "Clinical Analyst",
        "capabilities": ["data_analysis", "statistical_testing", "result_interpretation", "chart_generation"],
        "description": "Responsible for statistical analysis and interpretation of clinical data"
    },
    "medical_writer": {
        "name": "Medical Writer",
        "capabilities": ["paper_writing", "literature_review", "method_description", "result_reporting"],
        "description": "Responsible for writing research papers and reports"
    },
    "protocol_designer": {
        "name": "Protocol Designer",
        "capabilities": ["study_design", "sample_size_calculation", "ethical_considerations", "protocol_writing"],
        "description": "Responsible for designing and writing research protocols"
    },
    "data_manager": {
        "name": "Data Manager",
        "capabilities": ["data_cleaning", "quality_control", "data_security", "document_management"],
        "description": "Responsible for research data management and quality control"
    },
    "project_coordinator": {
        "name": "Project Coordinator",
        "capabilities": ["task_assignment", "progress_tracking", "team_coordination", "report_generation"],
        "description": "Responsible for coordinating and managing multi-agent projects"
    }
}

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
    
    print("Medical research multi-agent system setup complete")
    print(f"System directory: {system.base_dir}")
    print(f"Registered agents: {len(system.agents)}")
    
    return system

def create_medical_research_tasks(system):
    """创建医疗研究任务示例"""
    tasks = [
        {
            "id": "task_001",
            "description": "Analyze the relationship between exercise habits and stroke risk in diabetic patients",
            "requirements": ["clinical_data_analysis", "survival_analysis", "risk_ratio_calculation"],
            "priority": "high"
        },
        {
            "id": "task_002",
            "description": "Write the statistical methods section for the coronary heart disease exercise study paper",
            "requirements": ["statistical_method_description", "R_code_documentation", "chart_explanation"],
            "priority": "medium"
        },
        {
            "id": "task_003",
            "description": "Design a new diabetes prevention research protocol",
            "requirements": ["study_design", "sample_size_calculation", "ethical_considerations"],
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
    
    print(f"Created {len(tasks)} medical research tasks")

def main():
    """主函数"""
    print("=== Simplified Multi-Agent System Setup ===")
    
    # 设置系统
    system = setup_medical_research_system()
    
    # 创建示例任务
    create_medical_research_tasks(system)
    
    # 分配任务示例
    system.assign_task("task_001", "clinical_analyst")
    system.assign_task("task_002", "medical_writer")
    system.assign_task("task_003", "protocol_designer")
    
    # 提交结果示例
    system.submit_result("task_001", "clinical_analyst", {
        "analysis": "Completed survival analysis",
        "findings": "Regular exercise associated with 25% lower stroke risk",
        "charts": ["km_curve.png", "forest_plot.png"]
    })
    
    # 显示系统状态
    status = system.get_system_status()
    print("\nSystem Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 保存状态报告
    report_file = os.path.join(system.base_dir, "system_status_report.json")
    with open(report_file, "w") as f:
        json.dump(status, f, indent=2)
    
    print(f"\nStatus report saved to: {report_file}")
    print("\n=== System Setup Complete ===")

if __name__ == "__main__":
    main()