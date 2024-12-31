# Introduction

I wanted to see if I could create a low-cost tool for the blind to get  live description of the scene in front of a camera. Since I was going for low cost (<30$), and wanted to learn more about software development on arduino, I bought a ESP32-CAM with built-in WiFi to capture the actual images.

To actually describe the image I selected the gpt-4o-mini model. I didnt think much about which model to use, but this seemed like a good start.

The proof-of-concept solution actually works, but is nowhere near to be a real product since it requires the cell-phone to have a browser opened to a specific page to read the audio descriptions that are updated on a web page.

Security is also not really considered in this project.

## Alternatives

One driving force for creating this tool is how expensive the alternatives are. However alternatives seem to be emerging at the moment so there is hope.


| Product  | Price   | Comment |
|----------|---------|---------|
| Ray-Ban Meta Glasses | $300 | No app available for visual descriptions (yet). Closed API. Can maybe be hacked.|
| EchoVision Smart Glasses | $599 | Interesting product that I need to investigate more | 
| Envision Glasses | $3200 | Google Glass Enterprise Edition 2 hardware |
| OrCam MyEye | $5900 | Clunky solution that you attach to glasses |


## My solution

Use a cell phone with internet sharing enabled that the ESP32-CAM connects to. Then software on the ESP32-CAM uploads images to a HTTP server, which then provides the image the OpenAI API which returns the description of the image. The description is updated on a page in the HTTP server which the cellphone has open.

When new text arrives, the voice-over (for iPhone) reads the updated text to the user.

![alt text](overview.png)

Setup using a powerbank as battery source for the ESP32-CAM.

![alt text](hw.png)


## Installing arduino software to ESP32-CAM

The source code for the ESP32-CAM is located in the "esp32" folder. Open it using the Arduino IDE. Update the WiFi credentials and target HTTP server before flashing. Some links that may help with installing the ESP32-CAM drivers.

https://randomnerdtutorials.com/upload-code-esp32-cam-mb-usb/
https://randomnerdtutorials.com/installing-esp32-arduino-ide-2-0/

Set the baud-rate to 115200 in the serial monitor to get the output from the ESP32-CAM.

## Running the HTTP server

Set the OpenAI API KEY as an environment variable before starting the web server. You need to update the server IP:PORT in both templates/index.html and server.py.

Powershell
```powershell
$Env:API_KEY = "sk-proj-BLABLABLA..."
```

Bash
```bash
export API_KEY = "sk-proj-BLABLABLA..."
```

Then the server can be started:

```bash
python server.py
```

If you only want to test prompts for the description of the image, test.py can be used to just send a saved image without involving the ESP32 hardware.

# Testing the solution

## First test

The first test was somewhat successful. The camera updated every 10 seconds and descriptions was pushed to the page as expected. However the descriptions contained a lot that is not interesting in this context. For example weather and guessing where the location is.

Prompt: "What’s in this scene and where? Less text is better."

### Examples

*"The scene shows a park area with a sign reading "Aseparken." There are trees and a pathway, likely in a semi-urban or rural location. The weather appears overcast."*

![Image](images/2024-12-28_142000.276.jpg)

### Log

[Full log](test_1.txt)

## Second test

Updated to a longer prompt to reduce "fluff" in the descriptions.

Prompt: "Give a short description of the image and where objects are located in the image. Do not mention that this is an image. Do not mention weather or geographical location. Less text is better."

The descriptions became much better and is sometimes useful, but the prompt can be improved for sure. Due to what I think is the low quality of the camera the descriptions are more "gloomy" than they actually are.

The API cost for the ~25 minute walk was $0.23 where one image was describes every 7 seconds.

### Examples

*"A pathway extends ahead, flanked by trees on both sides. To the left, a bench is positioned alongside the path. There is a slight curve in the path leading into the distance."*

![Image](images/2024-12-31_114137.446.jpg)

*"A grassy slope is in the background, with pathways leading to a fork on the left and right. On the left side, there’s a signpost. In the foreground, there is a small object lying on the ground. A building is visible on the right side."*

![Image](images/2024-12-31_114646.763.jpg)

*"A pathway runs through the center, with grass on both sides. Toward the far left, a person is near the edge of the grass. In the background, there are vehicles and a few trees on the left. A sign structure is visible on the right side."*

![Image](images/2024-12-31_115126.815.jpg)

"*A person walks on a path holding the handle of a stroller. Another individual walks alongside them. To the left, there are trees, and a light pole stands beside the path. In the background, there are grassy areas and some structures."*

![Image](images/2024-12-31_115306.805.jpg)

*"A dirt path leads into a grassy area, flanked by trees. To the left, there are two magpies on the ground. In the background, a brick building is visible, with additional structures further down the path on the right side. The scene has a sparse, open feel."*

![Image](images/2024-12-31_115508.385.jpg)

### Log

[Full log](test_2.txt)