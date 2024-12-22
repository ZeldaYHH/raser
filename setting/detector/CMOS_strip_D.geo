// GMSH Geometry File: CMOS_strip_D.geo

SetFactory("OpenCASCADE");

lc = 5e-5;
lp = 5e-5;
ln_up = 5e-5;
ln = 5e-5;
ln_well = 5e-5;

// outer
Point(1) = {0, 0, 0, lp};
Point(2) = {0, 75.5e-4, 0, lp};
Point(3) = {147e-4, 75.5e-4, 0, lc};
Point(4) = {147e-4, 0, 0, lc};

// p stop 1
Point(5) = {0, 1e-4, 0, lp};
Point(6) = {-1e-4, 1e-4, 0, lp};
Point(7) = {-1e-4, 0, 0, lp};

Line(1) = {1, 7};
Line(2) = {7, 6};
Line(3) = {6, 5};
Line(4) = {1, 5};

Line Loop(1) = {1, 2, 3, -4};
Plane Surface(1) = {1};

Transfinite Line {1, 2, 3, 4} = 10;
Transfinite Surface {1};

// p well 1
Point(8) = {2e-4, 0, 0, lp};
Point(9) = {2e-4, 1e-4, 0, lp};

Line(5) = {1, 8};
Line(6) = {8, 9};
Line(7) = {9, 5};

Line Loop(2) = {5, 6, 7, -4};
Plane Surface(2) = {2};

Transfinite Line {5, 6, 7} = 10;
Transfinite Surface {2};

// p stop 2 
Point(10) = {0, 74.5e-4, 0, lp};
Point(11) = {-1e-4, 75.5e-4, 0, lp};
Point(12) = {-1e-4, 74.5e-4, 0, lp};

Line(8) = {10, 12};
Line(9) = {12, 11};
Line(10) = {11, 2};
Line(11) = {10, 2};

Line Loop(3) = {8, 9, 10, -11};
Plane Surface(3) = {3};

Transfinite Line {8, 9, 10, 11} = 10;
Transfinite Surface {3};

// p well 2 
Point(13) = {2e-4, 75.5e-4, 0, lp};
Point(14) = {2e-4, 74.5e-4, 0, lp};

Line(12) = {2, 13};
Line(13) = {13, 14};
Line(14) = {14, 10};

Line Loop(4) = {12, 13, 14, 11};
Plane Surface(4) = {4};

Transfinite Line {12, 13, 14} = 10;
Transfinite Surface {4};

// n stop 
Point(15) = {0, 30.25e-4, 0, ln_up};
Point(16) = {0, 45.25e-4, 0, ln_up};
Point(17) = {-0.5e-4, 45.25e-4, 0, ln_up};
Point(18) = {-0.5e-4, 30.25e-4, 0, ln_up};
Point(19) = {-1e-4, 45.25e-4, 0, ln_up};
Point(20) = {-1e-4, 30.25e-4, 0, ln_up};

Line(15) = {19, 17};
Line(16) = {17, 18};
Line(17) = {18, 20};
Line(18) = {20, 19};

Line Loop(5) = {15, 16, 17, 18};
Plane Surface(5) = {5};

Transfinite Line {15, 16, 17, 18} = 15;
Transfinite Surface {5};

Line(19) = {16, 17};
Line(20) = {18, 15};
Line(21) = {15, 16};

Line Loop(6) = {19, 16, 20, 21};
Plane Surface(6) = {6};

Transfinite Line {19, 20, 21} = 15;
Transfinite Surface {6};

// n well 
Point(21) = {2e-4, 46.75e-4, 0, ln_well};
Point(22) = {2e-4, 28.75e-4, 0, ln_well};
Point(23) = {0e-4, 46.75e-4, 0, ln_well};
Point(24) = {0e-4, 28.75e-4, 0, ln_well};

Line(22) = {15, 22};
Line(23) = {22, 21};
Line(24) = {21, 16};

Line Loop(7) = {22, 23, 24, -21};
Plane Surface(7) = {7};

Transfinite Line {22, 23, 24} = 15;
Transfinite Surface {7};

Line(26) = {21, 23};
Line(27) = {23, 16};

Line Loop(8) = {26, 27, -24};
Plane Surface(8) = {8};

Transfinite Line {26, 27} = 10;
Transfinite Surface {8};

