import logging
import os

import cv2
import imutils
from skimage.filters import threshold_local
from matplotlib import pyplot as plt
import img2pdf

from src.modules.transform import four_point_transform
from src.modules.image_tools import get_edged, get_screen_contour


def get_transformed_image(image, bnw=False, plotting=False):
    try:
        ratio = image.shape[0] / 500.0
        orig = image.copy()
        image = imutils.resize(image, height=500)

        edged = get_edged(image)
        if plotting:
            plt.subplot(221), plt.imshow(image), plt.title('Input')
            plt.subplot(222), plt.imshow(edged), plt.title('Edged')

        screen_cnt = get_screen_contour(edged)
        screen_cnt_img = image.copy()
        cv2.drawContours(screen_cnt_img, [screen_cnt], -1, (0, 255, 0), 5)
        if plotting:
            plt.subplot(223), plt.imshow(screen_cnt_img), plt.title('Screen contour')

        warped = four_point_transform(orig, screen_cnt * ratio)
        if bnw:
            # convert the warped image to grayscale, then threshold it
            # to give it that 'black and white' paper effect
            warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            T = threshold_local(warped, 11, offset = 10, method = "gaussian")
            warped = (warped > T).astype("uint8") * 255

        if plotting:
            plt.subplot(224), plt.imshow(warped, cmap='gray', vmin = 0, vmax = 255), plt.title('Transformed')

        # TODO:
        # Auto detect real page ratio
        # Re scale to page size (ex: A4)
        # Adjust brightness
        # Make brightness uniform throughout the image
        return warped
    except Exception as e:
        logging.error(str(e))

    finally:
        plt.show()

def convert_to_pdf(image_file_path, pdf_file_path):
    pdf_bytes = img2pdf.convert((image_file_path,), dpi=150, x=None, y=None)
    with open(pdf_file_path,"wb") as f:
        f.write(pdf_bytes)

if __name__ == "__main__":
    # For testing/ debugging image processing without the api
    image_location = os.getenv('IMAGE_DIR', '../../images/input/')
    tf_image_location = os.getenv('TF_IMAGE_DIR', '../../images/output/')
    file_name = 'IMG_20200704_143727.jpg'
    image = cv2.imread(image_location + file_name)
    tf_image = get_transformed_image(image, bnw=False, plotting=False)
    pdf_location = os.getenv('PDF_DIR', '../../images/output/')
    cv2.imwrite(tf_image_location + file_name, tf_image)
    convert_to_pdf(tf_image_location + file_name, pdf_location + '/{}.pdf'.format(file_name[:-4]))