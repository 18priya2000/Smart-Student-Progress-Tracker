from flask import Flask, flash, request, redirect, url_for, render_template
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta, datetime
from flask_mail import Mail, Message
from datetime import datetime 
from flask import current_app
from config.config import Config 
from extensions import db
from models.users import User
from models.other import Leave, Attendance
from models.classes import Class, Students, Subjects, Marks, Tests
from models.dashboard import Syllabus, Student_progress
from datetime import date, timedelta, datetime
import joblib # Ensure you have joblib imported at the top
from models import Attendance # Ensure Attendance is imported

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME='priyaviroja7@gmail.com',
        MAIL_PASSWORD='qmsv ntts ovvz ziuj'
    )

    db.init_app(app)
    mail.init_app(app)


    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    @app.route("/")
    def home():
        return redirect(url_for("login")) 


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            
            login_id = request.form.get("email").strip() 
            password = request.form.get("password").strip()
            user = User.query.filter((User.email == login_id) | (User.username == login_id)).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash(f"Login successful! Welcome back, {user.username}.", "success")
                
                if user.role == 'admin':return redirect(url_for('admin_panel'))
                    
                elif user.role == 'teacher': return redirect(url_for('dashboard'))
                   
                elif user.role == 'parent':return redirect(url_for('parent_dashboard'))
                    
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
                
            else:
                flash("Invalid emails or password.", "danger")
                return render_template("login.html")
                    
        return render_template("login.html")
  
    
    @app.route("/dashboard")
    @login_required
    def dashboard():
        subject = Subjects.query.filter_by(teacher_id=current_user.id).first()
        if not subject: return "No Subject Assigned", 404
        
        students = Students.query.filter_by(class_id=subject.class_id).all()
        syllabus_list = Syllabus.query.filter_by(subject_id=subject.id).order_by(Syllabus.ch_no).all()
      
        all_tests = db.session.query(Marks.test_name).filter_by(subject_id=subject.id).distinct().all()
        selected_test = request.args.get('test_filter', 'Overall')

        if selected_test != 'Overall':
            marks_data = Marks.query.filter_by(test_name=selected_test, subject_id=subject.id).distinct().all()
        else:
            marks_data = Marks.query.filter_by(subject_id=subject.id).all()

        passed = len([m for m in marks_data if m.marks >= 33])
        failed = len([m for m in marks_data if m.marks < 33])
        top = len([m for m in marks_data if m.marks >= 75])
        absent = len([m for m in marks_data if m.marks is None])
        scores = [m.marks  for m in marks_data]
        avg = (sum(scores) / len(scores) if len(scores) > 0 else 0)
        avgs = len([m for m in marks_data if m.marks >= 33 and m.marks < 75 ])

        return render_template("dashboard.html", subject=subject, students=students, 
                               syllabus=syllabus_list, 
                               all_tests=all_tests, selected_test=selected_test,
                               pie_data=[top, avgs, failed], avg_marks=round(avg, 2))
       
     
    @app.route("/add_syllabus", methods=["GET", "POST"]) 
    @login_required
    def add_syllabus():

        subject = Subjects.query.filter_by(teacher_id=current_user.id).first()

        if not subject:
            return "Error: No subject assigned to you. Please contact admin."

        if request.method == "POST":
            new_chapter = Syllabus(
                ch_no=request.form.get("ch_no"), 
                ch_name=request.form.get("ch_name"), 
                subject_id=subject.id
            )
            db.session.add(new_chapter)
            db.session.commit()
            return redirect(url_for("dashboard")) 
        
        return render_template("add_syllabus.html", subject=subject)

    @app.route("/delete_chapter/<int:ch_id>", methods=["POST"])
    @login_required
    def delete_chapter(ch_id):
        chapter = Syllabus.query.get_or_404(ch_id)
        db.session.delete(chapter)
        db.session.commit()
        return redirect(url_for("dashboard"))

    @app.route("/update_chapter/<int:ch_id>", methods=["GET", "POST"])
    @login_required
    def update_chapter(ch_id):
        chapter = Syllabus.query.get_or_404(ch_id)
        
        if request.method == "POST":
            chapter.ch_no = request.form.get("ch_no")
            chapter.ch_name = request.form.get("ch_name")
            
            db.session.commit()
            return redirect(url_for("dashboard"))
    
        return render_template("update_chapter.html", chapter=chapter) 
    
            
    @app.route("/progress_grid") 
    @login_required
    def progress_grid():
        subject = Subjects.query.filter_by(teacher_id=current_user.id).first()
        if not subject:
            return "No subject assigned", 404

        chapters = Syllabus.query.filter_by(subject_id=subject.id).order_by(Syllabus.ch_no).all()
        students = Students.query.filter_by(class_id=subject.class_id).all()

        chapter_ids = [c.id for c in chapters]
        student_ids = [s.id for s in students]
        
        existing_records = Student_progress.query.filter(
            Student_progress.student_id.in_(student_ids),
            Student_progress.chapter_id.in_(chapter_ids)
        ).all()

        progress_map = {(r.student_id, r.chapter_id): r.status for r in existing_records}

        return render_template("grid.html", 
                            chapters=chapters, 
                            students=students, 
                            progress_map=progress_map)

    @app.route("/save_progress", methods=["POST"])
    @login_required
    def save_progress():
        for key, value in request.form.items():
            if key.startswith("status_"):
                parts = key.split("_")
               
                if len(parts) == 3:
                    try:
                        s_id = int(parts[1])
                        c_id = int(parts[2])
                        
                        record = Student_progress.query.filter_by(student_id=s_id, chapter_id=c_id).first()
                        
                        if record:
                            record.status = value
                        else:
                            new_prog = Student_progress(student_id=s_id, chapter_id=c_id, status=value)
                            db.session.add(new_prog)
                    except ValueError:
                        continue 
                else:
                    print(f"Skipping invalid key: {key}")

        db.session.commit()
        flash("?Update successfully!", "success")
        return redirect(url_for('progress_grid'))

    @app.route("/attendance", methods=["GET", "POST"])
    @login_required
    def attendance():
        subject = Subjects.query.filter_by(teacher_id=current_user.id).first()
        if not subject:
            
            return "No subject assigned", 404
            
        students = Students.query.filter_by(class_id=subject.class_id).all()
        today = date.today()
        valid_dates = []
        check_date = today
        while len(valid_dates) < 6:
            if check_date.weekday() != 6: 
                valid_dates.append(check_date)
            check_date -= timedelta(days=1)

        date_str = request.args.get("date")
        if date_str:
            try:
                selected_date = date.fromisoformat(date_str)
            except ValueError:
                selected_date = today
        else:
           
            selected_date = today if today.weekday() != 6 else valid_dates[0]

        if request.method == "POST":
            posted_date_str = request.form.get("attendance_date")
        
            posted_date = date.fromisoformat(posted_date_str)
            
            for s in students:
                status = request.form.get(f"status_{s.id}")
                if status:
                   
                    rec = Attendance.query.filter_by(
                        student_id=s.id, 
                        attendance_date=posted_date
                    ).first()
                    
                    if rec:
                        rec.status = status
                    else:
                        new_attendance = Attendance(
                            student_id=s.id, 
                            attendance_date=posted_date, 
                            status=status
                        )
                        db.session.add(new_attendance)
            
            db.session.commit()
          
            return redirect(url_for("attendance", date=posted_date.isoformat()))

        attendance_records = Attendance.query.filter_by(
            attendance_date=selected_date
        ).all()
        
        attendance_map = {r.student_id: r.status for r in attendance_records}

        return render_template("attendance.html", 
                            students=students, 
                            attendance=attendance_map, 
                            dates=valid_dates, 
                            selected_date=selected_date)
    


    @app.route("/prediction/<int:student_id>")
    @login_required
    def prediction(student_id): 
        student = Students.query.get_or_404(student_id)
        past_marks = Marks.query.filter_by(student_id=student_id).all()
        
        total_days = Attendance.query.filter_by(student_id=student_id).count()
        present_days = Attendance.query.filter_by(student_id=student_id, status='Present').count()
        att_rate = (present_days / total_days * 100) if total_days > 0 else 75
        
        progress_records = Student_progress.query.filter_by(student_id=student_id).all()
        best = len([p for p in progress_records if p.status == 'Best'])
        weak = len([p for p in progress_records if p.status == 'Weak'])
        average = len([p for p in progress_records if p.status == 'Average'])

        pred = 75 + (best * 2) - (weak * 5)

        subject = Subjects.query.filter_by(class_id=student.class_id).first()
        syllabus = Syllabus.query.filter_by(subject_id=subject.id).all() if subject else []
        status_map = {p.chapter_id: p.status for p in progress_records}

        return render_template(
            "prediction.html",
            student=student, 
            syllabus=syllabus, 
            status_map=status_map,
            prediction=pred,
            best=best, 
            weak=weak,
            marks=past_marks, 
            average=average,
            attendance=round(att_rate, 1)
        )

    @app.route("/leave-approval")
    @login_required
    def leave_approval():
        teacher_sub = Subjects.query.filter_by(teacher_id=current_user.id).first()
        
        leaves = Leave.query.join(Students).filter(
            Students.class_id == teacher_sub.class_id,
            Leave.status == "pending" 
        ).all()
        
        return render_template("leave_approval.html", leaves=leaves)
    

    @app.route("/marks", methods=["GET", "POST"])
    @login_required
    def marks():
        teacher_subject = Subjects.query.filter_by(teacher_id=current_user.id).first()
        
        if not teacher_subject:
            flash("You are not assigned to any subject.", "warning")
            return redirect(url_for("dashboard"))

        subject_id = str(teacher_subject.id)
        test_id = request.args.get("test_id")
        
        if request.method == "POST":
            t_id = request.form.get("test_id")
            current_test = Tests.query.get(t_id)
            
            relevant_students = Students.query.filter_by(class_id=teacher_subject.class_id).all()
            for s in relevant_students:
                val = request.form.get(f"marks_{s.id}")
                if val is not None and val.strip() != "":
                    m_rec = Marks.query.filter_by(student_id=s.id, test_id=t_id, subject_id=teacher_subject.id).first()
                    if m_rec:
                        m_rec.marks = int(val)
                    else:
                        new_mark = Marks(
                            student_id=s.id, test_id=t_id, subject_id=teacher_subject.id,
                            marks=int(val), test_name=current_test.test_name, test_date=current_test.test_date
                        )
                        db.session.add(new_mark)
            db.session.commit()
            return redirect(url_for("marks", test_id=t_id))

        marks_map = {}
        tests = Tests.query.filter_by(subject_id=teacher_subject.id).all()
        students = Students.query.filter_by(class_id=teacher_subject.class_id).all()
        
        if test_id:
            all_marks = Marks.query.filter_by(test_id=test_id, subject_id=teacher_subject.id).all()
            for m in all_marks:
                marks_map[m.student_id] = m.marks
        
        return render_template("marks.html", 
                                subject=teacher_subject, 
                                tests=tests, 
                                students=students, 
                                marks_map=marks_map, 
                                test_id=test_id)


    @app.route("/add-test", methods=["GET", "POST"])
    @login_required
    def add_test():
        if request.method == "POST":
            date_str = request.form.get("test_date")
            test_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            new_t = Tests(
                test_name=request.form.get("test_name"), 
                test_date=test_date_obj,  
                subject_id=request.form.get("subject_id"), 
                teacher_id=current_user.id
            )
            db.session.add(new_t)
            db.session.commit()
            
            return redirect(url_for("marks", subject_id=new_t.subject_id))
            
        all_subjects = Subjects.query.filter_by(teacher_id = current_user.id)
        return render_template("add_test.html", subjects=all_subjects)

    @app.route("/mails", methods=["GET", "POST"])
    @login_required
    def send_mails():
        if request.method == "POST":
            recipients = [s.parent_email for s in Students.query.all() if s.parent_email]
            
            if recipients:
                msg = Message(
                    subject=request.form.get("subject"),
                    sender=current_app.config.get("MAIL_USERNAME"),
                    recipients=recipients,
                    body=request.form.get("message"))
                    
                try:
                    mail.send(msg)
                    return "Emails sent successfully!"
                except Exception as e:
                    return f"Error: {str(e)}"

        return render_template("mails.html", students=Students.query.all())

    @app.route("/logout")
    @login_required
    def logout():
        logout_user() 
        flash("You have been logged out successfully!", "info")
        return redirect(url_for('login'))
    
   
