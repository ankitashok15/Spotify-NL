from __future__ import annotations

import json
from dataclasses import dataclass

from sqlalchemy.orm import Session

from phase05.database.repositories import InsightRepository
from phase05.insights.aggregator import ComplaintAggregator
from phase05.insights.emerging import EmergingIssuesDetector
from phase05.insights.opportunities import OpportunityFinder
from phase05.insights.root_cause import RootCauseSynthesizer
from phase05.insights.trends import TrendAnalyzer


@dataclass
class WeeklyReport:
    top_complaints: list[dict]
    emerging_issues: list[dict]
    feature_requests: list[dict]
    segment_analysis: list[dict]
    trends: list[dict]

    def to_dict(self) -> dict:
        return {
            "top_complaints": self.top_complaints,
            "emerging_issues": self.emerging_issues,
            "feature_requests": self.feature_requests,
            "segment_analysis": self.segment_analysis,
            "trends": self.trends,
        }


class InsightReporter:
    def __init__(self, session: Session):
        self.session = session
        self.insights = InsightRepository(session)
        self.aggregator = ComplaintAggregator(session)
        self.emerging = EmergingIssuesDetector(session)
        self.opportunities = OpportunityFinder(session)
        self.trends = TrendAnalyzer(session)
        self.root_cause = RootCauseSynthesizer()

    def build_weekly_report(self) -> WeeklyReport:
        return WeeklyReport(
            top_complaints=self.aggregator.top_complaints(),
            emerging_issues=self.emerging.detect(),
            feature_requests=self.opportunities.feature_request_frequency(),
            segment_analysis=self.aggregator.segment_breakdown(),
            trends=self.trends.issue_time_series(),
        )

    def persist_insights(self, report: WeeklyReport) -> list:
        saved = []
        for row in report.top_complaints[:10]:
            saved.append(
                self.insights.save(
                    {
                        "insight_type": "top_complaint",
                        "title": f"Top issue: {row['primary_issue']}",
                        "summary": f"{row['review_count']} reviews, avg rating {row['avg_rating']}",
                        "confidence": float(row.get("avg_confidence") or 0.7),
                        "evidence_document_ids": [],
                        "payload": row,
                    }
                )
            )
        for row in report.emerging_issues[:10]:
            saved.append(
                self.insights.save(
                    {
                        "insight_type": "emerging_issue",
                        "title": f"Emerging: {row['primary_issue']}",
                        "summary": f"Growth rate {round((row['growth_rate'] or 0) * 100, 1)}% over prior window",
                        "confidence": 0.75,
                        "evidence_document_ids": [],
                        "payload": row,
                    }
                )
            )
        for row in report.feature_requests[:10]:
            saved.append(
                self.insights.save(
                    {
                        "insight_type": "feature_request",
                        "title": f"Feature request: {row['feature_request']}",
                        "summary": f"Mentioned {row['mention_count']} times",
                        "confidence": 0.8,
                        "evidence_document_ids": [],
                        "payload": row,
                    }
                )
            )

        weekly = self.insights.save(
            {
                "insight_type": "weekly_report",
                "title": "Weekly discovery insights report",
                "summary": json.dumps(report.to_dict())[:4000],
                "confidence": 0.85,
                "evidence_document_ids": [],
                "payload": report.to_dict(),
            }
        )
        saved.append(weekly)
        return saved
