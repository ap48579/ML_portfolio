from turtle import Screen, Turtle
import time

START = [(0,0), (-20,0), (-40,0)]

class Snake:

    def __init__(self):
        self.segments = []
        self.create_snake()
        self.head = self.segments[0]
    
    def create_snake(self):
        for pos in START:
            new_seg = Turtle(shape= "square")
            new_seg.color("white")
            new_seg.penup()
            new_seg.goto(pos)
            self.segments.append(new_seg)

    def move(self):
        for seg_num in range(len(self.segments)-1,0,-1):
            new_x = self.segments[seg_num-1].xcor()
            new_y = self.segments[seg_num-1].ycor()

            self.segments[seg_num].goto(new_x, new_y)
        
        self.segments[0].forward(20)
    
    def up(self):
        if self.segments[0].heading() != 270:
            self.segments[0].setheading(90)
    
    def down(self):
        if self.segments[0].heading() != 90:
            self.segments[0].setheading(270)
    
    def left(self):
        if self.segments[0].heading() != 0:
            self.segments[0].setheading(180)
    
    def right(self):
        if self.segments[0].heading() != 180:
            self.segments[0].setheading(0)
