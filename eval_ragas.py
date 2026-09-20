import json
import os
import sys
from pathlib import Path
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))
from src.task10_generation import generate_with_citation
from src.task9_retrieval_pipeline import retrieve
import src.task10_generation as gen_module

load_dotenv()

GOLDEN_DATASET_PATH = Path("group_project/evaluation/golden_dataset.json")

def generate_answers_for_config(use_reranking: bool):
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        golden_data = json.load(f)
        
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    # Temporarily monkey-patch retrieve to force config
    original_retrieve = gen_module.retrieve
    gen_module.retrieve = lambda q, top_k: original_retrieve(q, top_k=top_k, use_reranking=use_reranking)
    
    print(f"Generating answers for use_reranking={use_reranking}...")
    for idx, item in enumerate(golden_data):
        q = item["question"]
        gt = item["expected_answer"]
        print(f"  [{idx+1}/15] {q}")
        
        # Call pipeline
        try:
            result = gen_module.generate_with_citation(q)
            ans = result["answer"]
            ctx = [src["content"] for src in result["sources"]]
        except Exception as e:
            print(f"Error on query {q}: {e}")
            ans = ""
            ctx = []
            
        questions.append(q)
        answers.append(ans)
        contexts.append(ctx)
        ground_truths.append([gt])
        
    # Restore monkey-patch
    gen_module.retrieve = original_retrieve
    
    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

def main():
    print("Evaluating Config A (Dense-only)")
    dataset_a = generate_answers_for_config(use_reranking=False)
    print("Running RAGAS for Config A...")
    result_a = evaluate(
        dataset=dataset_a,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
    )
    print("Result A:", result_a)

    print("\nEvaluating Config B (Hybrid RRF)")
    dataset_b = generate_answers_for_config(use_reranking=True)
    print("Running RAGAS for Config B...")
    result_b = evaluate(
        dataset=dataset_b,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
    )
    print("Result B:", result_b)

if __name__ == "__main__":
    main()
