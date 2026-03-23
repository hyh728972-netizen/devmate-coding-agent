from devmate.agent.planner import plan_task

import logging
logger = logging.getLogger(__name__)

def run_coding_agent(user_request: str):
    logger.info("Planning task started")

    plan = plan_task(user_request)

    logger.info("Plan generated: %s", plan)

    # 未来这里会加
    # tool calling
    # rag search
    # code execution

    return plan