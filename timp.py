import pyautogui
# Path to the icon image file
icon_path = "C:\\Users\\magene\\OneDrive - NVIDIA Corporation\\Desktop\\myProjects\\pythonTestAutomation\\icons\\fail.png"

def find_and_click_icon(icon_path, timeout=10):
    try:
        # Locate the icon on the screen
        icon_location = pyautogui.locateOnScreen(icon_path, confidence=0.9, grayscale=True, region=(0, 0, 1920, 1080))
        
        if icon_location is not None:
            # If the icon is found, click on it
            icon_center = pyautogui.center(icon_location)
            print(icon_center)
            print(icon_location)
            #pyautogui.click(icon_certer)
            print("Icon clicked successfully.")
            return True
        else:
            print("Icon not found.")
            return False
    except Exception as e:
        print("Error:", e)
        return False


