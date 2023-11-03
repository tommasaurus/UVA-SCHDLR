class Department:
    def __init__(self, name, URL, courses = []):
        self.name = name
        self.url = URL
        self.courses = courses

    def __str__(self):
        return f"Department Name: {self.name}\nURL: {self.url}\nCourses: {self.courses}"

    def getName(self):
        return self.name

    def getURL(self):
        if not self.url == None:
            return self.url
        print("URL does not exist for department:", self.name)
    
    def getCourses(self):
        return self.courses

    def getCourseNames(self):
        if len(self.courses) > 0:
            return [course[1].getCourseName() for course in self.courses]
        print("Department", self.name, "has no courses")