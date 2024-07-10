import carla
import cv2
import numpy as np
import random
import time

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
client.load_world('Town06')
client.reload_world()
world = client.get_world()
# Non-rendering mode on carla world
settings = world.get_settings()
if not settings.no_rendering_mode:
    settings.no_rendering_mode = True
    world.apply_settings(settings)

# Get the blueprint library and filter for the vehicle blueprints
vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')
truck_bp = world.get_blueprint_library().find('vehicle.carlamotors.carlacola')
truck_bp.set_attribute('role_name', 'hero')

# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()

# Traffic: Spawn 50 vehicles randomly
for i in range(50):
    vehicle_bp = random.choice(vehicle_blueprints.filter('vehicle'))
    npc = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))

# Set npc traffic in motion
for v in world.get_actors().filter('*vehicle*'):
    v.set_autopilot(True)

# Spawn truck
ego_vehicle = world.spawn_actor(truck_bp, random.choice(spawn_points))

# Create a transform to place the camera on top of the vehicle
camera_init_trans = carla.Transform(carla.Location(x=1,y=0,z=2.5))

# We create the camera through a blueprint that defines its properties
camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')

# We spawn the camera and attach it to our ego vehicle
camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=ego_vehicle)

# Callback sends images to a cv2 window that acts as the camera viewer
def camera_callback(image, data_dict):
    # Reshapes the array to be a proper rgba representation of raw data.
    data_dict['image'] = np.reshape(np.copy(image.raw_data),
                                    (image.height, image.width, 4))

# Sets the image dimensions and fills it with arrays of 0.
camera_data = {'image': np.zeros((camera_bp.get_attribute('image_size_x').as_int(),
                       camera_bp.get_attribute('image_size_y').as_int(), 4))}

camera.listen(lambda image: camera_callback(image, camera_data))
# Have CARLA drive the ego vehicle around
#ego_vehicle.set_autopilot(True)

cv2.namedWindow('RGB Cam', cv2.WINDOW_AUTOSIZE)
cv2.imshow('RGB Cam', camera_data['image'])
cv2.waitKey(1)

while True:
    cv2.imshow('RGB Cam', camera_data['image'])
    #print(camera_data['image'])
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
#time.sleep(5)