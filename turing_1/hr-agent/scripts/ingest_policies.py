"""
Create sample company policy files and ingest them into Chroma.
Run: python scripts/ingest_policies.py
"""
from pathlib import Path
from app.rag.rag_service import ingest_documents_from_folder

DATA_DIR = Path("data/company_policies")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# sample docs
samples = {
    "leave_policy.txt": """Annual leave: Employees are entitled to 12 days of paid annual leave per year.
Sick leave: 6 days of paid sick leave per year.
Casual leave: 4 days per year. For more details contact HR.""",
    "expense_policy.txt": """Capex and expense policy: Team capex approvals require manager sign-off.
Bonuses are paid as per yearly review cycle. Expense claims should include receipts.""",
    "security_policy.txt": """Security policy: Use company VPN for remote access. Do not share credentials.
Report incidents to security@company.com."""
}

# write samples
for name, text in samples.items():
    p = DATA_DIR / name
    if not p.exists():
        p.write_text(text, encoding="utf-8")

res = ingest_documents_from_folder(str(DATA_DIR))
print(res)
