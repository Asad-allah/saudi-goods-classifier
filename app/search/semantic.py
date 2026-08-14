from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from os import getpid
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
    """Delegates dense FAISS semantic vector search to a remote Colab GPU microservice."""

    def __init__(self, remote_url: str, model_version: str = "ai-gpu@colab") -> None:
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


class GeminiSemanticRetriever(BaseSemanticRetriever):
    """Semantic retriever powered by Google Gemini Embeddings API (text-embedding-004)."""

    def __init__(self, catalog: Catalog, api_key: str = "", cache_root: Path | None = None) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            raise SemanticUnavailable("GEMINI_API_KEY is not set")

        self.model_version = "google-gemini@text-embedding-004"
        self._faiss_index = None

        sem_dir = cache_root
        if sem_dir is None:
            candidate_sem_dir = Path(__file__).resolve().parent.parent.parent / "storage" / "semantic"
            if candidate_sem_dir.exists():
                sem_dir = candidate_sem_dir
            else:
                sem_dir = Path("storage") / "semantic"
        faiss_path = sem_dir / "catalog_faiss.index"
        faiss_meta_path = sem_dir / "catalog_faiss_metadata.json"

        if faiss_path.exists() and faiss_meta_path.exists():
            import faiss
            self._faiss_index = faiss.read_index(str(faiss_path))
            with open(faiss_meta_path, "r", encoding="utf-8") as f:
                raw_metadata = json.load(f)
            self._documents = tuple(
                SemanticDocument(
                    root_good_type_id=int(item["root_good_type_id"]),
                    source_good_type_id=int(item["source_good_type_id"]),
                    source_type=str(item["source_type"]),
                    matched_term=str(item["matched_term"]),
                    is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                    is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                    text=str(item["text"]),
                )
                for item in raw_metadata
            )
            logger.info("Loaded Gemini FAISS index with %d documents", len(self._documents))
        else:
            raise SemanticUnavailable(f"FAISS index not found at {faiss_path}")

    def is_available(self) -> bool:
        return self._faiss_index is not None

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self._documents or self._faiss_index is None:
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
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            
            vec = np.array([result["embedding"]["values"]], dtype=np.float32)
            norm = np.linalg.norm(vec, axis=1, keepdims=True)
            norm[norm == 0] = 1.0
            query_embedding = vec / norm

            raw_scores, raw_indices = self._faiss_index.search(
                query_embedding,
                min(top_k, len(self._documents)),
            )
            top_indices = [int(i) for i in raw_indices[0] if i >= 0]
            scores_list = [float(s) for s, i in zip(raw_scores[0], raw_indices[0]) if i >= 0]

            hits: list[CandidateHit] = []
            for rank, (index, score) in enumerate(zip(top_indices, scores_list), start=1):
                document = self._documents[index]
                hits.append(
                    CandidateHit(
                        root_good_type_id=document.root_good_type_id,
                        source_good_type_id=document.source_good_type_id,
                        rank=rank,
                        score=score,
                        method="SEMANTIC",
                        matched_term=document.matched_term,
                        is_cross_root_ambiguous=document.is_cross_root_ambiguous,
                        is_cross_good_type_ambiguous=document.is_cross_good_type_ambiguous,
                    )
                )
            return hits
        except Exception as exc:
            logger.warning("Gemini embedding search failed: %s", exc)
            return []


