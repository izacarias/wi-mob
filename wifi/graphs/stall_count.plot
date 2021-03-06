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
set key at 4.7,70 Left
set output "stall_count_graph.pdf"
# set title "Number of Video Stalls"
set title
set xlabel "Simultaneous video streams being served"
set ylabel "Number of video stalls"  
set xrange [ 0.300000 : 9.700000 ] noreverse nowriteback
set yrange [ 0 : 70 ]
plot "gnuplot.txt" i 0 using ($1-0.15):4:(0.3) w boxes ls 1 t "Random Walk", \
     ""            i 0 using ($1-.15):4:5 w yerrorbars ls 3 t "", \
     ""            i 1 using ($0+1.15):4:(0.3) w boxes ls 2 t "Random Way Point", \
     ""            i 1 using ($0+1.15):4:5 w yerrorbars ls 3 t ""
