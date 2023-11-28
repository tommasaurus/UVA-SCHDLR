class Student:
     def __init__(self, username, password, schedules):
        self._username = username
        self._password = password
        self.schedules = schedules

        def __str__(self):
        return f"Student Username: {self.username}\nSchedules: {self.schedules}"