About the movie

Left panel:
    The round red fiducial point and the x-marked black perturbed points move according to the Lorenz system.
    
Right panel:
    The round red points are the eigenvalues of DF at the fiducial point.
    The x-marked blue points are the eigenvalues of (DF + DF^T)/2, where DF^T is the transpose of DF.

The Lorenz Eq: 
    du/dt = F(u),

where    

u = (x,y,z),

F =         
    [
        [-sigma * x + sigma * y],
        [-sigma * x - y - x * z],
        [-b * z + x * y - b * (r + sigma)]
    ].

The Jacobian DF is

    DF = 
        [
            [-sigma, sigma, 0],
            [-sigma - z, -1, -x],
            [y, x, -b]
        ].
