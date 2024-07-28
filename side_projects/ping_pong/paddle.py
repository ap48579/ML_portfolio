from turtle import Screen, Turtle

class Paddle(Turtle):

    def __init__(self,location):
        super().__init__()
        self.shape("square")
        self.shapesize(stretch_wid=5, stretch_len=1)
        self.color("white")
        self.penup()
        self.speed(0)
        self.goto(location)

    def up(self):
        y = self.ycor()
        y += 20
        self.goto(self.xcor(),y)

    def down(self):
        y = self.ycor()
        y -= 20
        self.goto(self.xcor(),y)