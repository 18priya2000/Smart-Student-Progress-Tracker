from datetime import date
from extensions import db


class Students(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    parent_email = db.Column(db.String(120), nullable=False) 
    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))

    parent = db.relationship("User", backref="children")
    student_class = db.relationship("Class", backref="students")


class Subjects(db.Model):
    __tablename__ = "subjects" 
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(200), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    
    teacher = db.relationship('User', backref='teaching_subjects')


class Marks(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.Date, default=date.today)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)

    student = db.relationship("Students", backref="marks")
    subject = db.relationship("Subjects", backref="marks")
    
    
    
    
class Tests(db.Model):
    __tablename__ = "tests"

    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    subject = db.relationship("Subjects", backref="tests")
    
    
    
class Class(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), unique=True) # e.g. "Class 10"    