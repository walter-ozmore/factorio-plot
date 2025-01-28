import time, json, os, yaml, statistics, math, subprocess, threading, shutil, sys, platform, requests
import tarfile
from datetime import datetime
from PIL import Image, ImageDraw


def match(entity, colorCode):
	name = entity["name"]
	func = "EXACT"
	if "func" in colorCode:
		func = colorCode["func"]
	
	# Check all names
	for ccName in colorCode["names"]:
		# Handle functions
		match func:
			case "EXACT": 
				if name == ccName: return True
			case "IN": 
				if ccName in name: return True
	return False


def getAspect(width, height):
	"""
	Grabs the aspect ratio of the screen
	"""
	width = int(width)
	height = int(height)
	# Calculate the greatest common divisor of the width and height
	gcd_value = math.gcd(width, height)

	# Simplify the aspect ratio
	aspect_ratio_width = width // gcd_value
	aspect_ratio_height = height // gcd_value

	return aspect_ratio_width, aspect_ratio_height


def drawSurface(surfaceName, localSurfaceConfig):
	"""
	Draws the given surface on to an image
	"""
	def drawRect(x, y, width=1, height=1, color = 'red', style = "solid"):
		nonlocal tileSize, draw, imageWidth, imageHeight

		# Make the center of the image 0, 0
		x -= (width /2)
		y -= (height/2)

		x -= imageCenterX
		y -= imageCenterY

		# Define the box parameters
		top_left = (
			(x*tileSize) + (imageWidth/2), 
			(y*tileSize) + (imageHeight/2) - (width/2)
		) # Starting point (x, y)
		box_size = (tileSize*width, tileSize*height)  # Width and height (width, height)

		# Out of the image
		if top_left[0] < 0 or top_left[1] < 0: return
		if box_size[0] > imageWidth or box_size[1] > imageHeight: return

		# Draw the red box
		cords = [top_left, (top_left[0] + box_size[0], top_left[1] + box_size[1])]
		match style:
			case "solid": draw.rectangle(cords, fill=color, outline=color)
			case "outline": draw.rectangle(cords, outline=color, width=2)

	# Store unhandled names and tiles to make life easier for the localSurfaceConfig writers
	unhandledNames = {}

	# Load our surface data
	print("  Loading script export file...", end="", flush=True)
	with open(f"factorio/script-output/{surfaceName}.json", 'r') as file:
		data = json.load(file)
	print(" done.")

	tileSize = 5
	imageCenterX, imageCenterY = 0, 0
	imageWidth  = tileSize * int(2000/2) # Default size
	imageHeight = tileSize * int(2000/2) # Default size

	# Grab all of the cords for use in image center, scale and scope
	print("  Finding scope of file...", end="", flush=True)
	xCords, yCords = [], []
	for entry in data["entities"]:
		for localSurfaceConfigEntry in localSurfaceConfig["entries"]:
			if match(entry, localSurfaceConfigEntry) == False: continue
			if "flags" not in localSurfaceConfigEntry: continue
			if "center" not in localSurfaceConfigEntry["flags"]: continue # Make sure that this preset has the center flag
			xCords.append(entry["x"])
			yCords.append(entry["y"])
	print(" done.")

	# Move the image center, scale and scope
	# Get the image center
	minx, maxx = min(xCords), max(xCords)
	miny, maxy = min(yCords), max(yCords)
	imageCenterX = (maxx+minx) / 2
	imageCenterY = (maxy+miny) / 2

	# Get the image bounds
	print(f"  Image Center: ({imageCenterX}, {imageCenterY})")

	# Find the min and max of our image
	tileWidth  = abs(minx) + abs(maxx)
	tileHeight = abs(miny) + abs(maxy)

	print(f"  X RANGE: ({minx}, {maxx})")
	print(f"  Y RANGE: ({miny}, {maxy})")

	tileWidth  = int(tileWidth )
	tileHeight = int(tileHeight)

	imageAreaWidth  = int(tileWidth  * tileSize)
	imageAreaHeight = int(tileHeight * tileSize)

	imageWidth  = imageAreaWidth
	imageHeight = imageAreaHeight

	# Grab the padding
	padding ="10%"
	if "%" in padding:
		padding = padding[0:-1]
		mult = 1+(float(padding) / 100)
		imageWidth *= mult
		imageHeight *= mult

	entries = data["tiles"] + data["entities"]
	del data

	# Alter the image width and height to fit our aspect ratio
	if "aspect-ratio" in config:
		print("  Updating aspect ratio")
		try:
			# Break our the ratio in to two strings
			ratio = config["aspect-ratio"]
			if ":" in config["aspect-ratio"]:
				expectedW, expectedY = ratio.split(":")
			elif "x" in config["aspect-ratio"]:
				expectedW, expectedY = ratio.split("x")

			# Make the strings into numbers
			expectedW, expectedY = float(expectedW), float(expectedY)
			print(f"    New ratio: ({expectedW}:{expectedY})")
		except:
			print(f"Error processing:'aspect-ratio: \"{ratio}\"'\tCorrect Example: 'aspect-ratio: \"16:9\"'")
			exit()


		# imageWidth, imageHeight = int(imageWidth), int(imageHeight)
		print(f"    Current image size: ({imageWidth}:{imageHeight})")
		w, h = getAspect(imageWidth, imageHeight)
		if w != expectedW and h != expectedY:
			# Create two options
			newWidth = imageHeight * (expectedW/expectedY)
			newHeight = (expectedY*imageWidth)/expectedW

			if newWidth  > imageWidth : imageWidth  = newWidth
			if newHeight > imageHeight: imageHeight = newHeight
		print(f"    New image size: ({imageWidth}:{imageHeight})")

	# Create our image
	backgroundColor = (0, 0, 0, 0)
	if "background-color" in localSurfaceConfig:
		backgroundColor = localSurfaceConfig["background-color"]
		print("BACKGROUND COLOR", backgroundColor)
	imageWidth, imageHeight = int(imageWidth), int(imageHeight)
	image = Image.new('RGBA', (imageWidth, imageHeight), backgroundColor) # Create a new image with a white background
	draw = ImageDraw.Draw(image) # Create a drawing context



	# Draw entities to our image
	drawCount = 0
	print(f"  Drawing image...", end="", flush=True)
	for entry in entries:
		name = entry["name"]

		# Set/load default values
		color = None
		style = "solid"
		size = (1, 1)
		x, y = entry["x"], entry["y"]

		# Skip this entry if its not in range of the drawn image
		# TODO var/2 is not correct and is over reaching, find the correct formula
		if x/2 < minx: continue
		if x/2 > maxx: continue
		if y/2 < miny: continue
		if y/2 > maxy: continue

		for localSurfaceConfigEntry in localSurfaceConfig["entries"]:
			# Make sure that this localSurfaceConfig matches this planet
			if len(localSurfaceConfigEntry["planets"]) > 0:
				if surfaceName not in localSurfaceConfigEntry["planets"]:
					continue
			
			if match(entry, localSurfaceConfigEntry) == False: continue
			if "size"  in localSurfaceConfigEntry: size  = localSurfaceConfigEntry["size"]
			if "color" in localSurfaceConfigEntry: color = localSurfaceConfigEntry["color"]
			if "style" in localSurfaceConfigEntry: style = localSurfaceConfigEntry["style"]
		
		if color == None:
			name = entry["name"]
			if name not in unhandledNames:
				unhandledNames[name] = 0
			unhandledNames[name] += 1
			continue # No color no draw
		# print(f"DRAW {name} Location: ({size[0]}, {size[1]}) Color: {color} Size: {size} Style: {style}")
		drawRect(entry["x"], entry["y"], size[0], size[1], color=color, style=style)
		drawCount += 1
	print(f" done. Draw Count: {drawCount}")



	# Sort our names
	unhandledNames = dict(sorted(unhandledNames.items(), key=lambda item: item[1]))

	for name in unhandledNames:
		print(f"  Unhandled entry: {name} ({unhandledNames[name]})")


	# Save the image or show it
	x = (imageWidth /2) - (imageAreaWidth /2)
	y = (imageHeight/2) - (imageAreaHeight/2)
	width  = imageAreaWidth 
	height = imageAreaHeight

	# Draw required draw area
	# draw.rectangle([(x, y), (x+width, y+height)], outline="red", width=2)

	string = config["filename"]
	string = format_string(string, datetime=timeTxt, surfaceName=surfaceName)
	imagePath = f"images/{string}.png"
	mkdirs( os.path.dirname(imagePath) ) # Make the folders
	image.save(imagePath)  # To save the image as a file
	outputFiles.append(imagePath)


