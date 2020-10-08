import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

#each knight has a colour
knightColours = [(255,0,0), (0,0,250), (0,255,0), (0,255, 250)]

#threshhold for identifying MUST be 0.95, lower will think all pieces are the same
threshold = 0.95 

def findKnight(template, val, img, img_gray, knightCoordinatesVal):
    w, h = template.shape[::-1] 
    res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
    loc = np.where( res >= threshold)
    prevPoint = None
    for pt in zip(*loc[::-1]): #iterate through points where a knight is found. Zip creates the points from the arrays of loc. [::-1] to have w,h  format
        if(prevPoint == None or prevPoint[0] + 50 < pt[0] or prevPoint[1] + 50 < pt[1]): #allows us to avoid counting duplicate points which are for the same knight (due to the coordinates being very close, but being detected as different knights)
            cv.rectangle(img, pt, (pt[0] + w, pt[1] + h), knightColours[val], 2)
            prevPoint = pt
            knightCoordinatesVal.append(((pt[1], pt[0]), val)) #append tuple containing coordinate and value; flip w,h to have row,column format
        
def convertToMatrixCoordinates(knightCoordinatesVal):
    minCoordinate = min([x for x,_ in knightCoordinatesVal]) #get minimum coordinate

    #Substract min coordinate from each knight coordinate to have 0,0 as a reference
    #Also, do int division to group coordinates wich represent the same rows/columns (i.e. within 70 pixels, considered same row/coordinate)
    knightCoordinatesVal = list(map(lambda x: (((x[0][0] - minCoordinate[0]) // 70, (x[0][1] - minCoordinate[1]) // 70), x[1]), knightCoordinatesVal))
   
    #print(len(set([x for x,_ in knightCoordinatesVal]))) remove comment to debug, ensures uniqueness of coordinates after int division, should return 480
    
    return knightCoordinatesVal

def base4ToString(base4Num):
    index = 0 #used to keep track of base 4 index
    result = 0 #used to hold inetger representation of base 4 string
    
    #go to each base 4 character
    for ch in base4Num[::-1]: #start at back since index is at back
        result += int(ch) * pow(4, index)
        index += 1
    result = bin(result)
    result = '0' + result[2:] #to remove that '0b' and add the leading 0 (to allow for groupings of 8 - ASCII)
    
    #return our binary as ASCII
    return ''.join(chr(int(result[i*8:i*8+8],2)) for i in range(len(result)//8))
        
   
if __name__ == '__main__':
    #Open original image
    img = cv.imread('knights.jpg')
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #Open template images - templates MUST be cropped using paint and without being resized
    front = cv.imread('knightFront.png',0) 
    right = cv.imread('knightRight.png',0) 
    left = cv.imread('knightLeft.png',0) 
    back = cv.imread('knightBack.png',0) 
    
    #List to store all coordinates of diffreent types of knights with their value
    #NOTE: points found will have format (row #, column #) (A.K.A (y, x)). Therefore, flip coordinates when putting in our list
    knightCoordinatesVal = []
    
    #Find each knight
    findKnight(front, 0, img, img_gray, knightCoordinatesVal)
    findKnight(right, 1, img, img_gray, knightCoordinatesVal)
    findKnight(back, 2, img, img_gray, knightCoordinatesVal)
    findKnight(left, 3, img, img_gray, knightCoordinatesVal)
    
    #convert coordinates into actual row, column coordinates (matrix coordinates)
    knightCoordinatesVal = convertToMatrixCoordinates(knightCoordinatesVal)
    
    #sort the list using the coordinates in each tuple, to allow knights to be sorted next to their value
    knightCoordinatesVal.sort(key = lambda tup: tup[0])
    
    #iterate through sorted elements to create the base4 string
    base4Num = ""
    for element in knightCoordinatesVal:
        base4Num += str(element[1])
    
    #print base4 string
    print('base4: ' + base4Num)
    
    #convert base4 to ascii string
    print('ASCII: ' + base4ToString(base4Num))

    cv.imwrite('res.png',img) #will create image showing where each knight is; not relavent to problem but more for fun