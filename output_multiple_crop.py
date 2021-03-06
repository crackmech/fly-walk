import os
from os.path import basename

os.environ['CUDA_VISIBLE_DEVICES'] = ''

from keras.models import load_model
import matplotlib.pyplot as plt
from skimage import io
import numpy as np
from skimage.color import gray2rgb, label2rgb
from skimage.io import imsave
from datetime import datetime
from functions import your_loss
import glob
from scipy.misc import imread
#from skimage.io import imread
import glob
import re
import time
import random
from datetime import datetime

labels = 4
channels = 1
size = 56
inner_size = 36
ysize = 36
batch_size = 254

def output_to_colors(result, x):
    zeros = np.zeros((rows,cols,4))
    #zeros[:,:,:-1]=gray2rgb(x.copy())
    #zeros = gray2rgb(x.copy())
    #output = result.argmax(axis=-1)
    zeros[output==2]=[0,0,1]
    return zeros

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_tiles(img, inner_size, overlap):
    img_padded = np.pad(img, ((overlap,overlap), (overlap,overlap)), mode='reflect')
    
    xs = []
    
    for i in xrange(0, img.shape[0], inner_size):
        for j in xrange(0, img.shape[1], inner_size):
            #print(i-overlap+overlap,i+inner_size+overlap+overlap,j-overlap+overlap, j+inner_size+overlap+overlap)
            img_overlapped = img_padded[i:i+inner_size+overlap+overlap,j:j+inner_size+overlap+overlap]
            xs.append(img_overlapped)
            
    return xs

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)



models = sorted(natural_sort(glob.glob('models/*')), key=lambda name: int(re.search(r'\d+', name).group()), reverse=True)[0:1]
print(models)
tick = datetime.now()
for model_n in models:
    model = load_model(model_n, custom_objects={'your_loss': your_loss})
    print("Loaded :%s", model_n)
    files_all = glob.glob('temp_cropped/*')
    #files_all = glob.glob('cleaned/raw/*.png')
    #files_all = glob.glob('images/single_frames/*.png')
    #files_all = glob.glob('images/all_grey/15_jpgs/*.jpg')
    #files_all = random.sample(files_all)
    #files_all = glob.glob('cleaned/penta/*')
    #files = files+files+files# + files[-4:-1]
    #print(files)

    file_chunks = chunks(files_all, batch_size)

    for idx, files in enumerate(file_chunks):
        file_names = [basename(path) for path in files]
        #print(file_names)
        imgs = np.array([np.pad(imread(fl, mode='L'), (8,8), mode='reflect').astype(float)/255 for fl in files])
        #import pdb; pdb.set_trace()
        tiles = np.array([get_tiles(img, 36, 10) for img in imgs])

        #print(file_chunks)
        #print("Processing: %s"%(fl))
        #print("Imgs shape: %s", tiles.shape)

        #Create input tensor
        xs = tiles.reshape(imgs.shape[0]*len(tiles[0]),size,size,channels)
        #print(np.unique(xs[0]))

        start_time = time.time()

        # Predict output
        ys = model.predict(xs)
        print("---- %s seconds for size: %d ----"%(time.time()-start_time, xs.shape[0]))
        ys = ys.reshape(imgs.shape[0],len(tiles[0]), ysize, ysize, labels)

        # Stitch it together
        for ix,y in enumerate(ys):
                #imgcount = 0
                count= 0
                img = imgs[ix]
                tile_output = np.zeros((img.shape[0],img.shape[1],4))
                zeros = np.zeros((img.shape[0],img.shape[1],4))

                for i in xrange(0, img.shape[0], inner_size):
                    for j in xrange(0, img.shape[1], inner_size):
                        zeros[i:i+inner_size,j:j+inner_size] = y[count]
                        count += 1
                
                for i in range(img.shape[0]):
                    for j in range(img.shape[1]):
                        output = tile_output[i,j]
                        zeros[i,j,np.argmax(output)] = 1
                        #count += 1

                #import pdb; pdb.set_trace()
                zeros[:,:,3]=1

                #color = output_to_colors(zeros, img)

                #colors = [output_to_colors(y, imgs[i]) for i,y in enumerate(ys)]
                #colors = [label2rgb(y.argmax(axis=-1), image=imgs[i], colors=[(1,0,0), (0,1,0), (0,0,1), (0,0,0)], alpha=0.9, bg_label=3) for i,y in enumerate(ys)]

                #[plt.imsave('plots/%s_%s'%(model_n, file_names[i]), zeros) for i,zeros in enumerate(colors)]
                #print(file_names)
                plt.imsave('plots/results/%s.png'%(file_names[ix]), zeros)

print "total processing done in: "+str((datetime.now()-tick).total_seconds())
