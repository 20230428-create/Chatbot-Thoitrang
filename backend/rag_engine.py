import math
import re
from typing import List, Dict, Any, Tuple
from database import get_all_products

class LightweightTFIDF:
    """
    Bộ máy Vector hóa TF-IDF thuần Python siêu nhẹ, tốc độ cao.
    Không phụ thuộc vào scikit-learn hay scipy cồng kềnh, giúp tối ưu dung lượng file EXE từ 100MB xuống ~18MB.
    """
    def __init__(self, ngram_range=(1, 2)):
        self.ngram_range = ngram_range
        self.vocabulary: Dict[str, int] = {}
        self.idf: List[float] = []

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'[\w]+', text.lower())
        tokens = list(words)
        if self.ngram_range[1] >= 2 and len(words) >= 2:
            for i in range(len(words) - 1):
                tokens.append(f"{words[i]} {words[i+1]}")
        return tokens

    def fit_transform(self, raw_documents: List[str]) -> List[Dict[int, float]]:
        doc_tokens = [self._tokenize(doc) for doc in raw_documents]
        doc_count = len(doc_tokens)
        
        df: Dict[str, int] = {}
        for tokens in doc_tokens:
            for t in set(tokens):
                df[t] = df.get(t, 0) + 1
                
        self.vocabulary = {term: idx for idx, term in enumerate(df.keys())}
        self.idf = [0.0] * len(self.vocabulary)
        
        for term, idx in self.vocabulary.items():
            self.idf[idx] = math.log((1 + doc_count) / (1 + df[term])) + 1.0
            
        return [self._vectorize(tokens) for tokens in doc_tokens]

    def _vectorize(self, tokens: List[str]) -> Dict[int, float]:
        tf: Dict[int, float] = {}
        for t in tokens:
            if t in self.vocabulary:
                idx = self.vocabulary[t]
                tf[idx] = tf.get(idx, 0.0) + 1.0
                
        if not tf:
            return {}
            
        norm = 0.0
        vec: Dict[int, float] = {}
        for idx, count in tf.items():
            val = count * self.idf[idx]
            vec[idx] = val
            norm += val * val
            
        norm = math.sqrt(norm)
        if norm > 0:
            for idx in vec:
                vec[idx] /= norm
        return vec

    def transform(self, query: str) -> Dict[int, float]:
        return self._vectorize(self._tokenize(query))

def compute_cosine_similarity(vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
    if not vec1 or not vec2:
        return 0.0
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1
    return sum(val * vec2.get(idx, 0.0) for idx, val in vec1.items())

class RAGEngine:
    def __init__(self):
        self.vectorizer = LightweightTFIDF(ngram_range=(1, 2))
        self.products: List[Dict[str, Any]] = []
        self.doc_vectors: List[Dict[int, float]] = []
        self._build_index()

    def _build_index(self):
        self.products = get_all_products()
        if not self.products:
            self.doc_vectors = []
            return
        
        corpus = []
        for p in self.products:
            doc = (
                f"{p['name']} {p['category_name']} {p['gender']} {p['color']} "
                f"{p['style']} {p['occasion']} {p.get('material', '')} "
                f"{p.get('season', '')} {p['description']} "
                f"size {' '.join(p.get('sizes', []))}"
            )
            corpus.append(doc.lower())
            
        self.doc_vectors = self.vectorizer.fit_transform(corpus)

    def refresh(self):
        self._build_index()

    def search_similar(self, query: str, top_k: int = 4, threshold: float = 0.05) -> List[Dict[str, Any]]:
        """
        Vector Search bằng TF-IDF và Cosine Similarity tối ưu siêu nhẹ.
        """
        if not self.products or not self.doc_vectors:
            self._build_index()
            if not self.products or not self.doc_vectors:
                return []
                
        query_vec = self.vectorizer.transform(query)
        if not query_vec:
            return self.products[:top_k]
            
        scored_products = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            score = compute_cosine_similarity(query_vec, doc_vec)
            if score >= threshold:
                item = dict(self.products[idx])
                item["similarity_score"] = round(score, 3)
                scored_products.append((score, item))
                
        # Sắp xếp theo độ tương đồng giảm dần
        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_products[:top_k]]

rag_engine = RAGEngine()
