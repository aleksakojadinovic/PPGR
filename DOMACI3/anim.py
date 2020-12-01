import ppgr_domaci_3
from ppgr_domaci_3 import Utils
from ppgr_domaci_3 import PPGR3

from OpenGL.GL import*
from OpenGL.GLU import*
from OpenGL.GLUT import*

import numpy as np
import sys

class AnimUtils:
    @staticmethod
    def draw_cs(size=100.0,
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

    @staticmethod
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

    @staticmethod
    def line_inter(P_START, P_END, t, tm):
        t = float(t)
        tm = float(tm)
        return P_START + (t/tm)*P_END

class Constants:
    SP_STACKS = 20
    SP_LW = 0.2

class AnimBall:

    def __init__(self, pos=[0, 0, 0],
                       aa=[None, None],
                       cr=0.0,
                       cg=0.0,
                       cb=0.0,
                       size=1.0,
                       show_cs=True,
                       in_measure='degrees'):
        self.pos = np.array(pos, dtype='float32')
        
        self.aa = aa
        if aa[0] is not None and in_measure == 'radians':
            self.aa[1] = np.rad2deg(self.aa[1])
        self.cr = cr
        self.cg = cg
        self.cb = cb
        self.size = size
        self.show_cs = show_cs

    def copy(self):
        return AnimBall(self.pos, self.aa, self.cr, self.cg, self.cb, self.size, self.show_cs, in_measure='degrees')

    def p(self):
        return self.aa[0]

    def phi(self):
        return self.aa[1]
    
    def phirad(self):
        return np.deg2rad(self.aa[1])

    def render(self):
        glLineWidth(Constants.SP_LW)
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        if self.aa[1] is not None:
            glRotatef(self.aa[1], self.aa[0][0], self.aa[0][1], self.aa[0][2])
        glColor3f(self.cr, self.cg, self.cb)
        glutWireSphere(self.size, Constants.SP_STACKS, Constants.SP_STACKS)
        if self.show_cs:
            AnimUtils.draw_cs(size=5*self.size, bidirectional=True, lw=5.0)
        glPopMatrix()

class AnimationInfo:
    ANIMATION_ON = False
    ANIMATION_TIME = 0.0
    ANIMATION_MAX = 1.0
    ANIMATION_DT = 0.01
    TIMER_REFRESH = 20

class CallBacks:
    @staticmethod
    def timer_callback(val):
        global AnimationInfo
        global OBJECTS
        AnimationInfo.ANIMATION_TIME += AnimationInfo.ANIMATION_DT

        if AnimationInfo.ANIMATION_TIME > AnimationInfo.ANIMATION_MAX:
            AnimationInfo.ANIMATION_TIME = 0.0

        currQ = AnimUtils.slerp(Objects.Q_START,
                                Objects.Q_END,
                                AnimationInfo.ANIMATION_TIME, AnimationInfo.ANIMATION_MAX)
        newp, newphi = PPGR3.Q2AxisAngle(currQ)
        newphi = np.rad2deg(newphi)
        Objects.BALL_CURR.aa = [newp, newphi]
        Objects.BALL_CURR.pos = AnimUtils.line_inter(Objects.BALL_START.pos,
                                                     Objects.BALL_END.pos,
                                                     AnimationInfo.ANIMATION_TIME,
                                                     AnimationInfo.ANIMATION_MAX)
            
        glutPostRedisplay()
        
        if AnimationInfo.ANIMATION_ON:
            glutTimerFunc(AnimationInfo.TIMER_REFRESH, CallBacks.timer_callback, 0)
    
    @staticmethod
    def keyboard_press(key, mouseX, mouseY):
        global AnimationInfo
        if ord(key) == ord('s'):
            if not AnimationInfo.ANIMATION_ON:
                AnimationInfo.ANIMATION_ON = True
                glutTimerFunc(AnimationInfo.TIMER_REFRESH, CallBacks.timer_callback, 0)
            else:
                AnimationInfo.ANIMATION_ON = False          
    
    @staticmethod
    def display_scene():
        global Objects
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        Objects.BALL_START.render()
        Objects.BALL_END.render()
        Objects.BALL_CURR.render()
        
        glutSwapBuffers()

class Objects:
    BALL_START = None
    BALL_END   = None
    BALL_CURR  = None
    Q_START    = None
    Q_END      = None

class Loader:
    @staticmethod
    def parse_angle(line):
        words = line.split(" ")
        if len(words) != 4:
            print(f'Expecting: [deg/rad] angle angle angle format, got {line}')
            sys.exit(1)
        words = [word.strip() for word in words]
        if words[0].lower() not in ['deg', 'rad']:
            print(f'Expected [deg/rad], got {words[0]}')
            sys.exit(1)
        words[0] = words[0].lower()
        try:
            angle1, angle2, angle3 = float(words[1]), float(words[2]), float(words[3])
        except:
            print(f'Failed to parse one or more of the angles: {words[1], words[2], words[3]}')
            sys.exit(1)
        if words[0] == 'deg':
            angle1, angle2, angle3 = np.deg2rad(angle1), np.deg2rad(angle2), np.deg2rad(angle3)

        return angle1, angle2, angle3

    @staticmethod
    def parse_point(line):
        words = line.split(" ")
        if len(words) != 3:
            print(f'Expecting: x y z, got {line}')
            sys.exit(1)
        try:
            x, y, z = float(words[0]), float(words[1]), float(words[2])
        except:
            print(f'Failed to parse point: {words[0], words[1], words[2]}')
            sys.exit(1)

        return x, y, z
            
    @staticmethod
    def parse_content(content):
        if len(content) != 4:
            print(f'Expected format:\n[deg\rad] anglestartX angleStartY angleStartZ\n[deg\rad] angleEndX angleEndY angleEndZ\npointStartX pointStartY pointStartZ\npointEndX pointEndY pointEndZ')
            sys.exit(1)

        anglestart =   Loader.parse_angle(content[0])
        angleend =     Loader.parse_angle(content[1])
        pointstart =   Loader.parse_point(content[2])
        pointend   =   Loader.parse_point(content[3])
        return anglestart, angleend, pointstart, pointend

    @staticmethod
    def load_from_file(filepath):
        # try:
        with open(filepath) as fp:
            return Loader.parse_content(fp.read().splitlines())
        # except:
        #     print('Failed to parse input file.')
        #     sys.exit(1)
    



def main():
    if len(sys.argv) < 2:
        c = input('No input file specified, load default example? [y/n]:  ')
        if c.lower() == 'y':
            os = [np.pi / 2, 2 * np.pi / 3, np.pi / 4] 
            oe = [np.pi / 5, np.pi / 4, 2 * np.pi / 3]
            cs = [0, 0, 0]
            ce = [5, 5, 5]
        else:
            sys.exit(1)
    else:
        os, oe, cs, ce = Loader.load_from_file(sys.argv[1])
    

    initialize_everything(os, oe, cs, ce)
    print('Press S to start/pause the animation')

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 800)
    glutInitWindowPosition(350, 200)
    glutCreateWindow('PPGR DOMACI 3: SLERP')
    glClearColor(0.764, 0.764, 0.764, 1.)

    glutKeyboardFunc(CallBacks.keyboard_press)
    glutDisplayFunc(CallBacks.display_scene)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1., 1., 40)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(13, 13, -13,
              0, 0, 0,
              0, 1, 0)
    glPushMatrix()
    glutMainLoop()
    return

def initialize_everything(os, oe, cs, ce):
    os1, os2, os3 = os
    oe1, oe2, oe3 = oe

    ballStart = AnimBall(pos=cs,
                        aa=list(PPGR3.AxisAngle(PPGR3.Euler2A(os1, os2, os3))),
                        in_measure='radians')
   
    ballEnd   = AnimBall(pos=ce,
                        aa=list(PPGR3.AxisAngle(PPGR3.Euler2A(oe1, oe2, oe3))),
                        in_measure='radians')

    ballCurrent = ballStart.copy()

    Objects.BALL_START = ballStart
    Objects.BALL_END   = ballEnd
    Objects.BALL_CURR  = ballCurrent
    Objects.Q_START    = PPGR3.AxisAngle2Q(ballStart.p(), ballStart.phirad())
    Objects.Q_END      = PPGR3.AxisAngle2Q(ballEnd.p(), ballEnd.phirad())
    

main()