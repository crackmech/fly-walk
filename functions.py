import matplotlib.pyplot as plt
#from skimage.io import imread
from keras import backend as K
import numpy as np

def resize_crop_image(image,scale,cutoff_percent):
	image = cv2.resize(image,None,fx=scale, fy=scale, interpolation = cv2.INTER_AREA)
	cut_off_vals = [image.shape[0]*cutoff_percent/100, image.shape[1]*cutoff_percent/100]


	end_vals = [image.shape[0]-int(cut_off_vals[0]),image.shape[1]-int(cut_off_vals[1])]

	image =image[int(cut_off_vals[0]):int(end_vals[0]),int(cut_off_vals[1]):int(end_vals[1])  ]
	#plt.imshow(image)
	#plt.show()
	return(image)

def rotate_thrice(square):
        return [square, np.rot90(square, 1), np.rot90(square, 2), np.rot90(square, 3)]

def transforms(square):
        return rotate_thrice(square) + rotate_thrice(np.fliplr(square))

def your_loss(y_true, y_pred):
	#weights = np.ones(4)
	#weights = np.array([ 1 ,  1,  1,  1])
	weights = np.array([ 0.32 ,  10,  1.3,  0.06])
        #weights = np.array([0.99524712791495196, 0.98911715534979427, 0.015705375514403319])
        #weights = np.array([ 0.91640706, 0.5022308, 0.1])
	#weights = np.array([ 0.05 ,  1.3,  0.55,  4.2])
	#weights = np.array([0.00713773, 0.20517703, 0.15813273, 0.62955252])
	#weights = np.array([1,,0.1,0.001])
	# scale preds so that the class probas of each sample sum to 1
	y_pred /= K.sum(y_pred, axis=-1, keepdims=True)
	# clip
	y_pred = K.clip(y_pred, K.epsilon(), 1)
	# calc
	loss = y_true*K.log(y_pred)*weights
	loss =-K.sum(loss,-1)
	return loss

def raw_to_labels(image, count):
    #assert(image.max()==255)
    #if count <= 5:
    body = (image[:,:,0]==79) & ( image[:,:,1] ==255) & (image[:,:,2] ==130 )
    legs = (image[:,:,0] == 255 ) & ( image[:,:,1] == 0) & (image[:,:,2] == 0)
    #else:
    #    legs = (image[:,:,0]>=150) & ( image[:,:,1] <= 120) & (image[:,:,2] <= 120 )
    #    body = (image[:,:,0] <= 120 ) & ( image[:,:,1] <= 120) & (image[:,:,2] >= 130 )
    antennae = (image[:,:,0] == 255 ) & ( image[:,:,1] == 225) & (image[:,:,2] == 10 )
    background = ~legs & ~antennae & ~body
    softmax_labeled_image = np.zeros((image.shape[0], image.shape[1], 4))
    softmax_labeled_image[body] = [1,0,0,0]
    softmax_labeled_image[antennae] = [0,1,0,0]
    softmax_labeled_image[legs] = [0,0,1,0]
    softmax_labeled_image[background] = [0,0,0,1]
    return softmax_labeled_image
