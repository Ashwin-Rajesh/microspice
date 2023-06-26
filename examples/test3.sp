* Pseudo Butterworth Filter

R1      1 2 1K
R2      2 3 1K
C1      2 4 126n
C2      3 0 113n
g1      4 0 3 4 100K
rbyp    4 0 900k
VIN     1 0 10


.option post
.TRAN 100nS 2mS
.alter
VIN     1 0  PULSE(0 1V 0ms 0.1ms 0.1ms 1ms 5ms) 

.alter
VIN     1 0  PWL(0ms,0V 0.5ms,1.1V 1ms,1.1V 1.3ms,0.2v )

.alter
VIN     1 0  SIN(0 1V 1khz 0ms 0 0 )

.print v(0)
.print v(1)
.print v(2)
.print v(3)
.print v(4)

.END

