import os
import glob

def init(board):
    if board == 'beaglebone':
        print('doing beaglebone-specific GPIO hardware init')

        # Beaglebone white specific
        if os.path.exists("/sys/kernel/debug/omap_mux/uart1_txd"):
            # we are not on the beaglebone black, setup uart1
            # echo 0 > /sys/kernel/debug/omap_mux/uart1_txd
            fw = open("/sys/kernel/debug/omap_mux/uart1_txd", "w")
            fw.write("%X" % (0))
            fw.close()
            # echo 20 > /sys/kernel/debug/omap_mux/uart1_rxd
            fw = open("/sys/kernel/debug/omap_mux/uart1_rxd", "w")
            fw.write("%X" % ((1 << 5) | 0))
            fw.close()

        ### if running on BBB/Ubuntu 14.04, setup pin muxing UART1
        pin24list = glob.glob("/sys/devices/ocp.*/P9_24_pinmux.*/state")
        for pin24 in pin24list:
            os.system("echo uart > %s" % (pin24))

        pin26list = glob.glob("/sys/devices/ocp.*/P9_26_pinmux.*/state")
        for pin26 in pin26list:
            os.system("echo uart > %s" % (pin26))


        ### Set up atmega328 reset control
        # The reset pin is connected to GPIO2_7 (2*32+7 = 71).
        # Setting it to low triggers a reset.
        # echo 71 > /sys/class/gpio/export

        ### if running on BBB/Ubuntu 14.04, setup pin muxing GPIO2_7 (pin 46)
        pin46list = glob.glob("/sys/devices/ocp.*/P8_46_pinmux.*/state")
        for pin46 in pin46list:
            os.system("echo gpio > %s" % (pin46))

        try:
            fw = open("/sys/class/gpio/export", "w")
            fw.write("%d" % (71))
            fw.close()
        except IOError:
            # probably already exported
            pass
        # set the gpio pin to output
        # echo out > /sys/class/gpio/gpio71/direction
        fw = open("/sys/class/gpio/gpio71/direction", "w")
        fw.write("out")
        fw.close()
        # set the gpio pin high
        # echo 1 > /sys/class/gpio/gpio71/value
        fw = open("/sys/class/gpio/gpio71/value", "w")
        fw.write("1")
        fw.flush()
        fw.close()

        ### Set up atmega328 reset control - BeagleBone Black
        # The reset pin is connected to GPIO2_9 (2*32+9 = 73).
        # Setting it to low triggers a reset.
        # echo 73 > /sys/class/gpio/export

        ### if running on BBB/Ubuntu 14.04, setup pin muxing GPIO2_9 (pin 44)
        pin44list = glob.glob("/sys/devices/ocp.*/P8_44_pinmux.*/state")
        for pin44 in pin44list:
            os.system("echo gpio > %s" % (pin44))

        try:
            fw = open("/sys/class/gpio/export", "w")
            fw.write("%d" % (73))
            fw.close()
        except IOError:
            # probably already exported
            pass
        # set the gpio pin to output
        # echo out > /sys/class/gpio/gpio73/direction
        fw = open("/sys/class/gpio/gpio73/direction", "w")
        fw.write("out")
        fw.close()
        # set the gpio pin high
        # echo 1 > /sys/class/gpio/gpio73/value
        fw = open("/sys/class/gpio/gpio73/value", "w")
        fw.write("1")
        fw.flush()
        fw.close()

        ### read stepper driver configure pin GPIO2_12 (2*32+12 = 76).
        # Low means Geckos, high means SMC11s

        ### if running on BBB/Ubuntu 14.04, setup pin muxing GPIO2_12 (pin 39)
        pin39list = glob.glob("/sys/devices/ocp.*/P8_39_pinmux.*/state")
        for pin39 in pin39list:
            os.system("echo gpio > %s" % (pin39))

        try:
            fw = open("/sys/class/gpio/export", "w")
            fw.write("%d" % (76))
            fw.close()
        except IOError:
            # probably already exported
            pass
        # set the gpio pin to input
        fw = open("/sys/class/gpio/gpio76/direction", "w")
        fw.write("in")
        fw.close()
        # set the gpio pin high
        fw = open("/sys/class/gpio/gpio76/value", "r")
        ret = fw.read()
        fw.close()
        print("Stepper driver configure pin is: " + str(ret))

    elif board == 'raspberrypi':
        print('doing Raspberry Pi specific GPIO hardware init')
        import RPi.GPIO as GPIO
        # GPIO.setwarnings(False) # surpress warnings
        GPIO.setmode(GPIO.BCM)  # use chip pin number
        pinSense = 7
        pinReset = 2
        # pinExt1 = 3
        # pinExt2 = 4
        # pinExt3 = 17
        # pinTX = 14
        # pinRX = 15
        # read sens pin
        GPIO.setup(pinSense, GPIO.IN)
        isSMC11 = GPIO.input(pinSense)  # why?
        # atmega reset pin
        GPIO.setup(pinReset, GPIO.OUT)
        GPIO.output(pinReset, GPIO.HIGH)
        # no need to setup the serial pins
        # although /boot/cmdline.txt and /etc/inittab needs
        # to be edited to deactivate the serial terminal login
        # (basically anything related to ttyAMA0)

    elif board == 'none':
        print('default hardware, not doing any GPIO initialization')

    else:
        raise RuntimeError('Unknown board configured: %r' % board)
