---
direction: rtl
tags: [ai-course, book]
chapter: 14
---
# מאגרי וקטורים

- **מה חסר ל־numpy:** התמדה, מסננים, upsert, מחיקה, ANN, כמה תהליכים. לא מהירות (בקטן).
- **אוצר מילים:** אוסף, id, וקטור, מסמך, מטא־נתונים, מרחק (קוסינוס = 1 פחות דמיון).
- **Chroma:** `PersistentClient`, `hnsw:space=cosine`, upsert, query עם `where`, תאריכים כמספרים,
  וקטורים שלנו, טלמטריה כבויה.
- **מודל במטא־נתונים של האוסף.** שונה? מסרבים לכתוב; אינדוקס מחדש או אוסף עם גרסה.
- **מבחן numpy מספיק:** גודל, התמדה, מסננים, תהליכים, עדכונים.
- **מסנן ≠ הרשאה.** מסמך ווקטור רגישים כמו המקור. שימור = מחיקה לפי תאריך.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
client    chromadb.PersistentClient(path=..., settings=Settings(anonymized_telemetry=False))
create    get_or_create_collection(name, metadata={"hnsw:space": "cosine", "embedding_model": model})
upsert    ids, embeddings=vectors.tolist(), documents, metadatas=[{"source": s, "day": 20260925}]
query     query_embeddings=[...], n_results=min(k, count), where={"$and": [{"day": {"$gte": d}}, {"source": "hn"}]}
result    result["ids"][0], result["distances"][0]  -> similarity = 1 - distance
reindex   stored_model != embedder.model -> delete_collection + recreate + upsert all
```

</div>

קישורים: [[13-search-fundamentals]] · [[15-rag-end-to-end]]
