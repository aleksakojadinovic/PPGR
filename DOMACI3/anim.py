import ppgr_domaci_3
from ppgr_domaci_3 import Utils
from ppgr_domaci_3 import PPGR3

from OpenGL.GL import*
from OpenGL.GLU import*
from OpenGL.GLUT import*

import numpy as np
import sys

ANIMATION_ON = False
ANIMATION_TIME = 0.0
ANIMATION_MAX = 1.0
ANIMATION_DT = 0.01
TIMER_REFRESH = 20

os1, os2, os3 =                 [np.pi / 2, 2 * np.pi / 3, np.pi / 4]
oe1, oe2, oe3 =                 [np.pi / 5, np.pi / 4, 2 * np.pi / 3]

CENTER_START =                  np.array([0, 0, 0])
CENTER_END =                    np.array([5, 5, 5])
CENTER_CURR =                   CENTER_START

P_START, PHI_START =            PPGR3.AxisAngle(PPGR3.Euler2A(os1, os2, os3))
P_END, PHI_END =                PPGR3.AxisAngle(PPGR3.Euler2A(oe1, oe2, oe3))
P_CURR, PHI_CURR =              P_START, PHI_START

Q_START =                       PPGR3.AxisAngle2Q(P_START, PHI_START)
Q_END =                         PPGR3.AxisAngle2Q(P_END, PHI_END)

def draw_coord(size=100.0,
               bidirectional=False,
               lw=1.0):
    glLineWidth(lw)

    glColor3f(1.0, 0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(size, 0, 0)
    glEnd()
    if bidirectional:
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(-size, 0, 0)
        glEnd()

    glColor3f(0, 1.0, 0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, size, 0)
    glEnd()
    if bidirectional:
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, -size, 0)
        glEnd()

    glColor3f(0.0, 0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, size)
    glEnd()
    if bidirectional:
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -size)
        glEnd()

def slerp(Q_START, Q_END, t, tm):
    t = float(t)
    tm = float(tm)
    cos0 = np.dot(Q_START, Q_END)
    if cos0 < 0:
        Q_START = -Q_START
        cos0 = -cos0
    
    if cos0 > 0.95:
        return Q_START
    
    phi0 = np.arccos(cos0)
    s = np.sin(phi0)
    a = (np.sin(phi0*(1 - t/tm)))/s
    b = (np.sin(phi0*t/tm))/s
    return a*Q_START + b*Q_END

def line_inter(P_START, P_END, t, tm):
    t = float(t)
    tm = float(tm)
    return P_START + (t/tm)*P_END

def timer_callback(val):
    global ANIMATION_ON
    global ANIMATION_TIME
    global ANIMATION_MAX
    global ANIMATION_DT
    global P_CURR
    global PHI_CURR
    global CENTER_START
    global CENTER_END
    global CENTER_CURR



    ANIMATION_TIME += ANIMATION_DT

    if ANIMATION_TIME > ANIMATION_MAX:
        ANIMATION_TIME = 0.0

    currQ = slerp(Q_START, Q_END, ANIMATION_TIME, ANIMATION_MAX)
    P_CURR, PHI_CURR =   PPGR3.Q2AxisAngle(currQ)
    CENTER_CURR = line_inter(CENTER_START, CENTER_END, ANIMATION_TIME, ANIMATION_MAX)    
    glutPostRedisplay()
    
    

    if ANIMATION_ON:
        glutTimerFunc(TIMER_REFRESH, timer_callback, 0)
    
def keyboard_press(key, mouseX, mouseY):
    global ANIMATION_ON
    if ord(key) == ord('s'):
        if not ANIMATION_ON:
            ANIMATION_ON = True
            glutTimerFunc(TIMER_REFRESH, timer_callback, 0)
        else:
            ANIMATION_ON = False          

def draw_world_cs():
    draw_coord(bidirectional=True)

def draw_position(angle, rot1, rot2, rot3, cx, cy, cz, col=(0, 0, 0)):
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glRotatef(angle, rot1, rot2, rot3)
    draw_coord(size=5.0, bidirectional=False, lw=5.0)
    glColor3f(col[0], col[1], col[2])
    glLineWidth(1.5)
    glutWireSphere(1.0, 10, 10)
    glPopMatrix()

def display_scene():
    global P_START
    global P_END
    global PHI_START
    global PHI_END
    global P_CURR
    global PHI_CURR
    global CENTER_START
    global CENTER_END
    global CENTER_CURR

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Svestki KS
    # draw_world_cs()

    # Pocetni polozaj
    draw_position(np.rad2deg(PHI_START), P_START[0], P_START[1], P_START[2], CENTER_START[0], CENTER_START[1], CENTER_START[2], col=(0, 0, 0))
    # Krajnji polozaj
    draw_position(np.rad2deg(PHI_END), P_END[0], P_END[1], P_END[2], CENTER_END[0], CENTER_END[1], CENTER_END[2], col=(0, 0, 0))
    # Trenutni polozaj
    draw_position(np.rad2deg(PHI_CURR), P_CURR[0], P_CURR[1], P_CURR[2], CENTER_CURR[0], CENTER_CURR[1], CENTER_CURR[2])



    glutSwapBuffers()
    return



def main():

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 800)
    glutInitWindowPosition(350, 200)
    glutCreateWindow('PPGR DOMACI 3: SLERP')

    glClearColor(0.764, 0.764, 0.764, 1.)

    glutKeyboardFunc(keyboard_press)
    glutDisplayFunc(display_scene)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1., 1., 40)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(13, 13, -13,
              0, 0, 0,
              0, 1, 0)
    glPushMatrix()
    glutMainLoop()
    return


main()