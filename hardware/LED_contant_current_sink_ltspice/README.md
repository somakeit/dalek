This is the ltspice model used to verify the circuit behaviour for bipolar sink and mosfet sink constant current sinks.  
These circuits are linear and not very accurate, but are very simple.
They are perfectly fine for driving strings of LEDs.

There are two LTSPICE IV models:

cc_led_driver.asc : verify component values with a generic N-Channel mosfet when running on 24V
cc_led_driver_bipolar.asc : verify component values, simulate a massive (see sine wave ripple at start of waveform) power supply variation
whilst ramping the PWM duty, and checking the peak current does not exceed 50mA. See cc_bipolar_w_pwm_50mA.png

This makes use of the PWM.asc components for achieving PWM in ltspice, as this is non-trivial.

The actual MOSFET selected is vn88af.pdf due to what I had lying around.

Enjoy.



