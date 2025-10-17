## SVG container and generator
Simple experiment to convert the image to svg and also, generate the random svg characeter.

### 1. Set Up the Environment

First, create a Python virtual environment and install the required dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> If you encounter issues installing **`pypotrace`**, it's likely due to missing system dependencies. Refer to the [pypotrace PyPI page](https://pypi.org/project/pypotrace/) for installation instructions.

### 2. Convert an Image to SVG

The script follows these main steps:

* Apply **K-means clustering** to reduce the image to *K* dominant colors.
* Generate a **binary mask** for each color cluster.
* Use **Potrace** to convert each binary mask into vector paths.
* Combine the paths into a single **SVG file**, using cluster colors as fill values.
* Save the result as a scalable vector image.

Run the script:

```bash
python img_to_svg.py
```

> Note: The image quantization method used in **Pillow** differs from that in **OpenCV**. If you're curious about the differences, check out this [notebook](./notebook/Donot_use_pillow_quantize.ipynb).
> Although `scikit-learn` could be used for quantization, OpenCV already provides the required functionality, so no additional libraries are necessary.

### 3. Create a Character in SVG

To generate a character in SVG format:

```bash
python character.svg
```

### 3. Create a Character animation in SVG

To generate a character in SVG format:

```bash
python character_animation.svg
```


### References

* 📘 [Pillow Documentation](https://pillow.readthedocs.io/en/stable/)
* 📘 [OpenCV Documentation](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
* 📘 [Potrace Documentation](https://pythonhosted.org/pypotrace/)
* 📦 [pypotrace on PyPI](https://pypi.org/project/pypotrace/)

