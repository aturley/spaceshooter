# Copyright (C) 2009  Andrew Turley <aturley@acm.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US

import pyglet
from pyglet.gl import *

import math
import random

import osc

game_time = 100
game_time_text = pyglet.text.Label('%d'%(0),
                          font_name='Times New Roman',
                          font_size=36,
                          x=10, y=10)

class GameState(object):
    def __init__(self):
        pass
    def update(self, dt):
        pass
    def enter(self):
        pass
    def exit(self):
        pass
    def move_start_handler(self, ipAddress, x, y):
        pass
    def move_end_handler(self, ipAddress, x, y):
        pass
    def shoot_start_handler(self, ipAddress, x, y):
        pass
    def shoot_end_handler(self, ipAddress, x, y):
        pass
    def draw(self):
        pass

class JoiningState(GameState):
    def __init__(self):
        self.state_timer = 10
        self.join_text = game_time_text = pyglet.text.Label('press the green patch to join',
                          font_name='Times New Roman',
                          font_size=36,
                          x=10, y=200)

    def update(self, dt):
        if len(players.values()) > 0:
            self.state_timer -= dt
        if (self.state_timer < 0):
            global current_state
            current_state.exit()
            current_state = playing_state
            current_state.enter()
            return
        for p in players.values():
            p.update(dt)
    def enter(self):
        global players
        players = {}
        global players_move_start
        players_move_start = {}
        global players_shoot_start
        players_shoot_start = {}
        global bullets
        bullets = []
        global kills
        kills = []
        self.state_timer = 10
    def exit(self):
        pass
    def move_start_handler(self, ipAddress, x, y):
        if not player_exists(ipAddress):
            add_player(ipAddress)
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        global game_time_text
        game_time_text.text = "%d"%(self.state_timer)
        game_time_text.draw()
        self.join_text.draw()
        for p in players.values():
            p.draw(title = True)

class PlayingState(GameState):
    def __init__(self):
        self.state_timer = 60
    def update(self, dt):
        self.state_timer -= dt
        if (self.state_timer < 0):
            global current_state
            current_state.exit()
            current_state = finishing_state
            current_state.enter()
            return
        for p in players.values():
            p.update(dt)
        for b in bullets:
            b.update(dt)
            if b.can_kill:
                for p in players.values():
                    if p.isAlive:
                        if ((p.x - b.x) ** 2 + (p.y - b.y) ** 2) < 225:
                            kills.append([b.ipAddress, p.ipAddress])
                            p.kill();

    def enter(self):
        self.state_timer = 60
        pass
    def exit(self):
        pass
    def move_start_handler(self, ipAddress, x, y):
        if player_exists(ipAddress):
            players_move_start[ipAddress] = (x, y)
    def move_end_handler(self, ipAddress, x, y):
        if not player_exists(ipAddress):
            return
        if (players_move_start.has_key(ipAddress)):
            if not players_move_start[ipAddress] == None:
                players[ipAddress].set_vector(x - players_move_start[ipAddress][0], -(y - players_move_start[ipAddress][1]))
                players_move_start[ipAddress] = None
    def shoot_start_handler(self, ipAddress, x, y):
        if player_exists(ipAddress) and players[ipAddress].isAlive:
            if (not players_shoot_start.has_key(ipAddress)) or (players_shoot_start[ipAddress] == None):
                players_shoot_start[ipAddress] = (x, y)
    def shoot_end_handler(self, ipAddress, x, y):
        if player_exists(ipAddress):
            if (players_shoot_start.has_key(ipAddress)):
                if not players_shoot_start[ipAddress] == None:
                    vec_x = x - players_shoot_start[ipAddress][0]
                    vec_y = -(y - players_shoot_start[ipAddress][1])
                    bullets.append(Bullet(ipAddress, players[ipAddress].x, players[ipAddress].y, vec_x * 5, vec_y * 5, bullets))
                    players_shoot_start[ipAddress] = None

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        global game_time_text
        game_time_text.text = "%d"%(self.state_timer)
        game_time_text.draw()
        for p in players.values():
            p.draw()
        for b in bullets:
            b.draw()

class FinishingState(GameState):
    def __init__(self):
        self.state_timer = 10
        self.win_text = pyglet.text.Label('',
                          font_name='Times New Roman',
                          font_size=36,
                          x=10, y=200)

    def update(self, dt):
        self.state_timer -= dt
        if (self.state_timer < 0):
            global current_state
            current_state.exit()
            current_state = joining_state
            current_state.enter()
            return
        for p in players.values():
            p.update(dt)
    def enter(self):
        self.state_timer = 10
        kill_chart = {}
        for k in kills:
            if not kill_chart.has_key(k[0]):
                kill_chart[k[0]] = 0
                if k[0] == k[1]:
                    kill_chart[k[0]] -= 1
            else:
                kill_chart[k[0]] += 1
        high_score = -100000
        winner = "NOBODY"
        for (ip, total_kills) in kill_chart.iteritems():
            if (total_kills > high_score):
                winner = ip

        self.win_text.text = "%s WINS"%(winner)
    def exit(self):
        pass
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.win_text.draw()
        for p in players.values():
            p.draw()


joining_state = JoiningState()
playing_state = PlayingState()
finishing_state = FinishingState()
current_state = joining_state

