from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from phase02.shared.llm_gemini import GeminiProvider
from phase05.clustering.assigner import IncrementalClusterAssigner, aggregate_cluster_stats
from phase05.clustering.clusterer import ReviewClusterer
from phase05.clustering.labeler import ClusterLabeler
from phase05.database.repositories import ClusterRepository, InsightRepository
from phase05.insights.indexer import InsightIndexer
from phase05.insights.reporter import InsightReporter
from phase05.insights.root_cause import RootCauseSynthesizer
from phase05.shared.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ClusterRunReport:
    vectors_loaded: int = 0
    clusters_created: int = 0
    memberships: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "vectors_loaded": self.vectors_loaded,
            "clusters_created": self.clusters_created,
            "memberships": self.memberships,
            "errors": self.errors,
        }


class ClusteringPipeline:
    def __init__(self, session: Session, llm: GeminiProvider | None = None):
        self.session = session
        self.repo = ClusterRepository(session)
        self.clusterer = ReviewClusterer()
        self.labeler = ClusterLabeler(llm)
        self.root_cause = RootCauseSynthesizer(llm)

    def run_full(self, *, vector_limit: int | None = None) -> ClusterRunReport:
        report = ClusterRunReport()
        try:
            points = self.clusterer.load_vectors(limit=vector_limit)
            report.vectors_loaded = len(points)
            if not points:
                report.errors.append("No vectors found in Qdrant; run Phase 3 embed first")
                return report

            assignments = self.clusterer.fit(points)
            stats_by_label = aggregate_cluster_stats(assignments, points)
            self.repo.clear_all()

            for label, stats in stats_by_label.items():
                if label < 0:
                    cluster_key = f"noise_{abs(label)}"
                else:
                    cluster_key = f"cluster_{label:02d}"

                label_info = self.labeler.label_cluster(
                    stats.get("sample_texts", []),
                    primary_issues=[i or "" for i in stats.get("primary_issues", [])],
                )
                cluster = self.repo.upsert_cluster(
                    cluster_key,
                    {
                        "label": label_info["label"],
                        "description": label_info["description"],
                        "taxonomy_theme_id": label_info.get("taxonomy_theme_id"),
                        "member_count": stats["member_count"],
                        "avg_rating": stats.get("avg_rating"),
                        "avg_thumbs_up": stats.get("avg_thumbs_up"),
                        "top_subscription_types": stats.get("top_subscription_types"),
                        "top_device_types": stats.get("top_device_types"),
                        "representative_review_ids": stats.get("representative_review_ids"),
                        "centroid": stats.get("centroid"),
                        "stats": stats,
                    },
                )
                report.clusters_created += 1

                for review_id in [p.review_id for p in points if assignments.get(p.review_id) == label]:
                    self.repo.add_membership(cluster.id, uuid.UUID(review_id))
                    self.repo.mark_review_clustered(uuid.UUID(review_id))
                    report.memberships += 1

                synthesis = self.root_cause.synthesize(
                    cluster.label,
                    stats.get("sample_texts", []),
                    evidence_ids=stats.get("representative_review_ids", []),
                )
                cluster.description = synthesis.get("summary") or cluster.description

            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            report.errors.append(str(exc))
            logger.exception("Clustering pipeline failed")
        return report


class InsightsPipeline:
    def __init__(self, session: Session):
        self.session = session
        self.reporter = InsightReporter(session)
        self.indexer = InsightIndexer()

    def run(self) -> dict:
        report = self.reporter.build_weekly_report()
        saved = self.reporter.persist_insights(report)
        self.indexer.index_batch(saved)
        self.session.commit()
        return {
            "insights_saved": len(saved),
            "report": report.to_dict(),
        }


class IncrementalPipeline:
    def __init__(self, session: Session):
        self.session = session
        self.assigner = IncrementalClusterAssigner(session)

    def run(self, *, limit: int = 200) -> dict:
        assigned = self.assigner.assign_pending(limit=limit)
        return {"assigned": assigned}
