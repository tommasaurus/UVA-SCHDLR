import re

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

        day_pattern = r'([A-Z][a-z]+|TBA)'
        time_pattern = r'(\d+:\d+[apm ]+- \d+:\d+[apm ]+|TBA)'

        day_match = re.finditer(day_pattern, time)
        time_match = re.search(time_pattern, time)
        self.time = {day.group() : time_match.group() for day in day_match}

    def __str__(self):
        return f"Class Name: {self.name}\nCourse Number: {self.course_num}\nID: {self.id}\nSection: {self.section}\nType: {self.class_type}\nCredits: {self.credits}\nAvailability: {self.availability}\nEnrollment: {self.enrollment}\nProfessor: {self.professor}\nTime: {self.time}\nLocation: {self.location}"

    def getCourseName(self):
        return self.name


temp = Course("Intro to math", "MATH 1000", "10000", "101","Lecture","3","Open","0/20","Professor Qu","TuTh 11:00am - 12:15pm", "New Cabell")
print(temp.time)