# Factorio Map Creator
A tool for turning Factorio maps in to pictures. Allows you to configure custom image ratios, colors, included structures, etc. Currently only compatiable with Linux due to the server files.

**Does not currently do ships and does not **

# Installation
1. Download the repo from GitHub `wget https://github.com/walter-ozmore/factorio-plot/archive/refs/heads/main.zip -O factorio-plot`
2. Unzip the repo and navigate to it `unzip factorio-plot && cd factorio-plot-main`
3. Run the sh file `./start.sh`

# Common issues
__Error__
`./start.sh: line 14: venv/bin/activate: No such file or directory`
__Solution__
Delete the `venv` folder in the directory.

# Customization
The customization is done using the `config.yaml` and a shaders `.yaml` file. Please see below for more information.

## config.yaml
The `config.yaml` file allows you to edit to edit all of the below details.

__aspect-ratio__ required
The desired aspect ratio for the generated images. Can be any number, including decibles. In this format: `num1:num2`.

__padding__
The dev made this a hardcoded value at 10% and any changes are purely placebo. Config coming soon.

__shader__ required
Lets you select your desired shader file. This project provides several defaults to pick from, or you can make your own. See more in the shader.yaml section below.

__filename__ requires
The name format for the generated images. You can use `{datetime}` and `{surfaceName}`. This acts as creating a path, so you will want to avoid slashes unless you are wanting them stored in a folder.

__auto-update-server__ required
When set to true, it will automatically download the newest Factorio server from their website and will use it to create the files. This is primarily for if someone is using an older version of Factorio and is unable to update.

__factorio-save-name__ required
Name of the Factorio save in the save path directory. You do not need to include the `.zip`.

__factorio-save-path__ required
The location of the save file.

__backgrounds-folder__
Where the files are moved to if you do not want them to be in the default `images` folder.

__auto-generated__
A flag to show whether or not you want the script's tutorial messages.

## Shaders