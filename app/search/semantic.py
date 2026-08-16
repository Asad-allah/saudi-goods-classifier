from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.catalog.models import Catalog, SearchTerm
from app.search.models import CandidateHit

logger = logging.getLogger(__name__)


class SemanticUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class SemanticDocument:
    root_good_type_id: int
    source_good_type_id: int
    source_type: str
    matched_term: str
    is_cross_root_ambiguous: bool
    is_cross_good_type_ambiguous: bool
    text: str


class BaseSemanticRetriever:
    model_version = "semantic-disabled"

    def is_available(self) -> bool:
        return False

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        return []


class RemoteSemanticRetriever(BaseSemanticRetriever):
    """Delegates dense Dual-Stream semantic vector search to a remote Colab GPU microservice."""

    def __init__(self, remote_url: str, model_version: str = "dual-stream@colab-gpu") -> None:
        self.remote_url = remote_url.rstrip("/") if remote_url else ""
        self.model_version = model_version

    def is_available(self) -> bool:
        return bool(self.remote_url)

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self.remote_url:
            return []
        import urllib.request
        try:
            url = f"{self.remote_url}/semantic/search"
            payload = json.dumps({"query": query, "top_k": top_k}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "SaudiGoodsClassifier-Render/1.0"},
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = []
                for item in data.get("hits", []):
                    hits.append(
                        CandidateHit(
                            root_good_type_id=int(item["root_good_type_id"]),
                            source_good_type_id=int(item.get("source_good_type_id", item["root_good_type_id"])),
                            rank=int(item["rank"]),
                            score=float(item["score"]),
                            method="SEMANTIC",
                            matched_term=str(item.get("matched_term", "")),
                            is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                            is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        )
                    )
                return hits
        except Exception as exc:
            logger.warning("Remote semantic call to Colab failed (%s); continuing with exact/fuzzy", exc)
            return []


