from io import BytesIO
import base64

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus


GROUP_FIELDS = {
    "status": Task.status,
    "topic": Task.topic,
    "assignee": Task.assignee_id,
}


def build_task_dataframe(db: Session) -> pd.DataFrame:
    tasks = db.query(Task).all()
    data = [
        {
            "status": task.status.value if isinstance(task.status, TaskStatus) else task.status,
            "topic": task.topic or "Unspecified",
            "assignee": task.assignee_id or 0,
        }
        for task in tasks
    ]
    return pd.DataFrame(data)


def compute_group_stats(df: pd.DataFrame, group_by: str) -> list[dict]:
    if df.empty:
        return []
    grouped = df.groupby(group_by).size().reset_index(name="count")
    return grouped.to_dict(orient="records")


def build_chart(grouped: list[dict], group_by: str) -> str | None:
    if not grouped:
        return None
    chart_df = pd.DataFrame(grouped)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=chart_df, x=group_by, y="count", ax=ax)
    ax.set_title(f"Tasks by {group_by}")
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
