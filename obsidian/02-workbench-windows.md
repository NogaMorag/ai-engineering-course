---
direction: rtl
tags: [ai-course, book]
chapter: 2
---
# סביבת העבודה והקריאה הראשונה למודל

- **מה הקמתי:** טרמינל חדש, Git, עורך, ומנהל חבילות אחד שמנהל גם את Python עצמו.
- **איך מריצים:** תמיד דרך uv, מתוך תיקיית הפרויקט, עם קובץ הסודות.
- **עברית בטרמינל:** משתנה סביבה אחד ברמת המשתמשת, ואז לפתוח טרמינל חדש.
- **סודות:** קובץ הסודות לא נכנס ל־Git. קובץ הדוגמה בלי המפתח כן נכנס.
- **הקריאה הראשונה:** יוצרים לקוח, שולחים בקשה אחת, קוראים טקסט ושימוש בטוקנים.
- **שאלה פתוחה:** ___

<div dir="ltr" align="left">

```text
tools    PowerShell 7 | winget | Git | VS Code | uv | Python 3.12 (managed by uv)
run      uv run --env-file .env python <file>          (from the ai-course folder)
hebrew   PYTHONUTF8=1 as a User environment variable -> open a new terminal
secrets  .env is git-ignored | .env.example is committed | git check-ignore .env prints ".env"
call     genai.Client() -> client.interactions.create(model=..., input=...) -> output_text, usage
models   MODEL_FAST=__________   MODEL_SMART=__________
limits   free tier: ____ requests/min, ____ requests/day   (from AI Studio)
```

</div>

קישורים: [[01-what-an-ai-engineer-builds]] · [[03-machine-learning-in-one-chapter]]
