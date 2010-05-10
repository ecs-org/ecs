#
# -r92 92dpi
# -OutputFile %d is placeholder for pagenumber
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -dFirstPage=1 -dLastPage=2 -sOutputFile=Meld_51_%04d.png Meld_51.pdf
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -dFirstPage=1 -dLastPage=18 -sOutputFile=ecs-09-submission-form_%04d.png ecs-09-submission-form.pdf

pdf2ps ecs-09-submission-form.pdf ecs-09-submission-form.ps
psnup -pa4 -9 ecs-09-submission-form.ps ecs-09-submission-form_3x3.ps
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -sOutputFile=ecs-09-submission-form_3x3_%04d.png ecs-09-submission-form_3x3.ps
rm ecs-09-submission-form_3x3.ps
psnup -pa4 -25 ecs-09-submission-form.ps ecs-09-submission-form_5x5.ps
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -sPAPERSIZE=a4 -r92 -sOutputFile=ecs-09-submission-form_5x5_%04d.png ecs-09-submission-form_5x5.ps
rm ecs-09-submission-form_5x5.ps
rm ecs-09-submission-form.ps
