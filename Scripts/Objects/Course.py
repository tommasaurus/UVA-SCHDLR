class Course:
    def __init__(self, name, course_num, id, section, class_type, credits, availability, enrollment, professor, time, location):
        self.name = name
        self.course_num = course_num
        self.id = id
        self.section = section
        self.class_type = class_type
        self.credits = credits
        self.availability = availability
        self.enrollment = enrollment
        self.professor = professor
        self.time = time
        self.location = location

    def __str__(self):
        return f"Class Name: {self.name}\nCourse Number: {self.course_num}\nID: {self.id}\nSection: {self.section}\nType: {self.class_type}\nCredits: {self.credits}\nAvailability: {self.availability}\nEnrollment: {self.enrollment}\nProfessor: {self.professor}\nTime: {self.time}\nLocation: {self.location}"
