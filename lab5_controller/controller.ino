#include <M5StickCPlus.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>

const int button = 37; // G37 on M5StickC

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BUTTON_UUID "e672f43d-ee01-4e48-bf96-4e772413c930"


BLEServer* pServer = NULL; 
BLECharacteristic* pButton = NULL;
bool deviceConnected = false;
bool advertising = false;

int num = 0;

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t *param) {
    Serial.println("Device connected");
    deviceConnected = true;
    advertising = false;
  };
  
  void onDisconnect(BLEServer* pServer) {
    Serial.println("Device disconnected");
    deviceConnected = false;
  }
};

void setup() {

  M5.begin(); 

  // Service Config
  BLEDevice::init("M5StickCPlus-Maddie");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Button Characterisitc Config
  pButton = pService->createCharacteristic(
                      BUTTON_UUID,
                      BLECharacteristic::PROPERTY_READ    |
                      BLECharacteristic::PROPERTY_NOTIFY 
                    );
  pButton->addDescriptor(new BLE2902());

  pService->start();
  BLEDevice::startAdvertising();

  M5.IMU.Init(); //initializing accelerometer

  pinMode(button, INPUT_PULLUP); // Set up button
}

#pragma pack(1) //force tight packing
typedef struct {
  uint8_t buttonA;
} Packet;

void send_status(uint8_t ping)
{
  Packet p;  
  p.buttonA = ping;
  pButton->setValue((uint8_t*)&p, sizeof(Packet));
  pButton->notify();

}

int button_press = 0;
int ping = 0;

void loop(){  

if (deviceConnected)
{

  Packet p;
  send_status(ping);

  if(digitalRead(37)==LOW && !button_press)
  {
    ping = 1;    
    send_status(ping);

    button_press = 1;
    Serial.println("Button press.");
  }

  if(digitalRead(37)==HIGH && button_press)
  {
    ping = 0;    
    send_status(ping);

    button_press = 0;
    Serial.println("Button off.");
  }

  
delay(1); // bluetooth stack will go into congestion, if too many packets are sent
  
}

if (!deviceConnected && !advertising){

delay(500); // give the bluetooth stack the chance to get things ready
BLEDevice::startAdvertising();
Serial.println("Starting advertising...");
advertising = true;

}


}
