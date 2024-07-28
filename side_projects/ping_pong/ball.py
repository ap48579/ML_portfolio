from turtle import Turtle

class Ball(Turtle):

    def __init__(self):
        super().__init__(shape="circle")
        self.color("white")
        self.speed("normal")
        self.penup()
        self.goto(0,0)
        self.x_move = 10
        self.y_move = 10

    def move(self):
        x = self.xcor() +self.x_move
        y = self.ycor() +self.y_move
        
        self.goto(x,y)
    
    def bounce(self):
        self.y_move *= -1