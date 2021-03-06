from __future__ import division
from collision import *
from visual import *
import numpy as np

class sense:

    def __init__(self, player_id, current_position, scope):
        self.player_id = player_id
        self.scope = scope
        self.current_position = current_position
        self.mesh_size = 0
        self.mesh_center = vector(current_position)
        self.scope_boundary = aabb(player_id, scope, current_position)
        self.dt = 1
        # Used only for visualization of net, not for detection.
        self.net_visual_display = list()
        self.net_visible_f = False
        self.blank_image = np.ndarray(())
        self.net = self.formNet(scope)
        self.image = None

    def formNet(self, scope):
        net = list()
        V_MIN = 1
        mesh_unit_size = V_MIN * self.dt
        # mesh_dim refers to the dimensions of a single quadrant or octant
        self.mesh_dim_x = int(floor(self.scope[0]/mesh_unit_size))
        self.mesh_dim_y = int(floor(self.scope[1]/mesh_unit_size))
        self.mesh_dim_z = int(floor(self.scope[2]/mesh_unit_size))
        # setting self.mesh_dim_y to 1 will effectively ignore vertical attacks but will reduce computation
        self.mesh_dim_y = 1
        quadrant_octant_factor = 4 # Set to 4 for Quadrant, 8 for octant
        # mesh_size will be the number of cell elements in the image array
        self.mesh_size = quadrant_octant_factor*self.mesh_dim_x * self.mesh_dim_y * self.mesh_dim_z
        self.blank_image = np.zeros((2*self.mesh_dim_x,2*self.mesh_dim_z), dtype=int)
        previous_id = self.scope_boundary.id

        # Populate mesh with bounding cells
        for z in range(-self.mesh_dim_z + 1, self.mesh_dim_z + 1, mesh_unit_size):
            for x in range(-self.mesh_dim_x + 1, self.mesh_dim_x + 1, mesh_unit_size):
                cell_x = self.mesh_center.x - (x - 1/2)*mesh_unit_size
                cell_y = self.mesh_center.y - 6
                cell_z = self.mesh_center.z - (z - 1/2)*mesh_unit_size
                mesh_position = vector(cell_x, cell_y , cell_z)
                u = .5*mesh_unit_size
                cell = aabb(previous_id + 1, (u, u, u), mesh_position)
                cell.player_id = self.player_id
                net.append(cell)
                if self.net_visible_f:
                    cell.display_box = box(pos = mesh_position, length=2*u-.1, width=2*u-.1, height=2*u-.1, color = color.blue)
                    self.net_visual_display.append( cell.display_box)
                previous_id += 1
        self.unit_size = 2*u-.1
        return net

    def move_net(self, new_position_center):
        displacement = new_position_center - self.mesh_center
        for cell in self.net:
            cell.move(displacement)
            self.mesh_center = vector(self.current_position)
        if self.net_visible_f:
            for cell_display in self.net_visual_display:
                cell_display.pos += displacement

    def look(self, current_position):
            threat_count = self.scope_boundary.check_for_players_in_scope(current_position)
            if threat_count == 0:
                self.move_net(current_position)
                return self.blank_image.copy()
            # if threats detected we will need to check all bounding boxes
            elif threat_count > 0:
                self.move_net(current_position)
                image = self.record_image()
                return image

    def record_image(self):
        array_dim_x = 2*self.mesh_dim_x
        array_dim_z = 2*self.mesh_dim_z
        image_array = np.zeros((array_dim_x,array_dim_z), dtype=int)
        list_index = 0
        for x in range(0,array_dim_x):
            for z in range(0, array_dim_z):
                image_array[array_dim_x - 1 - x][array_dim_z - 1 - z] = \
                    self.net[list_index].check_for_players_in_cell()
                list_index += 1
        return image_array

    def blank(self):
        return self.blank_image.copy()



    def remove_net_visual(self):
        for cell in self.net:
            cell.display_box.length  = 0
            cell.display_box.width   = 0
            cell.display_box.height  = 0
            cell.display_box.visble = False
            del cell.display_box

    def restore_net_visual(self):
        self.formNet(self.scope)
