import os
import subprocess

class ADB:
    def __init__(self, show_logs = False):
        self.show_logs = show_logs

    def capture_screenshot(self):
        output_dir = "./img"
        output_file = os.path.join(output_dir, "screenshot.png")
        print("screenshot")
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, "wb") as f:
            process = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f, stderr=subprocess.PIPE)
        if process.returncode == 0 and self.show_logs:
            print(f"Screenshot salvo como {output_file}")
        elif self.show_logs:
            print(f"Erro ao capturar screenshot: {process.stderr.decode()}")

    def scrool(self):
        command = ["adb", "shell", "input", "swipe", "500", "1600", "500", "300", "300"]
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if self.show_logs:
                print("Scrool to up!")
            if result.stdout:
                if self.show_logs:
                    print("Output:", result.stdout)
            if result.stderr:
                if self.show_logs:
                    print("Errors:", result.stderr)
        except subprocess.CalledProcessError as error:
            if self.show_logs:
                print("Error executing the command:", error)
                print("Output:", error.stdout)
                print("Errors:", error.stderr)

    def tap(x, y):
        command = ["adb", "shell", "input", "tap", str(x), str(y)]
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Tap: ",x, y)
            if result.stdout:
                print("Output:", result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except subprocess.CalledProcessError as error:
            print("Error executing the command:", error)
            print("Output:", error.stdout)
            print("Errors:", error.stderr)