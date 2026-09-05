"""
Search Evaluation - Measure search quality metrics
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.indexing.bm25 import BM25
from app.retrieval.semantic import SemanticSearch
from app.retrieval.hybrid import HybridSearch
from app.database.database import Database
from app.database.repositories import DocumentRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchEvaluator:
    def __init__(self, dataset_path: str = "evaluation/dataset.json"):
        self.dataset_path = dataset_path
        self.dataset = self._load_dataset()
        self.documents = self._load_documents()
        
        self.bm25 = BM25()
        self.semantic = SemanticSearch()
        self.hybrid = HybridSearch()
        
        self._index_documents()
    
    def _load_dataset(self) -> Dict:
        with open(self.dataset_path, 'r') as f:
            return json.load(f)
    
    def _load_documents(self) -> List[Dict]:
        db = Database("data/search.db")
        repo = DocumentRepository(db)
        docs = repo.get_all()
        
        result = []
        for doc in docs:
            result.append({
                'id': doc.id,
                'title': doc.title or '',
                'content': doc.content or ''
            })
        return result
    
    def _index_documents(self):
        for doc in self.documents:
            doc_id = str(doc['id'])
            title = doc['title']
            content = doc['content']
            
            self.bm25.add_document(doc_id, title, content)
            self.semantic.add_document(doc_id, title, content)
            self.hybrid.add_document(doc_id, title, content)
    
    def evaluate(self, search_func, k: int = 5) -> Dict:
        results = []
        
        for query_data in self.dataset['queries']:
            query = query_data['query']
            relevant = set(str(doc_id) for doc_id in query_data['relevant_documents'])
            
            search_results = search_func(query)
            retrieved = [str(r['id']) for r in search_results[:k]]
            
            results.append({
                'query': query,
                'relevant': relevant,
                'retrieved': retrieved,
                'relevant_retrieved': len(set(retrieved) & relevant),
                'total_relevant': len(relevant)
            })
        
        return self._calculate_metrics(results, k)
    
    def _calculate_metrics(self, results: List[Dict], k: int) -> Dict:
        total_precision = 0
        total_recall = 0
        total_mrr = 0
        total_ndcg = 0
        
        for r in results:
            precision = r['relevant_retrieved'] / k if k > 0 else 0
            total_precision += precision
            
            recall = r['relevant_retrieved'] / r['total_relevant'] if r['total_relevant'] > 0 else 0
            total_recall += recall
            
            mrr = self._calculate_mrr(r['retrieved'], r['relevant'])
            total_mrr += mrr
            
            ndcg = self._calculate_ndcg(r['retrieved'], r['relevant'])
            total_ndcg += ndcg
        
        n = len(results)
        
        return {
            'precision@k': round(total_precision / n, 4) if n > 0 else 0,
            'recall@k': round(total_recall / n, 4) if n > 0 else 0,
            'mrr': round(total_mrr / n, 4) if n > 0 else 0,
            'ndcg@k': round(total_ndcg / n, 4) if n > 0 else 0,
            'k': k,
            'total_queries': n
        }
    
    def _calculate_mrr(self, retrieved: List[str], relevant: Set[str]) -> float:
        for i, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                return 1.0 / i
        return 0.0
    
    def _calculate_ndcg(self, retrieved: List[str], relevant: Set[str]) -> float:
        dcg = 0
        for i, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                dcg += 1 / math.log2(i + 1)
        
        ideal = min(len(relevant), len(retrieved))
        idcg = 0
        for i in range(1, ideal + 1):
            idcg += 1 / math.log2(i + 1)
        
        return dcg / idcg if idcg > 0 else 0
    
    def compare_engines(self, k: int = 5) -> Dict:
        return {
            'bm25': self.evaluate(self._search_bm25, k),
            'semantic': self.evaluate(self._search_semantic, k),
            'hybrid': self.evaluate(self._search_hybrid, k)
        }
    
    def _search_bm25(self, query: str) -> List[Dict]:
        return self.bm25.get_top_documents(query, limit=10)
    
    def _search_semantic(self, query: str) -> List[Dict]:
        return self.semantic.get_top_documents(query, limit=10)
    
    def _search_hybrid(self, query: str) -> List[Dict]:
        return self.hybrid.get_top_documents(query, limit=10)
    
    def print_report(self, results: Dict):
        print("\n" + "="*60)
        print("📊 SEARCH EVALUATION REPORT")
        print("="*60 + "\n")
        
        print(f"{'Engine':<12} {'P@5':<10} {'R@5':<10} {'MRR':<10} {'NDCG@5':<10}")
        print("-"*60)
        
        for engine, metrics in results.items():
            print(f"{engine:<12} {metrics['precision@k']:<10} {metrics['recall@k']:<10} {metrics['mrr']:<10} {metrics['ndcg@k']:<10}")
        
        print("\n" + "="*60)
        print("✅ Evaluation complete!")
        print("="*60 + "\n")
    
    def run_evaluation(self, k: int = 5):
        logger.info(f"Running evaluation with k={k}")
        logger.info(f"Dataset: {len(self.dataset['queries'])} queries")
        logger.info(f"Documents: {len(self.documents)} documents")
        
        results = self.compare_engines(k)
        self.print_report(results)
        
        output_path = f"evaluation/results_k{k}.json"
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_path}")
        
        return results


def main():
    evaluator = SearchEvaluator()
    evaluator.run_evaluation(k=5)


if __name__ == "__main__":
    main()