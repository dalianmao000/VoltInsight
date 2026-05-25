# Project: VoltInsight Research Assistant

## 目标
构建以 Claude Code 为基座的汽车与电池材料研究助理 AI 系统

## 核心流程
新闻监控 → 数据更新 → 快评生成 → 审批 → 归档

## 技术栈
- Claude Code / Claude API
- Python 3.11+
- ChromaDB (向量库)
- Obsidian (笔记)
- LangGraph (工作流编排)
- APScheduler (定时调度)
- SQLAlchemy (数据库)

## 关键约定
- 所有计算通过 Python 代码执行，LLM 仅负责逻辑描述
- 敏感内容需人工审批后才能发布
- 数据源 MCP 配置外置，支持按需切换

## Skills
- `/research` - 新闻监控与快评
- `/data` - 数据更新与校验
- `/report` - 报告生成
- `/review` - 内容审查