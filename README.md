# MeatBagPnP
The year is 2040. The robot uprising is complete, and most humans are enslaved for their purposes. This tool is written to provide an easy tool for the robot overlords to now use humans as a pick-n-place machine. It's rumored that by contributing to this repo you will be given a task involving less poisonous materials.

To use: scan barcode on a part bag, and utility tells you where to place part on PCB. Helps you [, the meatbag,](https://www.youtube.com/watch?v=f-1ry9zMi4o) become a pick-n-place.

## Installing

The tool runs on Python 2.7, which is still around in 2040.

### Dependencies

Yes

### Scanner Setup

The tool is designed to run with a crappy barcode scanner. It probably works with a good barcode scanner, but I don't have one.

It automatically collects keystrokes while the window has focus.

## PnP File Format

You can modify this as needed. Right now it assumes the following rough format (which is basically a default Altium output with some other stuff enabled):

    "Designator","Comment","Layer","Footprint","Center-X(mm)","Center-Y(mm)","Rotation","Description","Manufacture Part Number 1","Supplier Part Number 1"
    "L4","FBMH3225HM102NTV","BottomLayer","INDC3225X06N","79.5274","5.9436","360","Ferrite Bead, 1K@100MHz, 2A, 1210, 100mOhm DC, AEC-Q200","FBMH3225HM102NTV","587-3835-1-ND"
    "L2","FBMH3225HM102NTV","BottomLayer","INDC3225X06N","84.3788","10.5918","180","Ferrite Bead, 1K@100MHz, 2A, 1210, 100mOhm DC, AEC-Q200","FBMH3225HM102NTV","587-3835-1-ND"
    "C58","100n","BottomLayer","CAPC0603_M","67.3354","36.0172","180","100n, 0603","C0603C104K5RACTU","399-5089-2-ND"
  
  NOTE1: Of all those fields, the only ones needed are "Designator", "Layer", "Center-X(mm)","Center-Y(mm)", and "Manufacture Part Number 1". They are hard-coded numbers in the Python right now regarding the column location.
  
  NOTE2: You MUST have set your origin/reference as the bottom left of the PCB.
  
## PCB Image

The tool uses a PCB image. This PCB image should be a .png file which exactly matches the PCB width/height. The tool is told the actual PCB dimensions (i.e., in mm) and automatically scales stuff assuming you have provided a correct image.

The image of the bottom side should be mirrored (i.e., so it looks like when you are holding the PCB). The easiest thing here if you have a tool with 3D rendering is to screen-shot the 3D view, and just crop it in paint or whatever. You could also just take a photo of your actual PCB.

## Future Plans

One day this thing might exist as a phone app, allowing you to do everything (take photo of PCB, scan barcodes, etc). This will have to wait until I know how to write phone apps. Be assured when it does become released, the screen will be so obscured with advertising it will be almost unusable.
