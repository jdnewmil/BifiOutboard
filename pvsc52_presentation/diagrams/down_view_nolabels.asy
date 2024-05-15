settings.outformat="svg";
settings.prc=false;
settings.render=8;
import graph3;
size(8.9cm, 0);
defaultpen(fontsize(10));

//Direction of a point toward the camera.
triple cameradirection(
    triple pt
    , projection P = currentprojection
) {
    if (P.infinity) {
        return unit(P.camera);
    }
    return unit(P.camera - pt);
}

//Move a point closer to the camera.
triple towardcamera(
    triple pt
    , real distance=1
    , projection P = currentprojection
) {
    return pt + distance * cameradirection(pt, P);
}


// dimensions
real pitch = 4;
real shadeline = 3;
real southline = -3;
real northline = 8;
real southedgeline = 2;
real L = 1;
real H = 2;
real phi = degrees(atan2(H, shadeline - southedgeline));
real psi = degrees(atan2(H, shadeline));
real aex = northline - southedgeline;
real aey = pitch/4;

// 2d paths
path phi_arc = arc(c=(0, 0), 0.3, 0, phi);
path psi_arc = arc(c=(0, 0), 0.5, 0, psi);
path arrayedge = (
    (aex, -aey) --
    (0, -aey) --
    (0, aey) --
    (aex, aey)
);
path arrayfill = arrayedge -- cycle;

// 3d paths
path3 phi_arc3 = shift(-H*Z+shadeline*Y)*rotate(-90,Y)*rotate(-90,Z)*path3(phi_arc);
path3 psi_arc3 = shift(-H*Z+shadeline*Y)*rotate(-90,Y)*rotate(-90,Z)*path3(psi_arc);
path3 myarc = (
    Arc(
        c=O
        , normal=Z
        , v1=-X
        , v2=X
        , n=30
    )
);
path3 arrayedge3 = shift(2Y)*rotate(90,Z)*path3(arrayedge);

// surfaces
surface unshaded = surface(
    myarc
    , angle1=0
    , angle2=180-psi
    , c=O
    , axis=X
    , n=1
);
surface shaded = surface(
    myarc
    , angle1=180-psi
    , angle2=180
    , c=O
    , axis=X
    , n=1
);


// pens
pen unshadedground_pen = gray(0.8)+opacity(1);
pen shadedground_pen = gray(0.4)+opacity(1);
pen array_pen = gray+opacity(0.9);

// ground plane
path unshadedground = (
    (-pitch, southline) --
    (-pitch, shadeline) --
    (-3/4*pitch, shadeline) --
    (-3/4*pitch, northline) --
    (-pitch/4, northline) --
    (-pitch/4, shadeline) --
    (pitch/4, shadeline) --
    (pitch/4, northline) --
    (3/4*pitch, northline) --
    (3/4*pitch, shadeline) --
    (pitch, shadeline) --
    (pitch, southline) --
    cycle
    // (-pitch, southline)
);
path shadedgroundpatch = box((-pitch/4, shadeline), (pitch/4, northline));
path halfshadedgroundpatch = box((0, shadeline), (pitch/4, northline));
draw(shift(-H*Z)*surface(path3(unshadedground)), surfacepen=unshadedground_pen);
draw(shift(-H*Z)*surface(path3(shadedgroundpatch)), surfacepen=shadedground_pen);
draw(shift(-H*Z + 3/4*pitch * X) * surface(path3(halfshadedgroundpatch)), surfacepen=shadedground_pen);
draw(shift(-H*Z - pitch * X)*surface(path3(halfshadedgroundpatch)), surfacepen=shadedground_pen);

// reference lines
// "post"
draw(2Y -- 2Y-2Z);
// "ground"
draw(southline*Y-2Z -- northline*Y-2Z);
// phi line
draw(2Y -- shadeline*Y-2Z);
draw(phi_arc3);
draw(psi_arc3);

// unshaded hemisphere
draw(
    unshaded
    , surfacepen=material(
        yellow+opacity(0.4)
        , emissivepen=0.0*yellow)
);
// psi line
draw(0Y -- shadeline*Y-2Z);
// shaded hemisphere
draw(
    shaded
    , surfacepen=material(
        diffusepen=0.3*white+opacity(0.9)
        , emissivepen=0.1*white)
);

// torque tube axis
draw(
    0*Y -- southedgeline*Y
    , p=blue+linewidth(1pt)
);
draw(
    southedgeline*Y -- northline*Y
    , p=blue+linewidth(1pt)
);

// array
draw(
    surface(shift((0,2))*rotate(90)*arrayfill)
    , surfacepen=array_pen
);
draw(
    arrayedge3
    , gray(0.5)
);

// labels
// label(Label("$\phi$"), position=towardcamera(shadeline*Y + 0.3Y - 1.9Z));
// label(Label("$\psi$"), position=towardcamera((shadeline+0.3)*Y + 1.5X - 2Z));

