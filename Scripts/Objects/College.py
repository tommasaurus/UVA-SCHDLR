class College:
    def __init__(self, name, departments):
        self.name = name
        self.departments = departments

    def __str__(self):
        return f"College Name: {self.name}\nDepartments: {self.departments}"