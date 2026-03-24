import json
import logging
from pathlib import Path

from devmate.agent.runtime import run_agent

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def save_generated_files(plan: dict):

    files = plan.get("files_to_create", [])

    for file in files:
        file_path = PROJECT_ROOT / file
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# 由 DevMate 自动生成\n")

        logger.info("已创建文件：%s", file_path)


def executor_loop():

    goal = input("请输入你的开发任务需求：\n> ")

    logger.info("智能体运行已启动")

    result = run_agent(goal)

    logger.info("任务规划已完成")

    if "answer" in result:
        logger.info("\n===== Agent 回答 =====\n")
        logger.info(result["answer"])
        return

    save_generated_files(result)

    logger.info("任务执行成功完成")


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    executor_loop()