def createBackgrounds(config):
	"""
	Creates backgrounds for each of the planets exported with the custom mod
	"""
	for filename in os.listdir("factorio/script-output"):
		startTime = time.time()

		filename = filename[0:-5]
		if debug and filename != "vulcanus": continue # nauvis vulcanus fulgora gleba
		print(f"Drawing {filename}...")
		drawSurface(filename, config)

		endTime = time.time()
		deltaTime = endTime - startTime
		timeString = unixDurationToText(deltaTime)
		print(f"Planet done in {timeString}\n")


def loadConfigV1(shaderFile = None, debug = False):
	def groupToSelector(groupName):
		if groupName not in config["group"]:
			print(f"ERROR: Group '{groupName}' was not found in '{shaderFile}'")
			exit()
		group = config["group"][groupName]
		names = group["names"]
		func = "EXACT"
		if "func" in group:
			func = group["func"]
		return names, func

	def createConfigEntry(entry, planet=None):
		nonlocal newConfig
		
		# Create defaults
		configEntry = {
			"names": [],
			"func": "EXACT",
			"flags": [],
			"planets": []
		}

		# Figure out the selector
		if "group" in entry: configEntry["names"], configEntry["func"] = groupToSelector(entry["group"])
		if "names" in entry: configEntry["names"] += entry["names"]
		if "name"  in entry: configEntry["names"] += [entry["name"]]
		if planet != None: configEntry["planets"] += [planet]

		# Add the config for this selector
		if "func"  in entry: configEntry["func" ] = entry["func" ]
		if "style" in entry: configEntry["style"] = entry["style"]
		if "size"  in entry: configEntry["size" ] = entry["size" ]
		if "color" in entry: configEntry["color"] = entry["color"]
		if "flags" in entry: configEntry["flags"] = entry["flags"]

		newConfig["entries"].append(configEntry)

	# Load our presets
	with open('presets.yaml', 'r') as f:
		presets = yaml.safe_load(f)

	# Load our shader file
	with open(f'shaders/{shaderFile}', 'r') as f:
		config = yaml.safe_load(f)
		shaderConfig = config

	# Create a config file that the program can better use & work with
	newConfig = {
		"entries": []
	}

	key = "background-color"
	if key in shaderConfig: newConfig[key] = shaderConfig[key]

	# Add the presets first so that they will be replaced
	for entry in presets:
		createConfigEntry(entry)

	# Add the shaders info - Defaults
	if "defaults" in config:
		for entry in config["defaults"]:
			createConfigEntry(entry)

	# Add shader info
	if "planets" in config:
		for planet in config["planets"]:
			for entry in config["planets"][planet]:
				createConfigEntry(entry, planet=planet)

	# Add general entries
	if "general" in config:
		for entry in config["general"]:
			createConfigEntry(entry)

	if debug:
		print(f"\nConfigs:")
		for configEntry in newConfig:
			print(" ", configEntry)
	return newConfig


