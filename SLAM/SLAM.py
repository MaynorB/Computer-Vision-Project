ffmpeg -i video\walk.mp4 -vf "lenscorrection=k1=0.15:k2=0.02" video\walk_fixed.mp4
ffmpeg -i video\walk_fixed.mp4 -vf "fps=3" frames/frame_%05d.jpg
