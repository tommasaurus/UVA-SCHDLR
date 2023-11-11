from datetime import datetime
from datetime import time
import sys, os
config_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(config_directory)
from Scripts.UVAObjects.Course import Course

class Schedule:
    def __init__(self):
        self.calendar = {
          "Mo" : [],
          "Tu" : [],
          "We" : [],
          "Th" : [],
          "Fr" : []
          }
     
    def __str__(self):
        return f"Monday: {self.calendar['Mo']}\nTuesday: {self.calendar['Tu']}\nWednesday: {self.calendar['We']}\nThursday: {self.calendar['Th']}\nFriday: {self.calendar['Fr']}"

    def checkAvailability(self, day, startTime, endTime):
        daySchedule = self.calendar[day]
        for event in daySchedule:
            if (event.start_time <= startTime and startTime <= event.end_time) or (event.start_time <= endTime and endTime <= event.end_time):
                print("There is a time conflict on ", day, "at", event.start_time, "to", event.end_time)
                return False
        print("You are available from", startTime, "to", endTime)
        return True

    def append(self, courseName, day, time):
        startTime, endTime = map(str.strip, time.split(' - '))
        start = datetime.strptime(startTime, "%I:%M%p").time()
        end = datetime.strptime(endTime, "%I:%M%p").time()
        self.calendar[day].append((courseName, TimeFrame(start, end)))

    def addCourse(self, course):
        """
        Adds a course to the schedule by populating the schedule with the respective course times/days
        Args:
            course (Course): Course object to be added to the schedule
        """
        for each in course.time:
            if each != "TBA":
                self.append(course.name, each, course.time[each])

class TimeFrame:
    def __init__(self, startTime, endTime):
        self.start_time = startTime
        self.end_time = endTime
    
    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


# temp = Course("Intro to math", "MATH 1000", "10000", "101","Lecture","3","Open","0/20","Professor Qu","TuTh 11:00am - 12:15pm", "New Cabell")
# temp2 = Course("Intro to COMPUTERS", "MATH 1000", "10000", "101","Lecture","3","Open","0/20","Professor Qu","MoWeFr 9:00pm - 11:27pm", "New Cabell")
# sched = Schedule()
# sched.addCourse(temp)
# sched.addCourse(temp2)
# print(sched)
# print(sched.calendar["Tu"][0])
# print(sched.calendar["Fr"][0])
# sched = Schedule()
# start = time(8, 30)
# end = time(9, 30)
# middle = time(9)
# frame = TimeFrame(start, end)
# start1 = time(18, 30)
# end1 = time(19, 30)
# frame1 = TimeFrame(start1, end1)
# sched.calendar["Mo"].append(frame1)
# print(sched.checkAvailability("Mo",middle, middle))
# sched.append("Tu", "11:00am - 12:15pm")
# print(sched)
