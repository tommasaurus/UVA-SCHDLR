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

        id_pattern = r'[A-Za-z]*(\d+)'
        id_match = re.search(id_pattern,id).group(1)
        self.id = id_match
        day_pattern = r'([A-Z][a-z]+|TBA)'
        time_pattern = r'(\d+:\d+[apm ]+- \d+:\d+[apm ]+|TBA)'

        # day_match = re.finditer(day_pattern, time)
        # time_match = re.search(time_pattern, time)
        # self.time = {day.group() : time_match.group() for day in day_match}

    def __str__(self):
        return f"Class Name: {self.name}\nCourse Number: {self.course_num}\nID: {self.id}\nSection: {self.section}\nType: {self.class_type}\nCredits: {self.credits}\nAvailability: {self.availability}\nEnrollment: {self.enrollment}\nProfessor: {self.professor}\nTime: {self.time}\nLocation: {self.location}"

    def getCourseName(self):
        return self.name