from flask import Flask
from flask import render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template(
        'test.html', name='mike')

@app.route('/my-link/')
def determineCapacity():
  print determineCapacity()

  return 'Click.'


if __name__ == '__main__':
    app.run()





# This function will take all stats for the room, and update the room's current capacity based on these stats
# @param room - the room that should be calculated
def determineCurrentCapacity(room):
    newCapacity = None
    posts = room.getPosts()
    for post in posts:
        if post.getScore >= .9:
            newCapacity = post.getText()
        elif post.getScore >= .8:
            if newCapacity is not None:
                range = newCapacity - post.getText()
                if -10 < range < 10:
                    newCapacity = post.getText()
                else:
                    newCapacity = (newCapacity + post.getText()) / 2

            else:
                newCapacity = post.getText
        elif post.getScore >= .7:
            if newCapacity is not None:
                range = newCapacity - post.getText()
                if -5 < range < 5:
                    newCapacity = post.getText()
                else:
                    newCapacity = (2 * newCapacity + post.getText) / 3
            else:
                newCapacity = post.getText()
        elif .5 <= post.getScore < .7:
            if newCapacity is not None:
                newCapacity = (4 * newCapacity + post.getText())
            else:
                newCapacity = post.getText()
        elif post.getScore < .5:
            if newCapacity is not None:
                newCapacity = (8 * newCapacity + post.getText())
            else:
                newCapacity = post.getText()
    room.setCurrent(newCapacity)
    return newCapacity


# verify if the user is in the room they are checking into
# @param user - the user attempting to check in
# @param studyRoom - the room the user wants to check into
# @Return - true if user in studyRoom, false if otherwise
def verifyRoom(user, studyRoom):
    distance = distanceCalculator(user, studyRoom)
    acceptableDistance = 5  # PICK A DISTANCE THATS IS ACCEPTABLE
    if (-acceptableDistance < distance < acceptableDistance):
        return True
    else:
        return False


# Takes a user and a room, returns how far apart the location's are from each other
# @param user - user to calculate distance for
# @param room - room to calculate distance for
# @Return - Returns a distance
def distanceCalculator(user, room):
    roomLocation = room.getLocation()
    userLocation = user.getLocation()
    longitude = abs(roomLocation[0] - userLocation[0])
    latitude = abs(roomLocation[1] - userLocation[1])
    return longitude + latitude


# A user checks into a room. Get all the info they enter, room they are in
# @param user - The user checking in
# @param room - The room the user is trying to check into
# @param post - Can be none if the user did not submit a post. Otherwise, it's the user's post of this check in
def userCheckIn(user, room, post=None, numberComp=None, noiseLevel=None):
    if verifyRoom(user, room):
        room.checkIn()
        if post is not None:
            room.newPost(post.getText())
            user.addPost(post)
            if numberComp is not None and (room.type() == "Computer Lab"):
                room.setOpenComp(numberComp)
            if noiseLevel is not None and (room.type() == "Quiet Room"):
                room.setNoiseLevel(noiseLevel)
    else:
        # TODO
        # This should bring up something that tells the user they need to be in the room to make a post
        return
def userCheckOut(user):
    room = user.getRoom()
    if room is not None:
        room.checkOut()
        user.setRoom(None)




# Increment thumbUp/thumbDown based on user vote
# @param post = the post being rated
# @param thumbType = was it a thumbUp or thumbDown
# @Return - Nothing
def ratePost(post, thumbType):
    if thumbType == "thumbUp":
        post.thumbUp()
    elif thumbType == "thumbDown":
        post.thumbDown()


# A user of the app
class User:
    #
    __username = None
    #
    __password = None
    # Where the user is currently at, list longitude and latitude
    __location = None
    # The room the user checked into
    __room = None
    # The capacity the user suggested for the room
    __capacityCheck = None
    # How accurate the users reports usually are
    __trustLevel = 0
    # List of posts the user has made
    __posts = {}

    # Create new user, user may not have checked into a room
    def __init__(self, username, password, location, room=None, capCheck=None):
        self.__username = username
        self.__password = password
        self.__location = location
        self.__room = room
        self.__capacityCheck = capCheck

    def setLocation(self, location):
        self.__location = location

    def getLocation(self):
        return self.__location

    def setRoom(self, room):
        self.__room = room

    def getRoom(self):
        return self.__room

    def setTrustLevel(self, trustLevel):
        self.__trustLevel = trustLevel

    def getTrustLevel(self):
        return self.__trustLevel

    def addPost(self, post):
        self.__posts.append(post)

    def getPosts(self):
        return self.__posts

    def calculateTrust(self):
        for post in self.__posts:
            if post.getScore() >= 10:
                self.__trustLevel += .5
            elif post.getScore() >= 5:
                self.__trustLevel += .1
            elif post.getScore < 0:
                self.__trustLevel -= .3
            elif post.getScore <= -5:
                self.__trustLevel -= .5

    def setPassword(self, password):
        self.__password = password

    def getPassword(self):
        return self.__password

    def setUsername(self, username):
        self.__username = username

    def getUsername(self):
        return self.__username


