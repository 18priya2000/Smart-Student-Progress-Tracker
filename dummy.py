import random
from datetime import date
from werkzeug.security import generate_password_hash

from app import db, create_app
from models.users import User
from models.classes import Class, Students, Subjects, Tests
from models.dashboard import Syllabus, Student_progress

app = create_app()

with app.app_context():
    print("🚀 Cleaning database and starting fresh...")
    db.drop_all() 
    db.create_all() 
    
    # 1. CREATE ADMIN
    admin = User(
        username="admin",
        email="admin@school.com", 
        password=generate_password_hash("123"), 
        role="admin"
    )
    db.session.add(admin)

    # 2. CREATE CLASSES (1 to 8)
    class_map = {}
    for i in range(1, 9):
        c = Class(class_name=f"Class {i}")
        db.session.add(c)
        db.session.flush() # This generates the ID without a full commit yet
        class_map[i] = c.id
    
    print("✅ Admin and Classes 1-8 created.")

    # 3. TEACHERS, SUBJECTS & SYLLABUS (For Classes 4 & 5)
    sub_names = ["Maths", "English", "Science", "Social", "Hindi"]
    
    for c_num in [4, 5]:
        cls_id = class_map[c_num]
        for sn in sub_names:
            full_sub_name = f"C{c_num}-{sn}"
            t_email = f"teacher_{sn.lower()}_c{c_num}@school.com"
            
            # Create Teacher
            t = User(
                username=f"T_{sn}_C{c_num}", 
                email=t_email, 
                password=generate_password_hash("123"), 
                role="teacher"
            )
            db.session.add(t)
            db.session.flush()

            # Create Subject
            new_sub = Subjects(subject_name=full_sub_name, class_id=cls_id, teacher_id=t.id)
            db.session.add(new_sub)
            db.session.flush()

            # Create Syllabus (5 Chapters)
            for ch in range(1, 6):
                chp = Syllabus(ch_no=ch, ch_name=f"Chapter {ch}: Basic {sn}", subject_id=new_sub.id)
                db.session.add(chp)

            # Create Test Slots
            for tt in ["Unit Test", "Mid Term", "Final"]:
                tst = Tests(
                    test_name=f"{full_sub_name} - {tt}", 
                    test_date=date.today(), 
                    subject_id=new_sub.id, 
                    teacher_id=t.id
                )
                db.session.add(tst)

    # 4. STUDENTS, PARENTS & PROGRESS
    db.session.commit() # Commit here so we can query Syllabus chapters
    all_chapters = Syllabus.query.all()
    
    for c_num in [4, 5]:
        cls_id = class_map[c_num]
        for s_num in range(1, 6):
            roll = f"S{c_num}-{s_num}"
            p_email = f"parent_{roll.lower()}@test.com"
            
            # Create Parent
            p = User(
                username=f"Parent_{roll}", 
                email=p_email, 
                password=generate_password_hash("123"), 
                role="parent"
            )
            db.session.add(p)
            db.session.flush()
            
            # Create Student
            s = Students(
                name=f"Student {roll}", 
                roll_no=roll, 
                parent_email=p_email, 
                parent_id=p.id, 
                class_id=cls_id
            )
            db.session.add(s)
            db.session.flush()

            # Syllabus Progress Entry
            # Find chapters belonging to this student's class
            student_subs = Subjects.query.filter_by(class_id=cls_id).all()
            sub_ids = [sub.id for sub in student_subs]
            
            for chp in all_chapters:
                if chp.subject_id in sub_ids:
                    prog = Student_progress(
                        student_id=s.id, 
                        chapter_id=chp.id, 
                        status=random.choice(["Best", "Average", "Weak", "Completed"])
                    )
                    db.session.add(prog)

    db.session.commit()
    print("✅ Mega Database Ready! All constraints passed.")