def unixDurationToText(unix_seconds):
	"""
	Converts a unix time int to a human readable string
	"""
	seconds = unix_seconds
	minutes = unix_seconds/60
	hours = minutes/60
	days = hours/24
	years = days/365

	text = ""

	if hours >= 1: text += f"{hours:<.0f} hours & "
	if minutes >= 1 and days < 1:
		num = (hours % 1) * 60
		text += f"{num:<.0f} minutes & "
	if seconds >= 1 and hours < 1:
		num = (minutes % 1) * 60
		text += f"{num:<.0f} seconds & "
	return text[0:-3]


def format_string(s, **kwargs):
	return s.format(**kwargs)


def mkdirs(directory_path):
	try:
		os.makedirs(directory_path)
	except FileExistsError:
		pass


def startServer():
	"""
	Runs the Factorio server
	"""
	# Empty our server output

	# Remove lock file
	lockFilePath = "factorio/.lock"
	if os.path.exists(lockFilePath):
		print("Removing server lockfile")
		os.remove(lockFilePath)

	# Run the command and get updates from its standard output
	print("Starting Factorio server")
	command = ["factorio/bin/x64/factorio", "--start-server", "factorio-save/"+config["factorio-save-name"], "--server-settings", "server-settings.json"]
	print(" ".join(command))
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	totalOutput = ""

	flagModLines = False
	modIndicator = "b8VmXhHtuENCBh6q" # The line the indicate that the mod is in control, further lines will be output from the mod

	while True:
		output_data = p.stdout.read(1) # Receive 1024 bytes of data from the pipe at a time
		
		if not output_data: break
		
		# Decode the output from bytes to string
		output_str = output_data.decode('utf-8')
		totalOutput += output_str

		if modIndicator in totalOutput:
			totalOutput = totalOutput[totalOutput.index(modIndicator)+len(modIndicator)+2:]
			flagModLines = True
		
		if flagModLines and "\n" in totalOutput:
			line = totalOutput[0:totalOutput.index("\n")]
			totalOutput = totalOutput[totalOutput.index("\n")+2:]
			if "Error ServerMultiplayerManager.cpp" in line: break
			if modIndicator not in line and len(line.strip()) > 0:
				print(f"Line: {line}")
				jobs.append(line)

	# Wait for the command to finish and get its final standard error
	final_output, final_error = p.communicate()

	if final_error:
		print(f"Error: {final_error.decode('utf-8')}")


