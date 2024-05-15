settings.outformat="pdf";
settings.prc=false;
settings.render=16;
import graph3;
size(0, 3.5 inches);
defaultpen(fontsize(10));

// run this with
// asy -u variant=something -o down_view_flat.svg

// variant=flat
//  array in flat position, with angle annotations
// variant=roll
//  array in rolled position, with angle annotations

string variant;
usersetting();

bool isin(string x, string[] v) {
    int i = 0;
    while (i < v.length) {
        if (v[i] == x) {
            return true;
        }
        ++i;
    }
    return false;
}

// start debugger
// breakpoint();

string[] variant_a = {};
if ("roll" == variant) {
    string[] va_opt = {"roll30"};
    variant_a.append(va_opt);
} else if ("flat" == variant) {
    string[] va_opt = {"roll0"};
    variant_a.append(va_opt);
} else if ("flatnolbl" == variant) {
    string[] va_opt = {"roll0", "nolabel"};
    variant_a.append(va_opt);
} else if ("flatgw" == variant) {
    string[] va_opt = {"roll0", "nolabel", "nougw", "noarray", "noreflines", "nopost"};
    variant_a.append(va_opt);
} else if ("longarray" == variant) {
    string[] va_opt = {"roll30", "nolabel", "noreflines", "longarray", "nowedge", "downhemi"};
    variant_a.append(va_opt);
} else if ("sungeom" == variant) {
    string[] va_opt = {"roll30", "nolabel", "sungeom", "noreflines", "nowedge", "downhemi"};
    variant_a.append(va_opt);
} else if ("flatunsh" == variant) {
    string[] va_opt = {"roll0", "nosgw"};
    variant_a.append(va_opt);
} else if ("rollgw" == variant) {
    string[] va_opt = {"roll30", "nolabel", "nougw", "noarray", "noreflines", "nopost", "nosw"};
    variant_a.append(va_opt);
} else if ("rollugw" == variant) {
    string[] va_opt = {"roll30", "nolabel", "nosgw", "noarray", "noreflines", "nopost", "nosw"};
    variant_a.append(va_opt);
} else if ("wedgeonly" == variant) {
    string[] va_opt = {"wedgeonly"};
    variant_a.append(va_opt);
}

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

//Double-wedge cut
/*
R is radius of sphere
theta_start is beginning of wedge
theta_end is end of wedge
plane_theta is theta of normal to plane
plane_phi is phi of normal to plane

a plane in point-normal form is
  A*(x - a) + B*(y - b) + C*(z - c) = 0
if a point in the plane is Q=(a, b, c)
and n=(A, B, C) is the normal vector.
We need to map psi=(-pi/2, pi/2) onto
a possibly-reduced smaller angle psi0 based
on where the plane intersects the sphere
along various lines of constant theta.

The transformation from spherical to
cartesian is

x = R*sin(phi)*cos(theta)
y = R*sin(phi)*sin(theta)
z = R*cos(phi)

so if we assume the plane passes through the
origin then the upper boundary of the mapped surface area
is

  A*x + B*y + C*z = 0
  A*R*sin(phi0max)*cos(theta) + B*R*sin(phi0max)*sin(theta) + C*R*cos(phi0max) = 0
  A*sin(phi0max)*cos(theta) + B*sin(phi0max)*sin(theta) + C*cos(phi0max) = 0

and the normal vector coordinates can be substituted as

A=sin(plane_phi)*cos(plane_theta)
B=sin(plane_phi)*sin(plane_theta)
C=cos(plane_phi)

so we get

  sin(plane_phi)*cos(plane_theta)*sin(phi0max)*cos(theta) + sin(plane_phi)*sin(plane_theta)*sin(phi0max)*sin(theta) + cos(plane_phi)*cos(phi0max) = 0

which can be solved to obtain

tan(phi0max) = cos(plane_phi) / (-sin(plane_phi)*(sin(plane_theta)*sin(theta) + cos(plane_theta)*cos(theta)))

This function maps a rectangular region

  (theta_start_rad, 0), (theta_end_rad, pi)

onto a region bounded by fixed theta values and either theta=0 up to a sinusoidal limit, or from
that sinusoidal limit up to pi. Which is used depends on the direction of the normal vector.
To help remember, the normal is set to point away from the surface that is not being removed.

The term "removed" is a convenient fiction for using the function. The actual calculation
stretches the surface so that it avoids extending past the "slicing" plane.
*/
surface wedge_plane(real R, real theta_start, real theta_end, real plane_theta, real plane_phi) {
    triple parametricSphere(pair p) {
        real theta = p.x;
        real phi = p.y;
        real plane_theta_rad = radians(plane_theta);
        real plane_phi_rad = radians(plane_phi);
        real cos_plane_phi = cos(plane_phi_rad);
        real phi0slice = atan2(
            cos_plane_phi
            , -sin(plane_phi_rad) * (sin(plane_theta_rad) * sin(theta) + cos(plane_theta_rad) * cos(theta))
        );
        real phi0;
        if (cos_plane_phi < 0) {
          phi0 = phi0slice * (phi / pi);
        } else {
          phi0 = phi0slice + (pi - phi0slice) * (phi / pi);
         }
        real z = R * cos(phi0);
        real r = R * sin(phi0);
        real x = r * cos(theta);
        real y = r * sin(theta);
        return (x, y, z);
    }
    return surface(parametricSphere, (radians(theta_start), 0), (radians(theta_end), pi), Spline);
}


