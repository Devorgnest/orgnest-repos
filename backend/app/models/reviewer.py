from backend.app import db

class Reviewer(db.Model):
    __tablename__ = 'reviewers_list'
    id = db.Column(db.Integer, primary_key=True)
    primary_reviewer = db.Column(db.Text)
    hr_reviewer = db.Column(db.Text)
    hiring_manager = db.Column(db.Text)
