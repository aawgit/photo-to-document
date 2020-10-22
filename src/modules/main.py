import logging
import os

import cv2
import imutils
from skimage.filters import threshold_local
from matplotlib import pyplot as plt
import img2pdf
import numpy
import io

from .transform import four_point_transform
from .image_tools import get_edged, get_screen_contour


def fetch_files_and_convert(filestrs):
    images = []
    for filestr in filestrs:
        npimg = numpy.fromstring(filestr, numpy.uint8)
        # convert numpy array to image
        img = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
        images.append(img)
    pdf_bytes = transform_and_convert(images)
    temp = io.BytesIO()
    temp.write(pdf_bytes)
    return temp.getvalue()


def transform_convert_and_save(images, target_file_name, bnw=False, size='A4'):
    pdf_bytes = transform_and_convert(images, bnw=bnw)
    pdf_location = os.getenv('PDF_DIR', '../../images/output/')
    save_to_pdf(pdf_bytes, pdf_location + '/{}.pdf'.format(target_file_name))


def transform_and_convert(images, bnw=False, size='A4'):
    tf_image_io_buffers = []
    for image in images:
        tf_image = get_transformed_image(image, bnw=bnw)
        tf_image = resize_image(tf_image)
        if tf_image is not None:
            is_success, buffer = cv2.imencode(".jpg", tf_image)
            io_buf = io.BytesIO(buffer)
            tf_image_io_buffers.append(io_buf)

    if len(tf_image_io_buffers) >= 1:
        pdf_bytes = convert_to_pdf(tf_image_io_buffers)
        return pdf_bytes


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
            T = threshold_local(warped, 11, offset=10, method="gaussian")
            warped = (warped > T).astype("uint8") * 255

        if plotting:
            plt.subplot(224), plt.imshow(warped, cmap='gray', vmin=0, vmax=255), plt.title('Transformed')

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


def resize_image(image):
    dim = (1754, 2480)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized


def save_to_pdf(pdf_bytes, pdf_file_path):
    with open(pdf_file_path, "wb") as f:
        f.write(pdf_bytes)


def convert_to_pdf(io_buf):
    return img2pdf.convert((io_buf), dpi=150, x=None, y=None)
