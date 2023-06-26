* Time Domain Simulation
r2      1  2  5e3
r3      2  3  400
r4      3  4  1e3
c1      4  0  9e-5
vdyn    1  0  10v


.options post
.TRAN  0.1ms 800ms

.alter
vdyn 1 0 PULSE( 1V 3V 0.1ms 0.1ms 0.1ms 40ms 100ms)

.alter
vdyn 1 0 pwl(0ms,3v 100ms,2v 200ms,0v 250ms,2v 300ms,3.5v 400ms,2V 500ms,0v 600ms,0v 700ms,3v 705ms,0v)

.alter
vdyn 1 0 sin(2v 2v 25Hz 2ms 0 90 )

.print v(0)
.print v(1)
.print v(2)
.print v(3)
.print v(4)

*.end


