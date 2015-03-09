This folder contains the DesignSpark PCB files for the first Dalek lighting driver circuit.
It is just a bunch of discrete transistor constant current sinks for running string of LEDs from 12V and 24V supplies.

The channel allocation is:
6 x 50 mA (R+G+B left/right) @ 24V
2 x 350mA (White) @ 24V
1 x 350mA (White) @ 12V
2 x 60mA @ 12V
1 x 50mA @ 12V

The DesignSpark PCB project file is Dalek_Lights.prj  You should open this file directly.
It contains a top level schematic design (top.sch) and a PCB layout file (top2_poured_copper_gnd_compress.pcb)
The SMI logo is defined by the library 'SMI' (which consists files: SMI.*)

These are 
SMI.psx / SMI.psl : PCB Component/Layout view library(i.e. a PCB thing you can use)
smi_logo_design.pcb : PCB file containing the layout data for the logo as defined by the above library
SMI.cmx / SMI.cml : 'Component' view of the layout above, which is a container for the above PCB component

Also used the library 'Fiducual - 3mm' which should be installed in the DesignSpark library path. 
It is used to create fiducual markers (optical alignment targets) in the corners of the PCB.  These are not needed for DIY pcb, but make good holes to drill for mounting :)

Output files (gerbers) can be found in the file 'manufacturing.zip' but these will not be needed.

For documentation, there are some screen grabs (see the png files)

***************************************************************************************************
* The PDF file 'top2_poured_copper_gnd_compress - PCB.pdf' is a printable view of the PCB layers. *
* USE THIS TO MAKE A DIY PCB!                                                                     *
* The component placement and drill locations are also shown in this file                         *
* A separate wiring diagram can be found in 'TBD'
***************************************************************************************************