// dimensions
real pitch = 5;
real shadeline = 4;
real southline = -3;
real northline = 5;
if (isin("longarray", variant_a)) {
    northline = 16;
}
real southedgeline = 2;
real L = 1;
real H = 2;
real phi = degrees(atan2(H, shadeline - southedgeline));
real psi = degrees(atan2(H, shadeline));
real psi_arc_d = 0.5;
real aex = northline - southedgeline;
real aey = pitch/4;
//real azsol = -(90 + degrees(azimuth(sunvec))); // PVsyst convention is relative to equatorial direction
real azsol = -30;
real hsol = degrees(acos(Cos(phi) / Cos(azsol)));
real sunz = 90 - hsol;
real sunR = 6 / (Cos(azsol) * Cos(hsol));
triple sunvec = (
    scale3(sunR)
    * (
        + Cos(phi) / Cos(azsol) * X
        - Cos(phi) * Y
        + Sin(phi) * Z
    )
);
real roll = 30;

// 2d paths
path phi_arc = arc(c=(0, 0), 0.3, 0, phi);
path psi_arc = arc(c=(0, 0), psi_arc_d, 0, psi);
path phiang_arc = arc(c=(0, 0), 0.5, 0, roll);
path hsol_arc = arc(c=(0,0), 0.5, 0, hsol);
path azsol_arc = arc(c=(0,0), 0.8, 0, abs(azsol));
path arrayedge = (
    (aex, -aey) --
    (0, -aey) --
    (0, aey) --
    (aex, aey)
);
path arrayfill = arrayedge -- cycle;
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
);
path shadedgroundpatch = box((-pitch/4, shadeline), (pitch/4, northline));
path halfshadedgroundpatch = box((0, shadeline), (pitch/4, northline));


// 3d locations
triple sunvec_x = dot(sunvec, X) * X;
triple sunvec_y = dot(sunvec, Y) * Y;
triple sunvec_z = dot(sunvec, Z) * Z;
triple sunvec_gnd = sunvec - sunvec_z;
triple postbase = southedgeline * Y - H * Z;
triple shadebase = shadeline * Y - H * Z;
triple wedgelabel1 = unit(X-Y+5Z);
triple wedgelabel2 = rotate(psi/2, X) * unit(2Y-X);
triple da_label = unit(Z-Y+2X);

// 3d paths
real[][] shadeline_arc_transform = (
    shift(-H * Z + shadeline * Y)
    * rotate(-90, Y)
    * rotate(-90, Z)
);
path3 phi_arc3 = shadeline_arc_transform * path3(phi_arc);
path3 psi_arc3 = shadeline_arc_transform * path3(psi_arc);
path3 phiang_arc3 = shift(northline * Y) * rotate(-90, X) * rotate(180, Z) * path3(phiang_arc);
path3 hsol_arc3 = rotate(90+azsol, -Z) * rotate(90, X) * path3(hsol_arc);
path3 azsol_arc3 = rotate(-90, Z) * path3(azsol_arc);
path3 myarc = (
    Arc(
        c=O
        , normal=Z
        , v1=-X
        , v2=X
        , n=30
    )
);
real[][] ae_transform = shift(2Y) * rotate(90, Z);
if (isin("roll30", variant_a)) {
    ae_transform = rotate(roll, Y) * ae_transform;
}
path3 arrayedge3 = ae_transform * path3(arrayedge);
path3 arrayfill3 = ae_transform * path3(arrayfill);
path3 sunR3 = O -- sunvec;
path3 sunR3gnd = planeproject(Z) * sunR3;
path3 sunR3yz = planeproject(X) * sunR3;
path3 sunR3x = O -- sunvec_x;
path3 sunR3y = O -- sunvec_y;
path3 sunR3z = O -- sunvec_z;

