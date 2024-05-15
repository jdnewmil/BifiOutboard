// wedge_by_removal.asy
// based on example from https://tex.stackexchange.com/questions/87009/how-to-cut-a-surface-at-the-intersection-with-another-surface-in-asymptote

settings.outformat="pdf";
settings.prc=false;
settings.render=8;
size(8.9cm, 0);

import three;
import solids;

currentprojection = perspective(3*(5,2,3));//obliqueY();

// path3 xyplane = path3(scale(10) * box((-1,-1),(1,1)));

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

draw(O -- X, L=Label("$x$", align=W, position=EndPoint));
draw(O -- Y, L=Label("$y$", align=E, position=EndPoint));
draw(O -- Z, L=Label("$z$", align=N, position=EndPoint));

surface w = wedge_plane(1, 0, 160, 270, 60);
draw(w,red+opacity(0.3));
