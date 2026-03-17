from extensions import db
from datetime import date, datetime

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    # Ensure this is db.Date and not db.DateTime
    attendance_date = db.Column(db.Date, nullable=False) 
    status = db.Column(db.String(10))
    
    student = db.relationship("Students", backref="attendance_records")    
    
# 6. LEAVE MODEL
class Leave(db.Model):
    __tablename__ = "leaves"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)   
    student = db.relationship("Students", backref="all_leaves")
