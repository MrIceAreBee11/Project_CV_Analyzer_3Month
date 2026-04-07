"""
Seeder: skill_dictionary_seeder.py
Layer  : Infrastructure > Persistence > Seeders
Fungsi : Mengisi tabel skill_dictionaries dengan data awal
Phase  : 2 - Basic Parser

Cara pakai:
    python -m src.infrastructure.persistence.seeders.skill_dictionary_seeder

Atau panggil fungsi run() dari script lain.
"""

import json
from sqlalchemy.orm import Session
from config.database import SessionLocal


# ── Data Seed ─────────────────────────────────────────────────────────────────
# Format: (skill_name, normalized_name, category, aliases_list)
SKILL_SEED_DATA = [

    # ── Backend ────────────────────────────────────────────────────────────────
    ("Python",       "python",       "backend",  ["py", "python3"]),
    ("FastAPI",      "fastapi",      "backend",  ["fast api"]),
    ("Django",       "django",       "backend",  ["django rest framework", "drf"]),
    ("Flask",        "flask",        "backend",  []),
    ("Node.js",      "nodejs",       "backend",  ["node", "nodejs", "node js"]),
    ("Express.js",   "expressjs",    "backend",  ["express", "expressjs"]),
    ("Laravel",      "laravel",      "backend",  []),
    ("Spring Boot",  "springboot",   "backend",  ["spring", "spring framework"]),
    ("Go",           "go",           "backend",  ["golang"]),
    ("PHP",          "php",          "backend",  []),
    ("Java",         "java",         "backend",  []),
    ("Kotlin",       "kotlin",       "backend",  []),

    # ── Frontend ───────────────────────────────────────────────────────────────
    ("JavaScript",   "javascript",   "frontend", ["js", "ecmascript", "es6"]),
    ("TypeScript",   "typescript",   "frontend", ["ts"]),
    ("React",        "react",        "frontend", ["react.js", "reactjs"]),
    ("Vue.js",       "vuejs",        "frontend", ["vue", "vuejs", "vue js"]),
    ("Angular",      "angular",      "frontend", ["angularjs"]),
    ("Next.js",      "nextjs",       "frontend", ["next", "nextjs"]),
    ("HTML",         "html",         "frontend", ["html5"]),
    ("CSS",          "css",          "frontend", ["css3"]),
    ("Tailwind CSS", "tailwindcss",  "frontend", ["tailwind"]),
    ("Bootstrap",    "bootstrap",    "frontend", []),
    ("Figma",        "figma",        "design",   ["figma design"]),
    ("Canva",        "canva",        "design",   []),
    ("UI Design",    "uidesign",     "design",   ["ui designer", "ui/ux", "user interface"]),
    ("UI/UX Design",         "uiuxdesign",       "design",    ["ui/ux", "ui design", "ux design", "user interface", "user experience"]),

    # ── Database ───────────────────────────────────────────────────────────────
    ("MySQL",        "mysql",        "database", []),
    ("PostgreSQL",   "postgresql",   "database", ["postgres", "psql"]),
    ("MongoDB",      "mongodb",      "database", ["mongo"]),
    ("Redis",        "redis",        "database", []),
    ("SQLite",       "sqlite",       "database", []),
    ("Oracle",       "oracle",       "database", ["oracle db"]),
    ("SQL Server",   "sqlserver",    "database", ["mssql", "microsoft sql server"]),
    ("Elasticsearch","elasticsearch","database", ["elastic", "es"]),
    ("Microsoft Office",     "microsoftoffice",      "tools",    ["ms office", "microsoft office suite", "word", "excel", "powerpoint"]),
    ("Google Workspace",     "googleworkspace",      "tools",    ["gsuite", "google docs", "google sheets", "google slides"]),
    ("Jira",         "jira",         "tools",    []),
    ("Confluence",   "confluence",   "tools",    []),
    ("Slack",        "slack",        "tools",    []),
    ("Trello",       "trello",       "tools",    []),
    ("Asana",        "asana",        "tools",    []),
    ("Notion",       "notion",       "tools",    []),
    ("GitHub",       "github",       "tools",    ["github.com"]),
    ("GitLab",       "gitlab",       "tools",    ["gitlab.com"]),
    ("Bitbucket",    "bitbucket",    "tools",    ["bitbucket.org"]),
    ("Visual Studio Code", "vscode", "tools", ["visual studio code", "vs code"]),
    ("IntelliJ IDEA", "intellij", "tools", ["intellij idea", "idea"]),
    ("PyCharm",      "pycharm",      "tools",    []),
    ("WebStorm",     "webstorm",     "tools",    []),
    ("Postman",      "postman",      "tools",    []),
    ("Swagger",      "swagger",      "tools",    ["openapi"]),
    ("Docker Compose","dockercompose", "devops",   ["docker compose"]),

    # ── DevOps & Cloud ─────────────────────────────────────────────────────────
    ("Docker",       "docker",       "devops",   []),
    ("Kubernetes",   "kubernetes",   "devops",   ["k8s"]),
    ("Git",          "git",          "devops",   ["github", "gitlab", "bitbucket"]),
    ("CI/CD",        "cicd",         "devops",   ["continuous integration", "continuous deployment"]),
    ("Jenkins",      "jenkins",      "devops",   []),
    ("AWS",          "aws",          "cloud",    ["amazon web services"]),
    ("GCP",          "gcp",          "cloud",    ["google cloud", "google cloud platform"]),
    ("Azure",        "azure",        "cloud",    ["microsoft azure"]),
    ("Nginx",        "nginx",        "devops",   []),
    ("Linux",        "linux",        "devops",   ["ubuntu", "centos", "debian"]),

    # ── Mobile ─────────────────────────────────────────────────────────────────
    ("Android",      "android",      "mobile",   []),
    ("iOS",          "ios",          "mobile",   ["swift", "objective-c"]),
    ("Flutter",      "flutter",      "mobile",   []),
    ("React Native", "reactnative",  "mobile",   ["react-native"]),

    # ── Data & AI ──────────────────────────────────────────────────────────────
    ("Machine Learning","machinelearning","data", ["ml"]),
    ("Deep Learning",  "deeplearning",  "data",  ["dl"]),
    ("TensorFlow",   "tensorflow",   "data",     []),
    ("PyTorch",      "pytorch",       "data",    []),
    ("Pandas",       "pandas",        "data",    []),
    ("NumPy",        "numpy",         "data",    []),
    ("Scikit-learn", "scikitlearn",   "data",    ["sklearn"]),
    ("SQL",          "sql",           "data",    []),
    ("Tableau",      "tableau",       "data",    []),
    ("Power BI",     "powerbi",       "data",    ["powerbi"]),

    # Languages & Tools
    ("Bahasa Inggris", "bahasainggris", "language",  ["english", "inggris", "bahasa inggris (b1)", "b1", "b2"]),
    ("Typing Speed",   "typingspeed", "tools",     ["kecepatan mengetik", "wpm", "typing"]),
   
    # Soft Skills
    ("Project Management",   "projectmanagement","softskill", ["project manager", "manajemen proyek"]),
    ("Communication",        "communication",    "softskill", ["komunikasi", "komunikasi efektif"]),
    ("Analytical Thinking",  "analyticalthinking","softskill",["berpikir analitis", "analytical"]),
    ("Time Management",      "timemanagement",   "softskill", ["manajemen waktu"]),

    # Data
    ("Data Mining",          "datamining",       "data",      ["data mine"]),
    ("Data Analysis",        "dataanalysis",     "data",      ["analisis data", "data analytics", "data analyst"]),
    ("Data Entry",           "dataentry",        "data",      ["entri data"]),

    ("Inventory Management",  "inventorymanagement", "operations", ["manajemen persediaan", "inventory"]),
    ("Point of Sale",         "pointofsale",         "tools",      ["pos", "sistem point of sale", "point of sale system"]),
    ("Merchandising",         "merchandising",       "operations", ["visual merchandising"]),
    ("Budgeting",             "budgeting",           "operations", ["penganggaran", "budget"]),
    ("Customer Service",      "customerservice",     "softskill",  ["pelayanan pelanggan", "customer care"]),
    ("Teamwork",              "teamwork",            "softskill",  ["kerja sama tim", "team work", "kolaborasi"]),
]



def run(db: Session) -> None:
    """
    Jalankan seeder untuk tabel skill_dictionaries.
    Skip jika skill sudah ada (idempotent).
    """
    from src.infrastructure.persistence.models.skill_dictionary_model import (
        SkillDictionaryModel
    )

    inserted = 0
    skipped = 0

    for skill_name, normalized, category, aliases in SKILL_SEED_DATA:
        # Cek apakah sudah ada
        existing = (
            db.query(SkillDictionaryModel)
            .filter(SkillDictionaryModel.skill_name == skill_name)
            .first()
        )

        if existing:
            skipped += 1
            continue

        skill = SkillDictionaryModel(
            skill_name=skill_name,
            normalized_skill_name=normalized,
            category=category,
            aliases_json=json.dumps(aliases) if aliases else None,
            is_active=True,
        )
        db.add(skill)
        inserted += 1

    db.commit()
    print(f"[SkillDictionarySeeder] Inserted: {inserted}, Skipped: {skipped}")


if __name__ == "__main__":
    db: Session = SessionLocal()
    try:
        run(db)
    finally:
        db.close()