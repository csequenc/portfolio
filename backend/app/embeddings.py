
"""Lightweight ONNX sentence embeddings for portfolio retrieval."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer


MODEL_REPO = "monju-lab/all-MiniLM-L6-v2-onnx"
MODEL_REVISION = "main"
MODEL_FILE = "onnx/model_quint8_avx2.onnx"
TOKENIZER_FILE = "tokenizer.json"

MAX_LENGTH = 256
BATCH_SIZE = 8


class EmbeddingEngine:
    """Generate normalized sentence embeddings using ONNX Runtime."""

    def __init__(self) -> None:
        model_path = hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILE,
            revision=MODEL_REVISION,
        )

        tokenizer_path = hf_hub_download(
            repo_id=MODEL_REPO,
            filename=TOKENIZER_FILE,
            revision=MODEL_REVISION,
        )

        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.enable_padding()
        self.tokenizer.enable_truncation(max_length=MAX_LENGTH)

        options = ort.SessionOptions()
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.enable_cpu_mem_arena = False
        options.enable_mem_pattern = False

        self.session = ort.InferenceSession(
            model_path,
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )

    def encode(self, texts: list[str]) -> np.ndarray:
        """Convert text into normalized 384-dimensional vectors."""

        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        all_vectors = []

        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]

            encoded = self.tokenizer.encode_batch(batch)

            input_ids = np.asarray(
                [item.ids for item in encoded],
                dtype=np.int64,
            )

            attention_mask = np.asarray(
                [item.attention_mask for item in encoded],
                dtype=np.int64,
            )

            token_type_ids = np.zeros_like(input_ids)

            outputs = self.session.run(
                None,
                {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "token_type_ids": token_type_ids,
                },
            )

            token_embeddings = outputs[0].astype(np.float32)

            # Attention-masked mean pooling.
            mask = attention_mask[..., np.newaxis].astype(np.float32)

            summed = np.sum(token_embeddings * mask, axis=1)
            counts = np.clip(np.sum(mask, axis=1), 1e-9, None)

            sentence_embeddings = summed / counts

            # L2 normalization makes dot product equal cosine similarity.
            norms = np.linalg.norm(
                sentence_embeddings,
                axis=1,
                keepdims=True,
            )

            sentence_embeddings = sentence_embeddings / np.clip(
                norms,
                1e-12,
                None,
            )

            all_vectors.append(sentence_embeddings)

        return np.vstack(all_vectors).astype(np.float32)


@lru_cache(maxsize=1)
def get_embedding_engine() -> EmbeddingEngine:
    """Load one shared embedding engine per backend process."""
    return EmbeddingEngine()


def embed_texts(texts: list[str]) -> np.ndarray:
    """Public function used by the knowledge retriever."""
    return get_embedding_engine().encode(texts)
