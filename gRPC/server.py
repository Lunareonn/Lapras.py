from concurrent import futures

import grpc
import screenshot_pb2
import screenshot_pb2_grpc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.set_preference('intl.accept_languages', 'en-GB')
driver = webdriver.Firefox(options=options)


class ScreenshotterService(screenshot_pb2_grpc.ScreenshotterServicer):
    def TakeScreenshot(self, request, context):
        print("TakeScreenshot(url=\"{}\", element=\"{}\", script=\"{}\")".format(request.url, request.element, request.script))
        driver.get(request.url)

        if request.script:
            driver.execute_script(request.script)

        reply = screenshot_pb2.TakeScreenshotResponse()

        if request.element:
            reply.image = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, request.element))).screenshot_as_png
        else:
            reply.image = driver.get_screenshot_as_png()

        return reply


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    screenshot_pb2_grpc.add_ScreenshotterServicer_to_server(ScreenshotterService(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("Listening for GRPC calls on 0.0.0.0:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