class SentenceTransformerRetriever(BaseSemanticRetriever):
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

        sem_dir = cache_root
        if sem_dir is None:
            candidate_sem_dir = Path(__file__).resolve().parent.parent.parent / "storage" / "semantic"
            if candidate_sem_dir.exists():
                sem_dir = candidate_sem_dir
            else:
                sem_dir = Path("storage") / "semantic"
        faiss_path = sem_dir / "catalog_faiss.index"
        faiss_meta_path = sem_dir / "catalog_faiss_metadata.json"

        # 1. Try loading native FAISS Index
        if faiss_path.exists() and faiss_meta_path.exists():
            try:
                import faiss
                self._faiss_index = faiss.read_index(str(faiss_path))
                with open(faiss_meta_path, "r", encoding="utf-8") as f:
                    raw_metadata = json.load(f)
                self._documents = tuple(
                    SemanticDocument(
                        root_good_type_id=int(item["root_good_type_id"]),
                        source_good_type_id=int(item["source_good_type_id"]),
                        source_type=str(item["source_type"]),
                        matched_term=str(item["matched_term"]),
                        is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                        is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        text=str(item["text"]),
                    )
                    for item in raw_metadata
                )
                self._embeddings = None

                # Detect model name from metadata if available
                detected_model = model_name
                if raw_metadata and "embedding_model" in raw_metadata[0]:
                    detected_model = raw_metadata[0]["embedding_model"]
                
                self.model_version = _model_version_label(detected_model)
                self._model = SentenceTransformer(detected_model)
                logger.info("Loaded native FAISS index with %d documents using %s", len(self._documents), detected_model)
                return
            except Exception as exc:
                logger.warning("Could not load native FAISS index (%s); trying fallback", exc)

        # 2. Try loading NPZ precompiled vector index
        index_artifact_path = sem_dir / "catalog_vector_index.npz"
        if index_artifact_path.exists():
            try:
                data = np.load(index_artifact_path, allow_pickle=True)
                raw_meta_obj = data["metadata_json"] if "metadata_json" in data else data["metadata"]
                raw_json = str(raw_meta_obj[0]) if hasattr(raw_meta_obj, "shape") and len(raw_meta_obj.shape) > 0 else str(raw_meta_obj)
                raw_metadata = json.loads(raw_json)
                self._documents = tuple(
                    SemanticDocument(
                        root_good_type_id=int(item["root_good_type_id"]),
                        source_good_type_id=int(item["source_good_type_id"]),
                        source_type=str(item["source_type"]),
                        matched_term=str(item["matched_term"]),
                        is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                        is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        text=str(item["text"]),
                    )
                    for item in raw_metadata
                )
                self._embeddings = np.asarray(data["embeddings"], dtype=np.float32)
                self.model_version = _model_version_label(model_name)
                self._model = SentenceTransformer(model_name)
                logger.info("Loaded precompiled vector index artifact with %d documents", len(self._documents))
                return
            except Exception as exc:
                logger.warning("Could not load precompiled vector index (%s); falling back to dynamic index", exc)

        self._documents = build_semantic_documents(catalog)
        self.model_version = _model_version_label(model_name)
        self._model = SentenceTransformer(model_name)
        cache_path = _embedding_cache_path(catalog, model_name, sem_dir)
        cached_embeddings = _load_embedding_cache(cache_path, expected_rows=len(self._documents))
        if cached_embeddings is not None:
            self._embeddings = cached_embeddings
        else:
            embeddings = self._encode_documents([item.text for item in self._documents])
            self._embeddings = _normalize(embeddings)
            _write_embedding_cache(cache_path, self._embeddings)

    def is_available(self) -> bool:
        return True

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self._documents:
            return []
        query_embedding = self._encode_query(query)
        query_embedding = _normalize(query_embedding.reshape(1, -1))[0]

        if hasattr(self, "_faiss_index") and self._faiss_index is not None:
            raw_scores, raw_indices = self._faiss_index.search(
                np.asarray([query_embedding], dtype=np.float32),
                min(top_k, len(self._documents)),
            )
            top_indices = [int(i) for i in raw_indices[0] if i >= 0]
            scores_list = [float(s) for s, i in zip(raw_scores[0], raw_indices[0]) if i >= 0]
        else:
            dot_scores = self._embeddings @ query_embedding
            top_indices = [int(i) for i in np.argsort(dot_scores)[::-1][:top_k]]
            scores_list = [float(dot_scores[i]) for i in top_indices]

        hits: list[CandidateHit] = []
        for rank, (index, score) in enumerate(zip(top_indices, scores_list), start=1):
            document = self._documents[index]
            hits.append(
                CandidateHit(
                    root_good_type_id=document.root_good_type_id,
                    source_good_type_id=document.source_good_type_id,
                    rank=rank,
                    score=score,
                    method="SEMANTIC",
                    matched_term=document.matched_term,
                    is_cross_root_ambiguous=document.is_cross_root_ambiguous,
                    is_cross_good_type_ambiguous=document.is_cross_good_type_ambiguous,
                )
            )
        return hits

    def _encode_documents(self, documents: list[str]) -> np.ndarray:
        is_e5 = "e5" in self.model_version.lower()
        prefixed = [
            doc if (not is_e5 or doc.startswith("passage: ")) else f"passage: {doc}"
            for doc in documents
        ]
        if hasattr(self._model, "encode_document"):
            return np.asarray(self._model.encode_document(prefixed, convert_to_numpy=True))
        return np.asarray(self._model.encode(prefixed, convert_to_numpy=True))

    def _encode_query(self, query: str) -> np.ndarray:
        is_e5 = "e5" in self.model_version.lower()
        q = query if (not is_e5 or query.startswith("query: ")) else f"query: {query}"
        if hasattr(self._model, "encode_query"):
            return np.asarray(self._model.encode_query(q, convert_to_numpy=True))
        return np.asarray(self._model.encode(q, convert_to_numpy=True))


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return matrix / norms


