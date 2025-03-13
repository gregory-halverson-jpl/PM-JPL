# JPL implementation of the MOD16 evapotranspiration remote sensing model

[![CI](https://github.com/JPL-Evapotranspiration-Algorithms/MOD16-JPL/actions/workflows/ci.yml/badge.svg)](https://github.com/JPL-Evapotranspiration-Algorithms/MOD16-JPL/actions/workflows/ci.yml)

The MODIS Global Evapotranspiration Project (MOD16) is a software package developed by a team of researchers from NASA Jet Propulsion Laboratory and the University of Montana. This software is a Python implementation of the MOD16 evapotranspiration algorithm, designed to process high-resolution instantaneous remote sensing imagery.

Unique features of the software include the ability to process remote sensing data with the MOD16 model and partition latent heat flux into canopy transpiration, interception, and soil evaporation. The MOD16 algorithm has been re-implemented to run on instantaneous high spatial resolution remote sensing imagery instead of 8-day MODIS imagery, making the model more accessible for remote sensing researchers.

The software is written entirely in Python and is intended to be distributed using the pip package manager.

The software was developed as part of a research grant by the NASA Research Opportunities in Space and Earth Sciences (ROSES) program. It was designed for use by the Ecosystem Spaceborne Thermal Radiometer Experiment on Space Station (ECOSTRESS) mission as a precursor for the Surface Biology and Geology (SBG) mission. However, it may also be useful for general remote sensing and GIS projects in Python. This package can be utilized for remote sensing research in Jupyter notebooks and deployed for operations in data processing pipelines. 

The software is being released according to the SPD-41 open-science requirements of NASA-funded ROSES projects.

Gregory H. Halverson (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

Kanishka Mallick (he/him)<br>
[kaniska.mallick@gmail.com](mailto:kaniska.mallick@gmail.com)<br>
Luxembourg Institute of Science and Technology

Claire Villanueva-Weeks (she/her)<br>
[claire.s.villanueva-weeks@jpl.nasa.gov](mailto:claire.s.villanueva-weeks@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

## Installation

```
pip install MOD16-JPL
```

## Usage

```
import MOD16_JPL
```

## References

- Mu, Q., Zhao, M., & Running, S. W. (2011). Improvements to a MODIS global terrestrial evapotranspiration algorithm. *Remote Sensing of Environment*, 115(8), 1781-1800. doi:10.1016/j.rse.2011.02.019
- Mu, Q., Heinsch, F. A., Zhao, M., & Running, S. W. (2007). Development of a global evapotranspiration algorithm based on MODIS and global meteorology data. *Remote Sensing of Environment*, 111(4), 519-536. doi:10.1016/j.rse.2007.04.015
