class Department:
    def __init__(self, name, college, classes):
        self.name = name
        self.college = college

    def __str__(self):
        return f"Department Name: {self.name}\nCollege: {self.college}\nCollege: {self.classes}"

    