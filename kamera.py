import cv2
import numpy as np
import pytesseract
import imutils
import smtplib
import os


def email():

    FROM = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    TO = os.environ.get('TO_MY_PRIVATE_MAIL')
    SUBJECT = "Parking"
    TEXT = "Your parking spot is taken"

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(FROM, gmail_password)
        server.sendmail(FROM, TO, message)
        server.close()
        print("Sent msg")
    except:
        print("Something went wrong")

def test(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        print("No contour detected")
        return 0
    else:
        detected = 1

    if detected == 1:
        cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
    new_image = cv2.bitwise_and(img, img, mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

    # Read the number plate
    text = pytesseract.image_to_string(Cropped, config='--psm 11')
    print("Detected Number is:", text)
    return text

cam = cv2.VideoCapture(0)

while(True):

    ret, img = cam.read()
    cv2.imshow("Kamera", img)


    if(test(img) == 0):
        test(img)
    else:
        if (test(img) == 'ABC 123'):
            print("The value is true")
            print("Finish program")


    if (cv2.waitKey(1) & 0xFF == ord('q')):
        email()
        break



cam.release()
cv2.destroyAllWindows()



