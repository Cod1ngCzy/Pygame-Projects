from settings import *

class TileImageManager():
    def __init__(self):
        self._required_file_paths = {
            'base_path': os.path.join('assets', 'tiles'),
            'background_folder_path': os.path.join('assets','tiles','background'),
            'foreground_folder_path': os.path.join('assets','tiles','foreground')
        }
     
        self.images = {
            'background': {},
            'foreground': {}
        }  
        self.image_objects = {
            'background': {},
            'foreground': {}
        } 
        self.image_lookup = {
            'background': {},
            'foreground': {}
        }  # To be changed 

        # Initialize 
        self._validate_file_paths()
        self._handle_background_layer_images()
        self._handle_foreground_layer_images()

    def _validate_file_paths(self):
        # Validates Required Folder/File Paths
        if not os.path.exists(self._required_file_paths['base_path']):
            os.makedirs(self._required_file_paths['base_path'])
        elif not os.path.exists(self._required_file_paths['background_folder_path']):
            os.makedirs(self._required_file_paths['background_folder_path'])
        elif not os.path.exists(self._required_file_paths['foreground_folder_path']):
            os.makedirs(self._required_file_paths['foreground_folder_path'])
    
    def _handle_background_layer_images(self):
        background_folder_path = [folder_name for folder_name in os.listdir(self._required_file_paths['background_folder_path'])]

        for folder_name in background_folder_path:
            folder_path = os.path.join(self._required_file_paths['background_folder_path'], folder_name)
            self.images['background'][folder_name] = [image_name for image_name in os.listdir(folder_path)]
            self.image_objects['background'][folder_name] = list(filter(None, map(lambda file: self._set_image_object(os.path.join(folder_path,file)), os.listdir(folder_path))))

        # Clear File Name Path
        self.images['background'] = {}
        self._set_image_tilenum(self.image_objects['background'],'background')

    def _handle_foreground_layer_images(self):
        foreground_folder_path = [folder_name for folder_name in os.listdir(self._required_file_paths['foreground_folder_path'])]

        for folder_name in foreground_folder_path:
            folder_path = os.path.join(self._required_file_paths['foreground_folder_path'], folder_name)
            self.images['foreground'][folder_name] = [image_name for image_name in os.listdir(folder_path)]
            self.image_objects['foreground'][folder_name] = list(filter(None, map(lambda file: self._set_image_object(os.path.join(folder_path,file)), os.listdir(folder_path))))
        
        # Clear File Name Path
        self.images['foreground'] = {}
        self._set_image_tilenum(self.image_objects['foreground'], 'foreground')

    def _set_image_object(self, image_file_path, tile_size=None):
        """Uses Tile class as basis for creating an object."""
        try:
            return Tile(image_file_path, 0, 0, tile_size)
        except Exception as e:
            print(f"Error loading image '{image_file_path}': {e}")
            return None
    
    def _set_image_tilenum(self, image_objects,layer):
        """Assigns unique tile numbers to all tile objects"""
        tile_num = 0
        
        for category_tiles in image_objects.values():
            for tile in category_tiles:
                tile_num += 1
                tile.tile_number = tile_num
                self.image_lookup[layer][tile_num] = tile
    
    # ==== OUTSIDE FUNCTIONS ==== #
    def get_tile_by_number(self, number, layer):
        """Retrieve a tile by its assigned number"""
        return self.image_lookup[layer].get(number)

    def get_image_object(self):
        if self.image_objects is None:
            raise ReferenceError("Image Object is empty. Might be error on handling process.")
        return self.image_objects

    def get_image_lookup(self):
        if self.image_lookup is None:
            raise ReferenceError("Image Lookup is empty. Might be error on handling process.")
        return self.image_lookup