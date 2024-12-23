from turtle import Screen, Turtle
from paddle import Paddle
from ball import Ball
import time

screen = Screen()
screen.title("Pong game")
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0)

r_paddle = Paddle((380,0))
l_paddle = Paddle((-390,0))


ball = Ball()


screen.listen()
screen.onkey(r_paddle.up,"Up")
screen.onkey(r_paddle.down,"Down")

screen.onkey(l_paddle.up,"w")
screen.onkey(l_paddle.down,"s")


game_is_on = True
while game_is_on:
    screen.update()
    
    ball.move()
    time.sleep(0.1)

    if ball.ycor() > 280 or ball.ycor() < -280:
        ball.bounce()
    

screen.exitonclick() 