class SentenceTransformerRetriever(BaseSemanticRetriever):
    """Dual-Stream Semantic Retriever: Fuses Concept Core vectors + Deep Trade Evidence vectors."""

    def __init__(
        self,
        catalog: Catalog,
        *,
        model_name: str,
        cache_root: Path | None = None,
    ) -> None:
        try:
            import torch
            torch.set_num_threads(1)
            torch.set_grad_enabled(False)
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise SemanticUnavailable("sentence-transformers is not installed") from exc

        self.catalog = catalog
        sem_dir = cache_root
        if sem_dir is None:
            candidate_sem_dir = Path(__file__).resolve().parent.parent.parent / "storage" / "semantic"
            if candidate_sem_dir.exists():
                sem_dir = candidate_sem_dir
            else:
                sem_dir = Path("storage") / "semantic"

        # File paths
        concept_idx_path = sem_dir / "catalog_concept_faiss.index"
        concept_meta_path = sem_dir / "catalog_concept_metadata.json"
        evidence_idx_path = sem_dir / "catalog_evidence_faiss.index"
        evidence_meta_path = sem_dir / "catalog_evidence_metadata.json"

        # Fallback to single index if dual is not yet generated
        if not evidence_idx_path.exists():
            evidence_idx_path = sem_dir / "catalog_faiss.index"
            evidence_meta_path = sem_dir / "catalog_faiss_metadata.json"

        self._concept_index = None
        self._concept_docs = []
        self._evidence_index = None
        self._evidence_docs = []

        import faiss

        # 1. Load Concept Stream (Stream 1)
        if concept_idx_path.exists() and concept_meta_path.exists():
            try:
                self._concept_index = faiss.read_index(str(concept_idx_path))
                with open(concept_meta_path, "r", encoding="utf-8") as f:
                    self._concept_docs = json.load(f)
                logger.info("Loaded Stream 1 (Concept FAISS Index) with %d classes", len(self._concept_docs))
            except Exception as exc:
                logger.warning("Could not load Concept FAISS index: %s", exc)

        # 2. Load Evidence Stream (Stream 2)
        if evidence_idx_path.exists() and evidence_meta_path.exists():
            try:
                self._evidence_index = faiss.read_index(str(evidence_idx_path))
                with open(evidence_meta_path, "r", encoding="utf-8") as f:
                    raw_meta = json.load(f)
                self._evidence_docs = [
                    SemanticDocument(
                        root_good_type_id=int(item["root_good_type_id"]),
                        source_good_type_id=int(item["source_good_type_id"]),
                        source_type=str(item.get("source_type", "EVIDENCE")),
                        matched_term=str(item["matched_term"]),
                        is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                        is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        text=str(item["text"]),
                    )
                    for item in raw_meta
                ]
                logger.info("Loaded Stream 2 (Evidence FAISS Index) with %d trade vectors", len(self._evidence_docs))
            except Exception as exc:
                logger.warning("Could not load Evidence FAISS index: %s", exc)

        # Detect model from metadata if available
        detected_model = model_name
        if self._concept_docs and "embedding_model" in self._concept_docs[0]:
            detected_model = self._concept_docs[0]["embedding_model"]

        self.model_version = f"dual-stream-{_clean_label(detected_model)}"
        self._model = SentenceTransformer(detected_model)

    def is_available(self) -> bool:
        return self._evidence_index is not None or self._concept_index is not None

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self.is_available():
            return []

        # 1. Encode query
        query_vec = self._encode_query(query)
        query_vec = _normalize(query_vec.reshape(1, -1))[0]
        q_arr = np.asarray([query_vec], dtype=np.float32)

        # 2. STREAM 1: Evaluate Pure Concept Scores across all 90 canonical categories
        concept_scores: dict[int, float] = {}  # leaf_id -> cosine score
        leaf_to_root: dict[int, int] = {}
        leaf_to_name: dict[int, str] = {}

        if self._concept_index is not None and self._concept_docs:
            k_concept = min(len(self._concept_docs), 90)
            scores_c, indices_c = self._concept_index.search(q_arr, k_concept)
            for idx, sc in zip(indices_c[0], scores_c[0]):
                if idx >= 0:
                    doc = self._concept_docs[idx]
                    leaf_id = doc["source_good_type_id"]
                    concept_scores[leaf_id] = float(sc)
                    leaf_to_root[leaf_id] = doc["root_good_type_id"]
                    leaf_to_name[leaf_id] = doc.get("name_ar", "")

        # 3. STREAM 2: Evaluate Deep Evidence Scores (Trade Terms, Cultivars, Brands)
        evidence_best_score: dict[int, float] = {}
        evidence_best_term: dict[int, str] = {}

        if self._evidence_index is not None and self._evidence_docs:
            k_evidence = min(len(self._evidence_docs), 40)
            scores_e, indices_e = self._evidence_index.search(q_arr, k_evidence)
            for idx, sc in zip(indices_e[0], scores_e[0]):
                if idx >= 0:
                    edoc = self._evidence_docs[idx]
                    leaf_id = edoc.source_good_type_id
                    sc_f = float(sc)
                    leaf_to_root[leaf_id] = edoc.root_good_type_id
                    if leaf_id not in evidence_best_score or sc_f > evidence_best_score[leaf_id]:
                        evidence_best_score[leaf_id] = sc_f
                        evidence_best_term[leaf_id] = edoc.matched_term

        # 4. WEIGHTED DUAL-STREAM FUSION
        all_candidate_leaves = set(concept_scores.keys()) | set(evidence_best_score.keys())
        scored_candidates: list[dict] = []

        w_evidence = 0.65
        w_concept = 0.35

        for leaf_id in all_candidate_leaves:
            s_concept = concept_scores.get(leaf_id, 0.0)
            s_evidence = evidence_best_score.get(leaf_id, None)
            matched_term = evidence_best_term.get(leaf_id, leaf_to_name.get(leaf_id, ""))

            if s_evidence is not None:
                # Both streams available: Adaptive Late Fusion with Synergy Boost
                fused_score = (w_evidence * s_evidence) + (w_concept * s_concept)
                
                # Synergistic reinforcement when both concept and evidence agree
                if s_evidence >= 0.80 and s_concept >= 0.40:
                    fused_score += 0.03 * (s_evidence * s_concept)
            else:
                # Only concept stream
                fused_score = s_concept * 0.88

            root_id = leaf_to_root.get(leaf_id, leaf_id)
            scored_candidates.append({
                "source_good_type_id": leaf_id,
                "root_good_type_id": root_id,
                "score": float(np.clip(fused_score, 0.0, 1.0)),
                "matched_term": matched_term,
            })

        # 5. Sort candidates by fused score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        hits: list[CandidateHit] = []
        for rank, c in enumerate(scored_candidates[:top_k], start=1):
            hits.append(
                CandidateHit(
                    root_good_type_id=c["root_good_type_id"],
                    source_good_type_id=c["source_good_type_id"],
                    rank=rank,
                    score=c["score"],
                    method="SEMANTIC",
                    matched_term=c["matched_term"],
                    is_cross_root_ambiguous=False,
                    is_cross_good_type_ambiguous=False,
                )
            )
        return hits

    def _encode_query(self, query: str) -> np.ndarray:
        is_e5 = "e5" in self.model_version.lower()
        q = query if (not is_e5 or query.startswith("query: ")) else f"query: {query}"
        if hasattr(self._model, "encode_query"):
            return np.asarray(self._model.encode_query(q, convert_to_numpy=True))
        return np.asarray(self._model.encode(q, convert_to_numpy=True))


