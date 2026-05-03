# Synthetic Thermal Load Generator

A tool for generating design-oriented, location-specific synthetic thermal load profiles based on air shade temperature and solar radiation, for use in finite element analysis of structures under environmental conditions.

## Description

The Synthetic Thermal Load Generator produces representative thermal boundary conditions by combining air shade temperature and solar radiation. The generated profiles are intended for engineering applications where realistic yet simplified environmental loading is required.

The methodology is based on the definition of heating and cooling cycles, allowing the estimation of temperature extremes and thermal gradients without the need of long-term climatic datasets.

## Key Features

- Generation of synthetic air shade temperature profiles
- Generation of synthetic solar radiation profiles
- Definition of heating and cooling phases
- Support for inclined surfaces and reflected radiation
- Export of structured data for numerical modelling

## Outputs

The tool generates:

- Radiation files (heating and cooling)
- Temperature files (heating and cooling)
- Optional solar position files for self-shadowing analysis

## Typical Applications

- Finite element thermal analysis
- Parametric studies
- Design of FRP and composite structures under environmental loading

## Notes

The generated loads are synthetic and design-oriented. They are intended to represent envelope conditions rather than exact site-specific measurements.

## Author

Marco Abreu Filho  
University of Minho, ISISE

## Related Tool

This tool can be used together with the **Self-Shadowing Analysis** tool for advanced evaluation of solar differential exposure effects.