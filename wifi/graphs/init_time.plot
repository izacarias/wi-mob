#!/usr/bin/gnuplot -persist
#
#    
#    	G N U P L O T
#    	Version 5.0 patchlevel 3    last modified 2016-02-21 
#    
#    	Copyright (C) 1986-1993, 1998, 2004, 2007-2016
#    	Thomas Williams, Colin Kelley and many others
#    
#    	gnuplot home:     http://www.gnuplot.info
#    	faq, bugs, etc:   type "help FAQ"
#    	immediate help:   type "help"  (plot window: hit 'h')
load "general-settings.gp"
set key at 5,1620 Left
set output "init_time_graph.pdf"
# set title "Playback Start Time" 
set title
set xlabel "Simultaneous video streams being served" 
set ylabel "Video startup time (ms)" 
set xrange [ 0.300000 : 9.700000 ] noreverse nowriteback
set yrange [ 0.00000 : 1600.00 ] noreverse nowriteback
plot "gnuplot.txt" i 0 using ($1-0.15):2:(0.3) w boxes ls 1 t "Random Walk", \
     ""            i 0 using ($1-.15):2:3 w yerrorbars ls 3 t "", \
     ""            i 1 using ($0+1.15):2:(0.3) w boxes ls 2 t "Random Way Point", \
     ""            i 1 using ($0+1.15):2:3 w yerrorbars ls 3 t ""
# EOF