def workerThread():
	while running and len(jobs) <= 0:
		time.sleep(1/20)
		if len(jobs) <= 0: continue

		filename = jobs.pop(0)
		print(f"Drawing {filename}...")
		drawSurface(filename, shaderConfig)


def updateServer():
	"""
	Pulls the latest server from wube
	"""
	url = "https://factorio.com/get-download/stable/headless/linux64"  # Server download URL
	output_path = "factorio.tar.xz"  # Server download path
	
	if os.path.exists(output_path):
		lastServerUpdate = os.stat(output_path).st_mtime
		if time.time() - lastServerUpdate < 86400:
			return


	# Download the new server
	print("Downloading new server...")
	response = requests.get(url) # Send a GET request to the URL
	if response.status_code != 200: # Check if the request was successful
		print("Response from server {url} was unsuccessfull, the server maybe old")
		return
		
	# Open the output file and write the content of the response to it
	with open(output_path, 'wb') as f:
		f.write(response.content)
	print(f"File downloaded successfully and saved to {output_path}")


	# Delete the old server 
	factorioServerPath = "factorio"
	if os.path.exists(factorioServerPath) and os.path.isdir(factorioServerPath):
		print("Removing old server path")
		shutil.rmtree(factorioServerPath)

	# Extract the new server
	print("Extracting server file")
	with tarfile.open("factorio.tar.xz", "r:xz") as tar:
		tar.extractall(path=".")

	os.mkdir("factorio/mods")
	updateMod()

	# rm -rf "factorio"
	# newestServer=$(ls factorio-headless_linux_* | sort -V | tail -n 1)
	# tar -xf "$newestServer"
	# mkdir factorio/mods


def updateMod():
	# Delete old mod
	modPath = "factorio/mods/CustomMod_0.0.1"
	if os.path.exists(modPath) and os.path.isdir(modPath):
		print("Removing old mod path")
		shutil.rmtree(modPath)

	# Copy new mod
	shutil.copytree("custom-mod", modPath)


startTime = time.time()

debug = False
running = True
jobs = [] # Stored jobs for the worker thread
outputFiles = [] # Paths to the output images
# config = loadConfigV1("factorio-map.yaml")

# Load our general config file
if os.path.exists('config.yaml') == False:
	shutil.copy('config-example.yaml', 'config.yaml')

with open('config.yaml', 'r') as f:
	config = yaml.safe_load(f)

if "auto-generated" in config and config["auto-generated"] == True:
	print("Please verify in config.yaml that the settings are correct. Then change auto-generated to False and run again.")
	exit()

shaderConfig = loadConfigV1(config["shader"])

# Calculate time text
timeObj = datetime.now()
timeTxt = timeObj.strftime("%Y-%m-%d %H:%M")

useServer = True # Run the server to generate the map

# Copy our save
if "factorio-save-path" in config:
	# Make sure our copy dst exists
	tmpSaveFolder = "factorio-save"
	if not os.path.exists(tmpSaveFolder):
		os.makedirs(tmpSaveFolder)

	# Move our files
	factorioSavePath = os.path.expanduser( config["factorio-save-path"] + "/" + config["factorio-save-name"] + ".zip" )
	if os.path.exists(factorioSavePath) == False:
		print(f"Looking for save at {factorioSavePath}\nThe save '{config['factorio-save-name']}' does not exist in the directory '{config['factorio-save-path']}'. Exiting")
		exit()
	print(f"Copying our Factorio save file '{factorioSavePath}'")
	shutil.copy(factorioSavePath, tmpSaveFolder+"/")



# Create our images
if useServer:
	updateMod()
	updateServer()

	# Creating worker thread
	workerThread = threading.Thread(target=workerThread, daemon=True)
	workerThread.start()

	# Start the server to gather data
	startServer()

	running = False # Signal the worker thread to stop
	workerThread.join()
else:
	createBackgrounds(shaderConfig)



# Copy our output images to the background folder
if "backgrounds-folder" in config:
	backgroundFolder = os.path.expanduser( config["backgrounds-folder"] )
	print(f"Copying our images to '{backgroundFolder}'")
	for entry in outputFiles:
		shutil.copy(entry, backgroundFolder)



endTime = time.time()
deltaTime = endTime - startTime
timeString = unixDurationToText(deltaTime)
print(f"Job done in {timeString}")