from astropy.io import fits
import spiceypy as spice
import numpy as np


# # Telemetered quaternions and gimbal angles
# boresite = {
#     "qPI": [0.86901498, -0.27779409, -0.34568208, -0.21723367],  # from msg ID 9
#     "qBHr": [2.94100939e-08, -3.87863111e-07, 6.20560695e-06, 1.0],  # from msg ID 5
#     "Elg": -21.08327866,  # elevetion in degrees
#     "Azg": 39.22232866,  # azimuth in degrees
# }

# # Multiple ground measurements taken to characterize the misalignment parameters
# angles = {"Azer": -1.708, "epsx": -0.087, "alfx": 0.013, "alfy": -0.306}

# # WCS parameters derived from star fiels of 2025-01-03 14:49:20 image
# wcs = {
#     "crpix": [1971.722015853095, 1075.167887220806],  # boresgiht pixel
#     "cdelt": 0.001810039520077789,  # plate scale in degrees
#     "crota": -1.6962362045362835,  # detector tilt in degrees
# }

class Quaternion:
    def __init__(self, array=None, phi=0.0, axis=0):
        if array is None:
            array = np.array([0, 0, 0, np.cos(phi / 2)])
            array[axis] = np.sin(phi / 2)
            self.array = array
        else:
            self.array = np.array(array)

        self.v = self.array[0:3]
        self.s = self.array[3]
        self.x = self.v[0]
        self.y = self.v[1]
        self.z = self.v[2]

        self.spice = np.array([self.s, -self.v[0], -self.v[1], -self.v[2]])

    def __add__(self, other):
        return Quaternion(self.array + other.array)

    def __mul__(self, other):
        v = self.s * other.v + other.s * self.v - np.cross(self.v, other.v)
        s = self.s * other.s - np.dot(self.v, other.v)
        return Quaternion([v[0], v[1], v[2], s])
    

    # Transform JD to Gregorian date
def jd2ymd(jd):
    l = int(jd + 68569)
    n = (4 * l) // 146097
    l = l - ((146097 * n + 3) // 4)
    i = (4000 * (l + 1)) // 1461001
    l = l - (1461 * i) // 4 + 31
    j = (80 * l) // 2447
    d = l - (2447 * j) // 80
    l = j // 11
    m = j + 2 - (12 * l)
    y = (100 * (n - 49)) + i + l
    return y, m, d


# Convert CODEC PCS timastamp to UTC
def timeFromPcsTimeStamp(timestamp=(0, 0)):
    seconds, subseconds = timestamp
    epochJd = 2440588  # Julian Day of 1970-01-01
    epochLeap = (
        27  # leap seconds since epoch (PCS sticks this in, so we need to remove it)
    )

    # Convert 16-bit subseconds to integer microseconds
    microseconds = int(15.2587890625 * subseconds)

    # Calculate Integer Julian Day from PCS seconds since epoch
    julianDay = epochJd + int(seconds - epochLeap) // 86400

    # Convert Julian Day to Gregorian Date
    year, month, day = jd2ymd(julianDay)

    # Calculate time of day in seconds from seconds since epoch using
    timeOfDay = int(seconds - epochLeap) % 86400

    # Convert time of day to hours, minutes, seconds
    remainder = int(timeOfDay)
    hour = remainder // 3600
    remainder = remainder % 3600
    minute = remainder // 60
    second = remainder % 60

    # Create UTC ISO string
    utc = "{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:06.3f}Z".format(
        year, month, day, hour, minute, second + microseconds / 1e6
    )

    return utc


# Transform celestial coordinates to CODEX projective coordinates
def radec2hpc(et, r, ra=0, dec=0, **kwargs):
    object = kwargs.get("object", None)
    n = np.size(ra)
    c = np.empty([3, n])

    if object is None:
        # Compute rect. coordinates from RA and Dec
        c[0] = np.cos(dec) * np.cos(ra)
        c[1] = np.cos(dec) * np.sin(ra)
        c[2] = np.sin(dec)
    else:
        # Compute rect. coordinates of the desired object in J2000 frame
        s, lt = spice.spkezr(object, et, "j2000", "none", "earth")
        c[:, 0] = s[0:3]

    for i in range(n):
        # Rotate coordinates from J2000 to CODEX frame
        c[:, i] = np.array(spice.reclat(r.dot(c[:, i])))

    # Change the sign of the longitude (TBC why it is needed)
    c[1] = -c[1]

    return c[1:3]


# Compute rotation matrix for a desired angle
def rot(x=0):
    r = np.array([[np.cos(x), -np.sin(x)], [np.sin(x), np.cos(x)]])

    return r


