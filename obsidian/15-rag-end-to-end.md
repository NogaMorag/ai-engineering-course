---
direction: rtl
tags: [ai-course, book]
chapter: 15
---
# RAG מקצה לקצה

- **שני מסלולים:** קליטה (טעינה, ניקוי, חלוקה, שיכון, מאגר) ושאילתה (אחזור, הקשר, תשובה, אימות).
- **קטע הוא יחידת ראיה.** קבוע 800 עם חפיפה 100, או לפי כותרות. המזהה הוא גיבוב של נתיב וטקסט.
- **מניפסט:** אותו גיבוב: דילוג; גיבוב אחר: מחיקת הישנים ושיכון; קובץ שנעלם: מחיקה. `sync`
  אידמפוטנטי.
- **הקשר:** מקורות `[n]` בתקציב תווים; רק מה שנכנס חוקי לציטוט; שאלה בסוף.
- **תשובה:** שלושה שדות (תשובה, ציטוטים, נתמך); אימות טווח; בלי ציטוט חוקי, הימנעות. מעוגן אינו נכון.
- **הקשר ארוך מול RAG:** עלות לשאלה, רעננות, ציטוטים. **מטמון:** קידומת יציבה, מינימום לפי מודל
  (אלפי טוקנים), `cached_tokens`.
- **דיבוג לפי שלבים:** מסמכים, קטעים, אחזור, הקשר, גרסת הנחיה, אימות.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
load      load_markdown_dir(root) -> Document(path, title, text, content_hash)
chunk     chunk_fixed(doc, 800, 100) | chunk_by_heading(doc, 1200)   id = sha256(path + "\x00" + text)[:16]
sync      NotesIndex(path, embedder, chunker).sync(docs) -> SyncReport(added, updated, skipped, removed, embedded)
retrieve  Retriever(index, "dense" | "hybrid").retrieve(question, k=5)
context   build_context(retrieved, max_chars=6000) -> (text, included); prompt = <sources> ... </sources> <question> ... </question>
answer    GroundedAnswer{answer, citations[int], supported}; valid = 1..len(included); none valid -> ABSTAIN
trace     documents, indexed_chunks, retrieved[], context_chunks/chars, prompt_variant, citations, invalid, cached_tokens
faults    --fault drop-doc | break-chunking | ignore-context
```

</div>

קישורים: [[14-vector-databases]] · [[16-evals]]