#########################################################################################
###############   *  ADMIN  *   #########################################################
#########################################################################################
    
    
    @app.route("/admin-panel")
    @login_required
    def admin_panel():
        from models import User, Class, Students
        t_count = User.query.filter_by(role='teacher').count()
        s_count = Students.query.count() 
        c_count = Class.query.count()
        all_classes = Class.query.all()
        all_teachers = User.query.filter_by(role='teacher').all()

        return render_template("admin_panel.html", t_count=t_count, s_count=s_count, c_count=c_count, classes=all_classes, teachers=all_teachers)
       

    @app.route("/add-teacher", methods = ["GET","POST"] )
    @login_required
    def add_teacher():
        
        if current_user.role != 'admin':
            return "Unauthorized!", 403
        
        
        if request.method == "POST":

            New_user = User(
                username = request.form.get("username"),
                email = request.form.get("email"),
                password=generate_password_hash(request.form.get("password")),
                role = 'teacher')
            db.session.add(New_user)
            db.session.commit()
            New_subject = Subjects(
                subject_name = request.form.get('subject_name'),
                teacher_id = New_user.id ,
                class_id = request.form.get('class_id')
                ) 
            db.session.add(New_subject)
            db.session.commit()
            flash("Teacher added successfully!")
            return redirect(url_for('admin_panel')    
            )
        else:
            classes = Class.query.all()
            return render_template ("add_teacher.html", classes=classes)    
        
       
    @app.route("/add-student", methods=["GET", "POST"])
    @login_required
    def add_student():
        if current_user.role != 'admin':
            return "Unauthorized", 403

        if request.method == "POST":
            s_name = request.form.get('student_name')
            s_roll = request.form.get('roll_no')
            p_email = request.form.get('parent_email')
            p_pass = request.form.get('parent_password') 
            c_id = request.form.get('class_id')


            parent_user = User.query.filter_by(email=p_email).first()
            if not parent_user:
                parent_user = User(
                    username=p_email.split('@')[0], 
                    email=p_email, 
                    password=generate_password_hash(p_pass), 
                    role='parent'
                )
                db.session.add(parent_user)
                db.session.commit()

            new_student = Students(
                name=s_name,roll_no=s_roll,parent_email=p_email,parent_id=parent_user.id, class_id=c_id)
           
            db.session.add(new_student)
            db.session.commit()

            flash(f"Student {s_name} added! ", "success")
            return redirect(url_for('admin_panel'))

        all_classes = Class.query.all()
        return render_template("add_student.html", classes=all_classes)