// surfaces
surface unshadedgroundwedge = surface(
    myarc
    , angle1=0
    , angle2=180-psi
    , c=O
    , axis=X
    , n=1
);
surface shadedgroundwedge = surface(
    myarc
    , angle1=180-psi
    , angle2=180
    , c=O
    , axis=X
    , n=1
);
surface skywedge;
if (isin("roll30", variant_a)) {
    real[][] wp_transform = rotate(-90, Z) * rotate(-90, X);
    shadedgroundwedge = wp_transform * wedge_plane(1, 180 - psi, 180, 270, 90 - roll);
    unshadedgroundwedge = wp_transform * wedge_plane(1, 0, 180 - psi, 270, 90 - roll);
    skywedge = rotate(90, Z) * surface(
        myarc
        , angle1=180
        , angle2=180+roll
        , c=O
        , axis=X
        , n=1
    );
}
surface sun = shift(sunvec) * scale3(0.2) * surface(
    myarc
    , angle1=0
    , angle2=360
    , c=O
    , axis=X
    , n=2
);
surface downhemi = rotate(90, Z) * surface(
    myarc
    , angle1=roll
    , angle2=180+roll
    , c=O
    , axis=X
    , n=1
);


// pens
pen unshadedground_pen = gray(0.8) + opacity(1);
pen shadedground_pen = gray(0.4) + opacity(1);
pen arrayfill_pen = gray + opacity(0.9);
pen arrayedge_pen = gray(0.5);
pen arrayaxis_pen = black;
pen sensormountaxis_pen = blue + linewidth(1pt);
material shadedgroundwedge_pen = material(
    diffusepen=0.5 * white + opacity(0.7)
    , emissivepen=0.1 * white
);
material unshadedgroundwedge_pen = material(
    yellow + opacity(0.4)
    , emissivepen=0.0*yellow
);
material downhemi_pen = material(
    yellow + opacity(0.4)
    , emissivepen=0.0*yellow
);
material skywedge_pen = material(
    blue + opacity(0.3)
    , emissivepen=0.0*blue
);
material sun_pen = material(
    yellow + opacity(0.8)
    , emissivepen=0.1*yellow
);


// ------ drawing ------

