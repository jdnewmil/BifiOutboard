settings.outformat="png";
settings.prc=false;
settings.render=8;

import flowchart;

unitsize(1mm);
size(0, 8.9cm);
defaultpen(fontsize(10));

// scalars
real row_spacing = 2.5;
real col_width = 5;
real label_space = 2.5;

// pairs
pair up = (0, row_spacing);
pair right = (col_width, 0);

pair col0base = (-label_space, 0);
pair col1base = (0, 0);
pair col2base = (col_width, 0);

// paths

// blocks
block e_rear_outboard = rectangle("$E_\mathrm{rear,outboard}$", col2base);
block globbakunshd = rectangle("$\mathrm{GlobBakUnshd}$", shift(up) * col1base);
block globbakframe = rectangle("$\mathrm{GlobBakFrame}$", shift(2 * up) * col1base);
block globbak = rectangle("$\mathrm{GlobBak}$", shift(3 * up) * col1base);
block e_cell = rectangle("$E_\mathrm{cell}$", shift(4 * up) * col1base);
block globeff = rectangle("$\mathrm{GlobEff}$", shift(5 * up) * col1base);
block globinc = rectangle("$\mathrm{GlobInc}$", shift(6 * up) * col1base);
block globhor = rectangle("$\mathrm{GlobHor}$", shift(7 * up) * col1base);
block dc_conv = rectangle("$\mathrm{EArrNom}$", shift(right) * shift(4 * up) * col1base);

Label outboard_bias = Label("Irradiance exposure bias", align=W, position=col1base);
Label rear_struct = Label("Array frame structural loss", align=W, position=shift(1.5 * up) * col1base);
Label mod_frame = Label("Module frame structural loss", align=W, position=shift(2.5 * up) * col1base);
Label bifaciality = Label("Bifaciality", align=W, position=shift(3.5 * up) * col1base);
Label spec_shd_soil = Label("Shade, spectrum, soiling", align=W, position=shift(5.5 * up) * col1base);
Label transpos = Label("Transposition, diffuse estimation", align=W, position=shift(6.5 * up) * col1base);

Label unshd_rear_sensor = Label("(not feasible; complex shade)", align=W, position=shift(left) * shift(up) * col0base);
Label midway_sensor = Label("Sensor at rear module frame???", align=W, position=shift(left) * shift(2 * up) * col0base);
Label channelled_sensor = Label("Sensor at rear laminate???", align=W, position=shift(left) * shift(3 * up) * col0base);
Label ref_module = Label("Reference module", align=W, position=shift(left) * shift(4 * up) * col0base);
Label eff_front = Label("(hardly feasible; diffuse shading)", align=W, position=shift(left) * shift(5 * up) * col0base);
Label outboard_front = Label("Standard front-facing outboard", align=W, position=shift(left) * shift(6 * up) * col0base);


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

label(unshd_rear_sensor);
label(midway_sensor);
label(channelled_sensor);
label(ref_module);
label(eff_front);
label(outboard_front);


add(
    new void(picture pic, transform t) {
        blockconnector operator --=blockconnector(pic,t);

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
    }
);