class Post:
    __user = None
    # The text of the users post, should be a number of people only
    __text = None
    # The time the post was made
    __time = None
    # The score of the post i.e thumbUps - thumbDowns
    __score = None
    __thumbsUp = 0
    __thumbsDown = 0
    # How much this post is worth when calculating roomCapacity checks
    __weight = 1
    # The value of the post when calculating room capacity
    __value = ((__thumbsUp - __thumbsDown) / (__thumbsUp + __thumbsDown)) * __weight
    # Initialize new Post
    def __init__(self, user, text, thumbsUp=None, thumbsDown=None):
        self.__user = user
        if self.__user.getTrustLevel() >= 5:
            self.__weight = 2
        elif self.__user.getTrustLevel() >= 0:
            self.__weight = 1
        elif self.__user.getTrustLevel < 0:
            self.__weight = .5
        elif self.__user.getTrustLevel < -5:
            self.__weight = .1
        self._time = datetime.now().time()
        self.__text = text
        self.__thumbsUp = thumbsUp
        self.__thumpsDown = thumbsDown
        self.__score = (thumbsUp - thumbsDown)

    # Increment thumbUps
    def thumbUp(self):
        self.__thumbsUp += 1

    # Increment thumbDowns
    def thumbDown(self):
        self.__thumbsDown += 1

    # set the weight, should only be called for use with user's trust levels
    def setWeight(self, weight):
        self.__weigth = weight

    # check the current time vs when this post was made
    def checkTime(self):
        # What time is it now
        now = datetime.now().time()
        # The difference in hours of this post and current time
        timeDiff = now.hour - self.__time.hour
        # if the post wasn't made today
        if now.day != self.__time.day:
            self.__weight = self.__weight * 0
        # if the post was made more than an hour ago
        elif timeDiff > 1:
            self.__weight = self.__weight * .5
        # if the post was made more than 2 hours ago
        elif timeDiff > 2:
            self.__weight = self.__weight * .25
        # if the post was made more than 4 hours ago
        elif timeDiff > 4:
            self.__weight = self.__weight * 0

    # get the current score of the post
    def getScore(self):
        return (self.__thumbsUp - self.__thumbsDown)

    def getText(self):
        return self.__text


class StudyRoom:
    # Type of room, i.e quiet or computer lab, string
    __type = None
    # How many people can the room hold, int
    __capacity = None
    # How many people are there currently, int
    __currentCapacity = None
    # Where is the room located, list longitude and latitude
    __location = None
    # The user posts for this room, it is a list
    __posts = {}

    # Create new Study room, there may be no posts, most likely there will be 0
    def __init__(self, type, capacity, currentCapacity, location, posts=None):
        self.__type = type
        self.__capacity = capacity
        self.__currentCapacity = currentCapacity
        self.__location = location
        self.__posts = posts

    # Set the type of room
    def setType(self, type):
        self.__type = type

    # Get type of room
    def getType(self):
        return self.__type

    # Set capacity of the room
    def setCapacity(self, capacity):
        self.__capacity = capacity

    # Get capacity of room
    def getCapacity(self):
        return self.__capacity

    # Set how many people are currently in the room
    def setCurrent(self, currentCap):
        self.__currentCapacity = currentCap

    # Get how many people are currently in the room
    def getCurrent(self):
        return self.__currentCapacity

    # Set location of the room
    def setLocation(self, location):
        self.__location = location

    # Get locatiom of room
    def getLocation(self):
        return self.__location

    def newPost(self, post):
        self.__posts.append(post)

    # When a user checks into the room, increment current capacity
    def checkIn(self):
        self.__currentCapacity += 1
    def checkOut(self):
        self.__currentCapacity -= 1


# Subclass of StudyRoom, inherits location, posts, capacity, currentCapacity
class ComputerLab(StudyRoom):
    # How many computers in the room
    __numComputers = None
    # How many of those computers are open
    __openComputers = None

    # create new computerLab
    def __init__(self, type, capacity, currentCapacity, location, computers, computersOpen):
        # Use StudyRoom constructor, set type to "Computer Lab"
        StudyRoom.__init__(self, "Computer Lab", capacity, currentCapacity, location)
        self.__numComputers = computers
        self.__openComputers = computersOpen

    # Set number of computers
    def setComputers(self, computers):
        self.__numComputers = computers

    # Get number of computers
    def getComputers(self):
        return self.__numComputers

    # Set number of open computers
    def setOpenComp(self, openComputers):
        self.__openComputers = openComputers

    # Get number of open computers
    def getOpenComp(self):
        return self.__openComputers


# Subclass of StudyRoom inherits all attributes
class QuietRoom(StudyRoom):
    # How loud is the room currently
    __noiseLevel = None

    # Create new QuietRoom using StudyRoom constructor, set type to "Quiet Room"
    def __init__(self, type, capacity, currentCapacity, location, noiseLevel):
        StudyRoom.__init__(self, "Quiet Room", capacity, currentCapacity, location)
        self.__noiseLevel = noiseLevel

    # Set noise level
    def setNoiseLevel(self, noiseLevel):
        self.__noiseLevel = noiseLevel

    # Get noise level
    def getNoiseLevel(self):
        return self.__noiseLevel
