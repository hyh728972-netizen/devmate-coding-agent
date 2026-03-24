from langsmith import traceable


@traceable(name="intent_router")
def detect_task_type(goal: str) -> str:
    text = goal.lower().strip()

    coding_keywords = [
        "做一个", "写一个", "开发", "实现", "创建", "生成",
        "build", "create", "develop", "implement", "code", "website", "网站", "页面"
    ]
    qa_keywords = [
        "是什么", "有哪些", "什么意思", "由什么组成", "架构", "规范", "文档"
    ]
    search_keywords = [
        "最新", "趋势", "搜索", "查一下", "news", "latest", "trend"
    ]
    file_keywords = [
        "修改", "阅读", "查看文件", "项目结构", "read file", "list tree", "main.py"
    ]

    if any(k in text for k in coding_keywords):
        return "DEV_TASK"

    if any(k in text for k in qa_keywords):
        return "QA_LOCAL"

    if any(k in text for k in search_keywords):
        return "QA_WEB"

    if any(k in text for k in file_keywords):
        return "FILE_OP"

    return "QA_LOCAL"


# ⭐⭐⭐⭐⭐ 对外统一 Router API
@traceable(name="intent_route_entry")
def route_intent(goal: str) -> str:
    return detect_task_type(goal)