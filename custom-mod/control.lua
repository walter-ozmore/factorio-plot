function processPlanet(surface)
	local area = {{-1000, -1000}, {1000, 1000}}
	local entities = game.surfaces[surface].find_entities(area)
	
	local exportTiles = {}

	for x = area[1][1], area[2][1], 1 do
		for y = area[1][2], area[2][2], 1 do
			local tile = game.surfaces[surface].get_tile(x, y)
			-- Skip nil tiles
			if tile.valid then
				local exportTile = {
						name = tile.name,
						x = tile.position.x,
						y = tile.position.y
				}
				table.insert(exportTiles, exportTile)
			end
		end
	end


	local exportEntities = {}
	for _, entity in pairs(entities) do
		-- print(entity.name) -- This will print the name of each entity
		local exportEntity = {
			name = entity.name,
			x = entity.position.x,
			y = entity.position.y,
		}
		table.insert(exportEntities, exportEntity)
	end

	-- print(helpers.table_to_json(entities))
	local data = {
		hello = "world",
		entities = exportEntities,
		tiles = exportTiles
	}


	filePath = surface .. '.json'
	helpers.write_file(filePath,
		helpers.table_to_json(data),
		false, 0
	)
end

script.on_init(function()
	-- Your initialization code here
	print("b8VmXhHtuENCBh6q")

	-- Loop though every planet and run the process function on them
	for planetName, planet in pairs(game.planets) do
		processPlanet(planetName)
		print(planetName)
	end

	-- local planetName = "aquilo"
	-- processPlanet(planetName)
	-- print(planetName)

	-- Crash the game
	helpers.print("AHH A CRASH")
end)