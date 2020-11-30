# -*- coding: utf-8 -*-
"""PPGR_DOMACI_3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rYnBdwM5H5LygJjcCCUYSJnycHRMo2HW
"""

import numpy as np
import numpy.linalg as la

class Utils:
  # X_AXIS = [[1], [0], [0]]
  # Y_AXIS = [[0], [1], [0]]
  # Z_AXIS = [[0], [0], [1]]
  X_AXIS = [1, 0, 0]
  Y_AXIS = [0, 1, 0]
  Z_AXIS = [0, 0, 1]
  ### Konvertuje tacku iz homogenih u afine koordinate
  @staticmethod
  def to_affine(p):
    if len(p) < 2 or len(p) > 3:
      raise ValueError(f'[to_affine] {p} is not a valid point.')
    if len(p) == 2:
      return np.array(p, dtype='float32')
    if p[2] == 0:
      raise ValueError(f'[to_affine] {p} is a vanish point.')
    return np.array([1.0*p[0]/p[2],
                     1.0*p[1]/p[2]])

  ### Konvertuje tacke iz afinih u homogene koordinate
  @staticmethod
  def to_homog(p):
    if len(p) < 2 or len(p) > 3:
      raise ValueError(f'[to_affine] {p} is not a valid point.')
    if len(p) == 3:
      return np.array(p, dtype='float32')
    return np.array([p[0], p[1], 1], dtype='float32')

  ### Vraca jedinicni vektor od datog vektora
  @staticmethod
  def to_unit(v):
    v = np.array(v, dtype='float32')
    mag = la.norm(v)
    return v/mag

  ### Row to column
  @staticmethod
  def rtoc(r):
    return np.array([[r[0]],
                     [r[1]],
                     [r[2]]], dtype='float32')

  @staticmethod
  def assert_orth_and_det1(A):
    return np.isclose(la.det(A), 1.0) and np.isclose(A @ A.T,
                                                     np.identity(3)).all()

  @staticmethod
  def assert_orth(A):
    return np.isclose(A @ A.T, np.identity(3)).all()

  @staticmethod
  def assert_det1(A):
    return np.isclose(la.det(A), 1.0)

  @staticmethod
  def assert_meas(m):
    return m in ['degrees', 'radians']

  ### Column to row
  @staticmethod
  def ctor(c):
    return np.array([c[0][0], c[1][0], c[2][0]], dtype='float32')

  ### Vraca proizvoljan vektor normalan na vektor v
  @staticmethod
  def get_normal(v):
    v = np.array(v, dtype='float32')
    if (v == 0).all():
      return np.array([1, 1, 1], dtype='float32')
    
    if v[0] != 0:
      return np.array([-v[2]/v[0] ,0, 1], dtype='float32')
    if v[1] != 0:
      return np.array([0, -v[2]/v[1] ,1], dtype='float32')
    if v[2] != 0:
      return np.array([0, 1, -v[1]/v[2]], dtype='float32')

