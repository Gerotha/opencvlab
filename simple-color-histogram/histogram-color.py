# pacotes necessarios
from matplotlib import pyplot as plt
from tqdm import tqdm
import requests
import numpy as np
import argparse
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-url", required = True, action = 'store', dest = 'url', help = "Image url")
args = vars(ap.parse_args())

# getting some image from url
def url_to_image(url):
	chunk_size = 1024
	r = requests.get(url, stream = True)
	total_size = int(r.headers['content-length'])
	filename = url.split('/')[-1]

	# write data in a created image file
	with open(filename, 'wb') as f:
		for data in tqdm(desc = filename, iterable = r.iter_content(chunk_size = chunk_size), total = total_size/chunk_size, unit = 'KB'):
			f.write(data)

	img = cv2.imread(filename)

	# return a image was numpy array
	return img	

# initialize images
image = url_to_image(args["url"])

# convert the image to grayscale and create a histogram
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

# create grayscale subplot
plt.figure(1)
plt.subplot(211) 
plt.title("Grayscale/RGB Histogram")
plt.plot(hist, color = "#171A1C")

# grab the image channels, initialize the tuple of colors the figure and the flattened feature vector
chans = cv2.split(image)
colors = ("b", "g", "r")

# create rgb subplot
plt.figure(1)
plt.subplot(212) 
 
# loop over the image channels
for (chan, color) in zip(chans, colors):
	# create a histogram for the current channel and concatenate the resulting histograms for each channel
	hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
 
	# plot rgb histogram
	plt.plot(hist, color = color)
	plt.xlim([0, 255])

# open windowed images 
cv2.imshow("Original", image)
cv2.imshow("Gray", gray)

# ajust and show plot
plt.subplots_adjust(hspace = 0.0)
plt.show()
