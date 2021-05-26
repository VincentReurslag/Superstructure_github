# -*- coding: utf-8 -*-
"""
Created on Sat May 22 12:39:39 2021

@author: Vincent Reurslag
"""

from gekko import GEKKO
m = GEKKO() # Initialize gekko
m.options.SOLVER=1  # APOPT is an MINLP solver
m.options.IMODE=3

# optional solver settings with APOPT
m.solver_options = ['minlp_maximum_iterations 500', \
                    # minlp iterations with integer solution
                    'minlp_max_iter_with_int_sol 10', \
                    # treat minlp as nlp
                    'minlp_as_nlp 0', \
                    # nlp sub-problem max iterations
                    'nlp_maximum_iterations 50', \
                    # 1 = depth first, 2 = breadth first
                    'minlp_branch_method 1', \
                    # maximum deviation from whole number
                    'minlp_integer_tol 0.05', \
                    # covergence tolerance
                    'minlp_gap_tol 0.01']
# Initialize variables
I = 2
J = 2
K = 3

HP = range(I) 
CP = range(J)
HU = range(1)
CU = range(1)
ST = range(K-1)

TIN_i = m.Param( [443,423] )
TIN_j = m.Param( [293,353] )
TIN_HU = m.Param( [450] )
TIN_CU = m.Param( [293] )

TOUT_i = m.Param( [333,303] )
TOUT_j = m.Param( [408,413] )
TOUT_HU = m.Param( [450] )
TOUT_CU = m.Param( [313] )

F_i = m.Param( [30,15] )
F_j = m.Param( [20,40] )


U = m.Const(1)
CCU = m.Const(20)
CHU = m.Const(80)
CF = m.Const(1000)
CF_CU = m.Const(1000)
CF_HU = m.Const(1000)
C = m.Const(1000)
B = m.Const(0.6)
OMEGA = m.Const(10000)
TAU = m.Const(1000)

dT = m.Array(m.Var, (I,J,K-1) , value = 1, lb = None, ub = None)
dT1 = m.Array(m.Var, (I,J,K-1) , value = 1, lb = None, ub = None)
dTcu = m.Array(m.Var, (I) , value = 1, lb = None, ub = None)
dThu = m.Array(m.Var, (J) , value = 1, lb = None, ub = None)

Q = m.Array(m.Var, (I,J,K-1) , value = 1, lb = None, ub = None)
Qcu = m.Array(m.Var, (I) , value = 1, lb = None, ub = None)
Qhu = m.Array(m.Var, (J) , value = 1, lb = None, ub = None)

Ti = m.Array(m.Var, (I,K), value = 1, lb = None, ub = None )
Tj = m.Array(m.Var, (J,K), value = 1, lb = None, ub = None )

z = m.Array(m.Var, (I,J,K-1), value = 1, integer = True )
zcu = m.Array(m.Var, (I), value = 1, integer = True )
zhu = m.Array(m.Var, (J), value = 1, integer = True )

Utility_cost = m.Var()
HXfixed_cost = m.Var()
CUfixed_cost = m.Var()
HUfixed_cost = m.Var()
HXarea_cost = m.Var()
CUarea_cost = m.Var()
HUarea_cost = m.Var()

#Defining the equations

#Heat balance of streams
m.Equations( (TIN_i[i] - TOUT_i[i] ) * F_i[i] == sum([sum([Q[i,j,k] for j in CP]) for k in ST]) + Qcu[i] for i in HP)
m.Equations( (TOUT_j[j] - TIN_j[j] ) * F_i[j] == sum([sum([Q[i,j,k] for i in HP]) for k in ST]) + Qhu[j] for j in CP)

   
#Heat balance at each stage
m.Equations( (Ti[i,k] - Ti[i,k+1] ) * F_i[i] == sum([Q[i,j,k] for j in CP]) for k in ST for i in HP)  
m.Equations( (Tj[j,k] - Ti[j,k+1] ) * F_i[j] == sum([Q[i,j,k] for i in HP]) for k in ST for j in CP)  


#Assignment of inlet temperatures
m.Equations( TIN_i[i] == Ti[i,0] for i in HP)
m.Equations( TIN_j[j] == Tj[j,K-1] for j in CP)

#Feasibility of temperatures
m.Equations( Ti[i,k] >= Ti[i,k+1] for k in ST for i in HP)
m.Equations( Tj[j,k] >= Tj[j,k+1] for k in ST for j in CP)
m.Equations( TOUT_i[i] <= Ti[i,K-1] for i in HP)
m.Equations( TOUT_j[j] >= Tj[j,0] for j in CP)


#Hot and cold uttility load
m.Equations( ( Ti[i,K-1] - TOUT_i[i] ) * F_i[i] == Qcu[i] for i in HP)
m.Equations( ( TOUT_j[j] - Tj[j,0] ) * F_j[j] == Qhu[j] for j in CP)

#Logical constrains
m.Equations( Q[i,j,k] - OMEGA * z[i,j,k] <= 0 for i in HP for j in CP for k in ST)
m.Equations( Qcu[i] - OMEGA * zcu[i] <= 0 for i in HP)
m.Equations( Qhu[j] - OMEGA * zhu[j] <= 0 for j in CP)

#Approach temperature calculations
m.Equations( dT[i,j,k] <= Ti[i,k] - Tj[j,k] + TAU * (1 - z[i,j,k] ) for k in ST for i in HP for j in CP )
m.Equations( dT1[i,j,k] <= Ti[i,k+1] - Tj[j,k+1] + TAU * (1 - z[i,j,k] ) for k in ST for i in HP for j in CP )
m.Equations( dTcu[i] <= Ti[i,K-1] - TOUT_CU + TAU * (1 - zcu[i]) for i in HP)
m.Equations( dThu[j] <= TOUT_HU - Tj[j,0] + TAU * (1 - zhu[j]) for j in CP)

#Avoiding infinite areas
m.Equations( dT[i,j,k] >= 0.1 for i in HP for j in CP for k in ST)
m.Equations( dT1[i,j,k] >= 0.1 for i in HP for j in CP for k in ST)
m.Equations( dTcu[i] >= 0.1 for i in HP)
m.Equations( dThu[j] >= 0.1 for j in CP)


#Objective definitions
m.Equation( Utility_cost == sum([ CCU * Qcu[i] for i in HP ]) + sum([ CHU * Qhu[j] for j in CP ]) )
m.Equation( HXfixed_cost == sum([ sum([ sum([ CF * z[i,j,k] for k in ST ]) for j in CP ]) for i in HP ]) )
m.Equation( CUfixed_cost == sum([ CF_CU * zcu[i] for i in HP ]) )
m.Equation( HUfixed_cost == sum([ CF_HU * zhu[j] for j in CP ]) )


m.Minimize(Utility_cost + HXfixed_cost + CUfixed_cost + HUfixed_cost)

m.solve()


