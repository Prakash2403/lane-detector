# Lane-detector
Lane detection using Computer Vision. Work in progress.

If you are changing your test set, make sure to change the co-ordinates in **get_vertices()** method, so that quadilateral 
formed by four co-ordinates contains the region where lanes are most likely present and noise is minimum.

## Algorithm for lane detection:
    
    1. Read the image.
    2. Convert it to grayscale.
    3. Apply Gaussian Blur to reduce the noice.
    4. Apply Canny Edge detection to detect edges.
    5. By manually analyzing images, decide a region where lanes are most likely to be present. Region must 
       be a quadilateral and has to be specified by 4 vertices, where each vertex is a (x, y) co-ordinate pair. 
       From now on, this region will be called as region of interest
    6. After applying Canny Edge detection and deciding a region of interest, except region of interest, 
       set the color of all pixels to black.
    7. Now image only contains a quadilateral, where lanes are most likely to be present. 
    8. Apply Probabilistic Hough transform to detect the straight line segments present in the region of interest.
    9. Probabilisitc Hough transform will return end co-ordinates of the detected line segments.
    10. Using end points of detected line segments, calculate slope and y-intercepts of the line segments and 
        store them in a list. If the slope or y-intercept is infinity, then don't add it to the list.
    11. Assuming that only two lanes are present in region of interest and slope of the both lanes are differ by
        a significant margin, divide the slope list in two parts, one containing all the slopes greater than total 
        slope mean and other containing all the slopes less than total slope mean. 
    12. Using the list obtained above, divide the intercept list in two parts.
    13. Take mean of both slope lists to get two slopes, each one will correspond to slope of a given lane. 
        Due to assumption taken in step 11, we will get two slopes which will differ by a significant margin.
    14. Take mean of both intercept list to get two different intercepts for lanes.
    15. Using y= mx + b equation, generate two pairs of (x, y) co-ordinates and pass them to opencv line method,
        to draw the lines.
        
## Future Work

This algorithm doesn't work efficiently when sharp edges are present. Outliers rejection is also required.
