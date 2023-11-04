class College:
    def __init__(self, name, departments = []):
        self.name = name
        self.departments = departments

    def __str__(self):
        return f"College Name: {self.name}\nDepartments: {self.departments}"

    def setDepartments(self, departments):
        self.departments = departments

    def getDepartments(self):
        return self.departments

    def getDepartment(self, departmentName):
        for each in self.departments:
            if departmentName == each.getName():
                return each
        print("This department does not exist:", departmentName)

    def getDepartmentNames(self):
        return [department.getName() for department in self.departments]

    def addDepartment(self, department):
        self.departments.append(department)

    def removeDepartment(self, departmentName):
        self.departments.remove(self.getDepartment(departmentName))

    def getClasses(self, departmentName):
        return self.getDepartment(departmentName).getClasses()