from extensions import db

# Sab kuch ab isi folder ke andar se aayega
from .users import User
from .other import Leave,  Attendance
from .classes import Students, Subjects, Marks, Tests,Class
from .dashboard import Syllabus, Student_progress

__all__ = [
    'User', 'Leave','Class', 'Attendance', 
    'Students', 'Subjects', 'Marks', 'Tests', 
    'Syllabus', 'Student_progress'

]