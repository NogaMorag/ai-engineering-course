---
direction: rtl
tags: [ai-course, book]
chapter: 12
---
# Embeddings ודמיון סמנטי

- **שיכון = וקטור משמעות.** קרוב במרחב, קרוב במשמעות (כפי שהמודל למד).
- **נרמול פעם אחת**, ואז מכפלת מטריצות = כל הקוסינוסים. שכנים = `argsort`.
- **הציון לא מכויל**, יש רצפה (0.3 עד 0.5), תלוי בתחום. ספים מהזוגות, עם אזור אפור.
- **מודל:** 768 ממדים, רב־לשוני, הוראת משימה זהה בשני הצדדים, לא מערבבים מודלים.
- **מטמון** במפתח `sha256(model + text)`, ב־SQLite. אצוות של 50.
- **אינם:** אנונימיזציה, מאגר ידע, הבנה, ניתנים להשוואה בין מודלים.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
call      client.models.embed_content(model="gemini-embedding-2", contents=[...], config=EmbedContentConfig(output_dimensionality=768))
vectors   [e.values for e in response.embeddings]  -> normalize_rows(np.array(...))
cosine    sim = A @ B.T            nearest = np.argsort(-sim, axis=1)
mutual    argmax(axis=1)[i] == i and argmax(axis=0)[i] == i
pairs     near_duplicate_pairs(sim, threshold)  -> (i, j, score), i < j, best first
cache     key = sha256(f"{model}\x00{text}")   table embeddings(key, model, dims, vector BLOB)
```

</div>

קישורים: [[11-robust-clients]] · [[13-search-fundamentals]]
