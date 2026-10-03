---
direction: rtl
lang: he
title: "תוכן העניינים הראשי"
---

<div dir="rtl" lang="he">

# הנדסת AI יישומית: ספר לימוד ותוכנית למידה

ספר לימוד בעברית למפתחת תוכנה מנוסה שעוברת להנדסת AI יישומית (Applied AI Engineering). הספר נכתב
מאפס, נבנה סביב קוד שרץ באמת, ומסתיים בפרויקט תיק עבודות: סוכן שמכין עיתון בוקר אישי.

איך קוראים: הדרך הנוחה היא גרסת ה־HTML בתיקייה `site/` (מופקת בפקודה
`uv run --with markdown tools/build_html.py`). אפשר גם לפתוח את התיקייה `book/` ב־Obsidian עם התוסף
RTL Support. לוח הלימוד היומי נמצא בנספח ו (ובאנגלית ב־`00-stage1/03-daily-schedule.md`).

## מצב הכתיבה

| סימון | משמעות |
| --- | --- |
| ✅ | הפרק כתוב במלואו, כולל תרגיל ופתק Obsidian |
| 🛠 | בכתיבה |
| ⏳ | טרם נכתב |

## חלק 0: לפני שמתחילים

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 0: איך ללמוד מהספר הזה | [`00-how-to-study.md`](00-how-to-study.md) | ✅ |

## חלק א: התמצאות וסביבת עבודה

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 1: מה בונה מהנדסת AI | [`01-what-an-ai-engineer-builds.md`](01-what-an-ai-engineer-builds.md) | ✅ |
| פרק 2: סביבת העבודה ב־Windows והקריאה הראשונה למודל | [`02-workbench-windows.md`](02-workbench-windows.md) | ✅ |

## חלק ב: איך מודלים עובדים (בדיוק כמה שצריך)

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 3: למידת מכונה בפרק אחד | [`03-machine-learning-in-one-chapter.md`](03-machine-learning-in-one-chapter.md) | ✅ |
| פרק 4: המתמטיקה המינימלית | [`04-minimal-math.md`](04-minimal-math.md) | ✅ |
| פרק 5: בתוך מודל שפה | [`05-inside-a-language-model.md`](05-inside-a-language-model.md) | ✅ |
| פרק 6: יצירת טקסט והכפתורים שלה | [`06-generation-and-its-knobs.md`](06-generation-and-its-knobs.md) | ✅ |

## חלק ג: בנייה עם ממשקי מודלים

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 7: ממשק ה־Interactions | [`07-the-interactions-api.md`](07-the-interactions-api.md) | ✅ |
| פרק 8: הנחיה כמפרט | [`08-prompt-design-as-specification.md`](08-prompt-design-as-specification.md) | ✅ |
| פרק 9: פלט מובנה | [`09-structured-outputs.md`](09-structured-outputs.md) | ✅ |
| פרק 10: קריאה לכלים | [`10-tool-calling.md`](10-tool-calling.md) | ✅ |
| פרק 11: לקוחות עמידים וניידות בין ספקים | [`11-robust-clients.md`](11-robust-clients.md) | ✅ |

## חלק ד: Embeddings, אחזור ו־RAG

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 12: Embeddings ודמיון סמנטי | [`12-embeddings.md`](12-embeddings.md) | ✅ |
| פרק 13: יסודות החיפוש | [`13-search-fundamentals.md`](13-search-fundamentals.md) | ✅ |
| פרק 14: מאגרי וקטורים | [`14-vector-databases.md`](14-vector-databases.md) | ✅ |
| פרק 15: RAG מקצה לקצה | [`15-rag-end-to-end.md`](15-rag-end-to-end.md) | ✅ |

## חלק ה: הערכה ואיכות

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 16: הערכות (Evals) | [`16-evals.md`](16-evals.md) | ✅ |
| פרק 17: ניתוח כשלים ודיבוג של מערכות AI | [`17-failure-analysis.md`](17-failure-analysis.md) | ✅ |
| פרק 18: בדיקות ליישומי AI | [`18-testing-ai-applications.md`](18-testing-ai-applications.md) | ✅ |

## חלק ו: סוכנים ותהליכי עבודה

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 19: תהליכי עבודה מול סוכנים, והלולאה ביד | [`19-workflows-vs-agents.md`](19-workflows-vs-agents.md) | ✅ |
| פרק 20: אמינות, מצב וזיכרון של סוכנים | [`20-agent-reliability-state-memory.md`](20-agent-reliability-state-memory.md) | ✅ |
| פרק 21: ספריות ופרוטוקולים: LangGraph ו־MCP | [`21-frameworks-and-protocols.md`](21-frameworks-and-protocols.md) | ✅ |

## חלק ז: פרודקשן

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 22: תצפיתיות (Observability) | [`22-observability.md`](22-observability.md) | ✅ |
| פרק 23: זמן תגובה, עלות ואמינות | [`23-latency-cost-reliability.md`](23-latency-cost-reliability.md) | ✅ |
| פרק 24: אבטחה ופרטיות | [`24-security-and-privacy.md`](24-security-and-privacy.md) | ✅ |
| פרק 25: פריסה ותזמון | [`25-deployment-and-scheduling.md`](25-deployment-and-scheduling.md) | ✅ |
| פרק 26: בחירת מודלים ושיטות | [`26-choosing-models-and-methods.md`](26-choosing-models-and-methods.md) | ✅ |

## חלק ח: קריירה

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 27: ראיונות תכנון מערכות AI | [`27-system-design-interviews.md`](27-system-design-interviews.md) | ✅ |
| פרק 28: בנק שאלות ראיון | [`28-interview-question-bank.md`](28-interview-question-bank.md) | ✅ |
| פרק 29: תיק עבודות, קורות חיים והצגת הפרויקט | [`29-portfolio-cv-presentation.md`](29-portfolio-cv-presentation.md) | ✅ |

## חלק ט: הפרויקט המסכם: Morning Brief

| פרק | קובץ | מצב |
| --- | --- | --- |
| פרק 30: מפרט וארכיטקטורה | [`30-project-spec-and-architecture.md`](30-project-spec-and-architecture.md) | ✅ |
| פרק 31: תשע אבני הדרך | [`31-project-milestones.md`](31-project-milestones.md) | ✅ |
| פרק 32: הערכה, ראיון והצגה של הפרויקט | [`32-project-evaluation-and-interview.md`](32-project-evaluation-and-interview.md) | ✅ |

## נספחים

| נספח | קובץ | מצב |
| --- | --- | --- |
| א: מילון מונחים | [`appendices/a-glossary.md`](appendices/a-glossary.md) | ✅ |
| ב: פתרון תקלות התקנה | [`appendices/b-troubleshooting.md`](appendices/b-troubleshooting.md) | ✅ |
| ג: מעקב עלויות ומחירים | [`appendices/c-costs.md`](appendices/c-costs.md) | ✅ |
| ד: תבניות פתקים ל־Obsidian | [`appendices/d-obsidian-templates.md`](appendices/d-obsidian-templates.md) | ✅ |
| ה: רשימות בדיקה: למידה ומוכנות לראיון | [`appendices/e-checklists.md`](appendices/e-checklists.md) | ✅ |
| ו: לוח הלימוד היומי | [`appendices/f-daily-schedule.md`](appendices/f-daily-schedule.md) | ✅ |

</div>
