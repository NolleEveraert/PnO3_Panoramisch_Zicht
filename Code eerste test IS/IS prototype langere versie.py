# Tutorial van https://morioh.com/p/bd1b6fc9d9eb

import cv2
import numpy as np
import matplotlib.pyplot as plt
import imageio
import imutils

# Zet op True om de tussenstappen te zien:
progress = True

# kies de mogelijke algoritmes
feature_extractor = 'orb'  # 4 mogelijke algoritmen om belangrijkste punten te bepalen:  'sift', 'brisk', 'orb' ('surf' gaat niet, is gepatenteerd
feature_matching = 'KNN'  # 2 mogelijke algoritmen om belangrijkste punten te verbinden: 'bf', 'KNN'

# lees de foto's in en zet ze in zwart-wit
# de trainimg zal de foto zijn  die getransformeerd zal worden
trainImg = imageio.imread('Campus 2.jpg')
trainImg_gray = cv2.cvtColor(trainImg, cv2.COLOR_RGB2GRAY)

queryImg = imageio.imread('Campus 1.jpg')
# OpenCV gebruikt de kleurcode BGR, zet om naar RGB voor matplotlib
queryImg_gray = cv2.cvtColor(queryImg, cv2.COLOR_RGB2GRAY)

if progress:
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, constrained_layout=False, figsize=(16, 9))
    ax1.imshow(queryImg, cmap="gray")
    ax1.set_xlabel("Query Image", fontsize=14)

    ax2.imshow(trainImg, cmap="gray")
    ax2.set_xlabel("Training Image (foto die getransformeerd)", fontsize=14)
    plt.show()


def detectAndDescribe(image, method=None):
    """
    Compute key points and feature descriptors using an specific method
    """

    assert method is not None, "You need to define a feature detection method. Values are: 'sift', 'surf', 'orb' of 'brisk' "

    # detect and extract features from the image
    descriptor = None
    if method == 'sift':
        descriptor = cv2.SIFT_create()
    # elif method == 'surf':  # er uit gehaald wegens patent
        # descriptor = cv2.xfeatures2d_SURF_create()
    elif method == 'brisk':
        descriptor = cv2.BRISK_create()
    elif method == 'orb':
        descriptor = cv2.ORB_create()

    # get keypoints and descriptors
    (kps, features) = descriptor.detectAndCompute(image, None)

    return kps, features


kpsA, featuresA = detectAndDescribe(trainImg_gray, method=feature_extractor)
kpsB, featuresB = detectAndDescribe(queryImg_gray, method=feature_extractor)

if progress:
    # teken de belangrijkste punten
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 8), constrained_layout=False)
    ax1.imshow(cv2.drawKeypoints(trainImg_gray, kpsA, None, color=(0, 255, 0)))
    ax1.set_xlabel("(a)", fontsize=14)
    ax2.imshow(cv2.drawKeypoints(queryImg_gray, kpsB, None, color=(0, 255, 0)))
    ax2.set_xlabel("(b)", fontsize=14)
    plt.show()


def createMatcher(method, crossCheck):
    """Create and return a Matcher Object"""

    if method == 'sift' or method == 'surf':
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=crossCheck)
    elif method == 'orb' or method == 'brisk':
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=crossCheck)
    return bf


def matchKeyPointsBF(featuresA, featuresB, method):
    bf = createMatcher(method, crossCheck=True)

    # Match descriptors.
    best_matches = bf.match(featuresA, featuresB)

    # Sort the features in order of distance.
    # The points with small distance (more similarity) are ordered first in the vector
    rawMatches = sorted(best_matches, key=lambda x: x.distance)
    print("Raw matches (Brute force):", len(rawMatches))
    return rawMatches


def matchKeyPointsKNN(featuresA, featuresB, ratio, method):
    bf = createMatcher(method, crossCheck=False)
    # compute the raw matches and initialize the list of actual matches
    rawMatches = bf.knnMatch(featuresA, featuresB, 2)
    print("Raw matches (knn):", len(rawMatches))
    matches = []

    # loop over the raw matches
    for m, n in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if m.distance < n.distance * ratio:
            matches.append(m)
    return matches


print("Gebruikte feature matcher: {}".format(feature_matching))

if progress:
    fig = plt.figure(figsize=(20, 8))

if feature_matching == 'bf':
    matches = matchKeyPointsBF(featuresA, featuresB, method=feature_extractor)
    img3 = cv2.drawMatches(trainImg, kpsA, queryImg, kpsB, matches[:100],
                           None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
elif feature_matching == 'KNN':
    matches = matchKeyPointsKNN(featuresA, featuresB, ratio=0.75, method=feature_extractor)
    img3 = cv2.drawMatches(trainImg, kpsA, queryImg, kpsB, np.random.choice(matches, 100),
                           None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

if progress:
    plt.imshow(img3)
    plt.show()


def getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh):
    # convert the keypoints to numpy arrays
    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])

    if len(matches) > 4:

        # construct the two sets of points
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches])

        # estimate the homography between the sets of points
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                                         reprojThresh)

        return (matches, H, status)
    else:
        return None


M = getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh=4)
if M is None:
    print("Error!")
(matches, H, status) = M

# corrigeer voor panorama effect
width = trainImg.shape[1] + queryImg.shape[1]
height = trainImg.shape[0] + queryImg.shape[0]

result = cv2.warpPerspective(trainImg, H, (width, height))
result[0:queryImg.shape[0], 0:queryImg.shape[1]] = queryImg

if progress:
    plt.figure(figsize=(20, 10))
    plt.imshow(result)
    plt.axis('off')
    plt.show()

# verander de foto in greyscale
gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

# vind de randen
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
c = max(cnts, key=cv2.contourArea)

(x, y, w, h) = cv2.boundingRect(c)
result = result[y:y + h, x:x + w]
plt.figure(figsize=(20, 10))
plt.imshow(result)
plt.show()
