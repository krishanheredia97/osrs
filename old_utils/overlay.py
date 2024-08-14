import time
import win32gui
import win32api
import win32con
import ctypes
from utils.window_handle import get_runelite_handle


class Overlay:
    def __init__(self, width=25, height=25):
        self.width = width
        self.height = height
        self.window_handle = None
        self.overlay_handle = None
        self.running = True
        self.last_pos = None

    def window_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_CLOSE:
            self.running = False
        elif msg == win32con.WM_LBUTTONDOWN:
            x, y = win32api.LOWORD(lparam), win32api.HIWORD(lparam)
            left, top = x - self.width // 2, y - self.height // 2
            right, bottom = x + self.width // 2, y + self.height // 2
            print(f"Coordinates: ({left}, {top}, {right}, {bottom})")
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def create_overlay(self):
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = "OverlayClass"
        wc.hbrBackground = win32gui.GetStockObject(win32con.NULL_BRUSH)
        wc.lpfnWndProc = self.window_proc
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        class_atom = win32gui.RegisterClass(wc)

        left, top, right, bottom = win32gui.GetWindowRect(self.window_handle)
        width, height = right - left, bottom - top
        print(f"Full window dimensions - width: {width}, height: {height}")

        self.overlay_handle = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST,
            class_atom,
            "Overlay",
            win32con.WS_POPUP | win32con.WS_VISIBLE,
            left, top, width, height,
            0, 0, win32gui.GetModuleHandle(None), None
        )

        win32gui.SetLayeredWindowAttributes(self.overlay_handle, 0, 1, win32con.LWA_ALPHA)

    def draw_rectangle(self):
        hdc = win32gui.GetDC(self.overlay_handle)

        # Create a memory DC and compatible bitmap
        mem_dc = win32gui.CreateCompatibleDC(hdc)
        bitmap = win32gui.CreateCompatibleBitmap(hdc, self.width, self.height)
        win32gui.SelectObject(mem_dc, bitmap)

        # Create a transparent brush and fill the bitmap
        brush = win32gui.CreateSolidBrush(win32api.RGB(255, 0, 0))
        win32gui.SelectObject(mem_dc, brush)
        win32gui.PatBlt(mem_dc, 0, 0, self.width, self.height, win32con.PATCOPY)

        # Get cursor position
        x, y = win32gui.GetCursorPos()
        left, top, right, bottom = win32gui.GetWindowRect(self.overlay_handle)
        x -= left
        y -= top

        # If position changed, update the overlay
        if (x, y) != self.last_pos:
            if self.last_pos:
                # Clear the old rectangle
                win32gui.BitBlt(hdc, self.last_pos[0] - self.width // 2, self.last_pos[1] - self.height // 2,
                                self.width, self.height, None, 0, 0, win32con.WHITENESS)

            # Draw the new rectangle
            win32gui.BitBlt(hdc, x - self.width // 2, y - self.height // 2,
                            self.width, self.height, mem_dc, 0, 0, win32con.SRCCOPY)

            self.last_pos = (x, y)

        # Clean up
        win32gui.DeleteObject(brush)
        win32gui.DeleteObject(bitmap)
        win32gui.DeleteDC(mem_dc)
        win32gui.ReleaseDC(self.overlay_handle, hdc)

    def run(self):
        self.window_handle = get_runelite_handle()
        if not self.window_handle:
            print("Game window not found.")
            return

        win32gui.ShowWindow(self.window_handle, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(self.window_handle)
        time.sleep(0.5)

        self.create_overlay()

        print("Overlay created. Click within the overlay to capture coordinates.")
        start_time = time.time()
        while self.running and time.time() - start_time < 10:  # Run for 20 seconds
            self.draw_rectangle()
            win32gui.PumpWaitingMessages()
            time.sleep(0.01)

        win32gui.DestroyWindow(self.overlay_handle)


if __name__ == "__main__":
    overlay = Overlay()
    overlay.run()