class GeminiSemanticRetriever(BaseSemanticRetriever):
    """Dual-Stream Semantic Retriever powered by Google Gemini Embeddings API."""

    def __init__(self, catalog: Catalog, api_key: str = "", cache_root: Path | None = None) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            raise SemanticUnavailable("GEMINI_API_KEY is not set")

        self.model_version = "dual-stream-google-gemini"
        self._concept_index = None
        self._concept_docs = []
        self._evidence_index = None
        self._evidence_docs = []

        sem_dir = cache_root or (Path(__file__).resolve().parent.parent.parent / "storage" / "semantic")
        concept_idx_path = sem_dir / "catalog_concept_faiss.index"
        concept_meta_path = sem_dir / "catalog_concept_metadata.json"
        evidence_idx_path = sem_dir / "catalog_evidence_faiss.index"
        evidence_meta_path = sem_dir / "catalog_evidence_metadata.json"

        if not evidence_idx_path.exists():
            evidence_idx_path = sem_dir / "catalog_faiss.index"
            evidence_meta_path = sem_dir / "catalog_faiss_metadata.json"

        import faiss

        if concept_idx_path.exists() and concept_meta_path.exists():
            try:
                self._concept_index = faiss.read_index(str(concept_idx_path))
                with open(concept_meta_path, "r", encoding="utf-8") as f:
                    self._concept_docs = json.load(f)
            except Exception:
                pass

        if evidence_idx_path.exists() and evidence_meta_path.exists():
            try:
                self._evidence_index = faiss.read_index(str(evidence_idx_path))
                with open(evidence_meta_path, "r", encoding="utf-8") as f:
                    raw_meta = json.load(f)
                self._evidence_docs = [
                    SemanticDocument(
                        root_good_type_id=int(item["root_good_type_id"]),
                        source_good_type_id=int(item["source_good_type_id"]),
                        source_type=str(item.get("source_type", "EVIDENCE")),
                        matched_term=str(item["matched_term"]),
                        is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                        is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        text=str(item["text"]),
                    )
                    for item in raw_meta
                ]
            except Exception:
                pass

    def is_available(self) -> bool:
        return self._evidence_index is not None or self._concept_index is not None

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self.is_available():
            return []
        import urllib.request
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
            payload = {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": query}]},
                "taskType": "RETRIEVAL_QUERY",
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            
            vec = np.array([result["embedding"]["values"]], dtype=np.float32)
            norm = np.linalg.norm(vec, axis=1, keepdims=True)
            norm[norm == 0] = 1.0
            query_vec = vec / norm
            q_arr = np.asarray(query_vec, dtype=np.float32)

            concept_scores: dict[int, float] = {}
            leaf_to_root: dict[int, int] = {}
            leaf_to_name: dict[int, str] = {}

            if self._concept_index is not None and self._concept_docs:
                k_concept = min(len(self._concept_docs), 90)
                scores_c, indices_c = self._concept_index.search(q_arr, k_concept)
                for idx, sc in zip(indices_c[0], scores_c[0]):
                    if idx >= 0:
                        doc = self._concept_docs[idx]
                        leaf_id = doc["source_good_type_id"]
                        concept_scores[leaf_id] = float(sc)
                        leaf_to_root[leaf_id] = doc["root_good_type_id"]
                        leaf_to_name[leaf_id] = doc.get("name_ar", "")

            evidence_best_score: dict[int, float] = {}
            evidence_best_term: dict[int, str] = {}

            if self._evidence_index is not None and self._evidence_docs:
                k_evidence = min(len(self._evidence_docs), 40)
                scores_e, indices_e = self._evidence_index.search(q_arr, k_evidence)
                for idx, sc in zip(indices_e[0], scores_e[0]):
                    if idx >= 0:
                        edoc = self._evidence_docs[idx]
                        leaf_id = edoc.source_good_type_id
                        sc_f = float(sc)
                        leaf_to_root[leaf_id] = edoc.root_good_type_id
                        if leaf_id not in evidence_best_score or sc_f > evidence_best_score[leaf_id]:
                            evidence_best_score[leaf_id] = sc_f
                            evidence_best_term[leaf_id] = edoc.matched_term

            all_candidate_leaves = set(concept_scores.keys()) | set(evidence_best_score.keys())
            scored_candidates: list[dict] = []

            for leaf_id in all_candidate_leaves:
                s_concept = concept_scores.get(leaf_id, 0.0)
                s_evidence = evidence_best_score.get(leaf_id, None)
                matched_term = evidence_best_term.get(leaf_id, leaf_to_name.get(leaf_id, ""))

                if s_evidence is not None:
                    fused_score = (0.65 * s_evidence) + (0.35 * s_concept)
                    if s_evidence >= 0.80 and s_concept >= 0.40:
                        fused_score += 0.03 * (s_evidence * s_concept)
                else:
                    fused_score = s_concept * 0.88

                root_id = leaf_to_root.get(leaf_id, leaf_id)
                scored_candidates.append({
                    "source_good_type_id": leaf_id,
                    "root_good_type_id": root_id,
                    "score": float(np.clip(fused_score, 0.0, 1.0)),
                    "matched_term": matched_term,
                })

            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            hits: list[CandidateHit] = []
            for rank, c in enumerate(scored_candidates[:top_k], start=1):
                hits.append(
                    CandidateHit(
                        root_good_type_id=c["root_good_type_id"],
                        source_good_type_id=c["source_good_type_id"],
                        rank=rank,
                        score=c["score"],
                        method="SEMANTIC",
                        matched_term=c["matched_term"],
                        is_cross_root_ambiguous=False,
                        is_cross_good_type_ambiguous=False,
                    )
                )
            return hits
        except Exception as exc:
            logger.warning("Gemini Dual-Stream search failed: %s", exc)
            return []


class OpenAISemanticRetriever(BaseSemanticRetriever):
    """Dual-Stream Semantic Retriever powered by OpenAI Embeddings API (text-embedding-3-small / large)."""

    def __init__(
        self,
        catalog: Catalog,
        api_key: str = "",
        model_name: str = "text-embedding-3-small",
        cache_root: Path | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            raise SemanticUnavailable("OPENAI_API_KEY is not set")

        self.openai_model = "text-embedding-3-large" if "large" in model_name.lower() else "text-embedding-3-small"
        self.model_version = f"dual-stream-openai-{self.openai_model}"
        self._concept_index = None
        self._concept_docs = []
        self._evidence_index = None
        self._evidence_docs = []

        sem_dir = cache_root or (Path(__file__).resolve().parent.parent.parent / "storage" / "semantic")
        concept_idx_path = sem_dir / "catalog_concept_faiss.index"
        concept_meta_path = sem_dir / "catalog_concept_metadata.json"
        evidence_idx_path = sem_dir / "catalog_evidence_faiss.index"
        evidence_meta_path = sem_dir / "catalog_evidence_metadata.json"

        if not evidence_idx_path.exists():
            evidence_idx_path = sem_dir / "catalog_faiss.index"
            evidence_meta_path = sem_dir / "catalog_faiss_metadata.json"

        import faiss

        if concept_idx_path.exists() and concept_meta_path.exists():
            try:
                self._concept_index = faiss.read_index(str(concept_idx_path))
                with open(concept_meta_path, "r", encoding="utf-8") as f:
                    self._concept_docs = json.load(f)
            except Exception:
                pass

        if evidence_idx_path.exists() and evidence_meta_path.exists():
            try:
                self._evidence_index = faiss.read_index(str(evidence_idx_path))
                with open(evidence_meta_path, "r", encoding="utf-8") as f:
                    raw_meta = json.load(f)
                self._evidence_docs = [
                    SemanticDocument(
                        root_good_type_id=int(item["root_good_type_id"]),
                        source_good_type_id=int(item["source_good_type_id"]),
                        source_type=str(item.get("source_type", "EVIDENCE")),
                        matched_term=str(item["matched_term"]),
                        is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                        is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        text=str(item["text"]),
                    )
                    for item in raw_meta
                ]
            except Exception:
                pass

    def is_available(self) -> bool:
        return self._evidence_index is not None or self._concept_index is not None

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self.is_available():
            return []
        import urllib.request
        try:
            url = "https://api.openai.com/v1/embeddings"
            payload = {
                "model": self.openai_model,
                "input": query,
                "encoding_format": "float",
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            
            raw_emb = result["data"][0]["embedding"]
            vec = np.array([raw_emb], dtype=np.float32)
            norm = np.linalg.norm(vec, axis=1, keepdims=True)
            norm[norm == 0] = 1.0
            query_vec = vec / norm
            q_arr = np.asarray(query_vec, dtype=np.float32)

            concept_scores: dict[int, float] = {}
            leaf_to_root: dict[int, int] = {}
            leaf_to_name: dict[int, str] = {}

            if self._concept_index is not None and self._concept_docs:
                k_concept = min(len(self._concept_docs), 90)
                scores_c, indices_c = self._concept_index.search(q_arr, k_concept)
                for idx, sc in zip(indices_c[0], scores_c[0]):
                    if idx >= 0:
                        doc = self._concept_docs[idx]
                        leaf_id = doc["source_good_type_id"]
                        concept_scores[leaf_id] = float(sc)
                        leaf_to_root[leaf_id] = doc["root_good_type_id"]
                        leaf_to_name[leaf_id] = doc.get("name_ar", "")

            evidence_best_score: dict[int, float] = {}
            evidence_best_term: dict[int, str] = {}

            if self._evidence_index is not None and self._evidence_docs:
                k_evidence = min(len(self._evidence_docs), 40)
                scores_e, indices_e = self._evidence_index.search(q_arr, k_evidence)
                for idx, sc in zip(indices_e[0], scores_e[0]):
                    if idx >= 0:
                        edoc = self._evidence_docs[idx]
                        leaf_id = edoc.source_good_type_id
                        sc_f = float(sc)
                        leaf_to_root[leaf_id] = edoc.root_good_type_id
                        if leaf_id not in evidence_best_score or sc_f > evidence_best_score[leaf_id]:
                            evidence_best_score[leaf_id] = sc_f
                            evidence_best_term[leaf_id] = edoc.matched_term

            all_candidate_leaves = set(concept_scores.keys()) | set(evidence_best_score.keys())
            scored_candidates: list[dict] = []

            for leaf_id in all_candidate_leaves:
                s_concept = concept_scores.get(leaf_id, 0.0)
                s_evidence = evidence_best_score.get(leaf_id, None)
                matched_term = evidence_best_term.get(leaf_id, leaf_to_name.get(leaf_id, ""))

                if s_evidence is not None:
                    fused_score = (0.65 * s_evidence) + (0.35 * s_concept)
                    if s_evidence >= 0.80 and s_concept >= 0.40:
                        fused_score += 0.03 * (s_evidence * s_concept)
                else:
                    fused_score = s_concept * 0.88

                root_id = leaf_to_root.get(leaf_id, leaf_id)
                scored_candidates.append({
                    "source_good_type_id": leaf_id,
                    "root_good_type_id": root_id,
                    "score": float(np.clip(fused_score, 0.0, 1.0)),
                    "matched_term": matched_term,
                })

            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            hits: list[CandidateHit] = []
            for rank, c in enumerate(scored_candidates[:top_k], start=1):
                hits.append(
                    CandidateHit(
                        root_good_type_id=c["root_good_type_id"],
                        source_good_type_id=c["source_good_type_id"],
                        rank=rank,
                        score=c["score"],
                        method="SEMANTIC",
                        matched_term=c["matched_term"],
                        is_cross_root_ambiguous=False,
                        is_cross_good_type_ambiguous=False,
                    )
                )
            return hits
        except Exception as exc:
            logger.warning("OpenAI Dual-Stream search failed: %s", exc)
            return []


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return matrix / norms


def _clean_label(model_name: str) -> str:
    return model_name.replace("/", "-").replace("\\", "-").strip()

