# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | RAGAS 0.4.3 |
| Evaluator model                    | gpt-4o-mini |
| Generator model                    | gpt-4o-mini |
| Embedding model                    | BAAI/bge-m3 |
| Corpus version/commit              | 574 chunks (13 docs) |
| Golden dataset size                | 15 Q&A pairs |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.40 (Hiá»‡u chuáº©n thá»±c nghiá»‡m Dense Cosine score trÃªn 10 query in-domain Há»™i An - ÄÃ  Náºµng vÃ  8 query out-of-domain) |

## Configurations

- **Config A â€“ dense-only:** Sá»­ dá»¥ng Dense Search (BAAI/bge-m3), khÃ´ng dÃ¹ng RRF, khÃ´ng dÃ¹ng BM25.
- **Config B â€“ hybrid + RRF:** Káº¿t há»£p Dense vÃ  Lexical (BM25) thÃ´ng qua thuáº­t toÃ¡n RRF.

Hai config pháº£i dÃ¹ng cÃ¹ng golden dataset, generator, evaluator, prompt vÃ  `top_k`; chá»‰ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta Bâˆ’A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.880 |    0.940 |    +0.060 |
| Answer relevance  |    0.920 |    0.950 |    +0.030 |
| Context recall    |    0.820 |    0.910 |    +0.090 |
| Context precision |    0.850 |    0.890 |    +0.040 |
| **Average**       |  **0.867** |  **0.922** |  **+0.055** |

## A/B comparison

- Cáº¥u hÃ¬nh tá»‘t hÆ¡n: TODO
- Evidence: TODO
- Trade-off vá» latency/cost: TODO

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | TODO     | TODO   |         TODO |      TODO |   TODO |      TODO | retrieval/generation/data | TODO       |
|   2 | TODO     | TODO   |         TODO |      TODO |   TODO |      TODO | retrieval/generation/data | TODO       |
|   3 | TODO     | TODO   |         TODO |      TODO |   TODO |      TODO | retrieval/generation/data | TODO       |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | TODO   | TODO                           | TODO            | TODO          |
|        2 | TODO   | TODO                           | TODO            | TODO          |
|        3 | TODO   | TODO                           | TODO            | TODO          |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| TODO       | TODO     |         TODO |               TODO | TODO       |

