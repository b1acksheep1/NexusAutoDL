#!/usr/bin/env python3
import ctypes
import os
import subprocess
import time
import logging
import click as click
import cv2
import mss
import numpy as np
import win32api
import win32con
import win32gui

user32 = ctypes.windll.user32


class System:
    def __init__(self, browser: str = None, vortex: bool = False, verbose: bool = False, force_primary: bool = False, window_title: str = None):

        logging.info("Initializing system")
        logging.info(f"Arguments: browser={browser}, vortex={vortex}, verbose={verbose}")

        self.monitors = self.get_monitors()
        if force_primary:
            self.monitors = [self.monitors[0]]
        else:
            self.monitors = sorted(self.monitors, key=lambda chunk: chunk[0])
        logging.info(f"Found {len(self.monitors)} monitors")
        logging.info(f"Monitors: {self.monitors}")

        self.vortex_btn, self.web_btn, self.click_btn, self.understood_btn, self.staging_btn, self.wabbajack_btn = self._load_assets()
        logging.info("Loaded assets")

        # Check if there are displays left of the primary display which makes their coordinates negative
        self.negative_displays = [m for m in self.monitors if m[0] < 0]
        logging.info(f"Found {len(self.negative_displays)} negative displays")
        logging.info(f"Negative displays: {self.negative_displays}")

        self.negative_offset_x = sum([m[0] for m in self.negative_displays])
        self.negative_offset_y = sorted(self.monitors, key=lambda monitor: monitor[1])[0][1]

        self.biggest_display = sorted(self.monitors, key=lambda monitor: abs(monitor[0]))[-1]
        logging.info(f"Biggest display: {self.biggest_display}")
        logging.info("Calculated offsets")

        (self.sift, self.vortex_desc, self.web_desc, self.wabbajack_desc,
         self.click_desc, self.understood_desc, self.staging_desc, self.matcher) = self._init_detector()
        logging.info("Initialized detector")

        self.screen, self.v_monitor = self._init_screen_capture()

        if browser:
            self.prep_browser(browser.lower())
        if vortex:
            self.prep_vortex()

        if window_title:
            self.prep_window_by_title(window_title)

        self.vortex = vortex
        self.verbose = verbose

    def _init_detector(self):
        logging.info("Initializing detector")
        sift = cv2.SIFT_create()

        def desc(img):
            g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            _, d = sift.detectAndCompute(g, mask=None)
            return d

        vortex_descriptors = desc(self.vortex_btn)
        website_descriptors = desc(self.web_btn)
        wabbajack_descriptors = desc(self.wabbajack_btn)
        click_descriptors = desc(self.click_btn)
        understood_descriptors = desc(self.understood_btn)
        staging_descriptors = desc(self.staging_btn)

        logging.info("Initialized descriptors")

        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        return (sift, vortex_descriptors, website_descriptors, wabbajack_descriptors,
                click_descriptors, understood_descriptors, staging_descriptors, matcher)

    def _init_screen_capture(self) -> (mss.mss, dict):
        screen = mss.mss()
        mon = screen.monitors[0]

        aspect_ratio = self.monitors[0][2] / self.monitors[0][3] if not self.negative_displays \
            else self.monitors[-1][2] / self.monitors[-1][3]
        monitor = {
            "top": sorted(self.monitors, key=lambda chunk: chunk[1])[0][1],
            "left": sorted(self.monitors, key=lambda chunk: chunk[0])[0][0],
            "width": sum([abs(m[2]) for m in self.monitors]),
            "height": abs(int(self.biggest_display[0] * (aspect_ratio ** -1))) if len(self.monitors) > 1 else
            self.monitors[0][3],
            "mon": 0,
        }
        logging.info(f"Initialized screen capture with monitor: {monitor}")

        return screen, monitor

    @staticmethod
    def _load_assets() -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
        vortex_path = "assets/VortexDownloadButton.png"
        web_path = "assets/WebsiteDownloadButton.png"
        click_path = "assets/ClickHereButton.png"
        understood_path = "assets/UnderstoodButton.png"
        staging_path = "assets/StagingButton.png"
        wabbajack_path = "assets/WabbajackDownloadButton.png"

        for path in [vortex_path, web_path, click_path, understood_path, staging_path, wabbajack_path]:
            if os.path.isfile(path):
                yield cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            else:
                raise FileNotFoundError(f"Asset {path} not found")

    def capture_screen(self) -> np.ndarray:
        img = np.array(self.screen.grab(self.v_monitor))
        logging.info("Captured screen")

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def click(x, y):
        o_pos = win32api.GetCursorPos()

        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        logging.info(f"Clicked at ({x}, {y})")

        win32api.SetCursorPos(o_pos)

    def detect(self, img, descriptors, threshold, bbox=None) -> tuple[int, int]:
        screenshot_keypoints, screenshot_desc = self.sift.detectAndCompute(img, mask=None)

        matches = self.matcher.knnMatch(descriptors, screenshot_desc, k=2)

        points = np.array([screenshot_keypoints[m.trainIdx].pt for m, _ in matches if m.distance < threshold]).astype(
            np.int32)

        if bbox:
            points = np.array([p for p in points if bbox[0] < p[0] < bbox[2] and bbox[1] < p[1] < bbox[3]])

        point = np.median(points, axis=0)
        if not np.isnan(point).any():
            return self.img_coords_to_mon_coords(int(point[0]), int(point[1]))

    def detect_improved(self, img, descriptors, min_matches=8, ratio=0.75, bbox=None):
        # Crop if we have a bbox (expects [x1,y1,x2,y2] in *image* coords)
        if bbox:
            x1, y1, x2, y2 = map(int, bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
            if x2 <= x1 or y2 <= y1:
                logging.info("detect(): invalid bbox after clipping; skipping")
                return None
            img_cropped = img[y1:y2, x1:x2]
        else:
            img_cropped = img

        # SIFT on grayscale for stability
        gray = cv2.cvtColor(img_cropped, cv2.COLOR_RGB2GRAY)
        kps, des = self.sift.detectAndCompute(gray, mask=None)
        if des is None or len(kps) == 0:
            logging.info("detect(): no keypoints in current frame region")
            return None

        # 2-NN + Lowe ratio test (canonical SIFT matching)
        matches = self.matcher.knnMatch(descriptors, des, k=2)
        good = []
        for m, n in matches:
            if m.distance < ratio * n.distance:
                good.append(m)

        if len(good) < min_matches:
            logging.info(f"detect(): only {len(good)} good matches (<{min_matches})")
            return None

        pts = np.float32([kps[m.trainIdx].pt for m in good])
        cx, cy = np.mean(pts, axis=0)  # safe now; pts not empty

        # Back to full-image coords if we cropped
        if bbox:
            cx += x1
            cy += y1

        # Convert to monitor coords for clicking
        return self.img_coords_to_mon_coords(int(cx), int(cy))

    @staticmethod
    def get_monitors() -> list[tuple[int, int, int, int]]:
        return [monitor[2] for monitor in win32api.EnumDisplayMonitors(None, None)]

    @staticmethod
    def get_vortex_bbox() -> list[int, int, int, int]:
        vortex = user32.FindWindowW(None, u"Vortex")
        bbox = list(win32gui.GetWindowRect(vortex))
        logging.info(f"Vortex bbox: {bbox}")

        return bbox

    def img_coords_to_mon_coords(self, pos_x, pos_y) -> tuple[int, int]:
        if len(self.monitors) > 1:
            click_x = self.negative_offset_x + pos_x
            click_y = self.negative_offset_y + pos_y
        else:
            click_x = pos_x
            click_y = pos_y

        return click_x, click_y

    def mon_coords_to_img_coords(self, pos_x, pos_y) -> tuple[int, int]:
        if len(self.monitors) > 1:
            click_x = pos_x - self.negative_offset_x
            click_y = pos_y
        else:
            click_x = pos_x
            click_y = pos_y

        return click_x, click_y

    def prep_browser(self, browser):
        commands = {"chrome": r'start chrome about:blank', "firefox": r'start firefox'}
        win_name = {"chrome": "about:blank - Google Chrome", "firefox": "Mozilla Firefox"}

        if browser not in commands.keys():
            raise ValueError(f"Browser \'{browser}\' not supported")

        subprocess.Popen(commands[browser], shell=True)
        time.sleep(0.4)
        h_browser = user32.FindWindowW(None, win_name[browser])

        logging.info("Found Firefox window")

        if len(self.monitors) > 1:
            user32.ShowWindow(h_browser, 1)
            x_b, y_b, w_b, h_b = self.monitors[0][0], self.monitors[0][1], self.monitors[0][2], self.monitors[0][3]
            win32gui.SetWindowPos(h_browser, None, x_b, y_b, w_b, h_b, True)
            user32.ShowWindow(h_browser, 3)
        logging.info("Moved chrome window")

    def prep_vortex(self):
        vortex = user32.FindWindowW(None, u"Vortex")
        logging.info("Found vortex window")

        if len(self.monitors) > 1:
            user32.ShowWindow(vortex, 1)
            x_v, y_v, w_v, h_v = self.monitors[1][0], self.monitors[1][1], self.monitors[1][2], self.monitors[1][3]
            win32gui.SetWindowPos(vortex, None, x_v, y_v, w_v, h_v, True)
            user32.ShowWindow(vortex, 3)
        logging.info("Moved vortex window")

    def prep_window_by_title(self, title_substr: str):
        handles = []

        def _enum_cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                t = win32gui.GetWindowText(hwnd)
                if t and title_substr.lower() in t.lower():
                    handles.append(hwnd)
            return True

        win32gui.EnumWindows(_enum_cb, None)
        if not handles:
            raise RuntimeError(f"No visible window contains title: {title_substr!r}")

        h = handles[0]  # pick first match; refine if needed
        logging.info(f"Found window '{win32gui.GetWindowText(h)}' for title match {title_substr!r}")

        if len(self.monitors) > 1:
            user32.ShowWindow(h, 1)
            x, y, w, hgt = self.monitors[0]
            win32gui.SetWindowPos(h, None, x, y, w, hgt, True)
            user32.ShowWindow(h, 3)

    def scan(self):
        v_found = False
        w_found = False
        web_loop = 0

        while True:
            img = self.capture_screen()

            if not v_found and self.vortex:
                vortex_bbox = list(self.get_vortex_bbox())
                fac = 5 + (5 - vortex_bbox[0] / 512)
                # Pad borders to ignore possible mismatches
                vortex_bbox[0] += vortex_bbox[2] * (1 / fac)
                vortex_bbox[1] += vortex_bbox[3] * (1 / fac)
                vortex_bbox[2] -= vortex_bbox[2] * (1 / fac)
                vortex_bbox[3] -= vortex_bbox[3] * (1 / fac)

                vortex_bbox[0], vortex_bbox[1] = self.mon_coords_to_img_coords(vortex_bbox[0], vortex_bbox[1])
                vortex_bbox[2], vortex_bbox[3] = self.mon_coords_to_img_coords(vortex_bbox[2], vortex_bbox[3])

                vortex_loc = self.detect_improved(img, self.vortex_desc, bbox=vortex_bbox)
                understood_btn_loc = self.detect_improved(img, self.understood_desc, min_matches=6, ratio=0.75)
                staging_btn_loc = self.detect_improved(img, self.staging_desc, min_matches=6, ratio=0.75)

                if staging_btn_loc:
                    logging.info(f"Staging button found at {staging_btn_loc}. Clicking...")
                    self.click(*staging_btn_loc);
                    time.sleep(1)
                elif understood_btn_loc:
                    logging.info(f"Understood button found at {understood_btn_loc}. Clicking...")
                    self.click(*understood_btn_loc);
                    time.sleep(1)

                if vortex_loc:
                    logging.info(f"Found vortex button at {vortex_loc}")
                    self.click(*vortex_loc)
                    v_found = True

            elif w_found:
                click_loc = self.detect_improved(img, self.click_desc, min_matches=6, ratio=0.75)

                if click_loc:
                    logging.info(f"Found click button at {click_loc}")
                    w_found = False
                    v_found = False
                    time.sleep(3)

            elif v_found or not self.vortex:
                web_loc = self.detect_improved(img, self.wabbajack_desc, min_matches=6, ratio=0.75)

                if web_loc:
                    logging.info(f"Found Wabbajack download button at {web_loc}")
                    self.click(*web_loc)
                    web_loop = 0
                    if self.vortex:
                        w_found = True
                elif web_loop > 5:
                    logging.info("Wabbajack button not found. Restarting...")
                    v_found = False
                    web_loop = 0
                else:
                    web_loop += 1

            logging.info("Waiting 2 seconds")
            time.sleep(2)


@click.command()
@click.option('--browser', is_flag=False, default=None, help='Specifies browser to automatically move next to Vortex. '
                                                             'Only works with --vortex. Supported browsers: chrome, '
                                                             'firefox')
@click.option('--vortex', is_flag=True, default=False, help='Enables vortex mode')
@click.option('--verbose', is_flag=True, default=False, help='Enables verbose mode')
@click.option('--force-primary', is_flag=True, default=False, help='Forces the script to use the primary monitor')
@click.option('--window-title', is_flag=False, default=None,
              help='Substring of an existing window title to position instead of launching a browser '
                   '(e.g. "Wabbajack")')
def main(browser, vortex, verbose, force_primary, window_title):
    assert browser in ["chrome", "firefox", None], f"Browser \'{browser}\' not supported"
    assert (browser and vortex) or window_title or (not browser and not window_title), \
        "Use --vortex with --browser or --window-title, or neither."

    if verbose:
        logging.basicConfig(level=logging.INFO, handlers=[
            logging.FileHandler("log.log"),
            logging.StreamHandler()
        ], format='[%(asctime)s - %(levelname)s] in %(funcName)s: %(message)s')
    else:
        logging.basicConfig(handlers=[
            logging.FileHandler("log.log"),
            logging.StreamHandler()
        ], format='[%(asctime)s - %(levelname)s]: %(message)s', level=logging.ERROR)

    agent = System(browser, vortex, verbose, force_primary, window_title)
    agent.scan()


if __name__ == "__main__":
    main()
