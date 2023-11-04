class UVA:
    def __init__(self, colleges = {}):
        self.colleges = {}

    def __str__(self):
        return f"Colleges: {self.colleges}"
    
    def addCollege(self, collegeName, college):
        self.colleges[collegeName] = college