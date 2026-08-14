from __future__ import annotations

import json
import logging
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
    """Delegates dense FAISS / E5 semantic vector search to a remote Colab GPU microservice."""

    def __init__(self, remote_url: str, model_version: str = "e5-small@colab-gpu") -> None:
        self.remote_url = remote_url.rstrip("/") if remote_url else ""
        self.model_version = model_version

    def is_available(self) -> bool:
        return bool(self.remote_url)

    def search(self, query: str, *, top_k: int = 20) -> list[CandidateHit]:
        if not self.remote_url:
            return []
        import json
        import urllib.request
        try:
            url = f"{self.remote_url}/semantic/search"
            req = urllib.request.Request(
                url,
                data=json.dumps({"query": query, "top_k": top_k}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = []
                for item in data.get("hits", []):
                    hits.append(
                        CandidateHit(
                            root_good_type_id=int(item["root_good_type_id"]),
                            source_good_type_id=int(item["source_good_type_id"]),
                            rank=int(item["rank"]),
                            score=float(item["score"]),
                            method="SEMANTIC",
                            matched_term=str(item["matched_term"]),
                            is_cross_root_ambiguous=bool(item.get("is_cross_root_ambiguous", False)),
                            is_cross_good_type_ambiguous=bool(item.get("is_cross_good_type_ambiguous", False)),
                        )
                    )
                return hits
        except Exception as exc:
            logger.warning("Remote semantic call to Colab failed (%s); continuing with exact/fuzzy", exc)
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
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise SemanticUnavailable("sentence-transformers is not installed") from exc

        self.model_version = _model_version_label(model_name)
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
                self._model = SentenceTransformer(model_name)
                logger.info("Loaded native FAISS index with %d documents", len(self._documents))
                return
            except Exception as exc:
                logger.warning("Could not load native FAISS index (%s); trying fallback", exc)

        # 2. Try loading NPZ precompiled vector index
        index_artifact_path = sem_dir / "catalog_vector_index.npz"
        if index_artifact_path.exists():
            try:
                data = np.load(index_artifact_path, allow_pickle=True)
                raw_meta_obj = data["metadata"]
                raw_json = str(raw_meta_obj[0]) if len(raw_meta_obj.shape) > 0 else str(raw_meta_obj)
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
                self._model = SentenceTransformer(model_name)
                logger.info("Loaded precompiled vector index artifact with %d documents", len(self._documents))
                return
            except Exception as exc:
                logger.warning("Could not load precompiled vector index (%s); falling back to dynamic index", exc)

        self._documents = build_semantic_documents(catalog)
        self._model = SentenceTransformer(model_name)
        cache_path = _embedding_cache_path(
            catalog,
            model_name,
            sem_dir,
        )
        cached_embeddings = _load_embedding_cache(
            cache_path,
            expected_rows=len(self._documents),
        )
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

        if self._faiss_index is not None:
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
                    is_cross_good_type_ambiguous=(
                        document.is_cross_good_type_ambiguous
                    ),
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
            return np.asarray(
                self._model.encode_document(prefixed, convert_to_numpy=True)
            )
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
    """Create semantic-search documents strictly from the imported catalog."""
    documents: list[SemanticDocument] = []
    terms_by_good_type: dict[int, list[SearchTerm]] = defaultdict(list)

    for term in catalog.selectable_terms:
        root = catalog.root(term.root_good_type_id)
        good_type = catalog.good_type(term.source_good_type_id)
        documents.append(
            SemanticDocument(
                root_good_type_id=term.root_good_type_id,
                source_good_type_id=term.source_good_type_id,
                source_type=term.source_type,
                matched_term=term.raw_term,
                is_cross_root_ambiguous=term.is_cross_root_ambiguous,
                is_cross_good_type_ambiguous=term.is_cross_good_type_ambiguous,
                text=(
                    f"{term.raw_term}. "
                    f"Goods type: {good_type.name_ar}. "
                    f"Main goods group: {root.name_ar}."
                ),
            )
        )
        terms_by_good_type[term.source_good_type_id].append(term)

    for good_type_id, terms in terms_by_good_type.items():
        good_type = catalog.good_type(good_type_id)
        root = catalog.root(catalog.root_id_for(good_type_id))
        documents.append(
            SemanticDocument(
                root_good_type_id=root.id,
                source_good_type_id=good_type_id,
                source_type="GOOD_TYPE_LABEL",
                matched_term=good_type.name_ar,
                is_cross_root_ambiguous=False,
                is_cross_good_type_ambiguous=False,
                text=(
                    f"{good_type.name_ar}. Main goods group: {root.name_ar}."
                ),
            )
        )
        examples = _term_examples(terms)
        if examples:
            documents.append(
                SemanticDocument(
                    root_good_type_id=root.id,
                    source_good_type_id=good_type_id,
                    source_type="GOOD_TYPE_PROFILE",
                    matched_term=good_type.name_ar,
                    is_cross_root_ambiguous=False,
                    is_cross_good_type_ambiguous=False,
                    text=(
                        f"Goods type: {good_type.name_ar}. "
                        f"Main goods group: {root.name_ar}. "
                        f"Related names: {examples}."
                    ),
                )
            )

    return tuple(documents)


def _term_examples(terms: list[SearchTerm], *, limit: int = 69) -> str:
    unique_terms = dict.fromkeys(term.raw_term for term in terms)
    return ", ".join(list(unique_terms)[:limit])


def _embedding_cache_path(catalog: Catalog, model_name: str, cache_root: Path) -> Path:
    cache_key = (
        f"semantic-documents-v3\x1f{catalog.version}\x1f"
        f"{catalog.source_sha256}\x1f{model_name}"
    )
    digest = sha256(cache_key.encode("utf-8")).hexdigest()[:20]
    return cache_root / f"{digest}.npy"


def _model_version_label(model_name: str) -> str:
    model_path = Path(model_name)
    if model_path.exists():
        return f"{model_path.name}@local"
    return f"{model_name}@local"


def _load_embedding_cache(path: Path, *, expected_rows: int) -> np.ndarray | None:
    try:
        embeddings = np.load(path, allow_pickle=False)
    except (OSError, ValueError):
        return None
    if embeddings.ndim != 2 or embeddings.shape[0] != expected_rows:
        return None
    if not np.isfinite(embeddings).all():
        return None
    return np.asarray(embeddings, dtype=np.float32)


def _write_embedding_cache(path: Path, embeddings: np.ndarray) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f"{path.stem}.{getpid()}.tmp.npy")
        np.save(temporary_path, embeddings)
        temporary_path.replace(path)
    except OSError:
        # The cache is an optimisation only; classification must still work without it.
        return
