
    Merge "atr72-500_out.stl";
    
    lc = 1; // Characteristic length (you can adjust this value for mesh refinement)
    
    // Define the corner points of the far-field box
    Point(1) = {-30, -30, -20, lc};
    Point(2) = {40, -30, -20, lc};
    Point(3) = {40, 30, -20, lc};
    Point(4) = {-30, 30, -20, lc};
    Point(5) = {-30, -30, 20, lc};
    Point(6) = {40, -30, 20, lc};
    Point(7) = {40, 30, 20, lc};
    Point(8) = {-30, 30, 20, lc};
    
    // Create lines connecting the points
    Line(1) = {1, 2};
    Line(2) = {2, 3};
    Line(3) = {3, 4};
    Line(4) = {4, 1};
    Line(5) = {5, 6};
    Line(6) = {6, 7};
    Line(7) = {7, 8};
    Line(8) = {8, 5};
    Line(9) = {1, 5};
    Line(10) = {2, 6};
    Line(11) = {3, 7};
    Line(12) = {4, 8};
    
    // Create line loops for the faces
    Line Loop(1) = {1, 2, 3, 4};
    Line Loop(2) = {5, 6, 7, 8};
    Line Loop(3) = {1, 10, -5, -9};
    Line Loop(4) = {2, 11, -6, -10};
    Line Loop(5) = {3, 12, -7, -11};
    Line Loop(6) = {4, -12, -8, 9};
    
    // Create surfaces from the line loops
    Plane Surface(2) = {1};
    Plane Surface(3) = {2};
    Plane Surface(4) = {3};
    Plane Surface(5) = {4};
    Plane Surface(6) = {5};
    Plane Surface(7) = {6};
    
    // Create surface loops for the volume (Corrections made here!!! added 1 to the SurfaceLoop)
    Surface Loop(1) = {1, 2, 3, 4, 5, 6, 7};
    
    // Create volume
    Volume(1) = {1};

    Physical Surface("Wing", 1) = {1};
    
    // Define the physical surfaces (if needed)
    Physical Surface("FarField") = {2,3,4,5,6,7};

    // Meshing
    Mesh 3;
