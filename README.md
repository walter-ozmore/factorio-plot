# Factorio Map Creator
A tool for turning Factorio maps in to saves.

# Installation
Download the repo `wget https://github.com/walter-ozmore/factorio-plot/archive/refs/heads/main.zip -O factorio-plot`

Unzip the repo and enter it `unzip factorio-plot && cd factorio-plot-main`

Run with `./start.sh`



The output images' file names can be edited using `config.yaml` and the colors can be edited by the files in the shader folder

# Common issues

Error: `./start.sh: line 14: venv/bin/activate: No such file or directory`

Solution: Delete the venv folder in the directory

# Shades
The primary way to edit the style of the output image is with shader files. Shader files can be selected via `shader: shades.yaml` in `config.yaml`. All shaders must be a yaml file inside of the shaders folder.