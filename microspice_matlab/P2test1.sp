* Time Domain Simulation 
R1      1       0       100k
c1      1       2       100u
c2      2       3       35u
r2      2       0       5
va      3       0       10V


.option post
.tran 0.005ms 5ms

.alter
va 3 0  pulse ( 0 12V 2ms 0.1ms 0.1ms 1ms 2ms )

.alter
va 3 0  pwl ( 2ms,0v 2.5ms,12v 2.75ms,5v 3ms,-5V 3.5ms,12v 3.6ms,5v 4ms,0v 4.5ms,3v) 

.alter
va 3 0  sin(0 12V 1kHz 2ms 10 45)

.print v(0)
.print v(1)
.print v(2)
.print v(3)

.end


