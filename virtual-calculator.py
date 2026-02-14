import cv2
import numpy as np

# --- Button Class ---
class Button:
    def __init__(self, pos, w, h, value):
        self.x, self.y = pos
        self.w = w
        self.h = h
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, (self.x, self.y), (self.x+self.w, self.y+self.h),
                      (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (self.x, self.y), (self.x+self.w, self.y+self.h),
                      (255, 255, 255), 2)
        cv2.putText(img, self.value, (self.x+20, self.y+60),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)

    def isClicked(self, px, py):
        return self.x < px < self.x+self.w and self.y < py < self.y+self.h

# --- Calculator Buttons ---
button_values = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', '.', '=', '+'],
    ['C', '<-']
]

button_list = []
for i, row in enumerate(button_values):
    for j, val in enumerate(row):
        xpos = j * 100 + 50
        ypos = i * 100 + 150
        button_list.append(Button((xpos, ypos), 100, 100, val))

# --- Safe Eval ---
def safe_eval(expr):
    try:
        return str(eval(expr, {"__builtins__": None}, {}))
    except:
        return "Error"

# --- Skin Mask Function ---
def get_skin_mask(frame):
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    lower = np.array([0, 133, 77], np.uint8)
    upper = np.array([255, 173, 127], np.uint8)
    mask = cv2.inRange(ycrcb, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask

# --- Main ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
equation = ""
delay_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    mask = get_skin_mask(frame)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fingertip = None
    click_gesture = False

    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) > 3000:
            # Simplify contour
            epsilon = 0.01 * cv2.arcLength(max_contour, True)
            approx = cv2.approxPolyDP(max_contour, epsilon, True)

            if len(approx) >= 4:
                hull = cv2.convexHull(approx, returnPoints=False)

                if hull is not None and len(hull) > 3:
                    defects = cv2.convexityDefects(approx, hull)
                    if defects is not None:
                        # Count fingers
                        cnt_fingers = 0
                        for i in range(defects.shape[0]):
                            s, e, f, d = defects[i, 0]
                            start = tuple(approx[s][0])
                            end = tuple(approx[e][0])
                            far = tuple(approx[f][0])
                            a = np.linalg.norm(np.array(start) - np.array(end))
                            b = np.linalg.norm(np.array(start) - np.array(far))
                            c = np.linalg.norm(np.array(end) - np.array(far))
                            angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c + 1e-6))
                            if angle <= np.pi/2 and d > 10000:
                                cnt_fingers += 1
                                cv2.circle(frame, far, 8, (0, 255, 0), -1)

                        # Gesture rule: fist = click
                        if cnt_fingers == 0:
                            click_gesture = True

            # Fingertip = topmost point
            topmost = tuple(max_contour[max_contour[:,:,1].argmin()][0])
            fingertip = topmost
            cv2.circle(frame, fingertip, 10, (0, 0, 255), -1)

    # Draw Buttons
    for btn in button_list:
        btn.draw(frame)

    # Draw Display
    cv2.rectangle(frame, (50, 50), (550, 120), (255, 255, 255), cv2.FILLED)
    cv2.putText(frame, equation, (60, 100),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

    # Click Detection
    if fingertip and click_gesture and delay_counter == 0:
        for btn in button_list:
            if btn.isClicked(fingertip[0], fingertip[1]):
                val = btn.value
                if val == "=":
                    equation = safe_eval(equation)
                elif val == "C":
                    equation = ""
                elif val == "<-":
                    equation = equation[:-1]
                else:
                    equation += val
                delay_counter = 1

    # Delay to avoid multiple clicks
    if delay_counter != 0:
        delay_counter += 1
        if delay_counter > 15:
            delay_counter = 0

    cv2.imshow("Virtual Calculator - Gesture Click", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