######################################################################################
###############     PARENT     #######################################################
######################################################################################       
   
    @app.route("/parent-dashboard")
    @login_required
    def parent_dashboard():
        student = Students.query.filter_by(parent_id=current_user.id).first()
        if not student: return "Student not found", 404

        marks_data = Marks.query.filter_by(student_id=student.id).all()
        total_marks = [m.marks for m in marks_data if m.marks is not None]
        avg_marks = sum(total_marks) / len(total_marks) if total_marks else 0
        failed_count = len([m for m in total_marks if m < 33])
        absent_count = len([m for m in marks_data if m.marks is None])
        test_labels = [m.test_name for m in marks_data]
        test_scores = [m.marks if m.marks else 0 for m in marks_data]

        return render_template("parent_dashboard.html", 
                            student=student, avg_marks=round(avg_marks, 2),
                            failed=failed_count, absent=absent_count,
                            labels=test_labels, scores=test_scores)
      
    @app.route("/chapter-performance")
    @login_required
    def chapter_performance():
        student = Students.query.filter_by(parent_id=current_user.id).first()
        subjects = Subjects.query.filter_by(class_id=student.class_id).all()
        
        progress = db.session.query(Syllabus, Student_progress).\
            join(Student_progress, Student_progress.chapter_id == Syllabus.id).\
            filter(Student_progress.student_id == student.id).all()
        
        return render_template("chapter_show.html", subjects=subjects, progress=progress)
        

    @app.route("/parent-attendance")
    @login_required
    def parent_attendance():
        student = Students.query.filter_by(parent_id=current_user.id).first()
        attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.attendance_date.desc()).all()
        return render_template("show_attendance.html", attendance=attendance)
        

    @app.route("/show-marks")
    @login_required
    def show_marks():
        student = Students.query.filter_by(parent_id=current_user.id).first()
        s_class_id = student.class_id
        subjects = Subjects.query.filter_by(class_id = s_class_id).all()
        tests = Tests.query.join(Subjects).filter(Subjects.class_id == s_class_id)
        marks = Marks.query.filter_by(student_id = student.id).all()
        
        return render_template("show_marks.html",student=student,subjects=subjects,tests=tests,marks=marks) 
        
    @app.route("/parent-mail", methods=["GET", "POST"])
    @login_required
    def parent_mail():
        student = Students.query.filter_by(parent_id=current_user.id).first()
        subjects = Subjects.query.filter_by(class_id=student.class_id).all()
        teachers = [User.query.get(s.teacher_id) for s in subjects]

        if request.method == "POST":
            teacher_email = request.form.get("teacher_email")
            flash(f"Mail sent to teacher!", "success")
        
        return render_template("parent_mail.html", teachers=teachers)

 
    @app.route("/apply-leave", methods=["GET", "POST"])
    @login_required
    def apply_leave():
       
        student = Students.query.filter_by(parent_id=current_user.id).first()
        
        if not student:
            return "Error: Student not found for this parent.", 404

        if request.method == "POST":
            date_str = request.form.get("date")
            reason = request.form.get("reason")
            
            try:
                leave_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return "Invalid Date Format", 400

            new_leave = Leave(
                student_id=student.id,
                date=leave_date,
                reason=reason,
                status="pending"
            )
            db.session.add(new_leave)
            db.session.commit()
            return redirect(url_for("apply_leave"))
 
        leaves = Leave.query.filter_by(student_id=student.id).order_by(Leave.id.desc()).all()
        return render_template("apply_leave.html", student=student, leaves=leaves)
      

    @app.route("/update-leave/<int:id>", methods=["POST"])
    @login_required 
    def update_leave(id):
        leave = Leave.query.get_or_404(id)
        new_status = request.form.get("status")
        
        if new_status:
            leave.status = new_status
            db.session.commit()
            flash(f"Leave {new_status} successfully!", "success")
        
        return redirect(url_for('leave_approval'))
        
    with app.app_context():
        from models import User, Students, Subjects, Marks, Tests, Leave, Attendance, Syllabus, Student_progress

        db.create_all()
        print("Database Tables Created Successfully!")

    return app



app = create_app()




if __name__ == "__main__":
    app.run(debug=True)
    

    

