"""Local smoke test: imports app_web against a throwaway SQLite DB and exercises
login, lookup, details, and form submissions. Touches NO real data.
Run:  python3 smoke_test.py
"""
import os, sys, tempfile
from datetime import datetime

tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp.close()
os.environ["SECRET_KEY"] = "smoke-test-key"
os.environ["SETUP_KEY"] = "smoke-test-setup"  # throwaway test value; app still fails fast without it in production
os.environ["DATABASE_URL"] = "sqlite:///" + tmp.name

import app_web
from werkzeug.security import generate_password_hash

app, db = app_web.app, app_web.db
results = []

def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))

with app.app_context():
    db.create_all()
    db.session.add_all([
        app_web.User(username="admin1", password_hash=generate_password_hash("pw", method="pbkdf2:sha256"), role="admin"),
        app_web.User(username="tech1", password_hash=generate_password_hash("pw", method="pbkdf2:sha256"), role="tech"),
        app_web.Appliance(store_name="Test", item_number="1234", brand="Acme",
                          model="M1", serial="S1", status="In"),
    ])
    db.session.commit()
check("import + init + create_all", True)

c = app.test_client()
r = c.post("/", data={"username": "tech1", "password": "bad"})
check("login rejects bad password", r.status_code == 200 and b"Invalid" in r.data, r.status_code)
r = c.post("/", data={"username": "tech1", "password": "pw"})
check("tech login redirects", r.status_code == 302 and "tech-dashboard" in r.location, r.status_code)
r = c.get("/tech-dashboard")
check("tech dashboard loads", r.status_code == 200 and b"1234" in r.data, r.status_code)
for label, data in [("item only", {"item_number": "1234"}), ("store only", {"store_name": "Test"}),
                    ("store+item", {"store_name": "Test", "item_number": "1234"})]:
    r = c.post("/tech-lookup", data=data)
    check(f"lookup {label} -> details redirect", r.status_code == 302 and "/tech-appliance-details/Test/1234" in r.location, r.status_code)
r = c.get("/tech-appliance-details/Test/1234")
check("details page shows brand/model", r.status_code == 200 and b"Acme" in r.data and b"M1" in r.data, r.status_code)
r = c.post("/tech-edit/Test/1234", data={"status": "Checked", "notes": "n", "verified_model": "M1", "verified_serial": "S1"})
check("tech edit success submit", r.status_code == 302, r.status_code)
with app.app_context():
    rec = app_web.Appliance.query.filter_by(store_name="Test", item_number="1234").first()
    check("edit persisted: status + notes", rec.status == "Checked" and rec.notes == "n", (rec.status, rec.notes))
    check("edit persisted: last_updated is a datetime", isinstance(rec.last_updated, datetime), type(rec.last_updated))
    hist = app_web.StatusHistory.query.filter_by(appliance_id=rec.id, status="Checked").all()
    tech = app_web.User.query.filter_by(username="tech1").first()
    check("edit persisted: status history row w/ verified model, serial, user",
          len(hist) == 1 and hist[0].verified_model == "M1" and hist[0].verified_serial == "S1" and hist[0].user_id == tech.id,
          [(h.status, h.verified_model, h.verified_serial, h.user_id) for h in hist])
# validation failure path (needs first_change=True, so use a fresh appliance)
with app.app_context():
    db.session.add(app_web.Appliance(store_name="Test", item_number="9999", brand="B", model="M", serial="S", status="In"))
    db.session.commit()
r = c.post("/tech-edit/Test/9999", data={"status": "Checked", "notes": "", "verified_model": "", "verified_serial": ""})
check("tech edit validation failure renders form", r.status_code == 200, r.status_code)
with app.app_context():
    rec = app_web.Appliance.query.filter_by(item_number="9999").first()
    check("validation failure persisted nothing", rec.status == "In" and not app_web.StatusHistory.query.filter_by(appliance_id=rec.id).all(), rec.status)

a = app.test_client()
r = a.post("/", data={"username": "admin1", "password": "pw"})
check("admin login redirects", r.status_code == 302 and "admin-dashboard" in r.location, r.status_code)
r = a.get("/admin-dashboard")
check("admin dashboard loads", r.status_code == 200, r.status_code)

os.unlink(tmp.name)
print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