def build_semantic_documents(catalog: Catalog) -> tuple[SemanticDocument, ...]:
    documents: list[SemanticDocument] = []
    terms_by_good_type: dict[int, list[SearchTerm]] = defaultdict(list)

    for term in catalog.selectable_terms:
        root = catalog.root(term.root_good_type_id)
        leaf = catalog.good_type(term.source_good_type_id)
        doc_text = f"تصنيف بضائع {leaf.name_ar} تابعة للمجموعة الرئيسية {root.name_ar}. منتج: {term.raw_term}."
        documents.append(
            SemanticDocument(
                root_good_type_id=term.root_good_type_id,
                source_good_type_id=term.source_good_type_id,
                source_type="SELECTABLE_TERM",
                matched_term=term.raw_term,
                is_cross_root_ambiguous=term.is_cross_root_ambiguous,
                is_cross_good_type_ambiguous=term.is_cross_good_type_ambiguous,
                text=doc_text,
            )
        )
        terms_by_good_type[term.source_good_type_id].append(term)

    return tuple(documents)


def _model_version_label(model_name: str) -> str:
    cleaned = model_name.replace("/", "-").replace("\\", "-").strip()
    return f"dense-{cleaned}"


def _embedding_cache_path(catalog: Catalog, model_name: str, cache_dir: Path) -> Path:
    hasher = sha256()
    hasher.update(catalog.version.encode("utf-8"))
    hasher.update(model_name.encode("utf-8"))
    for term in catalog.selectable_terms:
        hasher.update(str(term.id).encode("utf-8"))
        hasher.update(term.normalized_term.encode("utf-8"))
        hasher.update(str(term.source_good_type_id).encode("utf-8"))
        hasher.update(str(term.root_good_type_id).encode("utf-8"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"embeddings_{hasher.hexdigest()[:16]}.npz"


def _load_embedding_cache(cache_path: Path, *, expected_rows: int) -> np.ndarray | None:
    if not cache_path.exists():
        return None
    try:
        data = np.load(cache_path)
        embeddings = data["embeddings"]
        if embeddings.shape[0] != expected_rows:
            return None
        return embeddings
    except Exception:
        return None


def _write_embedding_cache(cache_path: Path, embeddings: np.ndarray) -> None:
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = cache_path.with_suffix(f".tmp.{getpid()}.npz")
        np.savez_compressed(tmp_path, embeddings=embeddings)
        tmp_path.replace(cache_path)
    except Exception:
        pass
