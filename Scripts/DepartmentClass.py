class DepartmentClasses:
    def __init__(self, name, credits, section, times, location):
        self.name = name
        self.credits = credits
        self.section = section
        self.times = times
        self.location = location

    def __str__(self):
        return f"Class Name: {self.name}\nCredits: {self.credits}\nSection: {self.section}\nTimes: {self.times}\nLocation: {self.location}"

    