import pytest

# List of dependencies
dependencies = [
    "affine",
    "astropy",
    "geopandas",
    "h5py",
    "keras",
    "matplotlib",
    "numpy",
    "PIL",
    "pandas",
    "pyproj",
    "pyresample",
    "rasterio",
    "requests",
    "scipy",
    "shapely",
    "six",
    "skimage",
    "sun_angles",
    "tensorflow",
    "urllib3"
]

# Generate individual test functions for each dependency
@pytest.mark.parametrize("dependency", dependencies)
def test_dependency_import(dependency):
    __import__(dependency)