if (isin("wedgeonly", variant_a)) {
    currentprojection = perspective(5, 6, 2);
    draw(
        path3(scale(0.1) * shift((-0.5, -0.5)) * unitsquare)
    );
    // unshaded wedge
    draw(
        reflect(Z-Z, X, Y) * unshadedgroundwedge
        , surfacepen=unshadedgroundwedge_pen);
    draw(
        reflect(Z-Z, X, Y) * shadedgroundwedge
        , surfacepen=shadedgroundwedge_pen);
    draw(-1.5X -- 1.5X, p=dashdotted, arrow=Arrow3);
    draw(
        1.2*da_label -- O
        , L=Label("$dA$", align=W, position=BeginPoint));
    draw(
        1.2 wedgelabel1 -- wedgelabel1
        , L=Label("$\frac{1+\cos{\psi}}{2}$", align=N, position=BeginPoint));
    draw(
        1.2 wedgelabel2 -- wedgelabel2
        , L=Label("$\frac{1-\cos{\psi}}{2}$", align=E, position=BeginPoint));
    draw(
        shift(sqrt(1-psi_arc_d^2) * X) * rotate(90, Z) * rotate(90, X) * path3(psi_arc)
        , L=Label("$\psi$", align=S, position=BeginPoint));
} else {
    draw(shift(-H*Z)*surface(path3(unshadedground)), surfacepen=unshadedground_pen);
    draw(shift(-H*Z)*surface(path3(shadedgroundpatch)), surfacepen=shadedground_pen);
    draw(shift(-H*Z + 3/4*pitch * X) * surface(path3(halfshadedgroundpatch)), surfacepen=shadedground_pen);
    draw(shift(-H*Z - pitch * X) * surface(path3(halfshadedgroundpatch)), surfacepen=shadedground_pen);

    // reference lines
    // "post"
    if (!isin("nopost", variant_a)) {
        if (!isin("nolabel", variant_a)) {
            draw(2Y -- 2Y-2Z, L=Label("$H$", align=W, position=Relative(0.7)));
        } else {
            draw(2Y -- 2Y-2Z);
        }
    }
    if (isin("sungeom", variant_a) || !isin("noreflines", variant_a)) {
        // "ground"
        if (isin("nolabel", variant_a)) {
            draw(southline*Y-2Z -- northline*Y-2Z);
        } else {
            draw(
                southline*Y-2Z -- northline*Y-2Z
                , L=Label(
                    "Equator"
                    , align=NW
                    , position=BeginPoint
                ));
        }
    }
    if (!isin("noreflines", variant_a)) {
        // shade line
        draw(
            shadeline * Y - 2Z - pitch * X -- shadeline * Y - 2Z + pitch * X
            , p=dashed
            , L=Label(
                "Shade line"
                , align=SW
                , position=EndPoint
            )
        );
        // phi line
        draw(2Y -- shadeline*Y-2Z);
        if (!isin("nolabel", variant_a)) {
            draw(phi_arc3);
            draw(psi_arc3);
            if (isin("roll30", variant_a)) {
                // PhiAng horizontal reference
                draw(northline * Y -- northline * Y - X);
                draw(phiang_arc3, L=Label("$\mathrm{PhiAng}$", align=3NE, position=Relative(0.0)));
            }
        }
    }

    // unshaded wedge
    if (!isin("nowedge", variant_a) & !isin("nougw", variant_a)) {
        // unshaded wedge
        draw(unshadedgroundwedge, surfacepen=unshadedgroundwedge_pen);
    } 

    // psi line
    if (!isin("noreflines", variant_a)) {
        draw(0Y -- shadeline*Y-2Z);
    }

    // shaded wedge
    if (!isin("nowedge", variant_a) && !isin("nosgw", variant_a)) {
        if (isin("roll30", variant_a)) {
            // shaded wedge
            draw(shadedgroundwedge, surfacepen=shadedgroundwedge_pen);
            if (!isin("nosw", variant_a)) {
                // sky hemisphere
                draw(skywedge, surfacepen=skywedge_pen);
            }
        } else {
            // shaded ground wedge
            draw(shadedgroundwedge, surfacepen=shadedgroundwedge_pen);
        }
    } else if (isin("downhemi", variant_a)) {
        // show hemisphere
        draw(downhemi, surfacepen=downhemi_pen);
    }

    if (!isin("nolabel", variant_a)) {
        // sensor mount axis
        draw(
            0*Y -- southedgeline*Y
            , p=sensormountaxis_pen
            , L=Label(
                "$L$"
                , align=N
                , position=Relative(0.75)
            )
        );
    } else {
        draw(
            0*Y -- southedgeline*Y
            , p=sensormountaxis_pen
        );
    }

    // sun geometry
    if (isin("sungeom", variant_a)) {
        draw(shift(shadebase) * sun, sun_pen);
        draw(shift(shadebase) * sunR3);
        draw(shift(shadebase) * sunR3gnd);
        draw(shift(shadebase + sunvec_gnd) * sunR3z);
        draw(shift(shadebase + sunvec_y) * sunR3x);
        draw(shift(shadebase + sunvec_y + sunvec_z) * sunR3x);
        draw(shift(shadebase + sunvec_y) * sunR3z);
        draw(shift(shadebase) * sunR3yz);
        draw(shift(shadebase) * hsol_arc3);
        label(Label("$\mathrm{HSol}$"), position=towardcamera(shadebase - 0.6X + 0.7Y, 2));
        draw(shift(shadebase) * azsol_arc3);
        label(Label("$\mathrm{AzSol}$"), position=towardcamera(shadebase + 3X + 1.5Y, 1));
    }

    if (!isin("noarray", variant_a)) {
        // array torque tube axis
        draw(
            southedgeline*Y -- northline*Y
            , p=arrayaxis_pen
        );

        // array
        draw(surface(arrayfill3), surfacepen=arrayfill_pen);
        draw(arrayedge3, arrayedge_pen);
    }

    if (!isin("nolabel", variant_a)) {
        // labels
        label(Label("$\phi$"), position=towardcamera(shadeline*Y + 0.3Y - 0.2X - 1.9Z));
        label(Label("$\psi$"), position=towardcamera((shadeline+0.1)*Y + X - 2Z));
    }
}