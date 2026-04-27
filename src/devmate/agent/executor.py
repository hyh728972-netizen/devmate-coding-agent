import logging

from devmate.agent.runtime import run_agent

logger = logging.getLogger(__name__)


def executor_loop():

    goal = input("请输入你的开发任务需求：\n> ")

    logger.info("智能体运行已启动")

    result = run_agent(goal)

    logger.info("任务执行已完成")
    logger.info("\n===== Agent 回答 =====\n")
    logger.info(result.get("answer", ""))


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    executor_loop()
