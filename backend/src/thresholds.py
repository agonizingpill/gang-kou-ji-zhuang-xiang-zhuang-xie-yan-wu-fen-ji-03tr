"""置信门槛的纯逻辑判定：版本选择、受理绑定与分级裁决。

路由与 worker 共用这个模块，保证三条规则只有一份实现：
- 分级受理时绑定当时生效的门槛版本；
- 推理失败重试不换版本（绑定只在首次受理时发生）；
- 撤回门槛只影响之后新受理的分级（已受理案件用绑定快照判断）。
"""

LEVELS = ("normal", "watch", "major", "critical")

PUBLISHED = "published"
WITHDRAWN = "withdrawn"

# 案件状态
STATUS_REVIEW = "review"  # 置信度低于门槛，待主管核级
STATUS_FAILED = "failed"  # 推理失败，可按原门槛版本重试
DISPATCHABLE_STATUSES = {"classified", "dispatched"}


def next_version(versions):
    """versions: 已存在的版本号列表，返回下一次发布的版本号。"""
    return max(versions, default=0) + 1


def effective_version(rows):
    """rows: (version, status) 序列，返回当前生效的版本号。

    最新一条仍为 published 的版本生效；撤回当前版本后次新的已发布版本
    自动恢复生效；全部撤回则不设门槛（None）。
    """
    published = [version for version, status in rows if status == PUBLISHED]
    return max(published, default=None)


def evaluate(confidence, threshold_value):
    """分级裁决：未设门槛或置信度达到门槛 -> classified，否则 -> review。"""
    if threshold_value is None or confidence >= threshold_value:
        return "classified"
    return STATUS_REVIEW


def dispatchable_levels(status, final_level):
    """本案当前可派工的等级：分级生效（达标或主管核级通过）后才可派工。"""
    if status in DISPATCHABLE_STATUSES and final_level:
        return [final_level]
    return []
