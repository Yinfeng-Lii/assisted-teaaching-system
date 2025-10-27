import cv2
import numpy as np
import pcl

# Load images
rgb_image = cv2.imread('rgb_image.png')
depth_image = cv2.imread('depth_image.png', cv2.IMREAD_ANYDEPTH)

# Camera intrinsic parameters (example values)
focal_length = 525.0
center_x = 319.5
center_y = 239.5

point_cloud = []

# Iterate over each pixel to create the point cloud
for v in range(depth_image.shape[0]):
    for u in range(depth_image.shape[1]):
        # Get depth value and convert to meters
        Z = depth_image[v, u] / 1000.0
        if Z == 0: continue # Skip pixels with no depth info

        # Unproject pixel to 3D space
        X = (u - center_x) * Z / focal_length
        Y = (v - center_y) * Z / focal_length
        point_cloud.append([X, Y, Z])

# Create a PCL PointCloud object
p = pcl.PointCloud(np.array(point_cloud, dtype=np.float32))

# --- Plane Segmentation (RANSAC) ---
seg = p.make_segmenter()
seg.set_model_type(pcl.SACMODEL_PLANE)
seg.set_method_type(pcl.SAC_RANSAC)
seg.set_distance_threshold(0.01) # Set distance threshold for plane
indices, model = seg.segment()

# Extract non-plane points (the objects)
cloud_filtered = p.extract(indices, negative=True)

# --- (Optional) Cluster Extraction ---
# To isolate main objects, you might want to cluster the remaining points
# tree = cloud_filtered.make_kdtree()
# ec = cloud_filtered.make_EuclideanClusterExtraction()
# ec.set_ClusterTolerance(0.02)
# ec.set_MinClusterSize(100)
# ec.set_MaxClusterSize(25000)
# ec.set_SearchMethod(tree)
# cluster_indices = ec.extract()
# Assuming you want the largest cluster if multiple exist
# cloud_cluster = cloud_filtered.extract(cluster_indices[0], negative=False)

# --- Mesh Reconstruction (Greedy Projection Triangulation) ---
# Note: GreedyProjection requires normals. Let's compute them first.
ne = cloud_filtered.make_NormalEstimation()
tree = cloud_filtered.make_kdtree()
ne.set_SearchMethod(tree)
ne.set_KSearch(20) # Search for 20 nearest neighbors
cloud_with_normals = ne.compute()

# Create a new search tree for the cloud with normals
tree2 = cloud_with_normals.make_kdtree()

triangles = cloud_with_normals.make_GreedyProjectionTriangulation()
triangles.set_search_radius(0.025)
triangles.set_mu(2.5)
triangles.set_maximum_nearest_neighbors(100)
triangles.set_normal_consistency(False) # Often works better when false
triangles.set_SearchMethod(tree2)

# Reconstruct the mesh
polygon_mesh = triangles.reconstruct()

# Save the mesh to a .ply file
pcl.save(polygon_mesh, 'model.ply')

print("Point cloud processed and model.ply saved.")