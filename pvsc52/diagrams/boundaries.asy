settings.outformat="pdf";
settings.prc=false;
settings.render=4;

import flowchart;

unitsize(1mm);
size(0, 3.5inches);
defaultpen(fontsize(10));

// scalars
real row_spacing = 10.0;   // vertical spacing
real col_width = 14;      // primary horizontal spacing
real label_space = 30.0;  // secondary horizontal spacing

// pairs
pair up = (0, row_spacing);
pair right = (col_width, 0);
pair left = -right;

pair col0base = (-label_space, 0);
pair col1base = (0, 0);
pair col2base = (col_width, 0);

// paths

// blocks
block e_rear_outboard = rectangle(
    "$E_\mathrm{rear,outboard}$", col2base, fillpen=lightblue);
block globbakunshd = rectangle(
    "$\mathrm{GlobBakUnshd}$", shift(up) * col1base);
block globbakframe = rectangle(
    "($\mathrm{GlobBakFrame}$)", shift(2 up) * col1base);
block globbak = rectangle(
    "$\mathrm{GlobBak}$", shift(3 up) * col1base);
block e_cell = rectangle(
    "$E_\mathrm{cell}$", shift(4 up) * col1base);
block globeff = rectangle(
    "$\mathrm{GlobEff}$", shift(5 up) * col1base);
block globinc = rectangle(
    "$\mathrm{GlobInc}$", shift(6 up) * col1base, fillpen=lightblue);
block globhor = rectangle(
    "$\mathrm{GlobHor}$", shift(7 up) * col1base);

block dc_conv = rectangle("$\mathrm{EArrNom}$", shift(4 up) * col2base);

Label outboard_bias = Label(
    "Irradiance exposure bias", align=W, position=shift(0.5 up) * col1base);
Label rear_struct = Label(
    "Array frame structural loss", align=W, position=shift(1.5 up) * col1base);
Label mod_frame = Label(
    "Module frame structural loss"
    , align=W
    , position=shift(2.5 up) * col1base);
Label bifaciality = Label(
    "Bifaciality", align=W, position=shift(3.5 up) * col1base);
Label spec_shd_soil = Label(
    "Shade, spectrum, soiling", align=W, position=shift(5.5 up) * col1base);
Label transpos = Label(
    "Transposition, diffuse estimation"
    , align=W
    , position=shift(6.5 up) * col1base);

block outboard_rear_sensor = roundrectangle(
    "Rear-facing outboard", col0base, fillpen=lightyellow);
block unshd_rear_sensor = roundrectangle(
    "(complex shade)", shift(up) * col0base);
block midway_sensor = roundrectangle(
    "Rear of module frame?", shift(2 up) * col0base);
block channelled_sensor = roundrectangle(
    "Rear of laminate?", shift(3 up) * col0base);
block ref_module = roundrectangle(
    "Reference module", shift(4 up) * col0base);
block eff_front = roundrectangle(
    "(not feasible; diffuse shading)", shift(5 up) * col0base);
block outboard_front = roundrectangle(
    "Front-facing outboard", shift(6 up) * col0base, fillpen=lightyellow);

// pens

// drawing

draw(e_rear_outboard);
draw(globbakunshd);
draw(globbakframe);
draw(globbak);
draw(e_cell);
draw(dc_conv);
draw(globeff);
draw(globinc);
draw(globhor);

label(outboard_bias);
label(rear_struct);
label(mod_frame);
label(bifaciality);
label(spec_shd_soil);
label(transpos);

draw(outboard_rear_sensor);
draw(unshd_rear_sensor);
draw(midway_sensor);
draw(channelled_sensor);
draw(ref_module);
draw(eff_front);
draw(outboard_front);

add(
    new void(picture pic, transform t) {
        blockconnector operator --=blockconnector(pic, t, p=currentpen);
        blockconnector operator ..=blockconnector(pic, t, p=dotted);

        e_rear_outboard -- Left -- Up -- Arrow
            -- globbakunshd     -- Up -- Arrow
            -- globbakframe     -- Up -- Arrow
            -- globbak          -- Up -- Arrow
            -- e_cell;
            
        globhor         -- Down -- Arrow
            -- globinc  -- Down -- Arrow
            -- globeff  -- Down -- Arrow
            -- e_cell;

        e_cell -- Right -- Arrow -- dc_conv;

        channelled_sensor -- Right .. globbak;
        midway_sensor -- Right .. globbakframe;
        unshd_rear_sensor -- Right .. globbakunshd;
        ref_module -- Right .. e_cell;
        eff_front -- Right .. globeff;
        outboard_front -- Right .. globinc;
    }
);

