from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin')
        u.set_password('admin123')
        db.session.add(u)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
