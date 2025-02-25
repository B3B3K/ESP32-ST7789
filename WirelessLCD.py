#http://ip_adresi/?input=30 karakter&x_axis=240 max&y_axis=125 max
import network
import socket
from time import sleep
import esp
import gc
import ure
from machine import Pin, SPI, PWM
import framebuf
import time

esp.osdebug(None)
gc.collect()

# Replace with your network credentials
SSID = '?'
PASSWORD = '?'

# Connect to Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

BL = 1
DC = 7
RST = 2
MOSI = 6
SCK = 9
CS = 8

while not station.isconnected():
    sleep(1)

print('Connection successful')
ip_add = station.ifconfig()

# Initialize socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

print('Listening on', addr)

class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135
        
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1, 10000_000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   = 0x07E0
        self.green = 0x001f
        self.blue  = 0xf800
        self.white = 0xffff
        self.black = 0x0000
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def pixel(self, x, y, color):
        """Draw a pixel with the specified color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (x + y * self.width) * 2
            self.buffer[index] = (color >> 8) & 0xFF
            self.buffer[index + 1] = color & 0xFF
    def fill_rect(self, x, y, w, h, color):
        """Fill a rectangle with the specified color"""
        for i in range(h):
            for j in range(w):
                self.pixel(x + j, y + i, color)

LCD = LCD_1inch14()



def print_text(text, x, y, color = LCD.white):
    LCD.fill_rect(x, y, len(text+"a")*8, y+8, LCD.black)  # Clear the area with black
    LCD.text(text, x, y, color)
    LCD.show()
    time.sleep(0.1)

def lcd_start():
    pwm = PWM(Pin(BL))
    pwm.freq(500)
    pwm.duty_u16(32768) # max 65535
    LCD.fill(LCD.black)
    print_text(ip_add[0],0,0)
    LCD.show()

lcd_start()
while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    request_line = cl_file.readline().decode('utf-8').strip()
    print(request_line)

    # Parse the URL for GET parameters
    match = ure.search(r'/\?input=(.*?)&x_axis=(.*?)&y_axis=(.*?) ', request_line)
    if match:
        input_text = match.group(1).replace('%20', ' ')
        x_axis = int(match.group(2).replace('%20', ' '))
        y_axis = int(match.group(3).replace('%20', ' '))
        if input_text=="kill":
            print_text(input_text, 120, 60,color=LCD.red)
            LCD.show()
            LCD = 0
            exit()
        if y_axis or x_axis <0:
            LCD.fill(0x0000)
            LCD.show()
        if y_axis>125:
            y_axis = 125
        if y_axis and x_axis >=0:
            print_text(input_text, x_axis, y_axis)
        
        print('Input:', input_text)
        print('X Axis:', x_axis)
        print('Y Axis:', y_axis)
        
    else:
        pass

    # Read and ignore the rest of the request headers
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break

    cl.send('HTTP/1.1 200 OK\n')
    cl.send('Content-Type: text/plain\n')
    cl.send('Connection: close\n\n')
    cl.sendall("\n")
    cl.close()