class PPGR3:
  ### Matrica rotacije oko orijentisane prave p za ugao fi
  @staticmethod
  def rodriguez(p,
                fi,
                measure='radians'):
    if not Utils.assert_meas(measure):
      raise ValueError(f'[rodriguez] Unknown measure {measure}')
    if measure == 'degrees':
      fi = np.deg2rad(fi)

    p = np.array(p)  
    if p.shape == (3, ):
      p = Utils.rtoc(p)
    p = Utils.to_unit(p)
    ppt = p @ p.T
    c = np.cos(fi)
    s = np.sin(fi)
    px = np.array([[0, -p[2], p[1]],
                   [p[2], 0, -p[0]],
                   [-p[1], p[0], 0]], dtype='float32')
    return ppt + c*(np.identity(n=3) - ppt) + s*px

  ### Konvertuje Ojlerove uglove u matricu rotacije
  @staticmethod
  def Euler2A(angleX, angleY, angleZ, measure='radians'):       
    Rx = PPGR3.rodriguez(p=Utils.X_AXIS, 
                         fi=angleX,
                         measure=measure)
    Ry = PPGR3.rodriguez(p=Utils.Y_AXIS,
                         fi=angleY,
                         measure=measure)
    Rz = PPGR3.rodriguez(p=Utils.Z_AXIS,
                         fi=angleZ,
                         measure=measure)
    return Rz @ Ry @ Rx 

  ### Za datu matricu A nalazi p i phi tako da je A = Rot_p(phi)
  @staticmethod
  def AxisAngle(A, measure='radians'):
    if not Utils.assert_meas(measure):
      raise ValueError(f'[AxisAngle] Unknown measure {measure}')
    A = np.array(A, dtype='float32')
    # if not Utils.assert_orth(A):
    #   raise ValueError(f'[AxisAngle] The matrix must be orthogonal.')
    if not Utils.assert_det1(A):
      raise ValueError(f'[AxisAngle] The determinant must be 1.')
    M = A - np.identity(3)
    p = None
    u = None
    for v1, v2 in [(M[0], M[1]), (M[1], M[2]), (M[0], M[2])]:
      p = np.cross(v1, v2)
      if p.any():
        if v1.any():
          u = v1
        if v2.any():
          u = v2
        break
    p = Utils.to_unit(p)
    u = Utils.to_unit(u)
    up = np.matmul(A, u)
    phi = np.arccos(np.dot(u, up))
    if np.dot(np.cross(u, up), p) < 0:
      p = -p
    
    if measure == 'degrees':
      phi = np.rad2deg(phi)
    return p, phi

  ### Za datu matricu A nalazi Ojlerove uglove
  @staticmethod
  def A2Euler(A, measure='radians'):
    if not Utils.assert_meas(measure):
      raise ValueError(f'[A2Euler] Unknown measure {measure}')
    A = np.array(A, dtype='float32')
    # if not Utils.assert_orth(A):
    #   raise ValueError(f'[A2Euler] The matrix must be orthogonal.')
    if not Utils.assert_det1(A):
      raise ValueError(f'[A2Euler] The determinant must be 1.')
      
    a11 = A[0][0]
    a12 = A[0][1]
    a13 = A[0][2]
    a21 = A[1][0]
    a22 = A[1][1]
    a23 = A[1][2]
    a31 = A[2][0]
    a32 = A[2][1]
    a33 = A[2][2]

    if a31 < 1:
      if a31 > -1:
        angle1 = np.arctan2(a21, a11)
        angle2 = np.arcsin(-a31)
        angle3 = np.arctan2(a32, a33)
      else:
        angle1 = np.arctan2(-a12, a22)
        angle2 = np.pi/2
        angle3 = 0.0
    else:
      angle1 = np.arctan2(-a12, a22)
      angle2 = -np.pi/2
      angle3 = 0
    
    if measure == 'degrees':
      angle1, angle2, angle3 = np.rad2deg(angle1), np.rad2deg(angle2), np.rad2deg(angle3)

    return angle3, angle2, angle1

  ### Za datu osu p i ugao phi vraca kvaternion q tako da je
  ### Cq = Rp(phi)
  @staticmethod
  def AxisAngle2Q(p, phi, measure='radians'):
    if not Utils.assert_meas(measure):
      raise ValueError(f'[AxisAngle2Q] Unknown measure {measure}')
    if measure == 'degrees':
      phi = np.deg2rad(phi)
    p = np.array(p, dtype='float32')
    w = np.cos(phi/2)
    p = Utils.to_unit(p)
    x, y, z = np.sin(phi/2)*p
    return np.array([x, y, z, w])

  @staticmethod
  def Q2AxisAngle(q, measure='radians'):
    if not Utils.assert_meas(measure):
      raise ValueError(f'[Q2AxisAngle] Unknown measure {measure}')
    q = np.array(q, dtype='float32')
    q = Utils.to_unit(q)
    x, y, z, w = q
    
    if w < 0:
      q = -q

    phi = 2*np.arccos(w)

    if np.isclose(np.abs(w), 1.0):
      p = np.array([1, 0, 0])
    else:
      p = Utils.to_unit([x, y, z])

    if measure == 'degrees':
      phi = np.rad2deg(measure)
    return p, phi

class Examples:
  @staticmethod
  def run_example_series(angleX,
                         angleY,
                         angleZ,
                         tag):
    print(f'[{tag}] TESTIRANJE FUNKCIJA')
    print(f'Pocinjemo sa uglovima {angleX, angleY, angleZ}')
    print(f'==============================================')

    A = PPGR3.Euler2A(angleX,
                      angleY,
                      angleZ)
    p, phi = PPGR3.AxisAngle(A)
    A2 = PPGR3.rodriguez(p, phi)
    o1, o2, o3 = PPGR3.A2Euler(A)
    q = PPGR3.AxisAngle2Q(p, phi)
    p2, phi2 = PPGR3.Q2AxisAngle(q)

    print(f'(1) Euler2A:')
    print(f'A=\n{A}\n')
    print(f'(2) AxisAngle:')
    print(f'p={p}, phi={phi}\n')
    print(f'(3) Rodriguez:')
    print(f'A2=\n{A2}\n')
    print(f'(4) A2Euler:')
    print(f'ojlerovi uglovi: {o1, o2, o3}\n')
    print(f'(5) AxisAngle2Q:')
    print(f'q={list(q)}\n')
    print(f'(6) Q2AxisAngle:')
    print(f'p={p2}, phi={phi2}')