class Player(object):
    def __init__(self, ipAddress, x = 0, y = 0, dx = 0, dy = 0):
        self.ipAddress = ipAddress
        self.dx = dx;
        self.dy = dy;
        self.x = x;
        self.y = y;
        self.color = (max(random.random(), 0.5), max(random.random(), 0.5), max(random.random(), 0.5))
        self.isAlive = True
        self.death_clock = 0.0
    def update(self, dt):
        if not self.isAlive:
            self.death_clock -= dt
        if self.death_clock < 0:
            self.isAlive = True
        if not self.isAlive:
            return
        self.x += dt * self.dx
        self.y += dt * self.dy
        if (self.x > 640) or (self.x < 0) or (self.y > 480) or (self.y < 0):
            self.dx = 0.0
            self.dy = 0.0
    def kill(self):
        self.isAlive = False
        self.dx = 0.0
        self.dy = 0.0
        self.death_clock = 5.0

    def set_vector(self, dx, dy):
        if not self.isAlive:
            return
        self.dx = dx
        self.dy = dy
    def draw(self, title = False):
        DEG2RAD = 3.14159/180
        radius = 10
        glPushMatrix()
        glColor3f(*self.color)
        glTranslatef(self.x, self.y, 0)
        if self.isAlive:
            glBegin(GL_LINE_LOOP)
            for i in xrange(0, 360, 5):
                degInRad = i * DEG2RAD
                glVertex2f(math.cos(degInRad)*radius,math.sin(degInRad)*radius)
            radius = 5
            glEnd()
            glBegin(GL_LINE_LOOP)
            for i in xrange(0, 360, 5):
                degInRad = i * DEG2RAD
                glVertex2f(math.cos(degInRad)*radius,math.sin(degInRad)*radius)
            glEnd()
        else:
            glBegin(GL_LINE_LOOP)
            for i in xrange(0, 360, 5):
                degInRad = i * DEG2RAD
                bradius = random.random() * radius
                glVertex2f(math.cos(degInRad)*bradius,math.sin(degInRad)*bradius)
            glEnd()
        if title:
            l = pyglet.text.Label(self.ipAddress,
                          font_name='Times New Roman',
                          font_size=10,
                          x=-10, y=-20)
            l.draw()

        glPopMatrix()

class Bullet(object):
    def __init__(self, ipAddress, x = 0, y = 0, dx = 0, dy = 0, bullet_list = None):
        self.dx = dx;
        self.dy = dy;
        self.x = x;
        self.y = y;
        self.color = (1, 1, 1)
        self.bullet_list = bullet_list
        self.lifetime = 5;
        self.ipAddress = ipAddress
        self.can_kill = False
    def update(self, dt):
        self.lifetime -= dt
        if (self.can_kill == False) and (((players[self.ipAddress].x - self.x) ** 2 + (players[self.ipAddress].y - self.y) ** 2) > 225):
            self.can_kill = True
        self.x += dt * self.dx
        self.y += dt * self.dy
        if self.lifetime < 0:
            self.bullet_list.remove(self)
    def draw(self):
        DEG2RAD = 3.14159/180
        radius = 3
        glPushMatrix()
        glColor3f(*self.color)
        glTranslatef(self.x, self.y, 0)
        glBegin(GL_LINE_LOOP)
 
        for i in xrange(0, 360):
            degInRad = i * DEG2RAD
            glVertex2f(math.cos(degInRad)*radius,math.sin(degInRad)*radius)
        glEnd();
        glPopMatrix()

def update(dt):
    global current_state
    current_state.update(dt)

players = {}
players_move_start = {}
players_shoot_start = {}

bullets = []

kills = []

try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4, 
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)

@window.event
def on_draw():
    global current_state
    current_state.draw()

@window.event
def on_close():
    osc.dontListen()

def setup():
    # One-time GL setup
    glClearColor(0, 0, 0, 0)
    glColor3f(1, 1, 1)
    glEnable(GL_DEPTH_TEST)

def move_start_handler(*msg):
    # ipAddress, x, y
    try:
        ipAddress = msg[0][2]
        x = msg[0][3]
        y = msg[0][4]
        global current_state
        current_state.move_start_handler(ipAddress, x, y)
    except Exception, e:
        print e

def move_end_handler(*msg):
    # ipAddress, x, y
    try:
        ipAddress = msg[0][2]
        x = msg[0][3]
        y = msg[0][4]
        global current_state
        current_state.move_end_handler(ipAddress, x, y)
    except Exception, e:
        print e

def shoot_start_handler(*msg):
    # ipAddress, x, y
    try:
        ipAddress = msg[0][2]
        x = msg[0][3]
        y = msg[0][4]
        global current_state
        current_state.shoot_start_handler(ipAddress, x, y)
    except Exception, e:
        print e

def shoot_end_handler(*msg):
    # ipAddress, x, y
    try:
        ipAddress = msg[0][2]
        x = msg[0][3]
        y = msg[0][4]
        global current_state
        current_state.shoot_end_handler(ipAddress, x, y)
    except Exception, e:
        print e

def add_player(ipAddress):
    players[ipAddress] = Player(ipAddress, random.randint(0, 639), random.randint(0, 479), 0, 0)

def player_exists(ipAddress):
    return players.has_key(ipAddress)

if __name__ == "__main__":
    setup()
    osc.init()
    osc.listen('127.0.0.1', 9002)
    osc.bind(move_start_handler, '/movestart')
    osc.bind(move_end_handler, '/moveend')
    osc.bind(shoot_start_handler, '/shootstart')
    osc.bind(shoot_end_handler, '/shootend')
    pyglet.clock.schedule(update)
    current_state.enter()
    pyglet.app.run()


