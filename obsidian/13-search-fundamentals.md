---
direction: rtl
tags: [ai-course, book]
chapter: 13
---
# יסודות החיפוש

- **חיפוש הוא דירוג.** מילולי: מזהים, שמות. צפוף: ניסוח, שפה. מבחן המזהה.
- **טוקניזציה:** אותיות קטנות, לשמור `3.14` ו־`e0502`, מילות עצירה; עברית: הרחבת שאילתה בלי אות
  קידומת.
- **BM25:** TF עם רוויה, IDF, אורך. אפס בלי מונח משותף. אינדקס הפוך.
- **שכנים מקורבים (HNSW):** מעט recall תמורת מהירות; עד מאות אלפים סריקה מלאה.
- **RRF:** דרגות, לא ציונים. הקבוע הוא 60.
- **דירוג מחדש:** צולב רואה יחד; רק על 20 הראשונים; אחרי מדידה.
- **מדדים:** hit@k, recall@k (RAG), precision@k, MRR. 20 שאילתות מתויגות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
tokenize  re: [a-z0-9][a-z0-9._-]*|[֐-׿]+   -> lower, strip ._- , drop stop words
bm25      BM25Okapi([tokenize(t) for t in texts]).get_scores(expand_query(tokenize(q)))
dense     scores = matrix @ embed([q])[0]; argsort(-scores)[:k]
rrf       score(d) = sum 1/(60 + rank);  rank from 1;  ties -> by id
rerank    one structured call: [id] text ... -> {"scores":[{"id","score" 0-10}]}; missing id -> 0
metrics   hit@k any(top k in rel) | recall@k |top k ∩ rel|/|rel| | mrr 1/first relevant position
```

</div>

קישורים: [[12-embeddings]] · [[14-vector-databases]]
