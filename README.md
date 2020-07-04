# Photo to document
Convert images to documents (PDF) including Perspective Transformation

## Installation and running
- Clone the repo and open 'photo-to-document' directory
- Create and activate the virtual environment
- run `pip install -r requirements.txt`
- _(Optional) Set env variables IMAGE_DIR, TF_IMAGE_DIR, and PDF_DIR_
- run main.py

## Results
Contour finding fail 1:
![No countour 1](documentation/no-contour.png)

Contour finding fail 2:
![No countour 2](documentation/no-contours-1.png)

Success 1:
![Success](documentation/success-1-bnw.png)

Success 2:
![Success](documentation/success-02.png)

Success 3:
![Success](documentation/success-03-color.png)

Success 4 - PDF converted:
![Success](documentation/pdf.png)

## Acknowledgement:
Initial version transform.py is from https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/