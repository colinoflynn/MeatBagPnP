# MeatBagPnP Kicad integration demo

The p&p placement file and PCB image in this directory were generated using kicad.
The actual PCB dimensions are
	* width: 53.5
	* height: 58.5

In order to enable kicad CSV parsing, you must specify the "--format kicad" argument when launching the program, e.g. (from the application directory):

    ./meatbag.py --format kicad --image demo/KiCad/kicaddemo.png --width 53.5 --height 58.5 --csv demo/KiCad/demo-all-pos.csv 


## Kicad PnP File Format

The PnP placement files created with Kicad (File -> Fabrication Outputs -> Footprint position (.pos) file) will work as-is, as long as you:
	* place a "drill and place offset" marker on the lower left corner of your board
	* select the CSV export format; 
	* use the "single file per board" option (rather than file per side); and
	* ensure the units match whatever you will specify as the PCB size, here.

For reference, the currently standard PnP format for kicad is

	Ref,Val,Package,PosX,PosY,Rot,Side

which MeatBadPnP now supports.

## Kicad PCB Image

You can produce an image anyway you like using kicad.  I've used the gerber viewer and the 3D viewer successfully, the important points are that the images must be head on (perspective won't be account for) and only include the PCB itself (no margins, unless you account for this when specifying your dimensions to meatbagpnp).


2018-04-30, Pat Deegan, psychogenic.com
