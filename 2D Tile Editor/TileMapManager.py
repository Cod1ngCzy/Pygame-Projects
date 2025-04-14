from settings import *

class TileMapManager():
    def __init__(self):
        self._root_path = 'assets/maps' 
        self._accessed_tilemap = ''
        self._cache_tilemaps = {} # {map_name: map_full_path}
        self._map_names = self._cache_tilemaps.keys()
        
        # Map Properties
        self.tilemap_dimension = {
            '800x600': {'width': 800, 'height': 600, 'tilesize': [16, 32, 64]},
            '1024x768': {'width': 1024, 'height': 768, 'tilesize': [16, 32, 64]},
            '1280x720': {'width': 1280, 'height': 720, 'tilesize': [16, 32]},
            '1280x960': {'width': 1280, 'height': 960, 'tilesize': [16, 32, 64]},
            '1366x768': {'width': 1366, 'height': 768, 'tilesize': [32]},
            '1440x900': {'width': 1440, 'height': 900, 'tilesize': [16, 32, 64]},
            '1600x900': {'width': 1600, 'height': 900, 'tilesize': [16, 32, 64]},
            '1920x1080': {'width': 1920, 'height': 1080, 'tilesize': [16, 32, 64]},
            '2560x1440': {'width': 2560, 'height': 1440, 'tilesize': [16, 32, 64]}
        }

        # Intialize Tile Map Manager
        self._init_tilemanager()
    
    def _handle_mapname_duplicate(self, map_name):
        base_name = map_name
        name_counter = 1

        while map_name in self._cache_tilemaps:
            if name_counter >= 3:
                break
            map_name = f'{base_name}_{name_counter}'
            
            name_counter += 1

        return map_name
    
    def _init_tilemanager(self):
        tilemaps_path = [map_name for map_name in os.listdir(self._root_path) if map_name.endswith('.csv')]

        if tilemaps_path:
            # First Item Only
            if len(tilemaps_path) > 1:
                map = tilemaps_path[0]

            map = tilemaps_path

            # Load Cache Data
            self._cache_tilemaps = {
                mapname: join(self._root_path, mapname)
                for mapname in map
            }
        else:
            self.create_tilemap()
            
    def load_tilemap(self, file_path):
        tilemap = {
            'metadata': {
                'world_width': None,
                'world_height':None,
                'world_tilesize': None,
                'world_name': None
            },
            'map': []
        }

        # If base check == true, open file
        with open(file_path) as file:
            csv_reader = csv.reader(file)
            parsing_metadata = False

            for row in csv_reader:
                if not row or row[0].startswith("#"):  # Skip empty lines & comments
                    if row and row[0] == "#metadata":
                        parsing_metadata = True  # Start reading metadata
                    elif row and row[0] == "#tilemap":
                        parsing_metadata = False  # Stop reading metadata
                    continue

                if parsing_metadata:
                    key, value = row
                    tilemap['metadata'][key] = int(value) if value.isdigit() else value # Store metadata
                else:
                    tilemap['map'].append([int(x) for x in row])  # Store tilemap

        return tilemap

    def save_tilemap(self,modified_tile_map):
        tile_map = modified_tile_map

        with open(self._cache_tilemaps.get(self._accessed_tilemap), 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write metadata
            writer.writerow(["#metadata"])
            for key, value in tile_map['metadata'].items():
                writer.writerow([key, value])
            writer.writerow([])  # Empty row to separate metadata from tilemap
            
            # Write tilemap data
            writer.writerow(["#tilemap"])
            for row in tile_map['map']:
                writer.writerow(row)
        
        return True
    
    def create_tilemap(self, width:int=None, height:int=None, tilesize:int=None, map_name:str=None):
        default_width = width if width else 1024
        default_height = height if height else 768
        default_tilesize = tilesize if tilesize else 32
        default_name = map_name if map_name else 'untitled_map'
        default_tile_map = [[1 for _ in range(default_width // default_tilesize)] for _ in range(default_height // default_tilesize)]

        world_name = self._handle_mapname_duplicate(default_name)
        full_path_map = join(self._root_path, f'{world_name}.csv')

        with open(full_path_map, 'w', newline='') as file:
            meta_data_header, tilemap_header = '#metadata', '#tilemap'
            csv_writer = csv.writer(file)

            # CREATE METADATA HEADER
            csv_writer.writerow([meta_data_header])
            meta_data = {
                    'world_width': default_width,
                    'world_height':default_height,
                    'world_tilesize': default_tilesize,
                    'world_name': world_name
                }
            
            for key, value in meta_data.items():
                csv_writer.writerow([key, value])
            
            # Create empty space for seperation
            csv_writer.writerow([])

            # CREATE TILEMAP HEADER
            csv_writer.writerow([tilemap_header])
            for row in default_tile_map:
                csv_writer.writerow(row)
        
        self._cache_tilemaps[world_name] = full_path_map # Updates and Stores, FILE NAME AND PATH ONLY (not loaded) lazy loading

    def access_tilemap(self, map_name):
        if map_name in self._cache_tilemaps:
           self._accessed_tilemap = map_name
           return self.load_tilemap(self._cache_tilemaps.get(map_name))
        else:
            raise FileNotFoundError
             