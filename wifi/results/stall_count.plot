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
GNUTERM = "qt"
# set terminal qt 0 size 500, 300 enhanced font "serif,10" persist
set terminal pdfcairo enhanced mono size 3.5in, 2.62in font "Times,10"
set style fill solid 0.25 noborder
set style line 1 linecolor rgb "#252525" linewidth 0.25 dashtype solid pointtype 7 pointsize 0
set style line 2 linecolor rgb "#252525" linewidth 0.125 dashtype solid pointtype 7 pointsize 0
set boxwidth 0.85 relative
set xlabel font "Times,12"
set ylabel font "Times,12"
set xtics nomirror
set ytics nomirror
set border 3
set grid x y
unset logscale
unset contour
unset key
set output "stall_count_graph.pdf"
# set title "Number of Video Stalls"
set title
set xlabel "Simultaneous video streams being served"
set ylabel "Number of video stalls"  
set xrange [ 0.300000 : 9.700000 ] noreverse nowriteback
set yrange [ 0 : 90 ]
plot "gnuplot.txt" i 0 using ($1-0.15):4:(0.3) w boxes ls 1, "" i 0 using ($1-.15):4:5 w yerrorbars ls 2, \
     ""            i 1 using ($0+1.15):4:(0.3) w boxes ls 1, "" i 1 using ($0+1.15):4:5 w yerrorbars ls 2
# 
# plot "gnuplot.txt" using ($0-0.15):6:(0.3) w boxes ls 1, \
#                 "" using ($0-0.15):6:7 w yerrorbars ls 2, \
#                 "" using ($0+0.15):2:(0.3) w boxes ls 2, \
#                 "" using ($0+0.15):2:3 w yerrorbars ls 2
# EOF