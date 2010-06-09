# rendering pdf -> various zoom level png files

# -r92 92dpi
# -OutputFile %d is placeholder for pagenumber
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -dFirstPage=1 -dLastPage=2 -sOutputFile=Meld_51_%04d.png Meld_51.pdf


# Method (I) 
#
# pdf->ps->psnup->png

gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -dFirstPage=1 -dLastPage=18 -sOutputFile=ecs-09-submission-form_%04d.png ecs-09-submission-form.pdf
pdf2ps ecs-09-submission-form.pdf ecs-09-submission-form.ps
psnup -pa4 -9 -b3 -d10 ecs-09-submission-form.ps ecs-09-submission-form_3x3.ps
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -sOutputFile=ecs-09-submission-form_3x3_%04d.png ecs-09-submission-form_3x3.ps
rm ecs-09-submission-form_3x3.ps
psnup -pa4 -25 -b3 -d10 ecs-09-submission-form.ps ecs-09-submission-form_5x5.ps
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -sOutputFile=ecs-09-submission-form_5x5_%04d.png ecs-09-submission-form_5x5.ps
rm ecs-09-submission-form_5x5.ps
rm ecs-09-submission-form.ps

## 800x1131: 800 * sqrt(2) = 1131
## 800 / (21 / 2.54) = 96.762dpi
## 1131 / (29.7 / 2.54) = 96.7225
#gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r96.762x96.725 -dFirstPage=1 -dLastPage=14 -sOutputFile=test-pdf-14-seitig_%04d.png test-pdf-14-seitig.pdf
#pdf2ps test-pdf-14-seitig.pdf test-pdf-14-seitig.ps
#psnup -pa4 -9 -b3 -d10 test-pdf-14-seitig.ps test-pdf-14-seitig_3x3.ps
#gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -sPAPERSIZE=a4 -r96.762x96.725 -sOutputFile=test-pdf-14-seitig_3x3_%04d.png test-pdf-14-seitig_3x3.ps
#rm test-pdf-14-seitig_3x3.ps
#psnup -pa4 -25 -b3 -d10 test-pdf-14-seitig.ps test-pdf-14-seitig_5x5.ps
#gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -sPAPERSIZE=a4 -r96.762x96.725 -sOutputFile=test-pdf-14-seitig_5x5_%04d.png test-pdf-14-seitig_5x5.ps
#rm test-pdf-14-seitig_5x5.ps
#rm test-pdf-14-seitig.ps


# Method II
#
# pdf -> png -> montage (XxX) -> convert (interlacing) -> png
#
# - much better quality than using method I (8-bit vs 16-bit colour?)

# 800x1131: 800 * sqrt(2) = 1131
# 800 / (21 / 2.54) = 96.762dpi
# 1131 / (29.7 / 2.54) = 96.7225
# test-pdf-14-seitig_0001.png: PNG image, 800 x 1131, 8-bit/color RGB, interlaced
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r96.762x96.725 -dFirstPage=1 -dLastPage=14 -sOutputFile=test-pdf-14-seitig_1_%04d.png test-pdf-14-seitig.pdf
convert -interlace PNG test-pdf-14-seitig_1_0001.png test-pdf-14-seitig_0001.png
convert -interlace PNG test-pdf-14-seitig_1_0002.png test-pdf-14-seitig_0002.png
convert -interlace PNG test-pdf-14-seitig_1_0003.png test-pdf-14-seitig_0003.png
convert -interlace PNG test-pdf-14-seitig_1_0004.png test-pdf-14-seitig_0004.png
convert -interlace PNG test-pdf-14-seitig_1_0005.png test-pdf-14-seitig_0005.png
convert -interlace PNG test-pdf-14-seitig_1_0006.png test-pdf-14-seitig_0006.png
convert -interlace PNG test-pdf-14-seitig_1_0007.png test-pdf-14-seitig_0007.png
convert -interlace PNG test-pdf-14-seitig_1_0008.png test-pdf-14-seitig_0008.png
convert -interlace PNG test-pdf-14-seitig_1_0009.png test-pdf-14-seitig_0009.png
convert -interlace PNG test-pdf-14-seitig_1_0010.png test-pdf-14-seitig_0010.png
convert -interlace PNG test-pdf-14-seitig_1_0011.png test-pdf-14-seitig_0011.png
convert -interlace PNG test-pdf-14-seitig_1_0012.png test-pdf-14-seitig_0012.png
convert -interlace PNG test-pdf-14-seitig_1_0013.png test-pdf-14-seitig_0013.png
convert -interlace PNG test-pdf-14-seitig_1_0014.png test-pdf-14-seitig_0014.png
rm test-pdf-14-seitig_1_*.png

# 266 x 377: 3*266=798 [-2], 3*377=1131
# 266 / (21 / 2.54) = 32.173
# 377 / (29.7 / 2.54) = 32.242
# test-pdf-14-seitig_3x3_0001.png: PNG image, 798 x 1131, 16-bit/color RGB, interlaced
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r32.173x32.242 -dFirstPage=1 -dLastPage=14 -sOutputFile=test-pdf-14-seitig_3_%04d.png test-pdf-14-seitig.pdf
# Note: change to strip by using "-mode Concatenate -tile x1"
montage -interlace PNG -background \#dddddd -geometry 266x377+0+0 -tile 3x3 test-pdf-14-seitig_3_0001.png test-pdf-14-seitig_3_0002.png test-pdf-14-seitig_3_0003.png test-pdf-14-seitig_3_0004.png test-pdf-14-seitig_3_0005.png test-pdf-14-seitig_3_0006.png test-pdf-14-seitig_3_0007.png test-pdf-14-seitig_3_0008.png test-pdf-14-seitig_3_0009.png test-pdf-14-seitig_3x3_0001.png
montage -interlace PNG -background \#dddddd -geometry 266x377+0+0 -tile 3x3 test-pdf-14-seitig_3_0010.png test-pdf-14-seitig_3_0011.png test-pdf-14-seitig_3_0012.png test-pdf-14-seitig_3_0013.png test-pdf-14-seitig_3_0014.png test-pdf-14-seitig_3x3_0002.png
rm test-pdf-14-seitig_3_*.png

# 160 x 226: 5*160=800, 5*226=1130 [-1]
# 800 / (21 / 2.54) / 5 = 19.352
# 1131 / (29.7 / 2.54) / 5 = 19.345
# test-pdf-14-seitig_5x5_0001.png: PNG image, 800 x 1130, 16-bit/color RGB, interlaced
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r19.352x19.345 -dFirstPage=1 -dLastPage=14 -sOutputFile=test-pdf-14-seitig_5_%04d.png test-pdf-14-seitig.pdf
montage -interlace PNG -background \#dddddd -geometry 160x226+0+0 -tile 5x5 test-pdf-14-seitig_5_0001.png test-pdf-14-seitig_5_0002.png test-pdf-14-seitig_5_0003.png test-pdf-14-seitig_5_0004.png test-pdf-14-seitig_5_0005.png test-pdf-14-seitig_5_0006.png test-pdf-14-seitig_5_0007.png test-pdf-14-seitig_5_0008.png test-pdf-14-seitig_5_0009.png test-pdf-14-seitig_5_0010.png test-pdf-14-seitig_5_0011.png test-pdf-14-seitig_5_0012.png test-pdf-14-seitig_5_0013.png test-pdf-14-seitig_5_0014.png test-pdf-14-seitig_5x5_0001.png
rm test-pdf-14-seitig_5_*.png
