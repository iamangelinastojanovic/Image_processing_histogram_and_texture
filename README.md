# Texture Analysis from the Brightness Histogram

Digital Image Processing homework (*Digitalna obrada slike*), implemented in Python with NumPy, OpenCV and Matplotlib.

## Task

The image `slika 222.jpg` shows a microscopic cross-section of muscle tissue. The goal is to compute the following statistical texture descriptors from its brightness histogram:

- the first three moments (mean, variance, third central moment / skewness),
- uniformity,
- average entropy,

and to comment, based on these values, whether the texture is mainly **smooth, coarse or regular**.

## Method

The image is loaded as grayscale and its normalized histogram `p(z_i)` is computed over `L = 256` brightness levels.

| Descriptor | Formula |
|---|---|
| Mean | `m = sum(z_i * p(z_i))` |
| Variance (2nd central moment) | `mu_2 = sum((z_i - m)^2 * p(z_i))` |
| Third central moment (skewness) | `mu_3 = sum((z_i - m)^3 * p(z_i))` |
| Uniformity | `U = sum(p(z_i)^2)` |
| Average entropy | `e = -sum(p(z_i) * log2(p(z_i)))` |

## Getting started

```bash
pip install -r requirements.txt
python main.py
```

The script prints all descriptors to the console and saves the brightness histogram as `Histogram sjajnosti slike.png`.

## Project structure

```
main.py            # histogram, moments, uniformity and entropy
slika 222.jpg      # test image
requirements.txt   # opencv-python, numpy, matplotlib
```
