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
real pitch = 4;
real shadeline = 3;
real southline = -3;
real northline = 4;
real southedgeline = 2;
real L = 1;
real H = 2;
real phi = degrees(atan2(H, shadeline - southedgeline));
real psi = degrees(atan2(H, shadeline));
real aex = northline - southedgeline;
real aey = pitch/4;
real roll = 30;

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

// surface unshaded = surface(
//     myarc
//     , angle1=0
//     , angle2=180-psi
//     , c=O
//     , axis=X
//     , n=1
// );
surface unshadedwedge = rotate(-90, Z) * rotate(-90, X) * wedge_plane(1, 180-psi, 180, 270, 90 - roll);
// surface shaded = surface(
//     myarc
//     , angle1=180-psi
//     , angle2=180
//     , c=O
//     , axis=X
//     , n=1
// );
surface shadedwedge = rotate(-90, Z) * rotate(-90, X) * wedge_plane(1, 0, 180 - psi, 270, 90 - roll);
surface skywedge = rotate(90, Z) * surface(
    myarc
    , angle1=180
    , angle2=180+roll
    , c=O
    , axis=X
    , n=1
);


// pens
pen unshadedground_pen = gray(0.8)+opacity(1);
pen shadedground_pen = gray(0.4)+opacity(1);
pen array_pen = gray+opacity(0.9);
material shadedgroundwedge_pen = material(
    diffusepen=0.3*white+opacity(0.9)
    , emissivepen=0.1*white
);
material unshadedgroundwedge_pen = material(
    yellow+opacity(0.4)
    , emissivepen=0.0*yellow
);
material skywedge_pen = material(
    blue+opacity(0.3)
    , emissivepen=0.0*blue
);


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
draw(2Y -- 2Y-2Z, L=Label("$H$", align=W, position=Relative(0.3)));
// "ground"
draw(southline*Y-2Z -- northline*Y-2Z);
// phi line
draw(2Y -- shadeline*Y-2Z);
draw(phi_arc3);
draw(psi_arc3);

// unshaded wedge
draw(unshadedwedge, surfacepen=unshadedgroundwedge_pen);
// psi line
draw(0Y -- shadeline*Y-2Z);
// shaded wedge
draw(shadedwedge, surfacepen=shadedgroundwedge_pen);
// sky hemisphere
draw(skywedge, surfacepen=skywedge_pen);

// torque tube axis
draw(
    0*Y -- southedgeline*Y
    , p=blue+linewidth(1pt)
    , L=Label(
        "$L$"
        , align=N
        , position=Relative(0.75)
    )
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
label(Label("$\phi$"), position=towardcamera(shadeline*Y + 0.3Y - 1.9Z));
label(Label("$\psi$"), position=towardcamera((shadeline+0.3)*Y + 1.5X - 2Z));

