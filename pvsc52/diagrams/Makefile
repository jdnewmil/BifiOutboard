# Makefile for rendering Asymptote language image files for presentation/paper
# Asymptote compiler name
ASY=asy
# subsets of 3d model
VARIANTS := flat roll flatnolbl flatgw longarray sungeom flatunsh rollgw rollugw wedgeonly
# asy output extension
ASYOUTEXT := pdf
# rendered graphic files
DOWNVIEWS := $(foreach var,$(VARIANTS),down_view_$(var).$(ASYOUTEXT))

all: $(DOWNVIEWS) boundaries.$(ASYOUTEXT)

# all down_view_xxx.png files come from specifying -u 'variant="xxx"'
# on the command line
# On WSL, the asy compiler terminates with a segmentation fault, but this
# does not seem to affect the output file
$(DOWNVIEWS): down_view.asy
	$(ASY) -u 'variant="$(subst down_view_,,$(subst .$(ASYOUTEXT),,$@))"' -o $@ down_view.asy

boundaries.$(ASYOUTEXT): boundaries.asy
	$(ASY) boundaries.asy
