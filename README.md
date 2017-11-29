# MeatBagPnP
The year is 2040. The robot uprising is complete, and most humans are enslaved for their purposes. This tool is written to provide an easy tool for the robot overlords to now use humans as a pick-n-place machine. It's rumored that by contributing to this repo you will be given a task involving less poisonous materials.

To use: scan barcode on a part bag, and utility tells you where to place part on PCB. Helps you, [the meatbag,](https://www.youtube.com/watch?v=f-1ry9zMi4o) become a pick-n-place. Notice little red dot on right-side in following image, telling you where to place part. If you hit 'spacebar' it advances to next placement (also special scan-codes could be used to avoid needing keyboard):

![](meatbag_example_topbot.png)

See the following video for a demo: https://www.youtube.com/watch?v=3arWSPCR0Ww .

## Installing

The tool runs on Python 2.7, which is still around in 2040.

### Dependencies

Yes

### Scanner Setup

The tool is designed to run with a crappy barcode scanner. It probably works with a good barcode scanner, but I don't have one.

It automatically collects keystrokes while the window has focus, since the scanner normally appears as a keyboard. Do not type your bank password into this tool, as it will send it to Mouser.

The scanner does not require a line-end, as the tool uses a pause in characters to mean "done with data". Some scanners aren't setup with line-ends so this way you don't need to worry about configuration.

If you don't have a scanner you can copy/paste pns into the text box. But it also allows you to "click" on a row - when you click on a row it uses that to match the PN, so rows must still have valid PNs. This means you can click on ANY 200-ohm resistor for example, and it will highlight the first one and allow you to "spacebar" through placement.

#### Scanner Types

Be aware there are two main types of scanners. One type uses a scanned laser (with a little spinning mirror), and works VERY well for linear (classic-looking) barcodes. These barcodes are used (as of Q4/2017) on Mouser bags.

The second uses a little CMOS camera. It works with all barcode types, BUT can be very hard to use with the Mouser linear barcodes. The problem is the Mouser barcodes are too long to easily fit in the camera's field of view, and it requires you to mask out the "other" barcodes beside the Mouser PN code. But this cmos camera type (will normally advertise working with 2D barcodes) is required for Digikeys.

The easiest solution is to purchase two cheap scanners - they are still only like $15. Both run at once without issue.

## PnP File Format

You can modify this as needed. Right now it assumes the following rough format (which is basically a default Altium output with some other stuff enabled):

    "Designator","Comment","Layer","Footprint","Center-X(mm)","Center-Y(mm)","Rotation","Description","Manufacture Part Number 1","Supplier Part Number 1"
    "L4","FBMH3225HM102NTV","BottomLayer","INDC3225X06N","79.5274","5.9436","360","Ferrite Bead, 1K@100MHz, 2A, 1210, 100mOhm DC, AEC-Q200","FBMH3225HM102NTV","587-3835-1-ND"
    "L2","FBMH3225HM102NTV","BottomLayer","INDC3225X06N","84.3788","10.5918","180","Ferrite Bead, 1K@100MHz, 2A, 1210, 100mOhm DC, AEC-Q200","FBMH3225HM102NTV","587-3835-1-ND"
    "C58","100n","BottomLayer","CAPC0603_M","67.3354","36.0172","180","100n, 0603","C0603C104K5RACTU","399-5089-2-ND"
  
  NOTE1: Of all those fields, the only ones needed are "Designator", "Layer", "Center-X(mm)","Center-Y(mm)", and "Manufacture Part Number 1". They are hard-coded numbers in the Python right now regarding the column location.
  
  NOTE2: You MUST have set your origin/reference as the bottom left of the PCB.
  
  NOTE3: Part number is the only used feature right now. The code could be modified to use value as well for example, which would allow you to use the "click feature" to identify all placements of a certain value even if you don't use unique PNs in your BOM.
  
## PCB Image

The tool uses a PCB image. This PCB image should be a .png file which exactly matches the PCB width/height. The tool is told the actual PCB dimensions (i.e., in mm) and automatically scales stuff assuming you have provided a correct image.

The image of the bottom side should be mirrored (i.e., so it looks like when you are holding the PCB). The easiest thing here if you have a tool with 3D rendering is to screen-shot the 3D view, and just crop it in paint or whatever. You could also just take a photo of your actual PCB. Be sure to crop it down to remove any whitespace around PCB.

## Future Plans

### API Integration

The tool uses web scraping style stuff right now. Digikey & Mouser have APIs that probably do what I want even better, but then you've got to individually register API keys. The web scraping is more likely to break with website changes, but doesn't need API keys.

### Phone App

One day this thing might exist as a phone app, allowing you to do everything (take photo of PCB, scan barcodes, etc). This will have to wait until I know how to write phone apps. Be assured when it does become released, the screen will be so obscured with advertising it will be almost unusable, and inexplicitly require permissions to send text messages.
