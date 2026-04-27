#!/usr/bin/env python3
"""
Medical Multi-Agent — 多智能体医学研究平台
5个AI Agent协作完成医学研究：文献检索、方法学设计、数据分析、论文写作、审稿
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Medical Multi-Agent API",
    description="多智能体医学研究平台 — 5个AI Agent协作完成医学研究",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class AgentRole(str, Enum):
    LITERATURE = "literature"      # 文献检索Agent
    METHODOLOGY = "methodology"    # 方法学设计Agent
    DATA_ANALYSIS = "data_analysis"  # 数据分析Agent
    WRITING = "writing"            # 论文写作Agent
    REVIEW = "review"              # 审稿Agent

class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"

class AgentInfo(BaseModel):
    id: str
    role: AgentRole
    name: str
    description: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE

class TaskRequest(BaseModel):
    topic: str = Field(..., description="研究主题")
    research_type: str = Field("systematic_review", description="研究类型")
    requirements: Optional[Dict[str, Any]] = Field(None, description="特殊要求")

class TaskStatus(BaseModel):
    task_id: str
    topic: str
    status: str
    progress: float
    agents: Dict[str, str]
    created_at: str
    results: Optional[Dict[str, Any]] = None


# ==================== Agent 定义 ====================

AGENTS = {
    "agent_literature": AgentInfo(
        id="agent_literature",
        role=AgentRole.LITERATURE,
        name="文献检索Agent",
        description="负责PubMed、CNKI等数据库文献检索和筛选",
        capabilities=["pubmed_search", "cnki_search", "citation_analysis", "prisma_flow"]
    ),
    "agent_methodology": AgentInfo(
        id="agent_methodology",
        role=AgentRole.METHODOLOGY,
        name="方法学设计Agent",
        description="负责研究方案设计、统计方法选择、样本量计算",
        capabilities=["study_design", "sample_size", "statistical_method", "bias_assessment"]
    ),
    "agent_data": AgentInfo(
        id="agent_data",
        role=AgentRole.DATA_ANALYSIS,
        name="数据分析Agent",
        description="负责数据清洗、统计分析、图表生成",
        capabilities=["data_cleaning", "statistical_test", "meta_analysis", "forest_plot"]
    ),
    "agent_writing": AgentInfo(
        id="agent_writing",
        role=AgentRole.WRITING,
        name="论文写作Agent",
        description="负责论文各章节撰写、格式规范",
        capabilities=["abstract_writing", "introduction", "methods", "results", "discussion"]
    ),
    "agent_review": AgentInfo(
        id="agent_review",
        role=AgentRole.REVIEW,
        name="审稿Agent",
        description="负责论文质量审核、语言润色、格式检查",
        capabilities=["quality_check", "language_edit", "format_check", "reference_check"]
    )
}

# 任务存储
tasks: Dict[str, TaskStatus] = {}


# ==================== API 端点 ====================

@app.get("/")
async def root():
    return {
        "service": "Medical Multi-Agent",
        "version": "1.0.0",
        "description": "多智能体医学研究平台",
        "agents": len(AGENTS),
        "endpoints": {
            "health": "/health",
            "agents": "/api/v1/agents",
            "create_task": "POST /api/v1/tasks",
            "task_status": "/api/v1/tasks/{task_id}"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "medical-multiagent",
        "timestamp": datetime.now().isoformat(),
        "agents_available": len(AGENTS),
        "active_tasks": len([t for t in tasks.values() if t.status == "in_progress"])
    }

@app.get("/api/v1/agents", response_model=List[AgentInfo])
async def list_agents():
    """获取所有Agent信息"""
    return list(AGENTS.values())

@app.get("/api/v1/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """获取单个Agent信息"""
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return AGENTS[agent_id]

@app.post("/api/v1/tasks", response_model=TaskStatus)
async def create_task(request: TaskRequest):
    """创建研究任务 — 5个Agent协作完成"""
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    # 初始化任务状态
    task = TaskStatus(
        task_id=task_id,
        topic=request.topic,
        status="in_progress",
        progress=0.0,
        agents={role.value: "pending" for role in AgentRole},
        created_at=datetime.now().isoformat(),
        results={
            "research_type": request.research_type,
            "requirements": request.requirements,
            "workflow": [
                {"step": 1, "agent": "literature", "task": "文献检索与筛选", "status": "pending"},
                {"step": 2, "agent": "methodology", "task": "研究方案设计", "status": "pending"},
                {"step": 3, "agent": "data_analysis", "task": "数据统计分析", "status": "pending"},
                {"step": 4, "agent": "writing", "task": "论文撰写", "status": "pending"},
                {"step": 5, "agent": "review", "task": "质量审核", "status": "pending"}
            ]
        }
    )
    
    tasks[task_id] = task
    return task

@app.get("/api/v1/tasks", response_model=List[TaskStatus])
async def list_tasks():
    """获取所有任务"""
    return list(tasks.values())

@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return tasks[task_id]

@app.post("/api/v1/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """执行任务 — 模拟Agent协作流程"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task = tasks[task_id]
    task.status = "completed"
    task.progress = 100.0
    
    # 更新所有Agent状态
    for role in AgentRole:
        task.agents[role.value] = "completed"
    
    # 更新工作流
    for step in task.results["workflow"]:
        step["status"] = "completed"
    
    # 添加模拟结果
    task.results["output"] = {
        "title": f"{task.topic}的系统评价与Meta分析",
        "abstract": f"本研究对{task.topic}进行了系统评价...",
        "literature_found": 156,
        "literature_included": 23,
        "conclusion": f"基于{23}项研究的Meta分析表明..."
    }
    
    return {"message": "Task completed", "task_id": task_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
