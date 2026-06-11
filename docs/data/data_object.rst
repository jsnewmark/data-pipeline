CODEX data structure
====================

Concept
-------
CODEX data is structured using the FITS extension framework, with 4 data arrays, one for each polarization, along with a corresponding World Coordinate System (WCS) describing the spatial coordinates of the data itself.
This allows for better integration with AstroPy software libraries, including coordinate and data reprojection or resampling.
For primary Level 2 CODEX data, connecting data with coordinates is critical given that the instrument is only 2
axis stabilized (azimuth and elevation), so the scene will have an apprent rotation throughout each orbit, aand data analysis is epxected to require both spatial and temporal averaging.

Uncertainty
-----------

The uncertainty is stored within the ???
