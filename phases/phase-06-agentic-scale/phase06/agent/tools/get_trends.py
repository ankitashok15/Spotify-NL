from __future__ import annotations

from sqlalchemy.orm import Session

from phase05.insights.trends import TrendAnalyzer
from phase06.agent.tools.base import AgentTool


class GetTrendsTool(AgentTool):
    name = "get_trends"
    description = "Time-series review counts for issues or clusters."

    def __init__(self, session: Session) -> None:
        self.session = session
        self.analyzer = TrendAnalyzer(session)

    def run(self, args: dict) -> dict:
        months = int(args.get("months", 6))
        primary_issue = args.get("primary_issue")
        issue_series = self.analyzer.issue_time_series(months=months)
        cluster_series = self.analyzer.cluster_time_series(months=months)

        if primary_issue:
            issue_series = [row for row in issue_series if row.get("primary_issue") == primary_issue]

        return {
            "months": months,
            "primary_issue_filter": primary_issue,
            "issue_series": issue_series,
            "cluster_series": cluster_series[:50],
        }
