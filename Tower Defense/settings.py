import os, pygame, math, random, json

class TileMapManager():
    def __init__(self):
        pass

    def _get_tile_images(self, base_path):
        images = {}

        for image in os.listdir(base_path):
            image_name = os.path.basename(image)
            images[image_name.rsplit('.')[0]] = pygame.image.load(os.path.join(base_path, image_name))

        return images
    
    def _create_tilemap(self, file_path):
        map_data = {
                'tilemap': {
                    'width' : 1024,
                    'height': 768,
                    'tilesize': 64
                },
                'tile': None,
                'object': None,
            }
        with open(file_path, 'w') as file:
            json.dump(map_data, file, indent=4)
    
    def _save_tilemap(self, file_path, tilemap):
        if os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump(tilemap, file, indent=4)

    def _load_tilemap(self, file_path):
        try:
            with open(file_path, 'r') as file:
                tilemap_data = json.load(file)
            return tilemap_data
        except:
            print(f'{file_path} does not exists')


