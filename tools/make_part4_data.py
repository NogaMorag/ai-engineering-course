"""Generate the shared Part 4 datasets (deterministic, no network).

    uv run --no-project python tools/make_part4_data.py

Writes:
    exercises/ch12-embeddings/data/headlines.jsonl   200 invented tech headlines, 30 planted near-duplicates
    exercises/ch12-embeddings/data/pairs.jsonl       10 Hebrew/English sentence pairs
    exercises/ch13-search/data/queries.jsonl         20 labeled queries (relevant headline ids)
All names of products, companies and people are invented.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ["devwire", "hn", "cloudbeat", "stackdaily", "orbitnews"]

# key, topic, headline, optional paraphrase (a planted near-duplicate)
BASE: list[tuple[str, str, str, str | None]] = [
    ("cargo_cache", "rust", "Cargo-Lite 2.0 ships a shared build cache that cuts compile times from 41 to 6 minutes",
     "Cargo-Lite 2.0 released: shared build cache brings 41-minute compiles down to six"),
    ("rust_e0502", "rust", "Rust compiler error E0502 explained: why the borrow checker rejects your mutable reference", None),
    ("rust_async", "rust", "Async Rust working group proposes a standard executor trait for the 2027 edition",
     "Proposal: a standard executor trait for async Rust lands in the 2027 edition discussion"),
    ("rust_kernel", "rust", "Linux 7.3 merges the first Rust network driver into the mainline kernel", None),
    ("rust_wasm", "rust", "Wasm toolchain Ferrous builds Rust to WebAssembly 40 percent faster in new release", None),
    ("rust_survey", "rust", "Annual Rust survey: compile times remain the top complaint for the fifth year",
     "Rust survey results: slow compile times are still developers' number one complaint"),
    ("rust_gui", "rust", "Iced 1.0 brings a stable cross-platform GUI toolkit to Rust", None),
    ("py_314", "python", "Python 3.14 released with the free-threaded build enabled by default on Linux",
     "Python 3.14 is out: free-threaded builds become the Linux default"),
    ("py_uv", "python", "uv 1.0 reaches stable: one tool for Python versions, packages and scripts", None),
    ("py_typing", "python", "PEP 812 proposes inline type syntax for lambda parameters", None),
    ("py_django", "python", "Django 6.0 adds native async ORM queries and drops Python 3.11 support",
     "Django 6.0 lands async ORM support; Python 3.11 is no longer supported"),
    ("py_pandas", "python", "Pandas 4.0 switches the default string dtype to Arrow-backed strings", None),
    ("py_jupyter", "python", "Jupyter notebooks gain real-time collaboration in JupyterLab 5", None),
    ("py_pytest", "python", "pytest 9 makes the new assertion rewriting engine the default", None),
    ("k8s_cni", "kubernetes", "Kubernetes 1.36 upgrade breaks pod networking for clusters using the legacy CNI plugin",
     "Clusters on the legacy CNI plugin lose pod networking after upgrading to Kubernetes 1.36"),
    ("k8s_gateway", "kubernetes", "Gateway API 2.0 graduates and the Ingress resource is formally deprecated", None),
    ("k8s_cost", "kubernetes", "Study: 60 percent of Kubernetes clusters request twice the CPU they use",
     "Report finds most Kubernetes workloads over-request CPU by a factor of two"),
    ("k8s_argo", "kubernetes", "Argo CD 4 adds progressive rollouts to every application by default", None),
    ("k8s_wasm", "kubernetes", "SpinKube runs WebAssembly workloads next to containers in production clusters", None),
    ("k8s_etcd", "kubernetes", "etcd 4.0 cuts snapshot restore time in half for large clusters", None),
    ("k8s_helm", "kubernetes", "Helm 4 released with OCI-only chart distribution and typed values", None),
    ("db_postmortem", "databases", "Postmortem: how a single long-running transaction took a payments database offline for 4 hours",
     "A payments database was down for four hours because of one long-running transaction, postmortem shows"),
    ("db_pg18", "databases", "PostgreSQL 18 ships asynchronous I/O and faster upgrades between major versions", None),
    ("db_sqlite", "databases", "SQLite adds native vector search in version 3.52", None),
    ("db_duck", "databases", "DuckDB 2.0 reads Iceberg tables directly from object storage",
     "DuckDB 2.0 can now query Iceberg tables straight from S3-compatible storage"),
    ("db_vector", "databases", "Benchmark: pgvector matches dedicated vector databases up to ten million vectors", None),
    ("db_migration", "databases", "Fintech Lumen moves 40 TB from MongoDB to Postgres with zero downtime", None),
    ("db_backup", "databases", "Backup failures went unnoticed for six months at hosting provider Nimbus, audit finds",
     "Audit: Nimbus hosting ran six months with silently failing backups"),
    ("sec_breach", "security", "Credential dump exposes 12 million passwords from the Lumen fintech breach",
     "Lumen breach: 12 million customer passwords leaked in credential dump"),
    ("sec_cve", "security", "CVE-2026-1234: remote code execution in the OpenSSH agent forwarding path patched", None),
    ("sec_supply", "security", "Malicious package on PyPI impersonated a popular HTTP library for three days",
     "Typosquatted PyPI package mimicked a popular HTTP client library for 72 hours before removal"),
    ("sec_passkeys", "security", "Passkeys overtake SMS codes as the most used second factor at major banks", None),
    ("sec_llm", "security", "Prompt injection through a calendar invite tricked an AI assistant into forwarding email", None),
    ("sec_ransom", "security", "Ransomware group targets backup servers first, incident reports show", None),
    ("sec_tls", "security", "Browsers will stop trusting certificates valid for more than 45 days starting 2028", None),
    ("ai_small", "ai", "A 3-billion-parameter model matches last year's frontier models on coding benchmarks",
     "Small 3B model reaches 2025 frontier-level coding scores, researchers report"),
    ("ai_embed", "ai", "New multilingual embedding model adds Hebrew and Arabic to its top-tier languages", None),
    ("ai_agents", "ai", "Survey: most production AI agents run fewer than five tool calls per task", None),
    ("ai_evals", "ai", "Open eval suite finds LLM judges prefer longer answers regardless of correctness",
     "Study: LLM-as-judge systems favor verbose answers even when they are wrong"),
    ("ai_cache", "ai", "Prompt caching cuts inference bills by 60 percent for retrieval-heavy workloads", None),
    ("ai_rag", "ai", "Long-context models did not kill RAG: retrieval still wins on cost and freshness, says report", None),
    ("ai_openweights", "ai", "Open-weights model family released under a permissive license with 1 million token context", None),
    ("hw_gpu", "hardware", "GPU shortage eases as two new fabs come online in Arizona and Dresden",
     "New fabs in Arizona and Dresden start to relieve the GPU shortage"),
    ("hw_riscv", "hardware", "First RISC-V laptop with a 12-core chip ships to developers", None),
    ("hw_memory", "hardware", "HBM4 memory enters mass production with double the bandwidth of HBM3e", None),
    ("hw_battery", "hardware", "Solid-state battery startup Voltaic begins pilot production for electric bikes",
     "Voltaic starts pilot production of solid-state batteries for e-bikes"),
    ("hw_chip", "hardware", "Chipmaker Helion unveils a 2-nanometer process with backside power delivery", None),
    ("hw_phone", "hardware", "Repairable phone maker Fairline sells its one millionth device", None),
    ("hw_quantum", "hardware", "Quantum computer corrects errors faster than it makes them for the first time", None),
    ("space_moon", "space", "Crewed lunar landing slips to 2029 after heat shield review",
     "Heat shield review pushes the crewed Moon landing to 2029"),
    ("space_sat", "space", "Satellite constellation photographs every hurricane from orbit within ten minutes", None),
    ("space_debris", "space", "Orbital Labs demonstrates capturing a dead satellite with a robotic arm", None),
    ("space_mars", "space", "Mars sample return mission finds a cheaper two-launch architecture",
     "Mars sample return redesigned around two launches to cut costs"),
    ("space_telescope", "space", "Space telescope spots water vapor on a temperate exoplanet", None),
    ("space_launch", "space", "Reusable rocket completes its 30th flight with the same first stage", None),
    ("space_station", "space", "Commercial space station module passes pressure tests ahead of 2028 launch", None),
    ("climate_recycle", "climate", "Battery recycling plant recovers 95 percent of lithium from used EV packs",
     "New recycling facility reclaims 95 percent of the lithium in spent electric vehicle batteries"),
    ("climate_grid", "climate", "Grid-scale storage hits 100 gigawatt-hours installed worldwide", None),
    ("climate_heat", "climate", "Heat pump sales pass gas boilers in Europe for the first year", None),
    ("climate_carbon", "climate", "Direct air capture plant in Iceland starts storing CO2 at commercial scale", None),
    ("climate_solar", "climate", "Perovskite solar panels reach 30 percent efficiency in outdoor tests",
     "Outdoor trials show perovskite solar cells hitting 30 percent efficiency"),
    ("climate_data", "climate", "Data centers now use 4 percent of national electricity, regulator reports", None),
    ("climate_rail", "climate", "New train line connects the airport to downtown in 18 minutes", None),
    ("biz_layoffs", "business", "Cloud startup Nimbus lays off 30 percent of staff after missing revenue targets",
     "Nimbus cuts 30 percent of its workforce following a revenue shortfall"),
    ("biz_ipo", "business", "Developer tools company Ferrous files for an IPO at a 9 billion dollar valuation", None),
    ("biz_remote", "business", "Four-day week trial at 60 tech companies ends with 90 percent keeping it", None),
    ("biz_acq", "business", "Database vendor Lumen acquires observability startup Tracewise for 400 million",
     "Lumen buys observability company Tracewise in a 400 million dollar deal"),
    ("biz_opensource", "business", "Open-source maintainers fund launches with 20 million from five cloud providers", None),
    ("biz_pricing", "business", "Per-seat software pricing gives way to usage-based billing, survey of 500 vendors finds", None),
    ("biz_chips", "business", "Chip export rules tighten again; hardware startups warn of 12-month delays", None),
]

FILLER_TEMPLATES = [
    "{project} {version} released with {feature} and {feature2}",
    "{company} migrates its {system} to {tech} and reports {gain}",
    "Why {team} replaced {old} with {new}: a two-year retrospective",
    "{project} maintainers deprecate {feature} ahead of the {version} release",
    "Benchmark: {tech} versus {tech2} on {workload}",
    "{company} open-sources {tool}, its internal {purpose} tool",
    "Postmortem: {incident} at {company} traced to {cause}",
    "{conference} talk: lessons from running {tech} at {scale}",
]
SLOTS = {
    "project": ["Nginx", "Redis", "Terraform", "Vite", "Svelte", "Deno", "Bun", "Zig", "Go", "Kotlin", "Swift", "Elixir", "Tokio", "Polars", "Ray", "Airflow", "Kafka", "NATS", "Caddy", "Traefik"],
    "version": ["2.0", "3.1", "4.0", "5.2", "7.0", "1.9", "12", "0.9"],
    "feature": ["structured logging", "a plugin API", "incremental builds", "zero-copy parsing", "live reload", "typed configuration", "native tracing", "workspace support", "a new scheduler", "lazy loading"],
    "feature2": ["faster startup", "lower memory use", "better error messages", "Windows ARM builds", "a stable ABI", "signed releases"],
    "company": ["Nimbus", "Lumen", "Ferrous", "Orbital Labs", "Helion", "Voltaic", "Tracewise", "Fairline", "Cloudbeat", "Stackdaily"],
    "system": ["billing pipeline", "search backend", "CI fleet", "event bus", "feature store", "edge network", "data warehouse", "auth service"],
    "tech": ["Rust", "Go", "Postgres", "ClickHouse", "Kafka", "gRPC", "WebAssembly", "Arrow", "SQLite", "Nix"],
    "tech2": ["Java", "Node.js", "MySQL", "Elasticsearch", "RabbitMQ", "REST", "containers", "Parquet", "LevelDB", "Docker"],
    "gain": ["40 percent lower cost", "half the latency", "a 3x throughput gain", "zero on-call pages in a quarter", "a 70 percent smaller fleet"],
    "team": ["a payments team", "a maps startup", "the platform group", "a games studio", "a hospital network", "an airline"],
    "old": ["microservices", "a monolith", "Jenkins", "spreadsheets", "a NoSQL store", "cron jobs"],
    "new": ["a modular monolith", "serverless functions", "GitHub Actions", "a real database", "Postgres", "a workflow engine"],
    "workload": ["time-series ingestion", "JSON parsing", "analytics queries", "image resizing", "log search", "message fan-out"],
    "tool": ["Beacon", "Lattice", "Quill", "Harbor", "Sprocket", "Compass", "Ledger", "Prism"],
    "purpose": ["incident management", "feature flagging", "schema migration", "cost monitoring", "load testing", "secrets rotation", "release orchestration", "data lineage"],
    "incident": ["a 90-minute outage", "duplicate invoices", "a 6-hour login failure", "lost telemetry", "a stuck deploy"],
    "cause": ["an expired certificate", "a leap-second bug", "a misconfigured autoscaler", "DNS caching", "a schema migration lock"],
    "conference": ["KubeCon", "PyCon", "RustConf", "QCon", "SREcon", "Strange Loop"],
    "scale": ["ten thousand nodes", "a petabyte a day", "a million users", "500 clusters", "the edge"],
}

PAIRS = [
    ("The build cache cut compile times from forty minutes to six.", "מטמון הבנייה קיצר את זמני הקומפילציה מארבעים דקות לשש."),
    ("The city will test a new traffic light system next spring.", "העירייה תנסה מערכת רמזורים חדשה באביב הקרוב."),
    ("Temperature divides the logits before the softmax.", "הטמפרטורה מחלקת את הלוגיטים לפני הסופטמקס."),
    ("Our cat sleeps on the keyboard every afternoon.", "החתולה שלנו ישנה על המקלדת כל אחר צהריים."),
    ("The library closes early on Fridays.", "הספרייה נסגרת מוקדם בימי שישי."),
    ("A retry is only safe for transient failures.", "ניסיון חוזר בטוח רק לכשלים זמניים."),
    ("The recipe needs three eggs and a cup of flour.", "המתכון דורש שלוש ביצים וכוס קמח."),
    ("Satellites photographed the storm from orbit.", "לוויינים צילמו את הסופה מהמסלול."),
    ("The new train line connects the airport to downtown.", "קו הרכבת החדש מחבר את שדה התעופה למרכז העיר."),
    ("Students must submit the assignment by midnight.", "הסטודנטים חייבים להגיש את המטלה עד חצות."),
]

# query, relevant base keys (the paraphrase of a key, when it exists, is relevant too)
QUERIES: list[tuple[str, list[str]]] = [
    ("faster rust builds with a shared cache", ["cargo_cache"]),
    ("compile times cut dramatically", ["cargo_cache", "rust_survey"]),
    ("E0502", ["rust_e0502"]),
    ("borrow checker rejects mutable reference", ["rust_e0502"]),
    ("Python 3.14 free-threaded", ["py_314"]),
    ("kubernetes upgrade broke pod networking", ["k8s_cni"]),
    ("clusters over-request CPU", ["k8s_cost"]),
    ("database outage caused by a long transaction", ["db_postmortem"]),
    ("CVE-2026-1234", ["sec_cve"]),
    ("password leak millions of users", ["sec_breach"]),
    ("typosquatting attack on a package registry", ["sec_supply"]),
    ("LLM judges biased toward long answers", ["ai_evals"]),
    ("does long context make retrieval obsolete", ["ai_rag"]),
    ("GPU supply improving", ["hw_gpu"]),
    ("when will humans land on the moon again", ["space_moon"]),
    ("recovering lithium from old EV batteries", ["climate_recycle"]),
    ("tech company layoffs after missing targets", ["biz_layoffs"]),
    ("vector search inside sqlite", ["db_sqlite"]),
    ("שדרוג קוברנטיס שבר את הרשת", ["k8s_cni"]),
    ("Helm 4 OCI charts", ["k8s_helm"]),
]


def main() -> None:
    rng = random.Random(2026)
    headlines: list[dict] = []
    key_to_ids: dict[str, list[str]] = {}

    def add(text: str, topic: str, key: str | None = None) -> None:
        hid = f"h{len(headlines) + 1:03d}"
        day = 20260901 + rng.randrange(0, 32)
        if day % 100 > 30:
            day = 20261001 + (day % 100 - 31)
        headlines.append({"id": hid, "text": text, "topic": topic, "source": rng.choice(SOURCES), "day": day})
        if key:
            key_to_ids.setdefault(key, []).append(hid)

    for key, topic, text, paraphrase in BASE:
        add(text, topic, key)
        if paraphrase:
            add(paraphrase, topic, key)

    seen = {h["text"] for h in headlines}
    while len(headlines) < 200:
        template = rng.choice(FILLER_TEMPLATES)
        text = template.format(**{slot: rng.choice(values) for slot, values in SLOTS.items()})
        if text in seen:
            continue
        seen.add(text)
        add(text, "misc")

    rng.shuffle(headlines)
    # Re-number after the shuffle so ids are not topic-ordered. Build the whole old->new map first and apply it
    # once: renaming in place while iterating let an already-renamed id collide with a later headline's old id,
    # which silently mislabelled half of the queries (found in the 2026-10-03 self-review).
    renumber = {h["id"]: f"h{n:03d}" for n, h in enumerate(headlines, start=1)}
    for h in headlines:
        h["id"] = renumber[h["id"]]
    for ids in key_to_ids.values():
        ids[:] = [renumber[i] for i in ids]

    out12 = ROOT / "exercises/ch12-embeddings/data"
    out13 = ROOT / "exercises/ch13-search/data"
    out12.mkdir(parents=True, exist_ok=True)
    out13.mkdir(parents=True, exist_ok=True)
    (out12 / "headlines.jsonl").write_text("".join(json.dumps(h, ensure_ascii=False) + "\n" for h in headlines), encoding="utf-8")
    (out12 / "pairs.jsonl").write_text("".join(json.dumps({"en": en, "he": he}, ensure_ascii=False) + "\n" for en, he in PAIRS), encoding="utf-8")
    queries = [
        {"id": f"q{n:02d}", "query": q, "relevant": sorted(i for k in keys for i in key_to_ids[k])}
        for n, (q, keys) in enumerate(QUERIES, start=1)
    ]
    (out13 / "queries.jsonl").write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in queries), encoding="utf-8")
    planted = sum(1 for _, _, _, p in BASE if p)
    print(f"headlines: {len(headlines)} (bases {len(BASE)}, planted near-duplicate pairs {planted}, filler {len(headlines) - len(BASE) - planted})")
    print(f"pairs: {len(PAIRS)} | queries: {len(queries)}")


if __name__ == "__main__":
    main()