Line(29) = {22, 24};
Line(30) = {24, 15};

Line Loop(9) = {29, 30, -22};
Plane Surface(9) = {9};

Transfinite Line {29, 30} = 10;
Transfinite Surface {9};

Line(31) = {5, 24};
Line(32) = {22, 9};

Line Loop(10) = {31, -29, 32, 7};
Plane Surface(10) = {10};

Transfinite Line {31, 32} = 25;
Transfinite Surface {10};

Line(33) = {10, 23};
Line(34) = {21, 14};

Line Loop(11) = {33, -26, 34, 14};
Plane Surface(11) = {11};

Transfinite Line {33, 34} = 25;
Transfinite Surface {11};

// bulk: front

Point(25) = {5e-4, 0, 0, lc};
Point(26) = {5e-4, 28.75e-4, 0, lc};
Point(27) = {5e-4, 46.75e-4, 0, lc};
Point(28) = {5e-4, 75.5e-4, 0, lc};

Line(35) = {8, 25};
Line(36) = {25, 9};

Line Loop(12) = {35, 36, -6};
Plane Surface(12) = {12};

Transfinite Line {35, 36} = 10;
Transfinite Surface {12};

Line(37) = {13, 28};
Line(38) = {28, 14};

Line Loop(13) = {37, 38, -13};
Plane Surface(13) = {13};

Transfinite Line {37, 38} = 10;
Transfinite Surface {13};

Line(39) = {21, 27};
Line(40) = {27, 28};

Line Loop(14) = {39, 40, 38, -34};
Plane Surface(14) = 14;

Transfinite Line {39} = 10;
Transfinite Line {40} = 25;
Transfinite Surface {14};

Line(41) = {25, 26};
Line(42) = {26, 22};

Line Loop(15) = {32, -36, 41, 42};
Plane Surface(15) = 15;

Transfinite Line {41} = 25;
Transfinite Line {42} = 10;
Transfinite Surface {15};

Line(43) = {26, 27};

Line Loop(16) = {42, 23, 39, -43};
Plane Surface(16) = 16;

Transfinite Line {43} = 15;
Transfinite Surface {16};

// bottom

Point(29) = {147e-4, 28.75e-4, 0, lc};
Point(30) = {147e-4, 46.75e-4, 0, lc};

Line(44) = {28, 3};
Line(45) = {3, 30};
Line(46) = {30, 27};

Line Loop(17) = {44, 45, 46, 40};
Plane Surface(17) = 17;

Transfinite Line {45} = 25;
Transfinite Line {44, 46} = 50;
Transfinite Surface {17};

Line(47) = {26, 29};
Line(48) = {29, 4};
Line(49) = {4, 25};

Line Loop(18) = {47, 48, 49, 41};
Plane Surface(18) = 18;

Transfinite Line {48} = 25;
Transfinite Line {47, 49} = 50;
Transfinite Surface {18};

Line(50) = {29, 30};

Line Loop(19) = {47, 50, 46, -43};
Plane Surface(19) = 19;

Transfinite Line {50} = 15;
Transfinite Surface {19};

Point(31) = {150e-4, 0, 0, lc};
Point(32) = {150e-4, 28.75e-4, 0, lc};
Point(33) = {150e-4, 46.75e-4, 0, lc};
Point(34) = {150e-4, 75.5e-4, 0, lc};

Line(51) = {3, 34};
Line(52) = {34, 33};
Line(53) = {33, 30};

Line Loop(20) = {51, 52, 53, 45};
Plane Surface(20) = 20;

Transfinite Line {51, 53} = 5;
Transfinite Line {52} = 25;
Transfinite Surface {20};

Line(54) = {29, 32};
Line(55) = {32, 31};
Line(56) = {31, 4};

Line Loop(21) = {54, 55, 56, -48};
Plane Surface(21) = 21;

Transfinite Line {54, 56} = 5;
Transfinite Line {55} = 25;
Transfinite Surface {21};

Line(57) = {33, 32};

Line Loop(22) = {57, -54, 50, -53};
Plane Surface(22) = 22;

Transfinite Line {57} = 15;
Transfinite Surface {22};

// physics groups
Physical Line("bot") = {52, 55, 57};
Physical Line("top") = {18};
Physical Surface("CMOS_strip_D") = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22};

// mesh
Mesh 2;
Mesh.MshFileVersion = 2.2;