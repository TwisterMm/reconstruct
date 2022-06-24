import cv2
import numpy as np
import pyrealsense2 as rs


if __name__ == '__main__':
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    #stream settings
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # #stream settings
    # config.enable_stream(rs.stream.depth,rs.format.z16, 30)
    # config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

    profile = pipeline.start(config)

    # colorizer = rs.colorizer()
    n = 0
    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    print("Depth Scale is: " , depth_scale)

    #FROM ALIGN
    align_to = rs.stream.color
    align = rs.align(align_to)


    try:
        for _ in range(10): #autoexposure
            pipeline.wait_for_frames() 
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()           
            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame() # 

            color_frame = aligned_frames.get_color_frame()
            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                continue  
            
        
            # # Convert images to numpy arrays
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

                        
            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            

            # If depth and color resolutions are different, resize color image to match depth image for display
            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))


        

            
            # Show images
            cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
            #resize for suitable output        
            cv2.imshow('RealSense', images)
            
            key = cv2.waitKey(1)

            
                
            if key in (27, ord("q")) or cv2.getWindowProperty('RealSense', cv2.WND_PROP_VISIBLE) < 0: 
                cv2.destroyAllWindows()
                break
            if key == ord("s"):
                
                # colorized = colorizer.process(aligned_frames)    

                cv2.imwrite('output/img%d.png' %n, color_image)
                # Create save_to_ply object
                ply = rs.save_to_ply("output/out%d.ply" %n)
            
                # # Set options to the desired values
                # # In this example we'll generate a textual PLY with normals (mesh is already created by default)
                ply.set_option(rs.save_to_ply.option_ply_binary, False)
                ply.set_option(rs.save_to_ply.option_ply_normals, True)
                ply.process(aligned_frames)
                print("saving pointcloud out%d and image img%d" %(n,n))          
                n = n +1


    finally:

        # Stop streaming
        pipeline.stop()