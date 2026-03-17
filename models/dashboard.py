from extensions import db

class Syllabus(db.Model):
    __tablename__ = "syllabus" 
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    ch_no = db.Column(db.Integer, nullable=False)
    ch_name = db.Column(db.String(200), nullable=False)
    progress_records = db.relationship('Student_progress', backref='chapter', cascade="all, delete-orphan")

class Student_progress(db.Model):
    __tablename__ = "student_progress"
       
    id = db.Column(db.Integer, primary_key=True) 
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('syllabus.id'), nullable=False)
    status = db.Column(db.String(20), default="Average") 
    